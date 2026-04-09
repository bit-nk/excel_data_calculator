import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_user, require_role
from app.models.users import User
from app.models.enums import UserRole, ChargebackStatus
from app.models.chargeback import ChargebackReport
from app.schemas.chargeback import (
    ChargebackReportResponse,
    ChargebackSummaryByBU,
    GenerateReportRequest,
)
from app.schemas.validators import validated_billing_period, validated_optional_billing_period
from app.services.chargeback import ChargebackEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chargeback", tags=["Chargeback Reports"])


@router.post("/generate", response_model=ChargebackReportResponse)
async def generate_chargeback_report(
    request: GenerateReportRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.ADMIN, UserRole.FINANCE)),
):
    logger.info("Chargeback report generation requested by user_id=%s for %s", user.id, request.billing_period)
    engine = ChargebackEngine(db)
    report = await engine.generate_report(
        billing_period=request.billing_period,
        generated_by=user.id,
    )
    await db.refresh(report, ["line_items"])
    return report


@router.get("/reports", response_model=list[ChargebackReportResponse])
async def list_reports(
    billing_period: str | None = Depends(validated_optional_billing_period),
    status: ChargebackStatus | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    query = select(ChargebackReport).options(selectinload(ChargebackReport.line_items))

    if billing_period:
        query = query.where(ChargebackReport.billing_period == billing_period)
    if status:
        query = query.where(ChargebackReport.status == status)

    query = query.order_by(ChargebackReport.generated_at.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/reports/{report_id}", response_model=ChargebackReportResponse)
async def get_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    result = await db.execute(
        select(ChargebackReport)
        .options(selectinload(ChargebackReport.line_items))
        .where(ChargebackReport.id == report_id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Not found")
    return report


@router.post("/reports/{report_id}/approve")
async def approve_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.ADMIN, UserRole.FINANCE)),
):
    result = await db.execute(
        select(ChargebackReport).where(ChargebackReport.id == report_id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Not found")

    if report.status == ChargebackStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Report already approved")

    report.status = ChargebackStatus.APPROVED
    report.approved_by = user.id
    report.approved_at = datetime.now(timezone.utc)
    await db.flush()

    logger.info("Report %s approved by user_id=%s", report_id, user.id)
    return {"message": "Report approved", "report_id": report_id}


@router.get("/summary", response_model=list[ChargebackSummaryByBU])
async def chargeback_summary(
    billing_period: str = Depends(validated_billing_period),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    """Get chargeback summary grouped by business unit with per-platform breakdown."""
    result = await db.execute(
        select(ChargebackReport)
        .options(selectinload(ChargebackReport.line_items))
        .where(ChargebackReport.billing_period == billing_period)
        .order_by(ChargebackReport.generated_at.desc())
    )
    report = result.scalars().first()
    if not report:
        return []

    bu_data: dict[int, dict] = {}
    for item in report.line_items:
        bu_id = item.business_unit_id
        if bu_id not in bu_data:
            bu_data[bu_id] = {
                "business_unit_name": "",
                "business_unit_code": "",
                "aws_cost": 0, "mongodb_cost": 0, "datadog_cost": 0,
                "confluent_cost": 0, "singlestore_cost": 0, "harness_cost": 0,
                "total_direct": 0, "shared_allocation": 0,
                "management_fee": 0, "grand_total": 0,
            }

        platform_key = f"{item.platform}_cost"
        if platform_key in bu_data[bu_id]:
            bu_data[bu_id][platform_key] += item.direct_cost

        bu_data[bu_id]["total_direct"] += item.direct_cost
        bu_data[bu_id]["shared_allocation"] += item.shared_cost_allocation
        bu_data[bu_id]["management_fee"] += item.management_fee
        bu_data[bu_id]["grand_total"] += item.total_cost

    return [ChargebackSummaryByBU(**data) for data in bu_data.values()]
