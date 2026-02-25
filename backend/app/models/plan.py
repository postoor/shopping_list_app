"""
ShoppingPlan / PlanItem / PurchaseRecord 模型
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Date, DateTime, Boolean, Numeric, Integer, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
import enum


class PlanStatus(str, enum.Enum):
    ongoing   = "ongoing"    # 進行中
    completed = "completed"  # 已完成


class ShoppingPlan(Base):
    __tablename__ = "shopping_plans"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name        = Column(String(200), nullable=False)
    creator_id  = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    group_id    = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="SET NULL"), nullable=True)
    exec_date   = Column(Date, nullable=True)           # 執行日期
    status      = Column(Enum(PlanStatus), nullable=False, default=PlanStatus.ongoing)
    created_at  = Column(DateTime, default=datetime.utcnow)
    completed_at= Column(DateTime, nullable=True)

    creator     = relationship("User", back_populates="plans")
    group       = relationship("Group", back_populates="plans")
    plan_items  = relationship("PlanItem", back_populates="plan", cascade="all, delete-orphan")
    records     = relationship("PurchaseRecord", back_populates="plan", cascade="all, delete-orphan")


class PlanItem(Base):
    """購物計畫中包含的物品"""
    __tablename__ = "plan_items"

    id       = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id  = Column(UUID(as_uuid=True), ForeignKey("shopping_plans.id", ondelete="CASCADE"), nullable=False)
    item_id  = Column(UUID(as_uuid=True), ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    is_done  = Column(Boolean, default=False)  # 購物時勾除

    plan = relationship("ShoppingPlan", back_populates="plan_items")
    item = relationship("Item", back_populates="plan_items")


class PurchaseRecord(Base):
    """計畫完成後自動轉存的購買紀錄"""
    __tablename__ = "purchase_records"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id      = Column(UUID(as_uuid=True), ForeignKey("shopping_plans.id", ondelete="CASCADE"), nullable=False)
    item_name    = Column(String(200), nullable=False)   # 快照：物品名稱
    quantity     = Column(Integer, nullable=False)
    actual_price = Column(Numeric(10, 2), nullable=True) # 實際購買價格
    category     = Column(String(50), nullable=True)
    note         = Column(Text, nullable=True)
    purchased_at = Column(DateTime, default=datetime.utcnow)

    plan = relationship("ShoppingPlan", back_populates="records")
