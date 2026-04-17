"""Parallel-run validator tests — UAT reconciliation against Excel baseline."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.models.chargeback import ChargebackLineItem, ChargebackReport
from app.models.enums import ChargebackStatus, CostCategory, Platform
from app.services.parallel_run import ParallelRunValidator


async def _seed_two_bu_report(db, business_units) -> ChargebackReport:
    geq, qst, _ = business_units
    report = ChargebackReport(
        billing_period="2026-03",
        status=ChargebackStatus.APPROVED,
        total_direct_cost=Decimal("400000"),
        total_shared_cost=Decimal("40000"),
        total_management_fee=Decimal("80000"),
        total_cost=Decimal("520000"),
        generated_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    db.add_all([
        ChargebackLineItem(
            report_id=report.id,
            business_unit_id=geq.id,
            platform=Platform.AWS.value,
            category=CostCategory.COMPUTE.value,
            direct_cost=Decimal("300000"),
            shared_cost_allocation=Decimal("30000"),
            management_fee=Decimal("60000"),
            total_cost=Decimal("390000"),
        ),
        ChargebackLineItem(
            report_id=report.id,
            business_unit_id=qst.id,
            platform=Platform.MONGODB.value,
            category=CostCategory.DATABASE.value,
            direct_cost=Decimal("100000"),
            shared_cost_allocation=Decimal("10000"),
            management_fee=Decimal("20000"),
            total_cost=Decimal("130000"),
        ),
    ])
    await db.commit()
    return report


@pytest.mark.asyncio
async def test_reconciliation_passes_on_exact_match(db, business_units):
    report = await _seed_two_bu_report(db, business_units)
    baseline = (
        "business_unit_code,direct_cost,shared_cost,management_fee,total_cost\n"
        "GEQ,300000.00,30000.00,60000.00,390000.00\n"
        "QST,100000.00,10000.00,20000.00,130000.00\n"
    )
    result = await ParallelRunValidator(db).reconcile(report.id, baseline)
    assert result.passed is True
    assert result.missing_in_engine == []
    assert result.missing_in_baseline == []
    assert all(d.within_tolerance for d in result.deltas)


@pytest.mark.asyncio
async def test_reconciliation_fails_when_over_tolerance(db, business_units):
    report = await _seed_two_bu_report(db, business_units)
    # Baseline has GEQ direct off by $100
    baseline = (
        "business_unit_code,direct_cost,shared_cost,management_fee,total_cost\n"
        "GEQ,299900.00,30000.00,60000.00,389900.00\n"
        "QST,100000.00,10000.00,20000.00,130000.00\n"
    )
    result = await ParallelRunValidator(db).reconcile(report.id, baseline)
    assert result.passed is False
    bad = [d for d in result.deltas if not d.within_tolerance]
    assert any(d.business_unit_code == "GEQ" and d.field == "direct_cost" for d in bad)


@pytest.mark.asyncio
async def test_reconciliation_detects_missing_bu(db, business_units):
    report = await _seed_two_bu_report(db, business_units)
    baseline = (
        "business_unit_code,direct_cost,shared_cost,management_fee,total_cost\n"
        "GEQ,300000.00,30000.00,60000.00,390000.00\n"
    )
    result = await ParallelRunValidator(db).reconcile(report.id, baseline)
    assert result.passed is False
    assert "QST" in result.missing_in_baseline


@pytest.mark.asyncio
async def test_parse_baseline_rejects_missing_columns(db):
    with pytest.raises(ValueError, match="missing columns"):
        ParallelRunValidator(db).parse_baseline("business_unit_code,direct_cost\nGEQ,1.0\n")
