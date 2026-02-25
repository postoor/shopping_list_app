from __future__ import annotations
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email:    EmailStr
    password: str = Field(min_length=8)
    name:     str = Field(min_length=1, max_length=100)
    # 透過邀請連結註冊時附帶 token
    invitation_token: str | None = None


class UserLogin(BaseModel):
    email:    EmailStr
    password: str


class UserOut(BaseModel):
    id:         UUID
    email:      str
    name:       str
    is_active:  bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name:     str | None = None
    password: str | None = Field(default=None, min_length=8)


class TokenResponse(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ── 好友 ─────────────────────────────────────────────────────────────────
class FriendOut(BaseModel):
    id:    UUID
    email: str
    name:  str

    model_config = {"from_attributes": True}


# ── 邀請 ─────────────────────────────────────────────────────────────────
class InvitationCreate(BaseModel):
    invitee_email: EmailStr


class InvitationOut(BaseModel):
    id:            UUID
    invitee_email: str
    is_used:       bool
    expires_at:    datetime
    created_at:    datetime

    model_config = {"from_attributes": True}
