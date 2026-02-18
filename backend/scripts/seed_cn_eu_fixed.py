import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import async_session
from app.models.hs_code import HSCode


async def seed_cn_eu_hs_codes():
    async with async_session() as db:
        # Check existing
        result = await db.execute(select(func.count()).select_from(HSCode).where(HSCode.country == 'CN'))
        cn_count = result.scalar()
        
        if cn_count > 0:
            print(f"Already have {cn_count} codes. Skipping.")
            return
        
        # China codes with FTA rates
        cn_codes = [
            HSCode(
                code="8703230010", 
                description="Cars, 1500-3000cc, off-road", 
                level="tariff", 
                country="CN",
                mfn_rate=15.0, 
                general_rate=230.0, 
                vat_rate=13.0, 
                consumption_tax=9.0,
                fta_rate=0.0,  # RCEP FTA rate
                fta_name="RCEP",
                fta_countries="JP,AU,NZ,ASEAN"
            ),
            HSCode(
                code="8703230090", 
                description="Cars, 1500-3000cc, other", 
                level="tariff", 
                country="CN",
                mfn_rate=15.0, 
                general_rate=230.0, 
                vat_rate=13.0, 
                consumption_tax=9.0,
                fta_rate=0.0,
                fta_name="RCEP",
                fta_countries="JP,AU,NZ,ASEAN"
            ),
            HSCode(
                code="8703240010", 
                description="Cars, >3000cc, off-road", 
                level="tariff", 
                country="CN",
                mfn_rate=15.0, 
                general_rate=230.0, 
                vat_rate=13.0, 
                consumption_tax=40.0,
                fta_rate=0.0,
                fta_name="RCEP",
                fta_countries="JP,AU,NZ,ASEAN"
            ),
            HSCode(
                code="8517130000", 
                description="Smartphones", 
                level="tariff", 
                country="CN",
                mfn_rate=0.0, 
                general_rate=130.0, 
                vat_rate=13.0, 
                consumption_tax=0.0,
                fta_rate=0.0,
                fta_name="RCEP",
                fta_countries="JP,AU,NZ,ASEAN,KR"
            ),
            HSCode(
                code="8471300000", 
                description="Laptops", 
                level="tariff", 
                country="CN",
                mfn_rate=0.0, 
                general_rate=70.0, 
                vat_rate=13.0, 
                consumption_tax=0.0,
                fta_rate=0.0,
                fta_name="RCEP",
                fta_countries="JP,AU,NZ,ASEAN,KR"
            ),
        ]
        
        # EU codes with FTA rates
        eu_codes = [
            HSCode(
                code="87032310", 
                description="Cars, 1500-3000cc, new", 
                level="cn8", 
                country="EU",
                mfn_rate=10.0, 
                vat_rate=19.0,
                fta_rate=0.0,
                fta_name="EU-Japan EPA",
                fta_countries="JP"
            ),
            HSCode(
                code="87032410", 
                description="Cars, >3000cc, new", 
                level="cn8", 
                country="EU",
                mfn_rate=10.0, 
                vat_rate=19.0,
                fta_rate=0.0,
                fta_name="EU-Japan EPA",
                fta_countries="JP"
            ),
            HSCode(
                code="85171300", 
                description="Smartphones", 
                level="cn8", 
                country="EU",
                mfn_rate=0.0, 
                vat_rate=20.0,
                fta_rate=0.0,
                fta_name="Various FTAs",
                fta_countries="JP,ASEAN,MERCOSUR"
            ),
            HSCode(
                code="84713000", 
                description="Laptops", 
                level="cn8", 
                country="EU",
                mfn_rate=0.0, 
                vat_rate=20.0,
                fta_rate=0.0,
                fta_name="Various FTAs",
                fta_countries="JP,ASEAN,MERCOSUR"
            ),
        ]
        
        db.add_all(cn_codes + eu_codes)
        await db.commit()
        print(f"Seeded {len(cn_codes)} CN and {len(eu_codes)} EU codes with FTA data")

if __name__ == "__main__":
    asyncio.run(seed_cn_eu_hs_codes())