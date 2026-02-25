"""
好友 & 邀請 路由
"""
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.user import User, Friendship, InvitationToken
from app.schemas import InvitationCreate, InvitationOut, FriendOut
from app.services.email import send_invitation_email

router = APIRouter(prefix="/friends", tags=["Friends & Invitations"])


# ── 取得好友清單 ──────────────────────────────────────────────────────────
@router.get("", response_model=list[FriendOut])
async def list_friends(
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    result = await db.execute(
        select(User).join(
            Friendship,
            or_(
                and_(Friendship.requester_id == me.id, Friendship.addressee_id == User.id),
                and_(Friendship.addressee_id == me.id, Friendship.requester_id == User.id),
            ),
        ).where(User.id != me.id)
    )
    return result.scalars().all()


# ── 移除好友 ─────────────────────────────────────────────────────────────
@router.delete("/{friend_id}", status_code=204)
async def remove_friend(
    friend_id: str,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Friendship).where(
            or_(
                and_(Friendship.requester_id == me.id,     Friendship.addressee_id == friend_id),
                and_(Friendship.requester_id == friend_id, Friendship.addressee_id == me.id),
            )
        )
    )
    rows = result.scalars().all()
    for row in rows:
        await db.delete(row)
    await db.commit()


# ── 寄送邀請信 ───────────────────────────────────────────────────────────
@router.post("/invite", response_model=InvitationOut, status_code=201)
async def invite_friend(
    body: InvitationCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    # 不能邀請自己
    if body.invitee_email == me.email:
        raise HTTPException(status_code=400, detail="不能邀請自己")

    # 若對方已是好友
    existing_user = (await db.execute(
        select(User).where(User.email == body.invitee_email)
    )).scalar_one_or_none()

    if existing_user:
        already = (await db.execute(
            select(Friendship).where(
                or_(
                    and_(Friendship.requester_id == me.id,             Friendship.addressee_id == existing_user.id),
                    and_(Friendship.requester_id == existing_user.id,  Friendship.addressee_id == me.id),
                )
            )
        )).scalar_one_or_none()
        if already:
            raise HTTPException(status_code=400, detail="對方已是好友")

    token_str  = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=settings.INVITATION_EXPIRE_HOURS)

    inv = InvitationToken(
        token         = token_str,
        inviter_id    = me.id,
        invitee_email = body.invitee_email,
        expires_at    = expires_at,
    )
    db.add(inv)
    await db.commit()
    await db.refresh(inv)

    # 背景發信
    background_tasks.add_task(
        send_invitation_email,
        to_email   = body.invitee_email,
        inviter_name = me.name,
        token      = token_str,
    )
    return inv


# ── 查詢邀請列表 ─────────────────────────────────────────────────────────
@router.get("/invitations", response_model=list[InvitationOut])
async def list_invitations(
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    result = await db.execute(
        select(InvitationToken).where(InvitationToken.inviter_id == me.id)
        .order_by(InvitationToken.created_at.desc())
    )
    return result.scalars().all()
