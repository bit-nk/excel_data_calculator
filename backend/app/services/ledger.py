"""
Accounting ledger export.

Generates the final ledger file (CSV or XLSX) for an approved chargeback report
to be sent to the Accounting department.

Ledger columns follow a standard general-ledger format:
    entry_date, period, account_code, debit, credit, department, portfolio_manager,
    platform, category, description, reference_id, currency

Credits all post to a clearing account (INFRA_CLEARING) and debits to each BU's
cost code, producing a balanced journal per report.
"""

from __future__ import annotations

import csv
import io
import logging
from decimal import Decimal
from typing import Iterable

from openpyxl import Workbook
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.business_units import BusinessUnit, PortfolioManager
from app.models.chargeback import ChargebackLineItem, ChargebackReport
from app.models.enums import ChargebackStatus

logger = logging.getLogger(__name__)

CLEARING_ACCOUNT = "INFRA_CLEARING"
LEDGER_COLUMNS = [
    "entry_date",
    "period",
    "account_code",
    "debit",
    "credit",
    "department",
    "portfolio_manager",
    "platform",
    "category",
    "description",
    "reference_id",
    "currency",
]


class LedgerRow(dict):
    pass


class LedgerExporter:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def build_rows(self, report_id: int) -> list[LedgerRow]:
        report = await self._load_report(report_id)

        if report.status not in (ChargebackStatus.APPROVED, ChargebackStatus.SENT_TO_ACCOUNTING):
            raise ValueError(
                f"Report {report_id} status is {report.status}; must be APPROVED before export"
            )

        bu_ids = {item.business_unit_id for item in report.line_items}
        pm_ids = {item.portfolio_manager_id for item in report.line_items if item.portfolio_manager_id}
        bu_lookup = await self._lookup_bus(bu_ids)
        pm_lookup = await self._lookup_pms(pm_ids)

        entry_date = (report.approved_at or report.generated_at).date().isoformat()
        rows: list[LedgerRow] = []
        total_debit = Decimal("0")

        for item in report.line_items:
            bu = bu_lookup.get(item.business_unit_id)
            pm = pm_lookup.get(item.portfolio_manager_id) if item.portfolio_manager_id else None
            bu_code = bu.code if bu else f"BU_{item.business_unit_id}"
            bu_name = bu.name if bu else ""
            account = item.cost_code or bu_code

            total = (item.direct_cost or 0) + (item.shared_cost_allocation or 0) + (item.management_fee or 0)
            if total == 0:
                continue
            total_debit += total

            rows.append(LedgerRow({
                "entry_date": entry_date,
                "period": report.billing_period,
                "account_code": account,
                "debit": _money(total),
                "credit": _money(Decimal("0")),
                "department": bu_name,
                "portfolio_manager": pm.name if pm else "",
                "platform": _plat(item.platform),
                "category": _cat(item.category),
                "description": _describe(item),
                "reference_id": f"CB-{report.id}-L{item.id}",
                "currency": "USD",
            }))

        # Balancing credit entry to the infra clearing account
        if total_debit > 0:
            rows.append(LedgerRow({
                "entry_date": entry_date,
                "period": report.billing_period,
                "account_code": CLEARING_ACCOUNT,
                "debit": _money(Decimal("0")),
                "credit": _money(total_debit),
                "department": "INFRASTRUCTURE",
                "portfolio_manager": "",
                "platform": "",
                "category": "",
                "description": f"Chargeback clearing for {report.billing_period}",
                "reference_id": f"CB-{report.id}-CLR",
                "currency": "USD",
            }))

        logger.info("Built ledger: report_id=%s rows=%s total=%s", report_id, len(rows), total_debit)
        return rows

    async def to_csv(self, report_id: int) -> bytes:
        rows = await self.build_rows(report_id)
        buf = io.StringIO(newline="")
        writer = csv.DictWriter(buf, fieldnames=LEDGER_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
        return buf.getvalue().encode("utf-8")

    async def to_xlsx(self, report_id: int) -> bytes:
        rows = await self.build_rows(report_id)
        wb = Workbook()
        ws = wb.active
        ws.title = "Ledger"
        ws.append(LEDGER_COLUMNS)
        for row in rows:
            ws.append([row.get(col, "") for col in LEDGER_COLUMNS])
        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue()

    async def _load_report(self, report_id: int) -> ChargebackReport:
        result = await self.db.execute(
            select(ChargebackReport)
            .options(selectinload(ChargebackReport.line_items))
            .where(ChargebackReport.id == report_id)
        )
        report = result.scalar_one_or_none()
        if not report:
            raise LookupError(f"Report {report_id} not found")
        return report

    async def _lookup_bus(self, ids: Iterable[int]) -> dict[int, BusinessUnit]:
        ids = [i for i in ids if i is not None]
        if not ids:
            return {}
        result = await self.db.execute(select(BusinessUnit).where(BusinessUnit.id.in_(ids)))
        return {bu.id: bu for bu in result.scalars().all()}

    async def _lookup_pms(self, ids: Iterable[int]) -> dict[int, PortfolioManager]:
        ids = [i for i in ids if i is not None]
        if not ids:
            return {}
        result = await self.db.execute(select(PortfolioManager).where(PortfolioManager.id.in_(ids)))
        return {pm.id: pm for pm in result.scalars().all()}


def _money(value: Decimal) -> str:
    return f"{Decimal(value).quantize(Decimal('0.01'))}"


def _plat(value) -> str:
    return value.value if hasattr(value, "value") else str(value or "")


def _cat(value) -> str:
    return value.value if hasattr(value, "value") else str(value or "")


def _describe(item: ChargebackLineItem) -> str:
    parts = [_plat(item.platform), _cat(item.category)]
    if item.service_name:
        parts.append(item.service_name)
    return " / ".join(p for p in parts if p)
