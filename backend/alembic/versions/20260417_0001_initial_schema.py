"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-17

Creates the full baseline schema for the FinOps Chargeback Automation platform:
identity (roles, users), business hierarchy (business_units, portfolio_managers,
cost_codes, cost_code_mappings), cloud accounts, normalized cost_records,
chargeback engine tables (shared_cost_rules, management_fee_rules,
chargeback_reports, chargeback_line_items), and audit_log.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- roles ---
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(30), nullable=False, unique=True),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("can_view_all_bus", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("can_approve_reports", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("can_manage_rules", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("can_export_ledger", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- business_units ---
    op.create_table(
        "business_units",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("parent_id", sa.Integer, sa.ForeignKey("business_units.id"), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- portfolio_managers ---
    op.create_table(
        "portfolio_managers",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True, unique=True),
        sa.Column("employee_id", sa.String(50), nullable=True, unique=True),
        sa.Column("business_unit_id", sa.Integer, sa.ForeignKey("business_units.id"), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- cost_codes ---
    op.create_table(
        "cost_codes",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- cost_code_mappings ---
    op.create_table(
        "cost_code_mappings",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("cost_code_id", sa.Integer, sa.ForeignKey("cost_codes.id"), nullable=False),
        sa.Column("portfolio_manager_id", sa.Integer, sa.ForeignKey("portfolio_managers.id"), nullable=True),
        sa.Column("business_unit_id", sa.Integer, sa.ForeignKey("business_units.id"), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source", sa.String(50), nullable=False, server_default="harness"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("business_unit_id", sa.Integer, sa.ForeignKey("business_units.id"), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- cloud_accounts ---
    op.create_table(
        "cloud_accounts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("platform", sa.String(20), nullable=False, index=True),
        sa.Column("account_id", sa.String(255), nullable=False, unique=True),
        sa.Column("account_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("credentials_ref", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("metadata_json", sa.JSON, nullable=True),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- cost_records ---
    op.create_table(
        "cost_records",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("platform", sa.String(20), nullable=False),
        sa.Column("cloud_account_id", sa.Integer, sa.ForeignKey("cloud_accounts.id"), nullable=False),
        sa.Column("source_record_id", sa.String(255), nullable=True),
        sa.Column("usage_date", sa.Date, nullable=False, index=True),
        sa.Column("billing_period", sa.String(7), nullable=False),
        sa.Column("service_name", sa.String(255), nullable=False),
        sa.Column("resource_id", sa.String(500), nullable=True),
        sa.Column("resource_name", sa.String(255), nullable=True),
        sa.Column("region", sa.String(50), nullable=True),
        sa.Column("category", sa.String(30), nullable=False),
        sa.Column("allocation_type", sa.String(30), nullable=False, server_default="direct"),
        sa.Column("usage_quantity", sa.Numeric(18, 6), nullable=False, server_default="0"),
        sa.Column("usage_unit", sa.String(50), nullable=True),
        sa.Column("unblended_cost", sa.Numeric(18, 6), nullable=False),
        sa.Column("blended_cost", sa.Numeric(18, 6), nullable=True),
        sa.Column("amortized_cost", sa.Numeric(18, 6), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("cost_code", sa.String(50), nullable=True),
        sa.Column("business_unit_id", sa.Integer, sa.ForeignKey("business_units.id"), nullable=True),
        sa.Column("portfolio_manager_id", sa.Integer, sa.ForeignKey("portfolio_managers.id"), nullable=True),
        sa.Column("tags", sa.JSON, nullable=True),
        sa.Column("raw_data", sa.JSON, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_cost_records_platform_date", "cost_records", ["platform", "usage_date"])
    op.create_index("ix_cost_records_cost_code", "cost_records", ["cost_code"])
    op.create_index("ix_cost_records_bu_date", "cost_records", ["business_unit_id", "usage_date"])
    op.create_index("ix_cost_records_period", "cost_records", ["billing_period"])

    # --- shared_cost_rules ---
    op.create_table(
        "shared_cost_rules",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("source_category", sa.String(50), nullable=False),
        sa.Column("distribution_method", sa.String(30), nullable=False),
        sa.Column("distribution_config", sa.JSON, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- management_fee_rules ---
    op.create_table(
        "management_fee_rules",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("fee_rate", sa.Numeric(5, 4), nullable=False, server_default="0.20"),
        sa.Column("applies_to_category", sa.String(30), nullable=True),
        sa.Column("applies_to_platform", sa.String(20), nullable=True),
        sa.Column("is_exception", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("exception_reason", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- chargeback_reports ---
    op.create_table(
        "chargeback_reports",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("billing_period", sa.String(7), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("total_direct_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("total_shared_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("total_management_fee", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("total_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("generated_by", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("approved_by", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_chargeback_reports_period_status", "chargeback_reports", ["billing_period", "status"]
    )

    # --- chargeback_line_items ---
    op.create_table(
        "chargeback_line_items",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "report_id",
            sa.Integer,
            sa.ForeignKey("chargeback_reports.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("business_unit_id", sa.Integer, sa.ForeignKey("business_units.id"), nullable=False),
        sa.Column(
            "portfolio_manager_id", sa.Integer, sa.ForeignKey("portfolio_managers.id"), nullable=True
        ),
        sa.Column("platform", sa.String(20), nullable=False),
        sa.Column("category", sa.String(30), nullable=False),
        sa.Column("cost_code", sa.String(50), nullable=True),
        sa.Column("service_name", sa.String(255), nullable=True),
        sa.Column("direct_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("shared_cost_allocation", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("management_fee", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("total_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("pro_rata_weight", sa.Numeric(10, 6), nullable=True),
        sa.Column("allocation_notes", sa.Text, nullable=True),
    )
    op.create_index(
        "ix_cb_line_items_report_bu", "chargeback_line_items", ["report_id", "business_unit_id"]
    )

    # --- audit_log ---
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True, index=True),
        sa.Column("action", sa.String(50), nullable=False, index=True),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.Integer, nullable=True),
        sa.Column("details", sa.JSON, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            index=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_index("ix_cb_line_items_report_bu", table_name="chargeback_line_items")
    op.drop_table("chargeback_line_items")
    op.drop_index("ix_chargeback_reports_period_status", table_name="chargeback_reports")
    op.drop_table("chargeback_reports")
    op.drop_table("management_fee_rules")
    op.drop_table("shared_cost_rules")
    for ix in (
        "ix_cost_records_period",
        "ix_cost_records_bu_date",
        "ix_cost_records_cost_code",
        "ix_cost_records_platform_date",
    ):
        op.drop_index(ix, table_name="cost_records")
    op.drop_table("cost_records")
    op.drop_table("cloud_accounts")
    op.drop_table("users")
    op.drop_table("cost_code_mappings")
    op.drop_table("cost_codes")
    op.drop_table("portfolio_managers")
    op.drop_table("business_units")
    op.drop_table("roles")
