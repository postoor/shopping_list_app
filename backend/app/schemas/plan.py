from __future__ import annotations
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.models.plan import PlanStatus


class PlanCreate(BaseModel):
    name:      str = Field(min_length=1, max_length=200)
    exec_date: date | None = None
    group_id:  UUID | None = None
    item_ids:  list[UUID] = []      # 加入計畫的物品 IDs


class PlanUpdate(BaseModel):
    name:      str | None = Field(default=None, max_length=200)
    exec_date: date | None = None
    status:    PlanStatus | None = None


class PlanItemToggle(BaseModel):
    is_done: bool


class PlanItemOut(BaseModel):
    id:      UUID
    item_id: UUID
    is_done: bool

    model_config = {"from_attributes": True}


class PlanOut(BaseModel):
    id:           UUID
    name:         str
    creator_id:   UUID
    group_id:     UUID | None
    exec_date:    date | None
    status:       PlanStatus
    created_at:   datetime
    completed_at: datetime | None
    plan_items:   list[PlanItemOut] = []

    model_config = {"from_attributes": True}


class PurchaseRecordOut(BaseModel):
    id:           UUID
    plan_id:      UUID
    item_name:    str
    quantity:     int
    actual_price: Decimal | None
    category:     str | None
    note:         str | None
    purchased_at: datetime

    model_config = {"from_attributes": True}
