"""
Group 路由：建立/管理群組與成員
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.group import Group, GroupMember, GroupRole
from app.schemas import (
    GroupCreate,
    GroupUpdate,
    GroupOut,
    GroupMemberAdd,
    GroupMemberOut,
)

router = APIRouter(prefix="/groups", tags=["Groups"])


def _group_to_dict(group: Group) -> dict:
    """Convert group to dict with user_name in members"""
    return {
        "id": group.id,
        "name": group.name,
        "creator_id": group.creator_id,
        "created_at": group.created_at,
        "members": [
            {
                "user_id": m.user_id,
                "user_name": m.user.name if m.user else None,
                "role": m.role,
                "joined_at": m.joined_at,
            }
            for m in group.members
        ],
    }


async def _get_group_or_404(group_id: UUID, db: AsyncSession) -> Group:
    result = await db.execute(
        select(Group)
        .options(selectinload(Group.members).selectinload(GroupMember.user))
        .where(Group.id == group_id)
    )
    g = result.scalar_one_or_none()
    if not g:
        raise HTTPException(status_code=404, detail="群組不存在")
    return g


@router.post("", response_model=GroupOut, status_code=201)
async def create_group(
    body: GroupCreate,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    group = Group(name=body.name, creator_id=me.id)
    db.add(group)
    await db.flush()
    # 建立者自動加入，角色 owner
    db.add(GroupMember(group_id=group.id, user_id=me.id, role=GroupRole.owner))
    await db.commit()
    # Re-fetch with members loaded
    group = await _get_group_or_404(group.id, db)
    return _group_to_dict(group)


@router.get("", response_model=list[GroupOut])
async def list_groups(
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Group)
        .options(selectinload(Group.members).selectinload(GroupMember.user))
        .join(GroupMember)
        .where(GroupMember.user_id == me.id)
    )
    groups = result.scalars().all()
    return [_group_to_dict(g) for g in groups]


@router.get("/{group_id}", response_model=GroupOut)
async def get_group(
    group_id: UUID,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    group = await _get_group_or_404(group_id, db)
    _assert_member(group, me)
    return _group_to_dict(group)


@router.patch("/{group_id}", response_model=GroupOut)
async def update_group(
    group_id: UUID,
    body: GroupUpdate,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    group = await _get_group_or_404(group_id, db)
    if group.creator_id != me.id:
        raise HTTPException(status_code=403, detail="只有建立者可修改群組")
    if body.name:
        group.name = body.name
    await db.commit()
    # Re-fetch with members loaded
    group = await _get_group_or_404(group_id, db)
    return _group_to_dict(group)


@router.delete("/{group_id}", status_code=204)
async def delete_group(
    group_id: UUID,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    group = await _get_group_or_404(group_id, db)
    if group.creator_id != me.id:
        raise HTTPException(status_code=403, detail="只有建立者可刪除群組")
    await db.delete(group)
    await db.commit()


# ── 成員管理 ─────────────────────────────────────────────────────────────
@router.post("/{group_id}/members", response_model=GroupMemberOut, status_code=201)
async def add_member(
    group_id: UUID,
    body: GroupMemberAdd,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    group = await _get_group_or_404(group_id, db)
    if group.creator_id != me.id:
        raise HTTPException(status_code=403, detail="只有建立者可新增成員")

    existing = (
        await db.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id, GroupMember.user_id == body.user_id
            )
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="使用者已在群組中")

    member = GroupMember(group_id=group_id, user_id=body.user_id, role=body.role)
    db.add(member)
    await db.commit()
    # Refresh with user loaded
    result = await db.execute(
        select(GroupMember)
        .options(selectinload(GroupMember.user))
        .where(GroupMember.group_id == group_id, GroupMember.user_id == body.user_id)
    )
    member = result.scalar_one()
    return {
        "user_id": member.user_id,
        "user_name": member.user.name if member.user else None,
        "role": member.role,
        "joined_at": member.joined_at,
    }


@router.get("/{group_id}/members", response_model=list[GroupMemberOut])
async def list_members(
    group_id: UUID,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    group = await _get_group_or_404(group_id, db)
    _assert_member(group, me)
    result = await db.execute(
        select(GroupMember).where(GroupMember.group_id == group_id)
    )
    return result.scalars().all()


@router.delete("/{group_id}/members/{user_id}", status_code=204)
async def remove_member(
    group_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    group = await _get_group_or_404(group_id, db)
    if group.creator_id != me.id and str(me.id) != str(user_id):
        raise HTTPException(status_code=403, detail="無權限移除成員")

    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id, GroupMember.user_id == user_id
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="成員不存在")
    await db.delete(member)
    await db.commit()


def _assert_member(group: Group, me: User):
    ids = [str(m.user_id) for m in group.members]
    if str(me.id) not in ids and str(group.creator_id) != str(me.id):
        raise HTTPException(status_code=403, detail="非群組成員")
