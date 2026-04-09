from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, DateTime, Date, Numeric, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.enums import Platform, CostCategory, CostAllocationType


class CostRecord(Base):
    """Raw cost data ingested from all platforms, normalized into a common format."""

    __tablename__ = "cost_records"
    __table_args__ = (
        Index("ix_cost_records_platform_date", "platform", "usage_date"),
        Index("ix_cost_records_cost_code", "cost_code"),
        Index("ix_cost_records_bu_date", "business_unit_id", "usage_date"),
        Index("ix_cost_records_period", "billing_period"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Source identification
    platform: Mapped[Platform] = mapped_column(String(20), nullable=False)
    cloud_account_id: Mapped[int] = mapped_column(ForeignKey("cloud_accounts.id"), nullable=False)
    source_record_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Time dimensions
    usage_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    billing_period: Mapped[str] = mapped_column(String(7), nullable=False)  # YYYY-MM

    # Cost dimensions
    service_name: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    resource_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    category: Mapped[CostCategory] = mapped_column(String(30), nullable=False)
    allocation_type: Mapped[CostAllocationType] = mapped_column(
        String(30), default=CostAllocationType.DIRECT
    )

    # Cost values
    usage_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=0)
    usage_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    unblended_cost: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    blended_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6), nullable=True)
    amortized_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Business mapping
    cost_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    business_unit_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("business_units.id"), nullable=True
    )
    portfolio_manager_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("portfolio_managers.id"), nullable=True
    )

    # Tags and metadata
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Audit
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    cloud_account: Mapped["CloudAccount"] = relationship(back_populates="cost_records")
    business_unit: Mapped[Optional["BusinessUnit"]] = relationship(back_populates="cost_records")
    portfolio_manager: Mapped[Optional["PortfolioManager"]] = relationship(
        back_populates="cost_records"
    )

    def __repr__(self) -> str:
        return f"<CostRecord {self.platform}:{self.service_name} ${self.unblended_cost}>"


from app.models.cloud_accounts import CloudAccount  # noqa: E402
from app.models.business_units import BusinessUnit, PortfolioManager  # noqa: E402
