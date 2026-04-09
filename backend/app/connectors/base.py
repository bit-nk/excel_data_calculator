from abc import ABC, abstractmethod
from datetime import date
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Optional
from app.models.enums import Platform, CostCategory


@dataclass
class NormalizedCostRecord:
    """Common format for cost data from any platform."""

    platform: Platform
    account_id: str
    usage_date: date
    billing_period: str  # YYYY-MM
    service_name: str
    category: CostCategory
    unblended_cost: Decimal
    currency: str = "USD"
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    region: Optional[str] = None
    usage_quantity: Decimal = Decimal("0")
    usage_unit: Optional[str] = None
    blended_cost: Optional[Decimal] = None
    amortized_cost: Optional[Decimal] = None
    cost_code: Optional[str] = None
    tags: dict = field(default_factory=dict)
    raw_data: dict = field(default_factory=dict)


@dataclass
class ConnectorHealthStatus:
    platform: Platform
    is_healthy: bool
    message: str
    last_checked: Optional[str] = None
    details: dict = field(default_factory=dict)


class BaseConnector(ABC):
    """Abstract base class for all platform connectors."""

    @property
    @abstractmethod
    def platform(self) -> Platform:
        ...

    @abstractmethod
    async def authenticate(self) -> bool:
        """Validate credentials and establish connection."""
        ...

    @abstractmethod
    async def fetch_costs(
        self, start_date: date, end_date: date, **kwargs
    ) -> list[NormalizedCostRecord]:
        """Fetch cost data for a date range, returned in normalized format."""
        ...

    @abstractmethod
    async def health_check(self) -> ConnectorHealthStatus:
        """Check connectivity and credential validity."""
        ...

    def _to_billing_period(self, d: date) -> str:
        return d.strftime("%Y-%m")
