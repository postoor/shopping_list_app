"""
Auth 路由：註冊、登入、刷新 Token、個人資料
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.deps import get_current_user
from app.models.user import User, InvitationToken, Friendship
from app.schemas import (
    UserCreate,
    UserLogin,
    UserOut,
    UserUpdate,
    TokenResponse,
    RefreshRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=201)
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)):
    logger.debug(f"Register attempt for email: {body.email}")
    # 檢查 Email 是否已存在
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        logger.debug(f"Registration failed: email {body.email} already exists")
        raise HTTPException(status_code=400, detail="此 Email 已被註冊")

    user = User(
        email=body.email,
        hashed_pw=hash_password(body.password),
        name=body.name,
    )
    db.add(user)
    await db.flush()  # 取得 user.id 供後續使用

    # ── 邀請連結流程：驗證 token 並建立好友關係 ──
    if body.invitation_token:
        logger.debug(f"Processing invitation token for email: {body.email}")
        result = await db.execute(
            select(InvitationToken).where(
                InvitationToken.token == body.invitation_token,
                InvitationToken.is_used == False,
                InvitationToken.invitee_email == body.email,
            )
        )
        inv = result.scalar_one_or_none()
        if inv:
            from datetime import datetime

            if inv.expires_at >= datetime.utcnow():
                # 雙向好友關係
                db.add(Friendship(requester_id=inv.inviter_id, addressee_id=user.id))
                db.add(Friendship(requester_id=user.id, addressee_id=inv.inviter_id))
                inv.is_used = True
                logger.debug(
                    f"Invitation accepted: inviter_id={inv.inviter_id}, invitee_id={user.id}"
                )
            else:
                logger.debug(f"Invitation token expired for email: {body.email}")
        else:
            logger.debug(
                f"Invitation token not found or already used for email: {body.email}"
            )

    await db.commit()
    await db.refresh(user)
    logger.debug(f"User registered successfully: id={user.id}, email={user.email}")
    return user


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)):
    logger.debug(f"Login attempt for email: {body.email}")
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.hashed_pw):
        logger.debug(f"Login failed for email: {body.email} - invalid credentials")
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    if not user.is_active:
        logger.debug(f"Login failed for email: {body.email} - account inactive")
        raise HTTPException(status_code=403, detail="帳號已停用")

    logger.debug(f"Login successful for user id={user.id}")
    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    logger.debug("Token refresh attempt")
    payload = decode_token(body.refresh_token)
    if payload.get("type") != "refresh":
        logger.debug("Token refresh failed: not a refresh token")
        raise HTTPException(status_code=401, detail="需要 Refresh Token")

    user_id = payload.get("sub")
    logger.debug(f"Token refresh for user_id={user_id}")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        logger.debug(f"Token refresh failed: user not found or inactive")
        raise HTTPException(status_code=401, detail="使用者不存在")

    logger.debug(f"Token refresh successful for user_id={user_id}")
    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    logger.debug(f"Get me: user_id={current_user.id}")
    return current_user


@router.patch("/me", response_model=UserOut)
async def update_me(
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.debug(
        f"Update me: user_id={current_user.id}, updates={body.model_dump(exclude_unset=True)}"
    )
    if body.name:
        current_user.name = body.name
    if body.password:
        current_user.hashed_pw = hash_password(body.password)
    await db.commit()
    await db.refresh(current_user)
    logger.debug(f"Update me successful: user_id={current_user.id}")
    return current_user
