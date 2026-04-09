from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class BusinessUnit(Base):
    __tablename__ = "business_units"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("business_units.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    parent: Mapped[Optional["BusinessUnit"]] = relationship(
        remote_side="BusinessUnit.id", back_populates="children"
    )
    children: Mapped[List["BusinessUnit"]] = relationship(back_populates="parent")
    portfolio_managers: Mapped[List["PortfolioManager"]] = relationship(
        back_populates="business_unit"
    )
    cost_records: Mapped[List["CostRecord"]] = relationship(back_populates="business_unit")
    cost_code_mappings: Mapped[List["CostCodeMapping"]] = relationship(
        back_populates="business_unit"
    )

    def __repr__(self) -> str:
        return f"<BusinessUnit {self.code}:{self.name}>"


class PortfolioManager(Base):
    __tablename__ = "portfolio_managers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    employee_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, unique=True)
    business_unit_id: Mapped[int] = mapped_column(
        ForeignKey("business_units.id"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    business_unit: Mapped["BusinessUnit"] = relationship(back_populates="portfolio_managers")
    cost_records: Mapped[List["CostRecord"]] = relationship(back_populates="portfolio_manager")
    cost_code_mappings: Mapped[List["CostCodeMapping"]] = relationship(
        back_populates="portfolio_manager"
    )

    def __repr__(self) -> str:
        return f"<PortfolioManager {self.name}>"


class CostCode(Base):
    __tablename__ = "cost_codes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    mappings: Mapped[List["CostCodeMapping"]] = relationship(back_populates="cost_code")

    def __repr__(self) -> str:
        return f"<CostCode {self.code}>"


class CostCodeMapping(Base):
    """Maps cost codes to portfolio managers and business units (sourced from Harness)."""

    __tablename__ = "cost_code_mappings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cost_code_id: Mapped[int] = mapped_column(ForeignKey("cost_codes.id"), nullable=False)
    portfolio_manager_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("portfolio_managers.id"), nullable=True
    )
    business_unit_id: Mapped[int] = mapped_column(
        ForeignKey("business_units.id"), nullable=False
    )
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    source: Mapped[str] = mapped_column(String(50), default="harness")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    cost_code: Mapped["CostCode"] = relationship(back_populates="mappings")
    portfolio_manager: Mapped[Optional["PortfolioManager"]] = relationship(
        back_populates="cost_code_mappings"
    )
    business_unit: Mapped["BusinessUnit"] = relationship(back_populates="cost_code_mappings")

    def __repr__(self) -> str:
        return f"<CostCodeMapping {self.cost_code_id} -> BU:{self.business_unit_id}>"


from app.models.cost_records import CostRecord  # noqa: E402
