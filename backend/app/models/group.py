"""
Group / GroupMember 模型
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
import enum


class GroupRole(str, enum.Enum):
    owner  = "owner"
    editor = "editor"
    viewer = "viewer"


class Group(Base):
    __tablename__ = "groups"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name       = Column(String(200), nullable=False)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", back_populates="groups_owned")
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    items   = relationship("Item", back_populates="group")
    plans   = relationship("ShoppingPlan", back_populates="group")


class GroupMember(Base):
    __tablename__ = "group_members"

    group_id   = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id",  ondelete="CASCADE"), primary_key=True)
    role       = Column(Enum(GroupRole), nullable=False, default=GroupRole.viewer)
    joined_at  = Column(DateTime, default=datetime.utcnow)

    group = relationship("Group", back_populates="members")
    user  = relationship("User", back_populates="group_members")
