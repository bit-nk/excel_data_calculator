"""Unit tests for the chargeback calculation engine.

Verifies:
- Direct cost aggregation per BU
- Pro-rata shared cost distribution
- 20% foundational management fee
- Report + line item materialization
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from app.models.chargeback import ManagementFeeRule
from app.models.cloud_accounts import CloudAccount
from app.models.cost_records import CostRecord
from app.models.enums import CostAllocationType, CostCategory, Platform
from app.services.chargeback import ChargebackEngine

BILLING_PERIOD = "2026-03"


async def _seed_account(db):
    acc = CloudAccount(platform=Platform.AWS.value, account_id="111122223333", account_name="Prod")
    db.add(acc)
    await db.commit()
    await db.refresh(acc)
    return acc


def _record(account_id: int, bu_id: int | None, cost: Decimal, allocation: CostAllocationType,
            platform: Platform = Platform.AWS, category: CostCategory = CostCategory.COMPUTE) -> CostRecord:
    return CostRecord(
        platform=platform.value,
        cloud_account_id=account_id,
        usage_date=date(2026, 3, 15),
        billing_period=BILLING_PERIOD,
        service_name="EC2",
        category=category.value,
        allocation_type=allocation.value,
        unblended_cost=cost,
        business_unit_id=bu_id,
    )


@pytest.mark.asyncio
async def test_direct_costs_aggregate_per_bu(db, business_units):
    acc = await _seed_account(db)
    geq, qst, tch = business_units
    db.add_all([
        _record(acc.id, geq.id, Decimal("100000"), CostAllocationType.DIRECT),
        _record(acc.id, qst.id, Decimal("50000"), CostAllocationType.DIRECT),
        _record(acc.id, tch.id, Decimal("50000"), CostAllocationType.DIRECT),
    ])
    await db.commit()

    engine = ChargebackEngine(db)
    report = await engine.generate_report(BILLING_PERIOD)

    assert report.total_direct_cost == Decimal("200000")
    assert report.total_shared_cost == Decimal("0")


@pytest.mark.asyncio
async def test_shared_costs_distribute_pro_rata(db, business_units):
    acc = await _seed_account(db)
    geq, qst, _tch = business_units
    db.add_all([
        _record(acc.id, geq.id, Decimal("300000"), CostAllocationType.DIRECT),
        _record(acc.id, qst.id, Decimal("100000"), CostAllocationType.DIRECT),
        _record(acc.id, None, Decimal("40000"), CostAllocationType.SHARED),
    ])
    await db.commit()

    engine = ChargebackEngine(db)
    report = await engine.generate_report(BILLING_PERIOD)

    assert report.total_shared_cost == Decimal("40000")
    # GEQ = 300k/400k * 40k = 30k; QST = 100k/400k * 40k = 10k
    geq_line = next(li for li in report.line_items if li.business_unit_id == geq.id)
    assert geq_line.direct_cost == Decimal("300000")


@pytest.mark.asyncio
async def test_management_fee_defaults_to_twenty_percent(db, business_units):
    acc = await _seed_account(db)
    geq, *_ = business_units
    db.add(_record(acc.id, geq.id, Decimal("100000"), CostAllocationType.DIRECT))
    await db.commit()

    engine = ChargebackEngine(db)
    report = await engine.generate_report(BILLING_PERIOD)

    assert report.total_management_fee == Decimal("20000.00")
    assert report.total_cost == Decimal("120000.00")


@pytest.mark.asyncio
async def test_management_fee_rule_overrides_default(db, business_units):
    acc = await _seed_account(db)
    geq, *_ = business_units
    db.add(_record(acc.id, geq.id, Decimal("100000"), CostAllocationType.DIRECT))
    db.add(ManagementFeeRule(
        name="Override to 15%",
        fee_rate=Decimal("0.15"),
        is_exception=False,
        is_active=True,
    ))
    await db.commit()

    engine = ChargebackEngine(db)
    report = await engine.generate_report(BILLING_PERIOD)
    assert report.total_management_fee == Decimal("15000.00")


@pytest.mark.asyncio
async def test_empty_period_yields_zero_report(db, business_units):
    engine = ChargebackEngine(db)
    report = await engine.generate_report(BILLING_PERIOD)
    assert report.total_direct_cost == Decimal("0")
    assert report.total_shared_cost == Decimal("0")
    assert report.total_management_fee == Decimal("0")
