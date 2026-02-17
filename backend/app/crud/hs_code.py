from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from app.models.hs_code import HSCode


async def get_hs_code_by_code(db: AsyncSession, code: str, country: str = "US") -> Optional[HSCode]:
    result = await db.execute(
        select(HSCode).where(HSCode.code == code, HSCode.country == country)
    )
    return result.scalar_one_or_none()


async def search_hs_codes(
    db: AsyncSession, 
    query: str, 
    country: str = "US", 
    skip: int = 0, 
    limit: int = 20
) -> List[HSCode]:
    search_pattern = f"%{query}%"
    
    stmt = (
        select(HSCode)
        .where(
            HSCode.country == country,
            or_(
                HSCode.code.ilike(search_pattern),
                HSCode.description.ilike(search_pattern)
            )
        )
        .order_by(
            HSCode.code == query,
            func.length(HSCode.code),
            HSCode.code
        )
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_hs_code_children(
    db: AsyncSession, 
    parent_code: str, 
    country: str = "US"
) -> List[HSCode]:
    result = await db.execute(
        select(HSCode)
        .where(
            HSCode.country == country,
            HSCode.parent_code == parent_code
        )
        .order_by(HSCode.code)
    )
    return result.scalars().all()
