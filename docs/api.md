# API Reference

All endpoints are mounted under `/api/v1`. Authentication is Bearer JWT obtained
from `POST /api/v1/auth/login`. Interactive OpenAPI docs are served at
`/api/docs` when `DEBUG=true`.

## Authentication

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/login` | public | Returns `{ access_token, token_type }` |
| GET | `/auth/me` | any | Current user profile **and** permission flags |

`UserResponse` body:

```json
{
  "id": 1,
  "email": "finance@nkfinops.local",
  "full_name": "Jane Doe",
  "role_name": "finance",
  "business_unit_id": null,
  "is_active": true,
  "permissions": {
    "view_all_bus": true,
    "approve_reports": true,
    "manage_rules": false,
    "export_ledger": true
  }
}
```

## Chargeback

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/chargeback/generate` | admin, finance | Run engine for a period |
| GET | `/chargeback/reports` | any | List reports (filter `billing_period`, `status`, `limit`) |
| GET | `/chargeback/reports/{id}` | any | Report with line items |
| POST | `/chargeback/reports/{id}/approve` | admin, finance | Move to APPROVED |
| GET | `/chargeback/summary` | any | Per-BU per-platform rollup |

`POST /chargeback/generate` body:

```json
{ "billing_period": "2026-03" }
```

## Accounting ledger export

All three require `can_export_ledger`. Ledger export is only allowed for
reports in `APPROVED` or `SENT_TO_ACCOUNTING` status.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/reports/ledger/{report_id}.csv` | Download balanced GL as CSV |
| GET | `/reports/ledger/{report_id}.xlsx` | Download balanced GL as XLSX |
| POST | `/reports/ledger/{report_id}/mark-sent` | Transition report → SENT_TO_ACCOUNTING |

Ledger columns:

```
entry_date, period, account_code, debit, credit, department,
portfolio_manager, platform, category, description, reference_id, currency
```

Each BU/line posts a debit to its cost code; a single balancing credit posts
to `INFRA_CLEARING` so debits and credits tie per report.

## Cost records & dashboard

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/costs/` | any | Paginated cost records; BU-scoped when user lacks `view_all_bus` |
| GET | `/costs/breakdown-by-platform` | any | Platform totals for a period |
| GET | `/costs/trend` | any | N-month trend series |

## Connectors

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/connectors/health` | any | Per-source health + last_sync_at |
| POST | `/connectors/ingest` | admin, finance | Trigger ingestion for a date range |

## Analytical reports (future phase)

These routes exist but return `{"status": "pending"}`. Kept for future
phases — anomaly, reserved-instance, tag compliance, multi-cloud,
sustainability.

## Errors

All errors follow FastAPI convention: `{ "detail": "<message>" }`.

| Status | Meaning |
|--------|---------|
| 401 | Missing/invalid token |
| 403 | Role or permission check failed |
| 404 | Entity not found |
| 409 | Invalid state transition (e.g. exporting an unapproved report) |
| 422 | Validation error (body / query params) |
| 429 | Rate-limit exceeded |

## Rate limits

Applied by `RateLimitMiddleware`, keyed on client IP:

- `/auth/*` — 10 requests / 60s
- Everything else — 100 requests / 60s
