"""Pytest fixtures shared across the test suite.

Uses an in-memory async SQLite database so tests run without any external
Postgres instance. SECRET_KEY is set before app.core.config loads so the
pydantic validator is satisfied.
"""
from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone

import pytest
import pytest_asyncio

os.environ.setdefault("SECRET_KEY", "test-secret-key-must-be-at-least-32-characters-long-xxx")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("DATABASE_SYNC_URL", "sqlite:///:memory:")
os.environ.setdefault("DEBUG", "true")

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.deps import get_current_user
from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.main import app
from app.models.business_units import BusinessUnit
from app.models.enums import UserRole
from app.models.users import Role, User


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_engine():
    # StaticPool keeps a single shared connection so :memory: data persists
    # across sessions within a single test.
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(db_engine):
    return async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def db(session_factory) -> AsyncSession:
    async with session_factory() as session:
        yield session
        await session.commit()


@pytest_asyncio.fixture
async def seed_roles(db: AsyncSession) -> dict[str, Role]:
    roles = {
        UserRole.ADMIN.value: Role(
            name=UserRole.ADMIN.value,
            can_view_all_bus=True,
            can_approve_reports=True,
            can_manage_rules=True,
            can_export_ledger=True,
        ),
        UserRole.FINANCE.value: Role(
            name=UserRole.FINANCE.value,
            can_view_all_bus=True,
            can_approve_reports=True,
            can_manage_rules=False,
            can_export_ledger=True,
        ),
        UserRole.PORTFOLIO_MANAGER.value: Role(
            name=UserRole.PORTFOLIO_MANAGER.value,
            can_view_all_bus=False,
            can_approve_reports=False,
            can_manage_rules=False,
            can_export_ledger=False,
        ),
        UserRole.VIEWER.value: Role(
            name=UserRole.VIEWER.value,
            can_view_all_bus=False,
            can_approve_reports=False,
            can_manage_rules=False,
            can_export_ledger=False,
        ),
    }
    for r in roles.values():
        db.add(r)
    await db.commit()
    for r in roles.values():
        await db.refresh(r)
    return roles


def _make_user(email: str, role: Role) -> User:
    return User(
        email=email,
        full_name=email.split("@")[0].title(),
        hashed_password=get_password_hash("password1234"),
        role_id=role.id,
        is_active=True,
        last_login_at=datetime.now(timezone.utc),
    )


@pytest_asyncio.fixture
async def users(db: AsyncSession, seed_roles) -> dict[str, User]:
    entries = {
        "admin": _make_user("admin@test.local", seed_roles[UserRole.ADMIN.value]),
        "finance": _make_user("finance@test.local", seed_roles[UserRole.FINANCE.value]),
        "pm": _make_user("pm@test.local", seed_roles[UserRole.PORTFOLIO_MANAGER.value]),
        "viewer": _make_user("viewer@test.local", seed_roles[UserRole.VIEWER.value]),
    }
    for u in entries.values():
        db.add(u)
    await db.commit()
    for u in entries.values():
        await db.refresh(u)
    return entries


@pytest_asyncio.fixture
async def business_units(db: AsyncSession) -> list[BusinessUnit]:
    bus = [
        BusinessUnit(name="Global Equities", code="GEQ", is_active=True),
        BusinessUnit(name="Quant Strategies", code="QST", is_active=True),
        BusinessUnit(name="Technology", code="TCH", is_active=True),
    ]
    for bu in bus:
        db.add(bu)
    await db.commit()
    for bu in bus:
        await db.refresh(bu)
    return bus


@pytest_asyncio.fixture
async def client(session_factory, users):
    """HTTP client with DB + auth dependency overrides.

    The `login_as` helper on the returned client switches which seeded user the
    request is authenticated as by swapping the get_current_user override.
    """

    current = {"user": users["admin"]}

    async def _override_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def _override_user():
        return current["user"]

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = _override_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        def login_as(key: str):
            current["user"] = users[key]
        c.login_as = login_as  # type: ignore[attr-defined]
        yield c

    app.dependency_overrides.clear()
