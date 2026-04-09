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

PRODUCT_CATEGORY_MAP = {
    "infra_host": CostCategory.COMPUTE,
    "logs": CostCategory.MONITORING,
    "apm": CostCategory.MONITORING,
    "custom_metrics": CostCategory.MONITORING,
    "synthetics": CostCategory.MONITORING,
    "rum": CostCategory.MONITORING,
    "network": CostCategory.NETWORK,
    "serverless": CostCategory.COMPUTE,
    "ci_visibility": CostCategory.PLATFORM,
    "security": CostCategory.PLATFORM,
}


class DatadogConnector(BaseConnector):
    def __init__(
        self,
        api_key: Optional[str] = None,
        app_key: Optional[str] = None,
        site: Optional[str] = None,
    ):
        self._api_key = api_key or settings.DATADOG_API_KEY
        self._app_key = app_key or settings.DATADOG_APP_KEY
        self._site = site or settings.DATADOG_SITE
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def platform(self) -> Platform:
        return Platform.DATADOG

    async def authenticate(self) -> bool:
        try:
            self._client = httpx.AsyncClient(
                base_url=f"https://api.{self._site}/api",
                headers={
                    "DD-API-KEY": self._api_key,
                    "DD-APPLICATION-KEY": self._app_key,
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
            response = await self._client.get("/v1/validate")
            response.raise_for_status()
            logger.info("Datadog authentication successful")
            return True
        except Exception as e:
            logger.error(f"Datadog authentication failed: {e}")
            return False

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def fetch_costs(
        self, start_date: date, end_date: date, **kwargs
    ) -> list[NormalizedCostRecord]:
        if not self._client:
            await self.authenticate()

        records: list[NormalizedCostRecord] = []

        # Fetch usage attribution (estimated cost by product)
        start_month = start_date.strftime("%Y-%m")
        response = await self._client.get(
            "/v2/usage/estimated_cost",
            params={
                "view": "sub-org",
                "start_month": start_month,
            },
        )
        response.raise_for_status()
        data = response.json()

        for item in data.get("data", []):
            attrs = item.get("attributes", {})
            charges = attrs.get("charges", [])
            org_name = attrs.get("org_name", "unknown")
            account_id = attrs.get("public_id", "unknown")

            for charge in charges:
                product = charge.get("product_name", "unknown")
                cost = Decimal(str(charge.get("cost", 0)))
                if cost == 0:
                    continue

                records.append(
                    NormalizedCostRecord(
                        platform=Platform.DATADOG,
                        account_id=account_id,
                        usage_date=start_date,
                        billing_period=start_month,
                        service_name=f"Datadog {product}",
                        category=PRODUCT_CATEGORY_MAP.get(product, CostCategory.MONITORING),
                        unblended_cost=cost,
                        resource_name=org_name,
                        tags={"org_name": org_name, "product": product},
                        raw_data=charge,
                    )
                )

        # Fetch hourly usage for detailed breakdown
        usage_response = await self._client.get(
            "/v2/usage/hourly_usage",
            params={
                "filter[timestamp][start]": f"{start_date.isoformat()}T00:00:00Z",
                "filter[timestamp][end]": f"{end_date.isoformat()}T23:59:59Z",
                "filter[product_families]": "all",
            },
        )
        if usage_response.status_code == 200:
            usage_data = usage_response.json()
            logger.info(
                f"Datadog: retrieved {len(usage_data.get('data', []))} hourly usage entries"
            )

        logger.info(f"Datadog: fetched {len(records)} cost records")
        return records

    async def health_check(self) -> ConnectorHealthStatus:
        try:
            is_auth = await self.authenticate()
            return ConnectorHealthStatus(
                platform=Platform.DATADOG,
                is_healthy=is_auth,
                message="Connected" if is_auth else "Authentication failed",
                last_checked=datetime.utcnow().isoformat(),
            )
        except Exception as e:
            return ConnectorHealthStatus(
                platform=Platform.DATADOG, is_healthy=False, message=str(e)
            )

    async def close(self):
        if self._client:
            await self._client.aclose()
