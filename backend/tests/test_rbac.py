"""RBAC tests — confirms permission-gated endpoints reject unauthorized roles."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.models.chargeback import ChargebackReport
from app.models.enums import ChargebackStatus


async def _seed_approved_report(db) -> ChargebackReport:
    report = ChargebackReport(
        billing_period="2026-03",
        status=ChargebackStatus.APPROVED,
        total_direct_cost=Decimal("0"),
        total_shared_cost=Decimal("0"),
        total_management_fee=Decimal("0"),
        total_cost=Decimal("0"),
        generated_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
        approved_at=datetime(2026, 4, 2, tzinfo=timezone.utc),
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


@pytest.mark.asyncio
async def test_me_returns_permissions_for_admin(client, users):
    client.login_as("admin")
    res = await client.get("/api/v1/auth/me")
    assert res.status_code == 200
    body = res.json()
    assert body["role_name"] == "admin"
    assert body["permissions"]["export_ledger"] is True
    assert body["permissions"]["approve_reports"] is True


@pytest.mark.asyncio
async def test_me_returns_permissions_for_viewer(client):
    client.login_as("viewer")
    res = await client.get("/api/v1/auth/me")
    body = res.json()
    assert body["role_name"] == "viewer"
    assert body["permissions"]["export_ledger"] is False
    assert body["permissions"]["approve_reports"] is False


@pytest.mark.asyncio
async def test_viewer_cannot_export_ledger(db, client, business_units):
    report = await _seed_approved_report(db)
    client.login_as("viewer")
    res = await client.get(f"/api/v1/reports/ledger/{report.id}.csv")
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_finance_can_export_ledger(db, client, business_units):
    report = await _seed_approved_report(db)
    client.login_as("finance")
    res = await client.get(f"/api/v1/reports/ledger/{report.id}.csv")
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/csv")


@pytest.mark.asyncio
async def test_pm_cannot_generate_report(client):
    client.login_as("pm")
    res = await client.post("/api/v1/chargeback/generate", json={"billing_period": "2026-03"})
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_generate_report(client, business_units):
    client.login_as("admin")
    res = await client.post("/api/v1/chargeback/generate", json={"billing_period": "2026-03"})
    assert res.status_code == 200
    body = res.json()
    assert body["billing_period"] == "2026-03"
