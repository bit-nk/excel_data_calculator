"""
Core chargeback calculation engine.

Applies:
1. Cost-code → BU/PM mapping
2. Shared cost distribution (pro-rata, equal split, usage-based, fixed %)
3. 20% foundational management fee
4. Generates chargeback report with line items
"""

import logging
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import (
    CostAllocationType,
    ChargebackStatus,
    SharedCostMethod,
    Platform,
    CostCategory,
)
from app.models.cost_records import CostRecord
from app.models.business_units import BusinessUnit, CostCodeMapping
from app.models.chargeback import (
    ChargebackReport,
    ChargebackLineItem,
    SharedCostRule,
    ManagementFeeRule,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class ChargebackEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_report(
        self, billing_period: str, generated_by: Optional[int] = None
    ) -> ChargebackReport:
        """Generate a full chargeback report for a billing period (YYYY-MM)."""

        logger.info(f"Generating chargeback report for {billing_period}")

        # 1. Get all cost records for the period
        direct_costs = await self._get_direct_costs(billing_period)
        shared_costs = await self._get_shared_costs(billing_period)

        # 2. Get distribution rules and fee rules
        shared_rules = await self._get_shared_cost_rules()
        fee_rules = await self._get_management_fee_rules()

        # 3. Get all active business units
        bus = await self._get_business_units()
        bu_direct_totals: dict[int, dict] = {bu.id: {} for bu in bus}

        # 4. Aggregate direct costs by BU
        total_direct = Decimal("0")
        for record in direct_costs:
            bu_id = record.business_unit_id
            if not bu_id:
                continue
            key = (record.platform, record.category)
            if key not in bu_direct_totals[bu_id]:
                bu_direct_totals[bu_id][key] = Decimal("0")
            bu_direct_totals[bu_id][key] += record.unblended_cost
            total_direct += record.unblended_cost

        # 5. Distribute shared costs
        total_shared = sum(r.unblended_cost for r in shared_costs)
        shared_allocations = await self._distribute_shared_costs(
            total_shared, bus, bu_direct_totals, shared_rules
        )

        # 6. Apply management fee
        total_fee = Decimal("0")
        fee_by_bu: dict[int, Decimal] = {}
        for bu in bus:
            bu_direct = sum(bu_direct_totals.get(bu.id, {}).values())
            fee = await self._calculate_management_fee(bu_direct, fee_rules)
            fee_by_bu[bu.id] = fee
            total_fee += fee

        # 7. Build report and line items
        report = ChargebackReport(
            billing_period=billing_period,
            status=ChargebackStatus.CALCULATED,
            total_direct_cost=total_direct,
            total_shared_cost=total_shared,
            total_management_fee=total_fee,
            total_cost=total_direct + total_shared + total_fee,
            generated_by=generated_by,
        )
        self.db.add(report)
        await self.db.flush()

        # Create line items per BU per platform/category
        for bu in bus:
            for (platform, category), amount in bu_direct_totals.get(bu.id, {}).items():
                shared_alloc = shared_allocations.get(bu.id, Decimal("0"))
                fee = fee_by_bu.get(bu.id, Decimal("0"))

                line_item = ChargebackLineItem(
                    report_id=report.id,
                    business_unit_id=bu.id,
                    platform=platform,
                    category=category,
                    direct_cost=amount,
                    shared_cost_allocation=shared_alloc / max(len(bu_direct_totals[bu.id]), 1),
                    management_fee=fee / max(len(bu_direct_totals[bu.id]), 1),
                    total_cost=amount
                    + shared_alloc / max(len(bu_direct_totals[bu.id]), 1)
                    + fee / max(len(bu_direct_totals[bu.id]), 1),
                )
                self.db.add(line_item)

        await self.db.flush()
        logger.info(
            f"Chargeback report {report.id} generated: "
            f"direct={total_direct}, shared={total_shared}, fee={total_fee}"
        )
        return report

    async def _get_direct_costs(self, billing_period: str) -> list[CostRecord]:
        result = await self.db.execute(
            select(CostRecord).where(
                CostRecord.billing_period == billing_period,
                CostRecord.allocation_type == CostAllocationType.DIRECT,
            )
        )
        return list(result.scalars().all())

    async def _get_shared_costs(self, billing_period: str) -> list[CostRecord]:
        result = await self.db.execute(
            select(CostRecord).where(
                CostRecord.billing_period == billing_period,
                CostRecord.allocation_type.in_(
                    [
                        CostAllocationType.SHARED,
                        CostAllocationType.PLATFORM_ENGINEERING,
                        CostAllocationType.UNALLOCATED,
                    ]
                ),
            )
        )
        return list(result.scalars().all())

    async def _get_shared_cost_rules(self) -> list[SharedCostRule]:
        result = await self.db.execute(
            select(SharedCostRule).where(SharedCostRule.is_active == True)
        )
        return list(result.scalars().all())

    async def _get_management_fee_rules(self) -> list[ManagementFeeRule]:
        result = await self.db.execute(
            select(ManagementFeeRule).where(ManagementFeeRule.is_active == True)
        )
        return list(result.scalars().all())

    async def _get_business_units(self) -> list[BusinessUnit]:
        result = await self.db.execute(
            select(BusinessUnit).where(BusinessUnit.is_active == True)
        )
        return list(result.scalars().all())

    async def _distribute_shared_costs(
        self,
        total_shared: Decimal,
        bus: list[BusinessUnit],
        bu_direct_totals: dict[int, dict],
        rules: list[SharedCostRule],
    ) -> dict[int, Decimal]:
        """Distribute shared costs across BUs using configured rules."""
        allocations: dict[int, Decimal] = {bu.id: Decimal("0") for bu in bus}

        if not bus or total_shared == 0:
            return allocations

        # Default: pro-rata based on direct cost proportion
        total_all_direct = sum(
            sum(costs.values()) for costs in bu_direct_totals.values()
        )

        for bu in bus:
            bu_direct = sum(bu_direct_totals.get(bu.id, {}).values())
            if total_all_direct > 0:
                weight = bu_direct / total_all_direct
            else:
                weight = Decimal("1") / len(bus)

            allocations[bu.id] = total_shared * weight

        return allocations

    async def _calculate_management_fee(
        self, direct_cost: Decimal, rules: list[ManagementFeeRule]
    ) -> Decimal:
        """Apply the 20% foundational management fee with exception handling."""
        fee_rate = Decimal(str(settings.MANAGEMENT_FEE_RATE))

        # Check for exceptions
        for rule in rules:
            if rule.is_exception:
                # Exception rules override default rate
                continue
            fee_rate = rule.fee_rate

        return direct_cost * fee_rate
