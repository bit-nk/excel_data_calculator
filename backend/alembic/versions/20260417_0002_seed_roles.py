"""seed default roles

Revision ID: 0002_seed_roles
Revises: 0001_initial
Create Date: 2026-04-17

Seeds the four canonical roles (admin, finance, portfolio_manager, viewer)
with the permission matrix required for RBAC-gated endpoints such as ledger
export and report approval.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_seed_roles"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ROLES = [
    {
        "name": "admin",
        "description": "Full administrative access",
        "can_view_all_bus": True,
        "can_approve_reports": True,
        "can_manage_rules": True,
        "can_export_ledger": True,
    },
    {
        "name": "finance",
        "description": "Finance team — generates and exports chargeback",
        "can_view_all_bus": True,
        "can_approve_reports": True,
        "can_manage_rules": False,
        "can_export_ledger": True,
    },
    {
        "name": "portfolio_manager",
        "description": "Portfolio Manager — sees own BU only",
        "can_view_all_bus": False,
        "can_approve_reports": False,
        "can_manage_rules": False,
        "can_export_ledger": False,
    },
    {
        "name": "viewer",
        "description": "Read-only viewer",
        "can_view_all_bus": False,
        "can_approve_reports": False,
        "can_manage_rules": False,
        "can_export_ledger": False,
    },
]


def upgrade() -> None:
    roles_table = sa.table(
        "roles",
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("can_view_all_bus", sa.Boolean),
        sa.column("can_approve_reports", sa.Boolean),
        sa.column("can_manage_rules", sa.Boolean),
        sa.column("can_export_ledger", sa.Boolean),
    )
    op.bulk_insert(roles_table, ROLES)


def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM roles WHERE name IN ('admin','finance','portfolio_manager','viewer')")
    )
