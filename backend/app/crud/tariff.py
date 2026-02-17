from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.tariff import Tariff


async def get_tariff_by_id(db: AsyncSession, tariff_id: str) -> Optional[Tariff]:
    result = await db.execute(select(Tariff).where(Tariff.id == tariff_id))
    return result.scalar_one_or_none()


async def search_tariffs(
    db: AsyncSession,
    hs_code: str,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    rate_type: Optional[str] = None
) -> List[Tariff]:
    stmt = select(Tariff).where(Tariff.hs_code == hs_code)
    
    if origin:
        stmt = stmt.where(Tariff.country_origin == origin)
    if destination:
        stmt = stmt.where(Tariff.country_destination == destination)
    if rate_type:
        stmt = stmt.where(Tariff.rate_type == rate_type)
    
    stmt = stmt.order_by(Tariff.duty_rate)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_applicable_tariffs(
    db: AsyncSession,
    hs_code: str,
    origin: str,
    destination: str
) -> List[Tariff]:
    """Get all applicable tariff rates for a trade lane, ordered by best rate first."""
    result = await db.execute(
        select(Tariff)
        .where(
            and_(
                Tariff.hs_code == hs_code,
                Tariff.country_origin == origin,
                Tariff.country_destination == destination
            )
        )
        .order_by(Tariff.duty_rate)
    )
    return result.scalars().all()
