"""
Parallel-run validation harness (SoW §5 Phase 5 / §12 Success Criteria).

Compares the engine's generated chargeback report against a baseline CSV
exported from the legacy Excel ("Pro-Rata" / "CCF Budget") process, and emits
a reconciliation report with per-BU and grand-total deltas. Used during UAT
to certify 100% mathematical parity before go-live.

Baseline CSV format (one row per business unit):

    business_unit_code,direct_cost,shared_cost,management_fee,total_cost
    GEQ,600750.00,72090.00,120150.00,792990.00
    QST,539875.00,64785.00,107975.00,712635.00

The tolerance is per-line, in dollars. Default $0.01 — i.e. rounding noise only.
"""
from __future__ import annotations

import csv
import io
import logging
from dataclasses import dataclass, field, asdict
from decimal import Decimal
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.business_units import BusinessUnit
from app.models.chargeback import ChargebackLineItem, ChargebackReport

logger = logging.getLogger(__name__)

BASELINE_COLUMNS = (
    "business_unit_code",
    "direct_cost",
    "shared_cost",
    "management_fee",
    "total_cost",
)


@dataclass
class BaselineRow:
    business_unit_code: str
    direct_cost: Decimal
    shared_cost: Decimal
    management_fee: Decimal
    total_cost: Decimal


@dataclass
class LineDelta:
    business_unit_code: str
    field: str
    baseline: Decimal
    engine: Decimal
    delta: Decimal
    within_tolerance: bool


@dataclass
class ReconciliationResult:
    report_id: int
    billing_period: str
    tolerance: Decimal
    passed: bool
    missing_in_engine: list[str] = field(default_factory=list)
    missing_in_baseline: list[str] = field(default_factory=list)
    deltas: list[LineDelta] = field(default_factory=list)
    totals_delta: dict[str, Decimal] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            **asdict(self),
            "tolerance": str(self.tolerance),
            "deltas": [
                {**asdict(d), "baseline": str(d.baseline), "engine": str(d.engine), "delta": str(d.delta)}
                for d in self.deltas
            ],
            "totals_delta": {k: str(v) for k, v in self.totals_delta.items()},
        }


class ParallelRunValidator:
    def __init__(self, db: AsyncSession, tolerance: Decimal = Decimal("0.01")):
        self.db = db
        self.tolerance = tolerance

    def parse_baseline(self, csv_text: str) -> list[BaselineRow]:
        reader = csv.DictReader(io.StringIO(csv_text))
        missing = set(BASELINE_COLUMNS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Baseline CSV missing columns: {sorted(missing)}")

        rows: list[BaselineRow] = []
        for raw in reader:
            rows.append(BaselineRow(
                business_unit_code=raw["business_unit_code"].strip().upper(),
                direct_cost=Decimal(raw["direct_cost"]),
                shared_cost=Decimal(raw["shared_cost"]),
                management_fee=Decimal(raw["management_fee"]),
                total_cost=Decimal(raw["total_cost"]),
            ))
        return rows

    async def reconcile(self, report_id: int, baseline_csv: str) -> ReconciliationResult:
        report = await self._load_report(report_id)
        baseline = self.parse_baseline(baseline_csv)
        engine_by_bu = await self._aggregate_engine(report)

        baseline_by_code = {r.business_unit_code: r for r in baseline}

        missing_in_engine = sorted(set(baseline_by_code) - set(engine_by_bu))
        missing_in_baseline = sorted(set(engine_by_bu) - set(baseline_by_code))

        deltas: list[LineDelta] = []
        for code in sorted(set(baseline_by_code) & set(engine_by_bu)):
            bl = baseline_by_code[code]
            eng = engine_by_bu[code]
            for field_name in ("direct_cost", "shared_cost", "management_fee", "total_cost"):
                baseline_value = getattr(bl, field_name)
                engine_value = eng[field_name]
                diff = (engine_value - baseline_value).copy_abs()
                deltas.append(LineDelta(
                    business_unit_code=code,
                    field=field_name,
                    baseline=baseline_value,
                    engine=engine_value,
                    delta=diff,
                    within_tolerance=diff <= self.tolerance,
                ))

        totals_delta = {
            "direct_cost": (report.total_direct_cost - sum(r.direct_cost for r in baseline)),
            "shared_cost": (report.total_shared_cost - sum(r.shared_cost for r in baseline)),
            "management_fee": (report.total_management_fee - sum(r.management_fee for r in baseline)),
            "total_cost": (report.total_cost - sum(r.total_cost for r in baseline)),
        }

        passed = (
            not missing_in_engine
            and not missing_in_baseline
            and all(d.within_tolerance for d in deltas)
            and all(abs(v) <= self.tolerance for v in totals_delta.values())
        )

        logger.info(
            "Parallel-run reconciliation report_id=%s passed=%s bus=%s deltas_out_of_tolerance=%s",
            report_id, passed, len(baseline), sum(1 for d in deltas if not d.within_tolerance),
        )

        return ReconciliationResult(
            report_id=report.id,
            billing_period=report.billing_period,
            tolerance=self.tolerance,
            passed=passed,
            missing_in_engine=missing_in_engine,
            missing_in_baseline=missing_in_baseline,
            deltas=deltas,
            totals_delta=totals_delta,
        )

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

    async def _aggregate_engine(self, report: ChargebackReport) -> dict[str, dict[str, Decimal]]:
        bu_ids = {item.business_unit_id for item in report.line_items}
        bu_lookup = await self._lookup_bus(bu_ids)

        aggregated: dict[str, dict[str, Decimal]] = {}
        for item in report.line_items:
            bu = bu_lookup.get(item.business_unit_id)
            if not bu:
                continue
            bucket = aggregated.setdefault(bu.code.upper(), {
                "direct_cost": Decimal("0"),
                "shared_cost": Decimal("0"),
                "management_fee": Decimal("0"),
                "total_cost": Decimal("0"),
            })
            bucket["direct_cost"] += item.direct_cost or Decimal("0")
            bucket["shared_cost"] += item.shared_cost_allocation or Decimal("0")
            bucket["management_fee"] += item.management_fee or Decimal("0")
            bucket["total_cost"] += item.total_cost or Decimal("0")
        return aggregated

    async def _lookup_bus(self, ids: Iterable[int]) -> dict[int, BusinessUnit]:
        ids = [i for i in ids if i is not None]
        if not ids:
            return {}
        result = await self.db.execute(select(BusinessUnit).where(BusinessUnit.id.in_(ids)))
        return {bu.id: bu for bu in result.scalars().all()}
