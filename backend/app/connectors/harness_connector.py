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

HARNESS_BASE_URL = "https://app.harness.io"


class HarnessConnector(BaseConnector):
    """
    Harness connector — primarily used for cost-code-to-PM/BU mappings,
    but also provides cloud cost management data.
    """

    def __init__(
        self,
        api_token: Optional[str] = None,
        account_id: Optional[str] = None,
    ):
        self._api_token = api_token or settings.HARNESS_API_TOKEN
        self._account_id = account_id or settings.HARNESS_ACCOUNT_ID
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def platform(self) -> Platform:
        return Platform.HARNESS

    async def authenticate(self) -> bool:
        try:
            self._client = httpx.AsyncClient(
                base_url=HARNESS_BASE_URL,
                headers={
                    "x-api-key": self._api_token,
                    "Harness-Account": self._account_id,
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
            response = await self._client.get(
                f"/ng/api/accounts/{self._account_id}",
            )
            response.raise_for_status()
            logger.info("Harness authentication successful")
            return True
        except Exception as e:
            logger.error(f"Harness authentication failed: {e}")
            return False

    async def fetch_cost_code_mappings(self) -> list[dict]:
        """Fetch cost-code-to-PM/Business Unit mappings from Harness."""
        if not self._client:
            await self.authenticate()

        response = await self._client.get(
            "/ccm/api/business-mapping",
            params={"accountIdentifier": self._account_id},
        )
        response.raise_for_status()
        data = response.json()

        mappings = []
        for bm in data.get("resource", {}).get("businessMappings", data.get("data", [])):
            cost_targets = bm.get("costTargets", [])
            for target in cost_targets:
                mappings.append(
                    {
                        "cost_code": target.get("name"),
                        "business_unit": bm.get("name"),
                        "rules": target.get("rules", []),
                        "source": "harness",
                    }
                )

        logger.info(f"Harness: fetched {len(mappings)} cost code mappings")
        return mappings

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def fetch_costs(
        self, start_date: date, end_date: date, **kwargs
    ) -> list[NormalizedCostRecord]:
        if not self._client:
            await self.authenticate()

        records: list[NormalizedCostRecord] = []

        # Fetch CCM perspective data
        response = await self._client.post(
            "/ccm/api/perspective/overview",
            params={"accountIdentifier": self._account_id},
            json={
                "filters": [
                    {
                        "field": {"fieldId": "startTime", "fieldName": "startTime"},
                        "operator": "AFTER",
                        "values": [f"{start_date.isoformat()}T00:00:00Z"],
                    },
                    {
                        "field": {"fieldId": "startTime", "fieldName": "startTime"},
                        "operator": "BEFORE",
                        "values": [f"{end_date.isoformat()}T23:59:59Z"],
                    },
                ],
                "groupBy": [
                    {"fieldId": "cloudProvider", "fieldName": "Cloud Provider"},
                    {"fieldId": "product", "fieldName": "Product"},
                ],
            },
        )
        response.raise_for_status()
        data = response.json()

        for item in data.get("data", []):
            cost = Decimal(str(item.get("cost", 0)))
            if cost == 0:
                continue

            records.append(
                NormalizedCostRecord(
                    platform=Platform.HARNESS,
                    account_id=self._account_id,
                    usage_date=start_date,
                    billing_period=self._to_billing_period(start_date),
                    service_name=item.get("product", "Harness"),
                    category=CostCategory.PLATFORM,
                    unblended_cost=cost,
                    tags={"cloud_provider": item.get("cloudProvider")},
                    raw_data=item,
                )
            )

        logger.info(f"Harness: fetched {len(records)} cost records")
        return records

    async def health_check(self) -> ConnectorHealthStatus:
        try:
            is_auth = await self.authenticate()
            return ConnectorHealthStatus(
                platform=Platform.HARNESS,
                is_healthy=is_auth,
                message="Connected" if is_auth else "Authentication failed",
                last_checked=datetime.utcnow().isoformat(),
            )
        except Exception as e:
            return ConnectorHealthStatus(
                platform=Platform.HARNESS, is_healthy=False, message=str(e)
            )

    async def close(self):
        if self._client:
            await self._client.aclose()
