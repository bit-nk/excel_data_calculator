import re
from pydantic import BaseModel, field_validator, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional
from app.models.enums import Platform, CostCategory, ChargebackStatus

BILLING_PERIOD_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


class ChargebackLineItemResponse(BaseModel):
    id: int
    business_unit_name: str
    business_unit_code: str
    portfolio_manager_name: Optional[str] = None
    platform: Platform
    category: CostCategory
    cost_code: Optional[str] = None
    service_name: Optional[str] = None
    direct_cost: Decimal
    shared_cost_allocation: Decimal
    management_fee: Decimal
    total_cost: Decimal

    model_config = {"from_attributes": True}


class ChargebackReportResponse(BaseModel):
    id: int
    billing_period: str
    status: ChargebackStatus
    total_direct_cost: Decimal
    total_shared_cost: Decimal
    total_management_fee: Decimal
    total_cost: Decimal
    generated_at: datetime
    approved_at: Optional[datetime] = None
    line_items: list[ChargebackLineItemResponse] = []

    model_config = {"from_attributes": True}


class ChargebackSummaryByBU(BaseModel):
    business_unit_name: str
    business_unit_code: str
    aws_cost: Decimal = Decimal("0")
    mongodb_cost: Decimal = Decimal("0")
    datadog_cost: Decimal = Decimal("0")
    confluent_cost: Decimal = Decimal("0")
    singlestore_cost: Decimal = Decimal("0")
    harness_cost: Decimal = Decimal("0")
    total_direct: Decimal = Decimal("0")
    shared_allocation: Decimal = Decimal("0")
    management_fee: Decimal = Decimal("0")
    grand_total: Decimal = Decimal("0")


class GenerateReportRequest(BaseModel):
    billing_period: str = Field(..., pattern=r"^\d{4}-(0[1-9]|1[0-2])$", examples=["2026-03"])

    @field_validator("billing_period")
    @classmethod
    def validate_period(cls, v: str) -> str:
        if not BILLING_PERIOD_RE.match(v):
            raise ValueError("billing_period must be YYYY-MM format (e.g. 2026-03)")
        return v


class CostBreakdownByPlatform(BaseModel):
    platform: Platform
    total_cost: Decimal
    percentage: Decimal
    service_breakdown: list[dict] = []


class CostTrendPoint(BaseModel):
    period: str
    total_cost: Decimal
    by_platform: dict[str, Decimal] = {}
