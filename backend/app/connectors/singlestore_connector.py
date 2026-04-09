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

SINGLESTORE_BASE_URL = "https://api.singlestore.com"


class SingleStoreConnector(BaseConnector):
    """SingleStore billing connector. Note: billing tracking is WIP on the client side."""

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or settings.SINGLESTORE_API_KEY
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def platform(self) -> Platform:
        return Platform.SINGLESTORE

    async def authenticate(self) -> bool:
        try:
            self._client = httpx.AsyncClient(
                base_url=SINGLESTORE_BASE_URL,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
            response = await self._client.get("/v1/organizations/current")
            response.raise_for_status()
            logger.info("SingleStore authentication successful")
            return True
        except Exception as e:
            logger.error(f"SingleStore authentication failed: {e}")
            return False

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def fetch_costs(
        self, start_date: date, end_date: date, **kwargs
    ) -> list[NormalizedCostRecord]:
        if not self._client:
            await self.authenticate()

        records: list[NormalizedCostRecord] = []

        # Fetch billing/usage data
        response = await self._client.get(
            "/v1/billing/usage",
            params={
                "startTime": f"{start_date.isoformat()}T00:00:00Z",
                "endTime": f"{end_date.isoformat()}T23:59:59Z",
            },
        )
        response.raise_for_status()
        data = response.json()

        for item in data.get("usage", data.get("data", [])):
            cost = Decimal(str(item.get("cost", item.get("amount", 0))))
            if cost == 0:
                continue

            records.append(
                NormalizedCostRecord(
                    platform=Platform.SINGLESTORE,
                    account_id=item.get("organizationID", "unknown"),
                    usage_date=start_date,
                    billing_period=self._to_billing_period(start_date),
                    service_name=item.get("sku", "SingleStore"),
                    category=CostCategory.DATABASE,
                    unblended_cost=cost,
                    resource_id=item.get("workspaceGroupID"),
                    resource_name=item.get("workspaceGroupName"),
                    usage_quantity=Decimal(str(item.get("computeCredit", 0))),
                    usage_unit="compute_credits",
                    raw_data=item,
                )
            )

        logger.info(f"SingleStore: fetched {len(records)} cost records")
        return records

    async def health_check(self) -> ConnectorHealthStatus:
        try:
            is_auth = await self.authenticate()
            return ConnectorHealthStatus(
                platform=Platform.SINGLESTORE,
                is_healthy=is_auth,
                message="Connected" if is_auth else "Authentication failed",
                last_checked=datetime.utcnow().isoformat(),
            )
        except Exception as e:
            return ConnectorHealthStatus(
                platform=Platform.SINGLESTORE, is_healthy=False, message=str(e)
            )

    async def close(self):
        if self._client:
            await self._client.aclose()
