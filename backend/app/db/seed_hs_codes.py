import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session
from app.models.hs_code import HSCode


async def seed_us_hs_codes():
    async with async_session() as db:
        # Check if already seeded
        from sqlalchemy import select, func
        result = await db.execute(select(func.count()).select_from(HSCode))
        count = result.scalar()
        
        if count > 0:
            print(f"Already seeded with {count} codes. Skipping.")
            return
        
        sample_codes = [
            HSCode(code="87", description="Vehicles other than railway or tramway rolling stock", level="chapter", country="US"),
            HSCode(code="8703", description="Motor cars and other motor vehicles principally designed for the transport of persons", parent_code="87", level="heading", country="US"),
            HSCode(code="8704", description="Motor vehicles for the transport of goods", parent_code="87", level="heading", country="US"),
            HSCode(code="8703.23", description="Of a cylinder capacity exceeding 1,500 cc but not exceeding 3,000 cc", parent_code="8703", level="subheading", country="US"),
            HSCode(code="8703.24", description="Of a cylinder capacity exceeding 3,000 cc", parent_code="8703", level="subheading", country="US"),
            HSCode(code="8703.23.00", description="Motor cars with spark-ignition engine, 1500-3000cc", parent_code="8703.23", level="tariff", country="US"),
            HSCode(code="8703.24.00", description="Motor cars with spark-ignition engine, over 3000cc", parent_code="8703.24", level="tariff", country="US"),
            HSCode(code="85", description="Electrical machinery and equipment", level="chapter", country="US"),
            HSCode(code="8517", description="Telephone sets, including telephones for cellular networks", parent_code="85", level="heading", country="US"),
            HSCode(code="8517.13", description="Smartphones", parent_code="8517", level="subheading", country="US"),
            HSCode(code="8517.13.00", description="Smartphones", parent_code="8517.13", level="tariff", country="US"),
        ]
        
        for code in sample_codes:
            db.add(code)
        
        await db.commit()
        print(f"Seeded {len(sample_codes)} HS codes")


if __name__ == "__main__":
    asyncio.run(seed_us_hs_codes())
