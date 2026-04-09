import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

import boto3
from tenacity import retry, stop_after_attempt, wait_exponential

from app.connectors.base import BaseConnector, NormalizedCostRecord, ConnectorHealthStatus
from app.core.config import settings
from app.models.enums import Platform, CostCategory

logger = logging.getLogger(__name__)

SERVICE_CATEGORY_MAP = {
    "Amazon Elastic Compute Cloud": CostCategory.COMPUTE,
    "Amazon Simple Storage Service": CostCategory.STORAGE,
    "Amazon Relational Database Service": CostCategory.DATABASE,
    "Amazon DynamoDB": CostCategory.DATABASE,
    "Amazon CloudWatch": CostCategory.MONITORING,
    "Amazon Virtual Private Cloud": CostCategory.NETWORK,
    "Amazon Elastic Load Balancing": CostCategory.NETWORK,
    "AWS Data Transfer": CostCategory.NETWORK,
}


class AWSConnector(BaseConnector):
    def __init__(
        self,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        region: Optional[str] = None,
    ):
        self._access_key_id = access_key_id or settings.AWS_ACCESS_KEY_ID
        self._secret_access_key = secret_access_key or settings.AWS_SECRET_ACCESS_KEY
        self._region = region or settings.AWS_REGION
        self._ce_client = None
        self._s3_client = None

    @property
    def platform(self) -> Platform:
        return Platform.AWS

    async def authenticate(self) -> bool:
        try:
            session = boto3.Session(
                aws_access_key_id=self._access_key_id,
                aws_secret_access_key=self._secret_access_key,
                region_name=self._region,
            )
            self._ce_client = session.client("ce")
            self._s3_client = session.client("s3")
            # Validate by calling get_cost_and_usage with a tiny range
            self._ce_client.get_cost_and_usage(
                TimePeriod={"Start": "2024-01-01", "End": "2024-01-02"},
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
            )
            logger.info("AWS authentication successful")
            return True
        except Exception as e:
            logger.error(f"AWS authentication failed: {e}")
            return False

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def fetch_costs(
        self, start_date: date, end_date: date, **kwargs
    ) -> list[NormalizedCostRecord]:
        if not self._ce_client:
            await self.authenticate()

        records: list[NormalizedCostRecord] = []
        next_token = None

        while True:
            params = {
                "TimePeriod": {
                    "Start": start_date.isoformat(),
                    "End": end_date.isoformat(),
                },
                "Granularity": "DAILY",
                "Metrics": ["UnblendedCost", "BlendedCost", "AmortizedCost", "UsageQuantity"],
                "GroupBy": [
                    {"Type": "DIMENSION", "Key": "SERVICE"},
                    {"Type": "DIMENSION", "Key": "LINKED_ACCOUNT"},
                ],
            }
            if next_token:
                params["NextPageToken"] = next_token

            response = self._ce_client.get_cost_and_usage(**params)

            for result_by_time in response.get("ResultsByTime", []):
                usage_date = date.fromisoformat(result_by_time["TimePeriod"]["Start"])

                for group in result_by_time.get("Groups", []):
                    service_name = group["Keys"][0]
                    account_id = group["Keys"][1] if len(group["Keys"]) > 1 else "unknown"
                    metrics = group["Metrics"]

                    unblended = Decimal(str(metrics["UnblendedCost"]["Amount"]))
                    if unblended == 0:
                        continue

                    records.append(
                        NormalizedCostRecord(
                            platform=Platform.AWS,
                            account_id=account_id,
                            usage_date=usage_date,
                            billing_period=self._to_billing_period(usage_date),
                            service_name=service_name,
                            category=SERVICE_CATEGORY_MAP.get(service_name, CostCategory.OTHER),
                            unblended_cost=unblended,
                            blended_cost=Decimal(str(metrics["BlendedCost"]["Amount"])),
                            amortized_cost=Decimal(str(metrics["AmortizedCost"]["Amount"])),
                            usage_quantity=Decimal(str(metrics["UsageQuantity"]["Amount"])),
                            usage_unit=metrics["UsageQuantity"].get("Unit"),
                            raw_data=group,
                        )
                    )

            next_token = response.get("NextPageToken")
            if not next_token:
                break

        logger.info(f"AWS: fetched {len(records)} cost records for {start_date} to {end_date}")
        return records

    async def fetch_cur_from_s3(self, bucket: str, prefix: str) -> list[dict]:
        """Fetch Cost & Usage Reports from S3 for detailed line-item data."""
        if not self._s3_client:
            await self.authenticate()

        objects = self._s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        manifests = [
            obj["Key"]
            for obj in objects.get("Contents", [])
            if obj["Key"].endswith(".csv.gz") or obj["Key"].endswith(".parquet")
        ]
        logger.info(f"AWS CUR: found {len(manifests)} report files in s3://{bucket}/{prefix}")
        return manifests

    async def health_check(self) -> ConnectorHealthStatus:
        try:
            is_auth = await self.authenticate()
            return ConnectorHealthStatus(
                platform=Platform.AWS,
                is_healthy=is_auth,
                message="Connected" if is_auth else "Authentication failed",
                last_checked=datetime.utcnow().isoformat(),
            )
        except Exception as e:
            return ConnectorHealthStatus(
                platform=Platform.AWS,
                is_healthy=False,
                message=str(e),
            )
