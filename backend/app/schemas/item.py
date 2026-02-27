from __future__ import annotations
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.models.item import ItemCategory, ItemStatus, SharePermission


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    quantity: int = Field(ge=1, default=1)
    est_price: Decimal | None = None
    category: ItemCategory = ItemCategory.essential
    brand_note: str | None = None
    note: str | None = None
    group_id: UUID | None = None


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    quantity: int | None = Field(default=None, ge=1)
    est_price: Decimal | None = None
    category: ItemCategory | None = None
    status: ItemStatus | None = None
    brand_note: str | None = None
    note: str | None = None


class ItemOut(BaseModel):
    id: UUID
    owner_id: UUID
    group_id: UUID | None
    name: str
    quantity: int
    est_price: Decimal | None
    category: ItemCategory
    status: ItemStatus
    brand_note: str | None
    note: str | None
    created_at: datetime
    updated_at: datetime
    is_shared: bool = False  # 是否為被分享的物品

    model_config = {"from_attributes": True}


class ItemShareCreate(BaseModel):
    shared_with: UUID
    permission: SharePermission = SharePermission.view


class ItemShareOut(BaseModel):
    id: UUID
    item_id: UUID
    shared_with: UUID
    permission: SharePermission
    created_at: datetime

    model_config = {"from_attributes": True}
