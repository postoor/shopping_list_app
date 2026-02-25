"""
ShoppingPlan 路由：建立計畫、勾除物品、完成計畫並轉存購買紀錄
"""
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.item import Item, ItemStatus
from app.models.plan import ShoppingPlan, PlanItem, PlanStatus, PurchaseRecord
from app.schemas import PlanCreate, PlanUpdate, PlanOut, PlanItemToggle, PurchaseRecordOut

router = APIRouter(prefix="/plans", tags=["Shopping Plans"])


async def _get_plan_or_404(plan_id: UUID, db: AsyncSession) -> ShoppingPlan:
    result = await db.execute(
        select(ShoppingPlan)
        .options(selectinload(ShoppingPlan.plan_items))
        .where(ShoppingPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="購物計畫不存在")
    return plan


@router.post("", response_model=PlanOut, status_code=201)
async def create_plan(
    body: PlanCreate,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    plan = ShoppingPlan(
        name       = body.name,
        creator_id = me.id,
        group_id   = body.group_id,
        exec_date  = body.exec_date,
    )
    db.add(plan)
    await db.flush()

    # 加入物品
    for item_id in body.item_ids:
        result = await db.execute(select(Item).where(Item.id == item_id, Item.owner_id == me.id))
        item   = result.scalar_one_or_none()
        if item:
            db.add(PlanItem(plan_id=plan.id, item_id=item_id))
            item.status = ItemStatus.shopping   # 標記為購物中

    await db.commit()
    await db.refresh(plan)
    return plan


@router.get("", response_model=list[PlanOut])
async def list_plans(
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ShoppingPlan)
        .options(selectinload(ShoppingPlan.plan_items))
        .where(ShoppingPlan.creator_id == me.id)
        .order_by(ShoppingPlan.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{plan_id}", response_model=PlanOut)
async def get_plan(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    plan = await _get_plan_or_404(plan_id, db)
    if plan.creator_id != me.id:
        raise HTTPException(status_code=403, detail="無權限查看")
    return plan


@router.patch("/{plan_id}", response_model=PlanOut)
async def update_plan(
    plan_id: UUID,
    body: PlanUpdate,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    plan = await _get_plan_or_404(plan_id, db)
    if plan.creator_id != me.id:
        raise HTTPException(status_code=403, detail="無權限修改")
    for field, val in body.model_dump(exclude_none=True).items():
        setattr(plan, field, val)
    await db.commit()
    await db.refresh(plan)
    return plan


# ── 勾除計畫中的單一物品 ─────────────────────────────────────────────────
@router.patch("/{plan_id}/items/{plan_item_id}", response_model=PlanOut)
async def toggle_plan_item(
    plan_id:      UUID,
    plan_item_id: UUID,
    body:         PlanItemToggle,
    db:           AsyncSession = Depends(get_db),
    me:           User = Depends(get_current_user),
):
    plan = await _get_plan_or_404(plan_id, db)
    if plan.creator_id != me.id:
        raise HTTPException(status_code=403, detail="無權限")

    result     = await db.execute(select(PlanItem).where(PlanItem.id == plan_item_id, PlanItem.plan_id == plan_id))
    plan_item  = result.scalar_one_or_none()
    if not plan_item:
        raise HTTPException(status_code=404, detail="計畫物品不存在")

    plan_item.is_done = body.is_done
    await db.commit()
    await db.refresh(plan)
    return plan


# ── 完成計畫：全部打勾並轉存購買紀錄 ────────────────────────────────────
@router.post("/{plan_id}/complete", response_model=PlanOut)
async def complete_plan(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    plan = await _get_plan_or_404(plan_id, db)
    if plan.creator_id != me.id:
        raise HTTPException(status_code=403, detail="無權限")
    if plan.status == PlanStatus.completed:
        raise HTTPException(status_code=400, detail="計畫已完成")

    for pi in plan.plan_items:
        result = await db.execute(select(Item).where(Item.id == pi.item_id))
        item   = result.scalar_one_or_none()
        if item:
            # 轉存購買紀錄
            db.add(PurchaseRecord(
                plan_id      = plan.id,
                item_name    = item.name,
                quantity     = item.quantity,
                actual_price = item.est_price,
                category     = item.category.value,
                note         = item.note,
            ))
            # 更新物品狀態
            item.status = ItemStatus.purchased

    plan.status       = PlanStatus.completed
    plan.completed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(plan)
    return plan


# ── 購買紀錄查詢 ──────────────────────────────────────────────────────────
@router.get("/{plan_id}/records", response_model=list[PurchaseRecordOut])
async def list_records(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    plan = await _get_plan_or_404(plan_id, db)
    if plan.creator_id != me.id:
        raise HTTPException(status_code=403, detail="無權限")
    result = await db.execute(
        select(PurchaseRecord).where(PurchaseRecord.plan_id == plan_id)
        .order_by(PurchaseRecord.purchased_at.desc())
    )
    return result.scalars().all()


@router.delete("/{plan_id}", status_code=204)
async def delete_plan(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user),
):
    plan = await _get_plan_or_404(plan_id, db)
    if plan.creator_id != me.id:
        raise HTTPException(status_code=403, detail="無權限刪除")
    await db.delete(plan)
    await db.commit()
