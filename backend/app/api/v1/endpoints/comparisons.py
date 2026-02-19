"""
Comparison endpoints for comparing multiple calculations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from decimal import Decimal
from datetime import datetime

from app.db.session import get_db
from app.api.deps import get_current_user
from app.api.deps_rate_limit import check_user_rate_limit
from app.models.user import User
from app.models.calculation import Calculation
from app.schemas.comparison import (
    ComparisonRequest,
    ComparisonResponse,
    ComparisonCalculationItem,
    ComparisonMetrics
)

router = APIRouter()


@router.post("/compare", response_model=ComparisonResponse, dependencies=[Depends(check_user_rate_limit)])
async def compare_calculations(
    request: ComparisonRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compare 2-5 calculations side-by-side.
    All calculations must belong to the current user/organization.

    Returns comparison with rankings, metrics, and difference from average.
    """
    # Fetch all calculations
    result = await db.execute(
        select(Calculation).where(
            and_(
                Calculation.id.in_(request.calculation_ids),
                Calculation.user_id == current_user.id,
                Calculation.deleted_at.is_(None)
            )
        )
    )
    calculations = result.scalars().all()

    # Validate all IDs found
    if len(calculations) != len(request.calculation_ids):
        found_ids = {c.id for c in calculations}
        missing_ids = set(request.calculation_ids) - found_ids
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Calculations not found or you don't have access: {', '.join(missing_ids)}"
        )

    # Determine comparison type
    comparison_type = _determine_comparison_type(calculations)

    # Calculate metrics
    metrics = _calculate_comparison_metrics(calculations, comparison_type)

    # Build comparison items with rankings
    comparison_items = _build_comparison_items(calculations, metrics)

    return ComparisonResponse(
        calculations=comparison_items,
        metrics=metrics,
        comparison_date=datetime.utcnow(),
        total_compared=len(calculations)
    )


def _determine_comparison_type(calculations: List[Calculation]) -> str:
    """
    Determine if comparing same HS code, same country, or mixed.

    Returns:
        - 'same_hs_different_countries': Same HS code, different destinations
        - 'different_hs_same_country': Different HS codes, same destination
        - 'mixed': Mixed comparison
    """
    hs_codes = set(c.hs_code for c in calculations)
    dest_countries = set(c.destination_country for c in calculations)

    if len(hs_codes) == 1 and len(dest_countries) > 1:
        return 'same_hs_different_countries'
    elif len(hs_codes) > 1 and len(dest_countries) == 1:
        return 'different_hs_same_country'
    else:
        return 'mixed'


def _calculate_comparison_metrics(
    calculations: List[Calculation],
    comparison_type: str
) -> ComparisonMetrics:
    """
    Calculate summary metrics for comparison.

    Calculates min, max, avg costs, duty rates, and FTA metrics.
    """
    costs = [float(c.total_cost) for c in calculations]

    min_cost = Decimal(str(min(costs)))
    max_cost = Decimal(str(max(costs)))
    avg_cost = Decimal(str(sum(costs) / len(costs)))
    spread = max_cost - min_cost
    spread_percent = float(spread / avg_cost * 100) if avg_cost > 0 else 0.0

    # Find best/worst by total cost
    sorted_calcs = sorted(calculations, key=lambda c: c.total_cost)
    best_id = sorted_calcs[0].id
    worst_id = sorted_calcs[-1].id

    # Duty rates (extract from result JSON if available)
    duty_rates = []
    for calc in calculations:
        if calc.result and isinstance(calc.result, dict):
            rates = calc.result.get('rates', {})
            if rates and rates.get('mfn') is not None:
                duty_rates.append(float(rates.get('mfn')))

    duty_metrics = {
        'min': min(duty_rates) if duty_rates else None,
        'max': max(duty_rates) if duty_rates else None,
        'avg': sum(duty_rates) / len(duty_rates) if duty_rates else None
    }

    # FTA metrics
    fta_eligible_calcs = [c for c in calculations if c.fta_eligible]
    total_fta_savings = sum(
        float(c.fta_savings) for c in fta_eligible_calcs if c.fta_savings
    ) if fta_eligible_calcs else None

    return ComparisonMetrics(
        min_total_cost=min_cost,
        max_total_cost=max_cost,
        avg_total_cost=avg_cost,
        cost_spread=spread,
        cost_spread_percent=spread_percent,
        min_duty_rate=duty_metrics['min'],
        max_duty_rate=duty_metrics['max'],
        avg_duty_rate=duty_metrics['avg'],
        best_option_id=best_id,
        worst_option_id=worst_id,
        has_fta_eligible=len(fta_eligible_calcs) > 0,
        total_fta_savings=Decimal(str(total_fta_savings)) if total_fta_savings else None,
        comparison_type=comparison_type
    )


def _build_comparison_items(
    calculations: List[Calculation],
    metrics: ComparisonMetrics
) -> List[ComparisonCalculationItem]:
    """
    Build comparison items with rankings and difference from average.

    Calculations are ranked by total cost (1 = lowest/best).
    """
    # Sort by total cost (ascending)
    sorted_calcs = sorted(calculations, key=lambda c: c.total_cost)
    items = []

    for rank, calc in enumerate(sorted_calcs, start=1):
        cost_vs_avg = calc.total_cost - metrics.avg_total_cost
        cost_vs_avg_percent = float(
            cost_vs_avg / metrics.avg_total_cost * 100
        ) if metrics.avg_total_cost > 0 else 0.0

        items.append(ComparisonCalculationItem(
            id=calc.id,
            name=calc.name,
            hs_code=calc.hs_code,
            product_description=calc.product_description,
            origin_country=calc.origin_country,
            destination_country=calc.destination_country,
            cif_value=calc.cif_value,
            currency=calc.currency,
            total_cost=calc.total_cost,
            customs_duty=calc.customs_duty,
            vat_amount=calc.vat_amount,
            fta_eligible=calc.fta_eligible,
            fta_savings=calc.fta_savings,
            result=calc.result,
            created_at=calc.created_at,
            rank=rank,
            cost_vs_average=cost_vs_avg,
            cost_vs_average_percent=cost_vs_avg_percent,
            is_best=(calc.id == metrics.best_option_id),
            is_worst=(calc.id == metrics.worst_option_id)
        ))

    return items
