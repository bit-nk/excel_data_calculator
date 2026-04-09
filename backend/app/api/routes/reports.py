"""PDF report generation endpoints for all report types."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.schemas.validators import validated_billing_period

router = APIRouter(prefix="/reports", tags=["PDF Reports"])


@router.get("/anomaly-detection")
async def anomaly_detection_report(
    billing_period: str = Depends(validated_billing_period),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    return {"report": "anomaly_detection", "period": billing_period, "status": "pending"}


@router.get("/reserved-instance")
async def reserved_instance_report(
    billing_period: str = Depends(validated_billing_period),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    return {"report": "reserved_instance", "period": billing_period, "status": "pending"}


@router.get("/tag-compliance")
async def tag_compliance_report(
    billing_period: str = Depends(validated_billing_period),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    return {"report": "tag_compliance", "period": billing_period, "status": "pending"}


@router.get("/multi-cloud-comparison")
async def multi_cloud_comparison_report(
    billing_period: str = Depends(validated_billing_period),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    return {"report": "multi_cloud_comparison", "period": billing_period, "status": "pending"}


@router.get("/sustainability")
async def sustainability_report(
    billing_period: str = Depends(validated_billing_period),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    return {"report": "sustainability", "period": billing_period, "status": "pending"}
