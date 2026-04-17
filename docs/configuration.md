# Configuration Reference

All configuration is read by [backend/app/core/config.py](../backend/app/core/config.py)
from environment variables or `backend/.env`. Case-sensitive.

## Application

| Variable | Default | Notes |
|----------|---------|-------|
| `APP_NAME` | `NkFinOps - Chargeback Automation` | Shown in OpenAPI docs |
| `APP_VERSION` | `0.1.0` | |
| `DEBUG` | `false` | When true, exposes `/api/docs` and verbose logging |
| `SECRET_KEY` | — **REQUIRED** | ≥ 32 chars; generate with `python -c "import secrets; print(secrets.token_urlsafe(64))"` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | JWT TTL |
| `ALLOWED_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Comma-separated CORS allowlist |

## Database

| Variable | Default | Notes |
|----------|---------|-------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/finops_chargeback` | Async driver — runtime |
| `DATABASE_SYNC_URL` | `postgresql+psycopg2://postgres:postgres@localhost:5432/finops_chargeback` | Sync driver — Alembic |

## Chargeback engine

| Variable | Default | Notes |
|----------|---------|-------|
| `MANAGEMENT_FEE_RATE` | `0.20` | Default 20% foundational fee; overridable per `ManagementFeeRule` |

## Cloud & billing connectors

All connector credentials are optional at process start — missing values only
disable the affected connector. Populate them through your secret manager.

### AWS

| Variable | Purpose |
|----------|---------|
| `AWS_ACCESS_KEY_ID` | IAM user/role key |
| `AWS_SECRET_ACCESS_KEY` | IAM secret |
| `AWS_REGION` | Default `us-east-1` |
| `AWS_CUR_S3_BUCKET` | Bucket hosting the Cost & Usage Report Parquet/CSV |
| `AWS_CUR_S3_PREFIX` | Object-key prefix under which the CUR partitions live |

IAM policy required: `ce:GetCostAndUsage`, `s3:GetObject`, `s3:ListBucket`
on the CUR bucket/prefix.

### MongoDB Atlas

| Variable | Purpose |
|----------|---------|
| `MONGODB_ATLAS_PUBLIC_KEY` | Programmatic API key (public part) |
| `MONGODB_ATLAS_PRIVATE_KEY` | Programmatic API key (private part) |
| `MONGODB_ATLAS_ORG_ID` | Organization to fetch invoices from |

### Datadog

| Variable | Purpose |
|----------|---------|
| `DATADOG_API_KEY` | API key |
| `DATADOG_APP_KEY` | App key with `usage_read` |
| `DATADOG_SITE` | `datadoghq.com`, `datadoghq.eu`, `us3.datadoghq.com`, … |

### Confluent

| Variable | Purpose |
|----------|---------|
| `CONFLUENT_API_KEY` | Cloud API key (billing scope) |
| `CONFLUENT_API_SECRET` | Cloud API secret |

### SingleStore

| Variable | Purpose |
|----------|---------|
| `SINGLESTORE_API_KEY` | Management API token |

### Harness

| Variable | Purpose |
|----------|---------|
| `HARNESS_API_TOKEN` | PAT with CCM read access |
| `HARNESS_ACCOUNT_ID` | Account identifier |

## Role / permission matrix

Seeded by [alembic/versions/20260417_0002_seed_roles.py](../backend/alembic/versions/20260417_0002_seed_roles.py):

| Role | view_all_bus | approve_reports | manage_rules | export_ledger |
|------|:-:|:-:|:-:|:-:|
| admin | ✓ | ✓ | ✓ | ✓ |
| finance | ✓ | ✓ |   | ✓ |
| portfolio_manager |   |   |   |   |
| viewer |   |   |   |   |

Adjust a role's permissions at runtime via direct SQL on the `roles` table;
every JWT refresh (`GET /auth/me`) re-reads the flags.

## Example `.env`

```ini
# Application
DEBUG=false
SECRET_KEY=replace-with-64-chars-from-secrets.token_urlsafe
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALLOWED_ORIGINS=https://finops.internal

# Database
DATABASE_URL=postgresql+asyncpg://finops:***@db.internal:5432/finops_chargeback
DATABASE_SYNC_URL=postgresql+psycopg2://finops:***@db.internal:5432/finops_chargeback

# Engine
MANAGEMENT_FEE_RATE=0.20

# AWS
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
AWS_CUR_S3_BUCKET=nkfinops-cur
AWS_CUR_S3_PREFIX=cur/monthly/

# Datadog
DATADOG_API_KEY=...
DATADOG_APP_KEY=...
DATADOG_SITE=datadoghq.com

# Confluent
CONFLUENT_API_KEY=...
CONFLUENT_API_SECRET=...

# MongoDB Atlas
MONGODB_ATLAS_PUBLIC_KEY=...
MONGODB_ATLAS_PRIVATE_KEY=...
MONGODB_ATLAS_ORG_ID=...

# SingleStore
SINGLESTORE_API_KEY=...

# Harness
HARNESS_API_TOKEN=...
HARNESS_ACCOUNT_ID=...
```
