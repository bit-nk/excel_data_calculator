"""
Orchestrates data ingestion from all platform connectors into the database.
"""

import asyncio
import logging
from datetime import date
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.connectors.base import BaseConnector, NormalizedCostRecord
from app.connectors import (
    AWSConnector,
    MongoDBAtlasConnector,
    DatadogConnector,
    ConfluentConnector,
    SingleStoreConnector,
    HarnessConnector,
)
from app.models.cost_records import CostRecord
from app.models.enums import Platform, CostAllocationType

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._connectors: dict[Platform, BaseConnector] = {
            Platform.AWS: AWSConnector(),
            Platform.MONGODB: MongoDBAtlasConnector(),
            Platform.DATADOG: DatadogConnector(),
            Platform.CONFLUENT: ConfluentConnector(),
            Platform.SINGLESTORE: SingleStoreConnector(),
            Platform.HARNESS: HarnessConnector(),
        }

    async def ingest_all(
        self,
        start_date: date,
        end_date: date,
        platforms: Optional[list[Platform]] = None,
    ) -> dict[str, int]:
        """Ingest cost data from all (or selected) platforms."""
        targets = platforms or list(self._connectors.keys())
        results = {}

        tasks = [
            self._ingest_platform(platform, start_date, end_date)
            for platform in targets
            if platform in self._connectors
        ]
        outcomes = await asyncio.gather(*tasks, return_exceptions=True)

        for platform, outcome in zip(targets, outcomes):
            if isinstance(outcome, Exception):
                logger.error(f"Ingestion failed for {platform}: {outcome}")
                results[platform.value] = -1
            else:
                results[platform.value] = outcome

        return results

    async def _ingest_platform(
        self, platform: Platform, start_date: date, end_date: date
    ) -> int:
        connector = self._connectors[platform]

        authenticated = await connector.authenticate()
        if not authenticated:
            raise ConnectionError(f"Failed to authenticate with {platform.value}")

        normalized_records = await connector.fetch_costs(start_date, end_date)
        count = await self._persist_records(normalized_records)

        logger.info(f"Ingested {count} records from {platform.value}")
        return count

    async def _persist_records(self, records: list[NormalizedCostRecord]) -> int:
        db_records = []
        for rec in records:
            db_record = CostRecord(
                platform=rec.platform,
                cloud_account_id=1,  # TODO: resolve from cloud_accounts table
                source_record_id=rec.raw_data.get("id") if rec.raw_data else None,
                usage_date=rec.usage_date,
                billing_period=rec.billing_period,
                service_name=rec.service_name,
                resource_id=rec.resource_id,
                resource_name=rec.resource_name,
                region=rec.region,
                category=rec.category,
                allocation_type=CostAllocationType.DIRECT,
                usage_quantity=rec.usage_quantity,
                usage_unit=rec.usage_unit,
                unblended_cost=rec.unblended_cost,
                blended_cost=rec.blended_cost,
                amortized_cost=rec.amortized_cost,
                currency=rec.currency,
                cost_code=rec.cost_code,
                tags=rec.tags,
                raw_data=rec.raw_data,
            )
            db_records.append(db_record)

        self.db.add_all(db_records)
        await self.db.flush()
        return len(db_records)

    async def check_health(self) -> dict:
        results = {}
        for platform, connector in self._connectors.items():
            status = await connector.health_check()
            results[platform.value] = {
                "is_healthy": status.is_healthy,
                "message": status.message,
            }
        return results
