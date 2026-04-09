from pydantic import BaseModel
from decimal import Decimal
from datetime import date, datetime
from typing import Optional
from app.models.enums import Platform, CostCategory, CostAllocationType


class CostRecordResponse(BaseModel):
    id: int
    platform: Platform
    usage_date: date
    billing_period: str
    service_name: str
    resource_name: Optional[str] = None
    region: Optional[str] = None
    category: CostCategory
    allocation_type: CostAllocationType
    unblended_cost: Decimal
    cost_code: Optional[str] = None
    business_unit_id: Optional[int] = None
    tags: Optional[dict] = None
    ingested_at: datetime

    model_config = {"from_attributes": True}


class CostFilters(BaseModel):
    platform: Optional[Platform] = None
    billing_period: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    business_unit_id: Optional[int] = None
    cost_code: Optional[str] = None
    category: Optional[CostCategory] = None


class CloudAccountResponse(BaseModel):
    id: int
    platform: Platform
    account_id: str
    account_name: str
    is_active: bool
    last_sync_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CloudAccountCreate(BaseModel):
    platform: Platform
    account_id: str
    account_name: str
    description: Optional[str] = None
    credentials_ref: Optional[str] = None
