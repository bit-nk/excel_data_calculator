from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, DateTime, Numeric, ForeignKey, Text, JSON, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.enums import (
    SharedCostMethod,
    ReportStatus,
    ChargebackStatus,
    CostCategory,
    Platform,
)


class SharedCostRule(Base):
    """Rules defining how shared/platform/unallocated costs are distributed across BUs."""

    __tablename__ = "shared_cost_rules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_category: Mapped[str] = mapped_column(String(50), nullable=False)
    distribution_method: Mapped[SharedCostMethod] = mapped_column(String(30), nullable=False)
    distribution_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<SharedCostRule {self.name}:{self.distribution_method}>"


class ManagementFeeRule(Base):
    """Rules for the 20% foundational management fee applied to qualifying direct costs."""

    __tablename__ = "management_fee_rules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    fee_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False, default=0.20)
    applies_to_category: Mapped[Optional[CostCategory]] = mapped_column(
        String(30), nullable=True
    )
    applies_to_platform: Mapped[Optional[Platform]] = mapped_column(
        String(20), nullable=True
    )
    is_exception: Mapped[bool] = mapped_column(Boolean, default=False)
    exception_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<ManagementFeeRule {self.name} rate={self.fee_rate}>"


class ChargebackReport(Base):
    """Monthly chargeback report that aggregates costs by BU/PM."""

    __tablename__ = "chargeback_reports"
    __table_args__ = (
        Index("ix_chargeback_reports_period_status", "billing_period", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    billing_period: Mapped[str] = mapped_column(String(7), nullable=False)  # YYYY-MM
    status: Mapped[ChargebackStatus] = mapped_column(
        String(30), default=ChargebackStatus.PENDING
    )
    total_direct_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    total_shared_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    total_management_fee: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    generated_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    approved_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    line_items: Mapped[List["ChargebackLineItem"]] = relationship(
        back_populates="report", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ChargebackReport {self.billing_period} status={self.status}>"


class ChargebackLineItem(Base):
    """Individual cost allocation line item within a chargeback report."""

    __tablename__ = "chargeback_line_items"
    __table_args__ = (
        Index("ix_cb_line_items_report_bu", "report_id", "business_unit_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    report_id: Mapped[int] = mapped_column(
        ForeignKey("chargeback_reports.id", ondelete="CASCADE"), nullable=False
    )
    business_unit_id: Mapped[int] = mapped_column(
        ForeignKey("business_units.id"), nullable=False
    )
    portfolio_manager_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("portfolio_managers.id"), nullable=True
    )
    platform: Mapped[Platform] = mapped_column(String(20), nullable=False)
    category: Mapped[CostCategory] = mapped_column(String(30), nullable=False)
    cost_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    service_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Cost breakdown
    direct_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    shared_cost_allocation: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    management_fee: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)

    # Pro-rata details
    pro_rata_weight: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6), nullable=True)
    allocation_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    report: Mapped["ChargebackReport"] = relationship(back_populates="line_items")

    def __repr__(self) -> str:
        return f"<ChargebackLineItem BU:{self.business_unit_id} {self.platform} ${self.total_cost}>"
