"""
Item CRUD & 共享權限 路由
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User, Friendship
from app.models.item import Item, ItemShare, SharePermission
from app.models.group import GroupMember
from app.schemas import ItemCreate, ItemUpdate, ItemOut, ItemShareCreate, ItemShareOut

router = APIRouter(prefix="/items", tags=["Items"])


async def _get_item_or_404(item_id: UUID, db: AsyncSession) -> Item:
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="物品不存在")
    return item


async def _assert_can_edit(item: Item, me: User, db: AsyncSession):
    """確認使用者是 owner、或有 edit 共享權限、或是群組成員"""
    if item.owner_id == me.id:
        return
    share = (
        await db.execute(
            select(ItemShare).where(
                ItemShare.item_id == item.id,
                ItemShare.shared_with == me.id,
                ItemShare.permission == SharePermission.edit,
            )
        )
    ).scalar_one_or_none()
    if share:
        return
    if item.group_id:
        member = (
            await db.execute(
                select(GroupMember).where(
                    GroupMember.group_id == item.group_id,
                    GroupMember.user_id == me.id,
                )
            )
        ).scalar_one_or_none()
        if member:
            return
    raise HTTPException(status_code=403, detail="無編輯權限")


# ── CRUD ─────────────────────────────────────────────────────────────────
@router.post("", response_model=ItemOut, status_code=201)
async def create_item(
    body: ItemCreate,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    item = Item(**body.model_dump(), owner_id=me.id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("", response_model=list[ItemOut])
async def list_items(
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    """列出：我建立的 + 被分享給我的 + 我加入群組的物品"""
    # 我的物品
    my_items = (
        (await db.execute(select(Item).where(Item.owner_id == me.id))).scalars().all()
    )

    # 被分享給我
    shared_ids = (
        (
            await db.execute(
                select(ItemShare.item_id).where(ItemShare.shared_with == me.id)
            )
        )
        .scalars()
        .all()
    )

    # 群組物品
    my_group_ids = (
        (
            await db.execute(
                select(GroupMember.group_id).where(GroupMember.user_id == me.id)
            )
        )
        .scalars()
        .all()
    )

    extra_items: list[Item] = []
    if shared_ids or my_group_ids:
        extra_result = await db.execute(
            select(Item).where(
                or_(
                    Item.id.in_(shared_ids),
                    Item.group_id.in_(my_group_ids),
                )
            )
        )
        extra_items = extra_result.scalars().all()

    # 合併去重，並標記是否為被分享的物品
    shared_ids_set = set(shared_ids)
    seen, result = set(), []
    for item in [*my_items, *extra_items]:
        if item.id not in seen:
            seen.add(item.id)
            # 標記是否為被分享的物品（非自己建立的）
            item.is_shared = item.owner_id != me.id and item.id in shared_ids_set
            result.append(item)
    return result


@router.get("/{item_id}", response_model=ItemOut)
async def get_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    item = await _get_item_or_404(item_id, db)
    # 簡單讀取權限：owner 或有任何 share 或同群組
    is_shared_item = False
    if item.owner_id != me.id:
        share = (
            await db.execute(
                select(ItemShare).where(
                    ItemShare.item_id == item.id, ItemShare.shared_with == me.id
                )
            )
        ).scalar_one_or_none()
        if not share:
            raise HTTPException(status_code=403, detail="無讀取權限")
        is_shared_item = True
    item.is_shared = is_shared_item
    return item


@router.patch("/{item_id}", response_model=ItemOut)
async def update_item(
    item_id: UUID,
    body: ItemUpdate,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    item = await _get_item_or_404(item_id, db)
    await _assert_can_edit(item, me, db)

    for field, val in body.model_dump(exclude_none=True).items():
        setattr(item, field, val)

    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
async def delete_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    item = await _get_item_or_404(item_id, db)
    if item.owner_id != me.id:
        raise HTTPException(status_code=403, detail="只有建立者可刪除")
    await db.delete(item)
    await db.commit()


# ── 共享 ─────────────────────────────────────────────────────────────────
@router.post("/{item_id}/shares", response_model=ItemShareOut, status_code=201)
async def share_item(
    item_id: UUID,
    body: ItemShareCreate,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    item = await _get_item_or_404(item_id, db)
    if item.owner_id != me.id:
        raise HTTPException(status_code=403, detail="只有建立者可分享")

    # 檢查這個 item 是否是被分享給我的（被分享的物品不能再分享）
    is_shared_to_me = (
        await db.execute(
            select(ItemShare).where(
                ItemShare.item_id == item.id,
                ItemShare.shared_with == me.id,
            )
        )
    ).scalar_one_or_none()
    if is_shared_to_me:
        raise HTTPException(status_code=403, detail="被分享的物品不能再分享")

    # 確認分享對象是好友（已接受的好友關係）
    friendship = (
        (
            await db.execute(
                select(Friendship).where(
                    Friendship.status == "accepted",
                    or_(
                        and_(
                            Friendship.requester_id == me.id,
                            Friendship.addressee_id == body.shared_with,
                        ),
                        and_(
                            Friendship.requester_id == body.shared_with,
                            Friendship.addressee_id == me.id,
                        ),
                    ),
                )
            )
        )
        .scalars()
        .first()
    )
    if not friendship:
        raise HTTPException(status_code=400, detail="只能分享給好友")

    share = ItemShare(item_id=item_id, **body.model_dump())
    db.add(share)
    await db.commit()
    await db.refresh(share)
    return share


@router.get("/{item_id}/shares", response_model=list[ItemShareOut])
async def list_shares(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    item = await _get_item_or_404(item_id, db)
    if item.owner_id != me.id:
        raise HTTPException(status_code=403, detail="無權限查看分享列表")
    result = await db.execute(select(ItemShare).where(ItemShare.item_id == item_id))
    return result.scalars().all()


@router.delete("/{item_id}/shares/{share_id}", status_code=204)
async def revoke_share(
    item_id: UUID,
    share_id: UUID,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    item = await _get_item_or_404(item_id, db)
    if item.owner_id != me.id:
        raise HTTPException(status_code=403, detail="無權限撤銷分享")
    result = await db.execute(
        select(ItemShare).where(ItemShare.id == share_id, ItemShare.item_id == item_id)
    )
    share = result.scalar_one_or_none()
    if not share:
        raise HTTPException(status_code=404, detail="分享記錄不存在")
    await db.delete(share)
    await db.commit()
