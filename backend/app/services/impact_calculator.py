from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Optional
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.catalog import CatalogItem
from app.models.hs_code import HSCode


class ImpactCalculator:
    """Service for calculating tariff impact on catalog items"""

    @staticmethod
    async def calculate_item_impact(
        item: CatalogItem,
        hs_code_data: HSCode,
        destination_country: str,
        db: AsyncSession
    ) -> CatalogItem:
        """
        Calculate tariff impact for a single catalog item

        Args:
            item: CatalogItem to calculate
            hs_code_data: HS code tariff data
            destination_country: Country where goods are imported to
            db: Database session

        Returns:
            Updated CatalogItem with calculated fields
        """
        # Determine applicable tariff rate
        applicable_rate = Decimal(str(hs_code_data.mfn_rate or 0))

        # Check FTA eligibility
        # FTA applies if origin country is in the destination's FTA partner list
        if hs_code_data.fta_rate is not None and hs_code_data.fta_countries:
            fta_countries = [c.strip() for c in hs_code_data.fta_countries.split(',')]
            if item.origin_country in fta_countries:
                applicable_rate = Decimal(str(hs_code_data.fta_rate))

        # Calculate costs
        tariff_cost = item.cogs * (applicable_rate / Decimal('100'))
        landed_cost = item.cogs + tariff_cost
        gross_margin = item.retail_price - landed_cost

        # Calculate margin percentage
        if item.retail_price > 0:
            margin_percent = (gross_margin / item.retail_price) * Decimal('100')
        else:
            margin_percent = Decimal('0')

        # Calculate annual tariff exposure
        annual_tariff_exposure = tariff_cost * Decimal(str(item.annual_volume))

        # Update item with calculated values (round to 2 decimal places)
        item.tariff_cost = tariff_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        item.landed_cost = landed_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        item.gross_margin = gross_margin.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        item.margin_percent = margin_percent.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        item.annual_tariff_exposure = annual_tariff_exposure.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return item

    @staticmethod
    async def calculate_catalog_impact(
        items: List[CatalogItem],
        destination_country: str,
        db: AsyncSession,
        recalculate: bool = False
    ) -> tuple[List[CatalogItem], Dict]:
        """
        Calculate tariff impact for all items in a catalog

        Args:
            items: List of catalog items
            destination_country: Country where goods are imported to
            db: Database session
            recalculate: If True, recalculate even if values exist

        Returns:
            Tuple of (updated_items, portfolio_metrics)
        """
        updated_items = []

        # Get all unique HS codes
        hs_codes = list(set(item.hs_code for item in items if item.hs_code))

        # Fetch HS code data in bulk
        result = await db.execute(
            select(HSCode).where(
                HSCode.code.in_(hs_codes),
                HSCode.country == destination_country
            )
        )
        hs_code_map = {hs.code: hs for hs in result.scalars().all()}

        # Calculate impact for each item
        for item in items:
            # Skip if already calculated and not recalculating
            if not recalculate and item.tariff_cost is not None:
                updated_items.append(item)
                continue

            # Get HS code data
            hs_code_data = hs_code_map.get(item.hs_code)
            if not hs_code_data:
                # If HS code not found, assume 0% rate
                item.tariff_cost = Decimal('0')
                item.landed_cost = item.cogs
                item.gross_margin = item.retail_price - item.cogs
                item.margin_percent = ((item.gross_margin / item.retail_price) * Decimal('100')).quantize(Decimal('0.01')) if item.retail_price > 0 else Decimal('0')
                item.annual_tariff_exposure = Decimal('0')
            else:
                # Calculate impact
                item = await ImpactCalculator.calculate_item_impact(
                    item, hs_code_data, destination_country, db
                )

            updated_items.append(item)

        # Calculate portfolio metrics
        portfolio_metrics = ImpactCalculator._calculate_portfolio_metrics(updated_items)

        return updated_items, portfolio_metrics

    @staticmethod
    def _calculate_portfolio_metrics(items: List[CatalogItem]) -> Dict:
        """
        Calculate aggregate portfolio metrics

        Args:
            items: List of catalog items with calculated values

        Returns:
            Dictionary of portfolio metrics
        """
        if not items:
            return {
                'total_tariff_exposure': 0,
                'total_revenue': 0,
                'total_landed_cost': 0,
                'avg_margin_percent': 0,
                'total_items': 0,
                'negative_margin_count': 0,
                'zero_tariff_count': 0,
                'by_category': [],
                'by_origin': []
            }

        total_tariff_exposure = sum(
            item.annual_tariff_exposure or Decimal('0') for item in items
        )

        total_revenue = sum(
            item.retail_price * item.annual_volume for item in items
        )

        total_landed_cost = sum(
            (item.landed_cost or Decimal('0')) * item.annual_volume for item in items
        )

        # Calculate weighted average margin (weighted by revenue)
        total_margin_value = sum(
            (item.margin_percent or Decimal('0')) * (item.retail_price * item.annual_volume)
            for item in items
        )
        avg_margin_percent = (total_margin_value / total_revenue) if total_revenue > 0 else Decimal('0')

        negative_margin_count = sum(
            1 for item in items if (item.margin_percent or Decimal('0')) < 0
        )

        zero_tariff_count = sum(
            1 for item in items if (item.tariff_cost or Decimal('0')) == 0
        )

        # Group by category
        by_category = ImpactCalculator._group_by_field(items, 'category')

        # Group by origin country
        by_origin = ImpactCalculator._group_by_field(items, 'origin_country')

        return {
            'total_tariff_exposure': float(total_tariff_exposure),
            'total_revenue': float(total_revenue),
            'total_landed_cost': float(total_landed_cost),
            'avg_margin_percent': float(avg_margin_percent.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'total_items': len(items),
            'negative_margin_count': negative_margin_count,
            'zero_tariff_count': zero_tariff_count,
            'by_category': by_category,
            'by_origin': by_origin
        }

    @staticmethod
    def _group_by_field(items: List[CatalogItem], field_name: str) -> List[Dict]:
        """
        Group items by a field and calculate aggregate metrics

        Args:
            items: List of catalog items
            field_name: Name of field to group by ('category' or 'origin_country')

        Returns:
            List of dictionaries with grouped metrics
        """
        grouped = defaultdict(lambda: {
            'total_tariff': Decimal('0'),
            'total_revenue': Decimal('0'),
            'margins': [],
            'count': 0,
            'items_value': Decimal('0')  # Total value for weighted margin
        })

        # Aggregate by field
        for item in items:
            field_value = getattr(item, field_name, None)
            key = field_value if field_value else 'Uncategorized'

            item_revenue = item.retail_price * item.annual_volume
            item_margin = item.margin_percent or Decimal('0')

            grouped[key]['total_tariff'] += item.annual_tariff_exposure or Decimal('0')
            grouped[key]['total_revenue'] += item_revenue
            grouped[key]['margins'].append(item_margin)
            grouped[key]['count'] += 1
            grouped[key]['items_value'] += item_revenue

        # Calculate weighted average margins and format output
        result = []
        for key, data in sorted(grouped.items()):
            # Calculate weighted average margin
            total_margin_value = sum(
                margin * (items[i].retail_price * items[i].annual_volume)
                for i, margin in enumerate(data['margins'])
                if i < len(items)
            )
            avg_margin = (total_margin_value / data['items_value']) if data['items_value'] > 0 else Decimal('0')

            result.append({
                field_name: key,
                'total_tariff': float(data['total_tariff'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'total_revenue': float(data['total_revenue'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'avg_margin': float(avg_margin.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'item_count': data['count']
            })

        return result
