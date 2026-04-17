# Deployment Guide

Target environments: internal Linux hosts on AWS. The platform
is a FastAPI + Postgres backend and a Vite/React SPA served behind the same
host/gateway.

## 1. Prerequisites

- Python 3.11+
- Node 20+
- Postgres 14+ (async driver: `asyncpg`)
- Credentials for each billing source — see [configuration.md](configuration.md)
- TLS-terminating reverse proxy (NGINX, ALB, or similar)

## 2. Backend — first-time install

```bash
cd backend
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Generate a secret key (32+ chars required by pydantic validator)
python -c "import secrets; print(secrets.token_urlsafe(64))" > .secret
```

Create `backend/.env`:

```ini
SECRET_KEY=<paste generated value>
DEBUG=false
DATABASE_URL=postgresql+asyncpg://finops:***@db.internal:5432/finops_chargeback
DATABASE_SYNC_URL=postgresql+psycopg2://finops:***@db.internal:5432/finops_chargeback
ALLOWED_ORIGINS=https://finops.internal
# Billing-source credentials — see docs/configuration.md
```

Run migrations (creates all tables and seeds the four default roles):

```bash
alembic upgrade head
```

Bootstrap an admin user (example — adapt to your secret manager):

```bash
python - <<'PY'
import asyncio
from app.core.database import async_session
from app.core.security import get_password_hash
from app.models.users import Role, User
from sqlalchemy import select

async def main():
    async with async_session() as db:
        role = (await db.execute(select(Role).where(Role.name == "admin"))).scalar_one()
        db.add(User(
            email="admin@nkfinops.local",
            full_name="Admin",
            hashed_password=get_password_hash("change-me-on-first-login"),
            role_id=role.id,
            is_active=True,
        ))
        await db.commit()

asyncio.run(main())
PY
```

## 3. Backend — running

Dev:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Prod (behind reverse proxy, 4 workers):

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --no-server-header
```

Health probe: `GET /api/health → {"status":"healthy"}`.

## 4. Frontend

```bash
cd frontend
npm ci
npm run build                        # outputs dist/
```

Serve `dist/` behind the same hostname as the API so `/api/*` requests reach
the backend. Example NGINX snippet:

```nginx
location /api/ {
  proxy_pass http://backend:8000;
  proxy_set_header Host $host;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
location / {
  root /srv/finops/dist;
  try_files $uri /index.html;
}
```

Dev (vite proxy config already routes `/api` to `http://localhost:8000`):

```bash
npm run dev
```

## 5. Migrations

| Task | Command |
|------|---------|
| Apply all | `alembic upgrade head` |
| New revision (autogenerate) | `alembic revision --autogenerate -m "<msg>"` |
| Roll back one | `alembic downgrade -1` |

Migrations live under [backend/alembic/versions/](../backend/alembic/versions/).
`0001_initial` creates the baseline schema; `0002_seed_roles` inserts the
four canonical roles — without it, JWT-authenticated requests resolve to no
role and permission checks all fail.

## 6. Tests

```bash
cd backend
pytest                               # uses in-memory SQLite; no DB required
```

## 7. UAT parallel-run

Before go-live, every chargeback report must reconcile against the legacy
Excel output. Export the Excel budget workbook to a CSV matching:

```
business_unit_code,direct_cost,shared_cost,management_fee,total_cost
```

then run:

```bash
python -m scripts.parallel_run --report-id 42 --baseline baseline_2026-03.csv
```

Exit code `0` = parity within tolerance (default $0.01). Non-zero = block
`SENT_TO_ACCOUNTING` transition.

## 8. Monitoring & audit

- `audit_log` table records mutating operations (user_id, action,
  entity_type, entity_id, ip_address, timestamp).
- Rate-limit rejects return HTTP 429 — monitor frequency to detect scraping
  or misconfigured clients.
- Log format: `%(asctime)s %(levelname)-8s [%(name)s] %(message)s`.
  Forward to your preferred log aggregator (CloudWatch, Datadog).

## 9. Rollback

The engine is idempotent — regenerating a report for the same period
overwrites previous totals. If a bad `SharedCostRule` or `ManagementFeeRule`
is activated, deactivate it and re-run `POST /chargeback/generate`. Ledger
files already sent to Accounting are immutable; correct via a subsequent
adjustment report.
