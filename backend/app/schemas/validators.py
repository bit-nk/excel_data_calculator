"""Shared query parameter validators."""

import re
from datetime import date, timedelta
from fastapi import HTTPException, Query
from typing import Optional

BILLING_PERIOD_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
MAX_DATE_RANGE_DAYS = 366  # Max 1 year


def validated_billing_period(
    billing_period: str = Query(..., description="YYYY-MM", min_length=7, max_length=7),
) -> str:
    if not BILLING_PERIOD_RE.match(billing_period):
        raise HTTPException(status_code=422, detail="billing_period must match YYYY-MM format")
    return billing_period


def validated_optional_billing_period(
    billing_period: Optional[str] = Query(None, min_length=7, max_length=7),
) -> Optional[str]:
    if billing_period and not BILLING_PERIOD_RE.match(billing_period):
        raise HTTPException(status_code=422, detail="billing_period must match YYYY-MM format")
    return billing_period


def validate_date_range(start_date: Optional[date], end_date: Optional[date]) -> None:
    if start_date and end_date:
        if start_date > end_date:
            raise HTTPException(status_code=422, detail="start_date must be before end_date")
        if (end_date - start_date).days > MAX_DATE_RANGE_DAYS:
            raise HTTPException(
                status_code=422,
                detail=f"Date range must not exceed {MAX_DATE_RANGE_DAYS} days",
            )
