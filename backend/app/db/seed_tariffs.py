import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import async_session
from app.models.tariff import Tariff


async def seed_tariffs():
    async with async_session() as db:
        # Check if already seeded
        result = await db.execute(select(func.count()).select_from(Tariff))
        count = result.scalar()
        
        if count > 0:
            print(f"Already seeded with {count} tariffs. Skipping.")
            return
        
        sample_tariffs = [
            # China -> US (Cars)
            Tariff(hs_code="8703.23.00", country_origin="CN", country_destination="US", rate_type="MFN", duty_rate=Decimal("2.5"), unit="%", notes="Most Favored Nation rate"),
            Tariff(hs_code="8703.23.00", country_origin="CN", country_destination="US", rate_type="Section 301", duty_rate=Decimal("27.5"), unit="%", notes="Additional duties on Chinese goods"),
            
            # US -> China (Cars)
            Tariff(hs_code="8703.23.00", country_origin="US", country_destination="CN", rate_type="MFN", duty_rate=Decimal("15"), unit="%", notes="Standard import duty"),
            Tariff(hs_code="8703.23.00", country_origin="US", country_destination="CN", rate_type="Retaliatory", duty_rate=Decimal("40"), unit="%", notes="Additional retaliatory tariffs"),
            
            # US -> EU (Cars)
            Tariff(hs_code="8703.23.00", country_origin="US", country_destination="EU", rate_type="MFN", duty_rate=Decimal("10"), unit="%", notes="Standard EU import duty"),
            
            # EU -> US (Cars)
            Tariff(hs_code="8703.23.00", country_origin="EU", country_destination="US", rate_type="MFN", duty_rate=Decimal("2.5"), unit="%", notes="Standard US import duty"),
            
            # China -> US (Phones)
            Tariff(hs_code="8517.13.00", country_origin="CN", country_destination="US", rate_type="MFN", duty_rate=Decimal("0"), unit="%", notes="Duty free under MFN"),
            Tariff(hs_code="8517.13.00", country_origin="CN", country_destination="US", rate_type="Section 301", duty_rate=Decimal("7.5"), unit="%", notes="Additional duties on Chinese electronics"),
            
            # US -> China (Phones)
            Tariff(hs_code="8517.13.00", country_origin="US", country_destination="CN", rate_type="MFN", duty_rate=Decimal("0"), unit="%", notes="Duty free"),
            
            # US -> EU (Phones)
            Tariff(hs_code="8517.13.00", country_origin="US", country_destination="EU", rate_type="MFN", duty_rate=Decimal("0"), unit="%", notes="Duty free"),
            
            # EU -> US (Phones)
            Tariff(hs_code="8517.13.00", country_origin="EU", country_destination="US", rate_type="MFN", duty_rate=Decimal("0"), unit="%", notes="Duty free"),
        ]
        
        for tariff in sample_tariffs:
            db.add(tariff)
        
        await db.commit()
        print(f"Seeded {len(sample_tariffs)} tariff rates")


if __name__ == "__main__":
    asyncio.run(seed_tariffs())
