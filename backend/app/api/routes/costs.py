from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.cost_records import CostRecord
from app.models.users import User
from app.models.enums import Platform, CostCategory, UserRole
from app.schemas.cost import CostRecordResponse
from app.schemas.chargeback import CostBreakdownByPlatform, CostTrendPoint
from app.schemas.validators import (
    validated_billing_period,
    validated_optional_billing_period,
    validate_date_range,
)

router = APIRouter(prefix="/costs", tags=["Cost Data"])


def _apply_bu_scope(query, user: User):
    """Restrict query to user's business unit unless they have full access."""
    if user.role and user.role.name in (UserRole.ADMIN.value, UserRole.FINANCE.value):
        return query  # Full access
    if user.business_unit_id:
        return query.where(CostRecord.business_unit_id == user.business_unit_id)
    return query.where(CostRecord.business_unit_id == -1)  # No BU assigned = no data


@router.get("/", response_model=list[CostRecordResponse])
async def list_costs(
    platform: Optional[Platform] = None,
    billing_period: Optional[str] = Depends(validated_optional_billing_period),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    business_unit_id: Optional[int] = None,
    cost_code: Optional[str] = Query(None, max_length=50),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    validate_date_range(start_date, end_date)

    query = select(CostRecord)

    # Row-level security: scope by user role
    await db.refresh(user, ["role"])
    query = _apply_bu_scope(query, user)

    if platform:
        query = query.where(CostRecord.platform == platform)
    if billing_period:
        query = query.where(CostRecord.billing_period == billing_period)
    if start_date:
        query = query.where(CostRecord.usage_date >= start_date)
    if end_date:
        query = query.where(CostRecord.usage_date <= end_date)
    if business_unit_id:
        query = query.where(CostRecord.business_unit_id == business_unit_id)
    if cost_code:
        query = query.where(CostRecord.cost_code == cost_code)

    query = query.order_by(CostRecord.usage_date.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/breakdown-by-platform", response_model=list[CostBreakdownByPlatform])
async def cost_breakdown_by_platform(
    billing_period: str = Depends(validated_billing_period),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    base_query = (
        select(CostRecord.platform, func.sum(CostRecord.unblended_cost).label("total"))
        .where(CostRecord.billing_period == billing_period)
        .group_by(CostRecord.platform)
    )

    await db.refresh(user, ["role"])
    base_query = _apply_bu_scope(base_query, user)

    result = await db.execute(base_query)
    rows = result.all()
    grand_total = sum(r.total for r in rows) or 1

    return [
        CostBreakdownByPlatform(
            platform=row.platform,
            total_cost=row.total,
            percentage=round(row.total / grand_total * 100, 2),
        )
        for row in rows
    ]


@router.get("/trend", response_model=list[CostTrendPoint])
async def cost_trend(
    months: int = Query(default=6, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    base_query = (
        select(
            CostRecord.billing_period,
            CostRecord.platform,
            func.sum(CostRecord.unblended_cost).label("total"),
        )
        .group_by(CostRecord.billing_period, CostRecord.platform)
        .order_by(CostRecord.billing_period.desc())
    )

    await db.refresh(user, ["role"])
    base_query = _apply_bu_scope(base_query, user)

    result = await db.execute(base_query)

    trends: dict[str, CostTrendPoint] = {}
    for row in result.all():
        period = row.billing_period
        if period not in trends:
            trends[period] = CostTrendPoint(period=period, total_cost=0)
        trends[period].total_cost += row.total
        trends[period].by_platform[row.platform] = row.total

    sorted_trends = sorted(trends.values(), key=lambda t: t.period, reverse=True)
    return sorted_trends[:months]
