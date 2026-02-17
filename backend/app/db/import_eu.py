import asyncio
from decimal import Decimal
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import async_session
from app.models.tariff import Tariff
from app.models.hs_code import HSCode


class EUTARICImporter:
    async def import_sample_data(self, db: AsyncSession):
        # Real EU MFN rates for US exports to EU
        eu_tariffs = [
            # Automotive
            {"hs_code": "8703.23.00", "description": "Motor cars, spark-ignition, 1500-3000cc", "mfn": 10.0},
            {"hs_code": "8703.24.00", "description": "Motor cars, spark-ignition, >3000cc", "mfn": 10.0},
            {"hs_code": "8704.21.00", "description": "Trucks, spark-ignition", "mfn": 22.0},
            
            # Electronics (mostly duty free)
            {"hs_code": "8517.13.00", "description": "Smartphones", "mfn": 0.0},
            {"hs_code": "8471.30.01", "description": "Portable computers", "mfn": 0.0},
            {"hs_code": "8528.72.64", "description": "TV reception apparatus", "mfn": 14.0},
            
            # Agriculture
            {"hs_code": "0203.19.00", "description": "Frozen pork cuts", "mfn": 6.0},
            {"hs_code": "0406.10.10", "description": "Fresh cheese", "mfn": 0.0},
            
            # Industrial goods
            {"hs_code": "7308.90.00", "description": "Steel structures", "mfn": 0.0},
            {"hs_code": "8409.91.00", "description": "Engine parts", "mfn": 0.0},
        ]
        
        imported = 0
        
        for item in eu_tariffs:
            hs_code = item["hs_code"]
            
            # Check if HS code exists
            result = await db.execute(select(HSCode).where(HSCode.code == hs_code))
            existing = result.scalar_one_or_none()
            
            if not existing:
                hs = HSCode(
                    code=hs_code,
                    description=item["description"],
                    level="tariff",
                    country="EU"
                )
                db.add(hs)
            
            # Check if tariff exists
            result = await db.execute(
                select(Tariff).where(
                    Tariff.hs_code == hs_code,
                    Tariff.country_origin == "US",
                    Tariff.country_destination == "EU"
                )
            )
            if result.scalar_one_or_none():
                continue
            
            # Add EU MFN rate
            tariff = Tariff(
                hs_code=hs_code,
                country_origin="US",
                country_destination="EU",
                rate_type="MFN",
                duty_rate=Decimal(str(item["mfn"])),
                unit="%",
                notes=f"EU MFN rate for {item['description']}"
            )
            db.add(tariff)
            imported += 1
        
        await db.commit()
        return imported


async def import_eu_data():
    async with async_session() as db:
        importer = EUTARICImporter()
        count = await importer.import_sample_data(db)
        print(f"Imported {count} EU tariff rates")


if __name__ == "__main__":
    asyncio.run(import_eu_data())
