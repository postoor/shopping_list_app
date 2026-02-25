"""
User / Friendship / InvitationToken 模型
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Boolean, DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


# ── 好友關係 (自關聯 M2M) ──────────────────────────────────────────────────
class Friendship(Base):
    __tablename__ = "friendships"

    requester_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    addressee_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    # pending | accepted | rejected
    status       = Column(String(16), nullable=False, default="accepted")
    created_at   = Column(DateTime, default=datetime.utcnow)


# ── 使用者 ────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email      = Column(String(255), unique=True, nullable=False, index=True)
    hashed_pw  = Column(String(255), nullable=False)
    name       = Column(String(100), nullable=False)
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 好友 (我發出的)
    sent_requests = relationship(
        "Friendship",
        foreign_keys=[Friendship.requester_id],
        backref="requester",
        cascade="all, delete-orphan",
    )
    # 好友 (我收到的)
    received_requests = relationship(
        "Friendship",
        foreign_keys=[Friendship.addressee_id],
        backref="addressee",
        cascade="all, delete-orphan",
    )

    items         = relationship("Item", back_populates="owner", cascade="all, delete-orphan")
    groups_owned  = relationship("Group", back_populates="creator", cascade="all, delete-orphan")
    group_members = relationship("GroupMember", back_populates="user", cascade="all, delete-orphan")
    plans         = relationship("ShoppingPlan", back_populates="creator", cascade="all, delete-orphan")
    invitations   = relationship("InvitationToken", back_populates="inviter", cascade="all, delete-orphan")


# ── 邀請 Token ──────────────────────────────────────────────────────────
class InvitationToken(Base):
    __tablename__ = "invitation_tokens"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token       = Column(String(255), unique=True, nullable=False, index=True)
    inviter_id  = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    invitee_email = Column(String(255), nullable=False)
    is_used     = Column(Boolean, default=False)
    expires_at  = Column(DateTime, nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow)

    inviter = relationship("User", back_populates="invitations")
