"""
ShoppingPlan 路由：建立計畫、勾除物品、完成計畫並轉存購買紀錄、分享計畫
"""

from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User, Friendship
from app.models.item import Item, ItemStatus
from app.models.plan import (
    ShoppingPlan,
    PlanItem,
    PlanStatus,
    PurchaseRecord,
    PlanShare,
    PlanSharePermission,
)
from app.schemas import (
    PlanCreate,
    PlanUpdate,
    PlanOut,
    PlanItemToggle,
    PurchaseRecordOut,
    PlanShareCreate,
    PlanShareOut,
)

router = APIRouter(prefix="/plans", tags=["Shopping Plans"])


async def _get_plan_or_404(plan_id: UUID, db: AsyncSession) -> ShoppingPlan:
    result = await db.execute(
        select(ShoppingPlan)
        .options(selectinload(ShoppingPlan.plan_items))
        .where(ShoppingPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="購物計畫不存在")
    return plan


async def _can_view_plan(
    plan: ShoppingPlan, me: User, db: AsyncSession
) -> PlanShare | None:
    """確認使用者是 creator 或有任何共享權限，回傳 share 記錄或 None"""
    if plan.creator_id == me.id:
        return None  # None 表示是 creator
    share = (
        await db.execute(
            select(PlanShare).where(
                PlanShare.plan_id == plan.id,
                PlanShare.shared_with == me.id,
            )
        )
    ).scalar_one_or_none()
    return share


async def _can_edit_plan(plan: ShoppingPlan, me: User, db: AsyncSession) -> bool:
    """確認使用者是 creator 或有 edit 共享權限"""
    if plan.creator_id == me.id:
        return True
    share = (
        await db.execute(
            select(PlanShare).where(
                PlanShare.plan_id == plan.id,
                PlanShare.shared_with == me.id,
                PlanShare.permission == PlanSharePermission.edit,
            )
        )
    ).scalar_one_or_none()
    return share is not None


@router.post("", response_model=PlanOut, status_code=201)
async def create_plan(
    body: PlanCreate,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    plan = ShoppingPlan(
        name=body.name,
        creator_id=me.id,
        group_id=body.group_id,
        exec_date=body.exec_date,
    )
    db.add(plan)
    await db.flush()

    # 加入物品
    for item_id in body.item_ids:
        result = await db.execute(
            select(Item).where(Item.id == item_id, Item.owner_id == me.id)
        )
        item = result.scalar_one_or_none()
        if item:
            db.add(PlanItem(plan_id=plan.id, item_id=item_id))
            item.status = ItemStatus.shopping  # 標記為購物中

    await db.commit()

    # 重新查詢並載入 plan_items 關聯
    result = await db.execute(
        select(ShoppingPlan)
        .options(selectinload(ShoppingPlan.plan_items))
        .where(ShoppingPlan.id == plan.id)
    )
    return result.scalar_one()


@router.get("", response_model=list[PlanOut])
async def list_plans(
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    """列出：我建立的 + 被分享給我的計畫"""
    # 我建立的計畫
    my_plans = (
        (
            await db.execute(
                select(ShoppingPlan)
                .options(selectinload(ShoppingPlan.plan_items))
                .where(ShoppingPlan.creator_id == me.id)
                .order_by(ShoppingPlan.created_at.desc())
            )
        )
        .scalars()
        .all()
    )

    # 被分享給我的計畫 IDs
    shared_plan_ids = (
        (
            await db.execute(
                select(PlanShare.plan_id).where(PlanShare.shared_with == me.id)
            )
        )
        .scalars()
        .all()
    )

    # 載入被分享的計畫
    shared_plans: list[ShoppingPlan] = []
    if shared_plan_ids:
        shared_result = await db.execute(
            select(ShoppingPlan)
            .options(selectinload(ShoppingPlan.plan_items))
            .where(ShoppingPlan.id.in_(shared_plan_ids))
            .order_by(ShoppingPlan.created_at.desc())
        )
        shared_plans = shared_result.scalars().all()

    # 合併去重並標記是否為被分享
    shared_ids_set = set(shared_plan_ids)
    seen, result = set(), []
    for plan in [*my_plans, *shared_plans]:
        if plan.id not in seen:
            seen.add(plan.id)
            plan.is_shared = plan.creator_id != me.id and plan.id in shared_ids_set
            result.append(plan)
    return result


@router.get("/{plan_id}", response_model=PlanOut)
async def get_plan(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    plan = await _get_plan_or_404(plan_id, db)
    share = await _can_view_plan(plan, me, db)
    if plan.creator_id != me.id and share is None:
        raise HTTPException(status_code=403, detail="無權限查看")
    plan.is_shared = share is not None
    return plan


@router.patch("/{plan_id}", response_model=PlanOut)
async def update_plan(
    plan_id: UUID,
    body: PlanUpdate,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    plan = await _get_plan_or_404(plan_id, db)
    if not await _can_edit_plan(plan, me, db):
        raise HTTPException(status_code=403, detail="無權限修改")
    for field, val in body.model_dump(exclude_none=True).items():
        setattr(plan, field, val)
    await db.commit()
    await db.refresh(plan)
    return plan


# ── 勾除計畫中的單一物品 ─────────────────────────────────────────────────
@router.patch("/{plan_id}/items/{plan_item_id}", response_model=PlanOut)
async def toggle_plan_item(
    plan_id: UUID,
    plan_item_id: UUID,
    body: PlanItemToggle,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    plan = await _get_plan_or_404(plan_id, db)
    if not await _can_edit_plan(plan, me, db):
        raise HTTPException(status_code=403, detail="無權限")

    result = await db.execute(
        select(PlanItem).where(PlanItem.id == plan_item_id, PlanItem.plan_id == plan_id)
    )
    plan_item = result.scalar_one_or_none()
    if not plan_item:
        raise HTTPException(status_code=404, detail="計畫物品不存在")

    plan_item.is_done = body.is_done
    await db.commit()
    await db.refresh(plan)
    return plan


# ── 完成計畫：全部打勾並轉存購買紀錄 ────────────────────────────────────
@router.post("/{plan_id}/complete", response_model=PlanOut)
async def complete_plan(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    plan = await _get_plan_or_404(plan_id, db)
    if not await _can_edit_plan(plan, me, db):
        raise HTTPException(status_code=403, detail="無權限")
    if plan.status == PlanStatus.completed:
        raise HTTPException(status_code=400, detail="計畫已完成")

    for pi in plan.plan_items:
        result = await db.execute(select(Item).where(Item.id == pi.item_id))
        item = result.scalar_one_or_none()
        if item:
            # 轉存購買紀錄
            db.add(
                PurchaseRecord(
                    plan_id=plan.id,
                    item_name=item.name,
                    quantity=item.quantity,
                    actual_price=item.est_price,
                    category=item.category.value,
                    note=item.note,
                )
            )
            # 更新物品狀態
            item.status = ItemStatus.purchased

    plan.status = PlanStatus.completed
    plan.completed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(plan)
    return plan


# ── 購買紀錄查詢 ──────────────────────────────────────────────────────────
@router.get("/{plan_id}/records", response_model=list[PurchaseRecordOut])
async def list_records(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    plan = await _get_plan_or_404(plan_id, db)
    share = await _can_view_plan(plan, me, db)
    if plan.creator_id != me.id and share is None:
        raise HTTPException(status_code=403, detail="無權限")
    result = await db.execute(
        select(PurchaseRecord)
        .where(PurchaseRecord.plan_id == plan_id)
        .order_by(PurchaseRecord.purchased_at.desc())
    )
    return result.scalars().all()


@router.delete("/{plan_id}", status_code=204)
async def delete_plan(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    plan = await _get_plan_or_404(plan_id, db)
    if plan.creator_id != me.id:
        raise HTTPException(status_code=403, detail="無權限刪除")
    await db.delete(plan)
    await db.commit()


# ── 計畫共享 ─────────────────────────────────────────────────────────────
@router.post("/{plan_id}/shares", response_model=PlanShareOut, status_code=201)
async def share_plan(
    plan_id: UUID,
    body: PlanShareCreate,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    plan = await _get_plan_or_404(plan_id, db)
    if plan.creator_id != me.id:
        raise HTTPException(status_code=403, detail="只有建立者可分享")

    # 檢查這個 plan 是否是被分享給我的（被分享的計畫不能再分享）
    is_shared_to_me = (
        await db.execute(
            select(PlanShare).where(
                PlanShare.plan_id == plan.id,
                PlanShare.shared_with == me.id,
            )
        )
    ).scalar_one_or_none()
    if is_shared_to_me:
        raise HTTPException(status_code=403, detail="被分享的計畫不能再分享")

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

    # 檢查是否已經分享給該好友
    existing_share = (
        await db.execute(
            select(PlanShare).where(
                PlanShare.plan_id == plan_id,
                PlanShare.shared_with == body.shared_with,
            )
        )
    ).scalar_one_or_none()
    if existing_share:
        raise HTTPException(status_code=400, detail="已分享給該好友")

    share = PlanShare(plan_id=plan_id, **body.model_dump())
    db.add(share)
    await db.commit()
    await db.refresh(share)
    return share


@router.get("/{plan_id}/shares", response_model=list[PlanShareOut])
async def list_plan_shares(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    plan = await _get_plan_or_404(plan_id, db)
    if plan.creator_id != me.id:
        raise HTTPException(status_code=403, detail="無權限查看分享列表")
    result = await db.execute(select(PlanShare).where(PlanShare.plan_id == plan_id))
    return result.scalars().all()


@router.delete("/{plan_id}/shares/{share_id}", status_code=204)
async def revoke_plan_share(
    plan_id: UUID,
    share_id: UUID,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    plan = await _get_plan_or_404(plan_id, db)
    if plan.creator_id != me.id:
        raise HTTPException(status_code=403, detail="無權限撤銷分享")
    result = await db.execute(
        select(PlanShare).where(PlanShare.id == share_id, PlanShare.plan_id == plan_id)
    )
    share = result.scalar_one_or_none()
    if not share:
        raise HTTPException(status_code=404, detail="分享記錄不存在")
    await db.delete(share)
    await db.commit()
