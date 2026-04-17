# Architecture Overview

NkFinOps — Cloud Cost Optimization & Chargeback Automation.

## 1. System context

The platform replaces a spreadsheet-based chargeback process with an automated
pipeline. Data flows monthly from six billing sources through a normalized cost
store, into a chargeback engine that applies pro-rata distribution and the 20%
foundational management fee, and out to both the internal "on-the-glass" portal
and the Accounting ledger file.

```
+---------------------+        +--------------------+        +------------------------+
|  Billing platforms  |        |   Ingestion layer  |        |  Normalized cost store |
|---------------------|        |--------------------|        |------------------------|
|  AWS Cost Explorer  | -----> |  aws_connector     | -----> |  cost_records          |
|  AWS CUR (S3)       |        |  datadog_connector |        |  cloud_accounts        |
|  Datadog            |        |  confluent_connect.|        |  business_units        |
|  Confluent Cloud    |        |  mongodb_connector |        |  cost_codes            |
|  MongoDB Atlas      |        |  singlestore_conn. |        |  cost_code_mappings    |
|  SingleStore        |        |  harness_connector |        +-----------+------------+
|  Harness (mappings) |        +---------+----------+                    |
+---------------------+                  |                               v
                                         v                  +---------------------------+
                                +-----------------+         |   Chargeback engine       |
                                |  ingestion.py   |         |---------------------------|
                                |  (orchestrator) |         |  direct cost aggregation  |
                                +-----------------+         |  pro-rata shared cost     |
                                                            |  20% foundational fee     |
                                                            |  line item materialization|
                                                            +-------------+-------------+
                                                                          |
                          +-----------------------------------------------+
                          |                                               |
                          v                                               v
            +----------------------------+              +------------------------------+
            |  On-the-glass portal API   |              |  Accounting ledger export    |
            |  /api/v1/chargeback/*      |              |  /api/v1/reports/ledger/*    |
            |  /api/v1/costs/*           |              |  CSV + XLSX, balanced GL     |
            |  BU-scoped RBAC            |              |  INFRA_CLEARING credit       |
            +----------------------------+              +------------------------------+
```

## 2. Layered components

| Layer | Directory | Responsibility |
|-------|-----------|----------------|
| API | [backend/app/api/routes/](../backend/app/api/routes/) | HTTP surface — auth, costs, chargeback, connectors, reports/ledger |
| Services | [backend/app/services/](../backend/app/services/) | Business logic — ingestion, chargeback engine, ledger export, parallel-run validator |
| Connectors | [backend/app/connectors/](../backend/app/connectors/) | Per-platform billing adapters with a common `BaseConnector` interface |
| Models | [backend/app/models/](../backend/app/models/) | SQLAlchemy ORM — identity, business hierarchy, cost records, chargeback, audit |
| Schemas | [backend/app/schemas/](../backend/app/schemas/) | Pydantic request/response + billing-period validators |
| Core | [backend/app/core/](../backend/app/core/) | Config, database, middleware (rate limit, security headers, audit), JWT |

## 3. Data model

- `cost_records` — normalized row per usage date/service; tagged with
  `platform`, `category`, `allocation_type` (direct / shared /
  platform_engineering / unallocated), and an optional `business_unit_id` /
  `portfolio_manager_id` resolved from `cost_code_mappings`.
- `chargeback_reports` — one record per `billing_period`, with totals and a
  lifecycle: `pending → calculated → reviewed → approved → sent_to_accounting`.
- `chargeback_line_items` — per-BU, per-platform, per-category rollup
  (`direct_cost`, `shared_cost_allocation`, `management_fee`, `total_cost`).
- `shared_cost_rules` — distribution strategy (pro-rata / equal split /
  usage-based / fixed %) keyed on `source_category`.
- `management_fee_rules` — fee rate (default 0.20) with category/platform
  scope and optional `is_exception` override.
- `roles` — permission matrix (`can_view_all_bus`, `can_approve_reports`,
  `can_manage_rules`, `can_export_ledger`).
- `audit_log` — action trail written by middleware for every mutating call.

## 4. Chargeback engine logic

Implemented in [backend/app/services/chargeback.py](../backend/app/services/chargeback.py).

1. Load direct cost records for the billing period, keyed by BU.
2. Aggregate direct costs per `(bu_id, platform, category)`.
3. Load shared/platform/unallocated records; distribute across BUs using
   active `SharedCostRule` (default pro-rata by direct-cost weight).
4. Apply 20% foundational management fee to each BU's direct total, using any
   active `ManagementFeeRule` overrides.
5. Materialize a `ChargebackReport` and one `ChargebackLineItem` per
   BU/platform/category combination.

## 5. RBAC and auth

- JWT bearer tokens signed with HS256, 60-min TTL, required-claims enforced
  (`exp`, `sub`).
- Four roles seeded by migration `0002_seed_roles`:

  | Role | view_all_bus | approve_reports | manage_rules | export_ledger |
  |------|:-:|:-:|:-:|:-:|
  | admin | ✓ | ✓ | ✓ | ✓ |
  | finance | ✓ | ✓ |   | ✓ |
  | portfolio_manager |   |   |   |   |
  | viewer |   |   |   |   |

- Endpoints use either `require_role(...)` (role allowlist) or
  `require_permission("export_ledger" | "approve_reports" | ...)` (flag check).
- Frontend mirrors this via `useAuth` + `<Can permission="...">` and a
  role-aware `<ProtectedRoute>` guard.

## 6. Middleware stack (outermost first)

| Middleware | Purpose |
|------------|---------|
| `AuditLogMiddleware` | Writes `audit_log` entries for authenticated mutating requests |
| `SecurityHeadersMiddleware` | CSP, HSTS, X-Content-Type-Options, etc. |
| `RateLimitMiddleware` | 10/min on `/auth/*`, 100/min elsewhere |
| `CORSMiddleware` | Allowlist controlled by `ALLOWED_ORIGINS` |

## 7. UAT parallel-run validator

Implemented in [backend/app/services/parallel_run.py](../backend/app/services/parallel_run.py)
and exposed as [backend/scripts/parallel_run.py](../backend/scripts/parallel_run.py).

Compares an engine-generated report against the legacy Excel baseline (CSV
export) with per-line and grand-total deltas under a configurable tolerance.
Required for the UAT parallel-run billing cycle before go-live.

## 8. Out of scope

- Azure VDI and on-premises allocation
- Modifications to the portal UI beyond the integration endpoints
- Accounting system restructuring
- Infrastructure provisioning
- 24/7 post-deployment managed services
