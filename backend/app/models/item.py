"""
Item / ItemShare 模型
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Numeric, Text, DateTime, ForeignKey, Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

import enum


class ItemCategory(str, enum.Enum):
    essential     = "essential"      # 必需品
    non_essential = "non_essential"  # 非必需品


class ItemStatus(str, enum.Enum):
    pending    = "pending"     # 待購
    shopping   = "shopping"    # 購物中
    purchased  = "purchased"   # 已購買


class SharePermission(str, enum.Enum):
    view = "view"
    edit = "edit"


class Item(Base):
    __tablename__ = "items"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id     = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    group_id     = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="SET NULL"), nullable=True)

    name         = Column(String(200), nullable=False)
    quantity     = Column(Integer, nullable=False, default=1)
    est_price    = Column(Numeric(10, 2), nullable=True)        # 預估價格
    category     = Column(Enum(ItemCategory), nullable=False, default=ItemCategory.essential)
    status       = Column(Enum(ItemStatus),   nullable=False, default=ItemStatus.pending)

    brand_note   = Column(Text, nullable=True)   # 廠牌偏好 / 備註
    note         = Column(Text, nullable=True)

    created_at   = Column(DateTime, default=datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner        = relationship("User", back_populates="items")
    group        = relationship("Group", back_populates="items")
    shares       = relationship("ItemShare", back_populates="item", cascade="all, delete-orphan")
    plan_items   = relationship("PlanItem", back_populates="item")


class ItemShare(Base):
    """將特定物品分享給好友"""
    __tablename__ = "item_shares"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id     = Column(UUID(as_uuid=True), ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    shared_with = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    permission  = Column(Enum(SharePermission), nullable=False, default=SharePermission.view)
    created_at  = Column(DateTime, default=datetime.utcnow)

    item        = relationship("Item", back_populates="shares")
    user        = relationship("User")
