"""Report generation endpoints.

Includes the accounting ledger export (SoW §4.3 / §8). The analytical PDF
reports (anomaly detection, reserved-instance, etc.) remain pending and are
not part of the core chargeback SoW scope.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_permission
from app.core.database import get_db
from app.models.chargeback import ChargebackReport
from app.models.enums import ChargebackStatus
from app.schemas.validators import validated_billing_period
from app.services.ledger import LedgerExporter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["Reports"])


# --- Accounting ledger export (SoW §4.3) -----------------------------------

@router.get(
    "/ledger/{report_id}.csv",
    response_class=Response,
    summary="Download accounting ledger as CSV",
)
async def ledger_csv(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("export_ledger")),
):
    exporter = LedgerExporter(db)
    try:
        data = await exporter.to_csv(report_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    logger.info("Ledger CSV exported: report_id=%s user_id=%s", report_id, user.id)
    filename = f"ledger_{report_id}.csv"
    return Response(
        content=data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/ledger/{report_id}.xlsx",
    response_class=Response,
    summary="Download accounting ledger as XLSX",
)
async def ledger_xlsx(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("export_ledger")),
):
    exporter = LedgerExporter(db)
    try:
        data = await exporter.to_xlsx(report_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    logger.info("Ledger XLSX exported: report_id=%s user_id=%s", report_id, user.id)
    filename = f"ledger_{report_id}.xlsx"
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/ledger/{report_id}/mark-sent")
async def ledger_mark_sent(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("export_ledger")),
):
    result = await db.execute(select(ChargebackReport).where(ChargebackReport.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.status != ChargebackStatus.APPROVED:
        raise HTTPException(status_code=409, detail="Report must be APPROVED to mark as sent")

    report.status = ChargebackStatus.SENT_TO_ACCOUNTING
    await db.flush()
    logger.info("Report %s marked SENT_TO_ACCOUNTING by user_id=%s", report_id, user.id)
    return {"report_id": report_id, "status": report.status}


# --- Analytical report stubs (out of SoW core scope) -----------------------

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
