import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.connectors.base import BaseConnector, NormalizedCostRecord, ConnectorHealthStatus
from app.core.config import settings
from app.models.enums import Platform, CostCategory

logger = logging.getLogger(__name__)

CONFLUENT_BASE_URL = "https://api.confluent.cloud"


class ConfluentConnector(BaseConnector):
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
    ):
        self._api_key = api_key or settings.CONFLUENT_API_KEY
        self._api_secret = api_secret or settings.CONFLUENT_API_SECRET
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def platform(self) -> Platform:
        return Platform.CONFLUENT

    async def authenticate(self) -> bool:
        try:
            self._client = httpx.AsyncClient(
                base_url=CONFLUENT_BASE_URL,
                auth=(self._api_key, self._api_secret),
                headers={"Content-Type": "application/json"},
                timeout=30.0,
            )
            response = await self._client.get("/org/v2/organizations")
            response.raise_for_status()
            logger.info("Confluent authentication successful")
            return True
        except Exception as e:
            logger.error(f"Confluent authentication failed: {e}")
            return False

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def fetch_costs(
        self, start_date: date, end_date: date, **kwargs
    ) -> list[NormalizedCostRecord]:
        if not self._client:
            await self.authenticate()

        records: list[NormalizedCostRecord] = []

        # Fetch billing costs
        response = await self._client.get(
            "/billing/v1/costs",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        )
        response.raise_for_status()
        data = response.json()

        for item in data.get("data", []):
            cost_data = item.get("attributes", item)
            cost = Decimal(str(cost_data.get("amount", 0)))
            if cost == 0:
                continue

            resource = cost_data.get("resource", {})
            line_type = cost_data.get("line_type", "UNKNOWN")
            product = cost_data.get("product", "Confluent Cloud")

            records.append(
                NormalizedCostRecord(
                    platform=Platform.CONFLUENT,
                    account_id=resource.get("environment", {}).get("id", "unknown"),
                    usage_date=start_date,
                    billing_period=self._to_billing_period(start_date),
                    service_name=f"Confluent {product}",
                    category=CostCategory.STREAMING,
                    unblended_cost=cost,
                    resource_id=resource.get("id"),
                    resource_name=resource.get("display_name"),
                    usage_quantity=Decimal(str(cost_data.get("quantity", 0))),
                    usage_unit=cost_data.get("unit"),
                    tags={
                        "line_type": line_type,
                        "environment": resource.get("environment", {}).get("id"),
                        "cluster": resource.get("id"),
                    },
                    raw_data=item,
                )
            )

        logger.info(f"Confluent: fetched {len(records)} cost records")
        return records

    async def fetch_partition_report(self, start_date: date, end_date: date) -> list[dict]:
        """Fetch the monthly partitions report for detailed cluster usage."""
        if not self._client:
            await self.authenticate()

        response = await self._client.get(
            "/billing/v1/costs",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "group_by": "resource",
            },
        )
        response.raise_for_status()
        return response.json().get("data", [])

    async def health_check(self) -> ConnectorHealthStatus:
        try:
            is_auth = await self.authenticate()
            return ConnectorHealthStatus(
                platform=Platform.CONFLUENT,
                is_healthy=is_auth,
                message="Connected" if is_auth else "Authentication failed",
                last_checked=datetime.utcnow().isoformat(),
            )
        except Exception as e:
            return ConnectorHealthStatus(
                platform=Platform.CONFLUENT, is_healthy=False, message=str(e)
            )

    async def close(self):
        if self._client:
            await self._client.aclose()
