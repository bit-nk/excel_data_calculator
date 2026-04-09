import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

import httpx
from httpx import DigestAuth
from tenacity import retry, stop_after_attempt, wait_exponential

from app.connectors.base import BaseConnector, NormalizedCostRecord, ConnectorHealthStatus
from app.core.config import settings
from app.models.enums import Platform, CostCategory

logger = logging.getLogger(__name__)

ATLAS_BASE_URL = "https://cloud.mongodb.com/api/atlas/v2"


class MongoDBAtlasConnector(BaseConnector):
    def __init__(
        self,
        public_key: Optional[str] = None,
        private_key: Optional[str] = None,
        org_id: Optional[str] = None,
    ):
        self._public_key = public_key or settings.MONGODB_ATLAS_PUBLIC_KEY
        self._private_key = private_key or settings.MONGODB_ATLAS_PRIVATE_KEY
        self._org_id = org_id or settings.MONGODB_ATLAS_ORG_ID
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def platform(self) -> Platform:
        return Platform.MONGODB

    async def authenticate(self) -> bool:
        try:
            self._client = httpx.AsyncClient(
                base_url=ATLAS_BASE_URL,
                auth=DigestAuth(self._public_key, self._private_key),
                headers={"Accept": "application/vnd.atlas.2023-11-15+json"},
                timeout=30.0,
            )
            response = await self._client.get(f"/orgs/{self._org_id}")
            response.raise_for_status()
            logger.info("MongoDB Atlas authentication successful")
            return True
        except Exception as e:
            logger.error(f"MongoDB Atlas authentication failed: {e}")
            return False

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def fetch_costs(
        self, start_date: date, end_date: date, **kwargs
    ) -> list[NormalizedCostRecord]:
        if not self._client:
            await self.authenticate()

        records: list[NormalizedCostRecord] = []

        # Fetch invoices for the organization
        response = await self._client.get(f"/orgs/{self._org_id}/invoices")
        response.raise_for_status()
        invoices = response.json().get("results", [])

        for invoice in invoices:
            invoice_date = date.fromisoformat(invoice["created"][:10])
            if not (start_date <= invoice_date <= end_date):
                continue

            # Fetch line items for each invoice
            invoice_id = invoice["id"]
            line_items_resp = await self._client.get(
                f"/orgs/{self._org_id}/invoices/{invoice_id}"
            )
            line_items_resp.raise_for_status()
            invoice_detail = line_items_resp.json()

            for item in invoice_detail.get("lineItems", []):
                cost = Decimal(str(item.get("totalPriceCents", 0))) / 100
                if cost == 0:
                    continue

                records.append(
                    NormalizedCostRecord(
                        platform=Platform.MONGODB,
                        account_id=self._org_id,
                        usage_date=invoice_date,
                        billing_period=self._to_billing_period(invoice_date),
                        service_name=item.get("sku", "MongoDB Atlas"),
                        category=CostCategory.DATABASE,
                        unblended_cost=cost,
                        resource_name=item.get("clusterName"),
                        usage_quantity=Decimal(str(item.get("quantity", 0))),
                        usage_unit=item.get("unit"),
                        tags={"group_id": item.get("groupId")},
                        raw_data=item,
                    )
                )

        logger.info(f"MongoDB: fetched {len(records)} cost records")
        return records

    async def health_check(self) -> ConnectorHealthStatus:
        try:
            is_auth = await self.authenticate()
            return ConnectorHealthStatus(
                platform=Platform.MONGODB,
                is_healthy=is_auth,
                message="Connected" if is_auth else "Authentication failed",
                last_checked=datetime.utcnow().isoformat(),
            )
        except Exception as e:
            return ConnectorHealthStatus(
                platform=Platform.MONGODB, is_healthy=False, message=str(e)
            )

    async def close(self):
        if self._client:
            await self._client.aclose()
