"""
Public Statistics API Endpoints
Provides anonymous aggregated statistics that don't require authentication.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.db.session import get_db
from app.models.calculation import Calculation
from app.models.hs_code import HSCode


router = APIRouter()


# Response Models
class PublicStats(BaseModel):
    total_calculations: int
    calculations_this_month: int
    calculations_today: int
    total_hs_codes: int
    supported_countries: List[str]


class PopularHSCode(BaseModel):
    hs_code: str
    description: str
    usage_count: int


class RecentActivity(BaseModel):
    date: str
    calculation_count: int


@router.get("/public", response_model=PublicStats)
async def get_public_stats(db: AsyncSession = Depends(get_db)):
    """
    Get public statistics (no authentication required).
    Returns anonymous aggregated data for dashboard display.
    """
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    month_start = datetime(now.year, now.month, 1)

    # Total calculations
    total_calcs_result = await db.execute(
        select(func.count(Calculation.id))
    )
    total_calculations = total_calcs_result.scalar() or 0

    # Calculations today
    calcs_today_result = await db.execute(
        select(func.count(Calculation.id)).where(
            Calculation.created_at >= today_start
        )
    )
    calculations_today = calcs_today_result.scalar() or 0

    # Calculations this month
    calcs_month_result = await db.execute(
        select(func.count(Calculation.id)).where(
            Calculation.created_at >= month_start
        )
    )
    calculations_this_month = calcs_month_result.scalar() or 0

    # Total HS codes
    total_codes_result = await db.execute(
        select(func.count(HSCode.id))
    )
    total_hs_codes = total_codes_result.scalar() or 0

    # Supported countries (hardcoded for now)
    supported_countries = ["CN", "EU", "US"]

    return PublicStats(
        total_calculations=total_calculations,
        calculations_today=calculations_today,
        calculations_this_month=calculations_this_month,
        total_hs_codes=total_hs_codes,
        supported_countries=supported_countries
    )


@router.get("/public/popular-hs-codes", response_model=List[PopularHSCode])
async def get_public_popular_hs_codes(
    db: AsyncSession = Depends(get_db)
):
    """
    Get most frequently used HS codes (public, no auth required).
    Limited to top 10 codes from last 30 days.
    """
    start_date = datetime.utcnow() - timedelta(days=30)

    # Get popular HS codes
    result = await db.execute(
        select(
            Calculation.hs_code,
            func.count(Calculation.id).label('usage_count')
        )
        .where(
            and_(
                Calculation.created_at >= start_date,
                Calculation.hs_code.isnot(None)
            )
        )
        .group_by(Calculation.hs_code)
        .order_by(func.count(Calculation.id).desc())
        .limit(10)
    )

    popular_codes = []
    for row in result:
        hs_code = row.hs_code
        usage_count = row.usage_count

        # Try to get description from HSCode table
        code_result = await db.execute(
            select(HSCode.description).where(HSCode.code == hs_code).limit(1)
        )
        description = code_result.scalar() or "No description available"

        popular_codes.append(PopularHSCode(
            hs_code=hs_code,
            description=description,
            usage_count=usage_count
        ))

    return popular_codes


@router.get("/public/activity", response_model=List[RecentActivity])
async def get_public_activity(db: AsyncSession = Depends(get_db)):
    """
    Get recent calculation activity (last 7 days).
    Public endpoint, no authentication required.
    """
    start_date = datetime.utcnow() - timedelta(days=7)

    result = await db.execute(
        select(
            func.date(Calculation.created_at).label('date'),
            func.count(Calculation.id).label('calculation_count')
        )
        .where(Calculation.created_at >= start_date)
        .group_by(func.date(Calculation.created_at))
        .order_by(func.date(Calculation.created_at))
    )

    activity_data = []
    for row in result:
        activity_data.append(RecentActivity(
            date=str(row.date) if row.date else "",
            calculation_count=row.calculation_count
        ))

    return activity_data
