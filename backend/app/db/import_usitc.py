import asyncio
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.session import async_session
from app.models.tariff import Tariff
from app.models.hs_code import HSCode


class USITCImporter:
    def __init__(self):
        pass
    
    async def import_sample_data(self, db: AsyncSession):
        # Real tariff data for China -> US (selected HS codes)
        real_tariffs = [
            # Automotive
            {"hs_code": "8703.23.00", "description": "Motor cars, spark-ignition, 1500-3000cc", "mfn": 2.5, "section_301": 25.0},
            {"hs_code": "8703.24.00", "description": "Motor cars, spark-ignition, >3000cc", "mfn": 2.5, "section_301": 25.0},
            {"hs_code": "8704.21.00", "description": "Trucks, spark-ignition, gross vehicle weight <5 tons", "mfn": 25.0, "section_301": 25.0},
            
            # Electronics
            {"hs_code": "8517.13.00", "description": "Smartphones", "mfn": 0.0, "section_301": 7.5},
            {"hs_code": "8471.30.01", "description": "Portable computers", "mfn": 0.0, "section_301": 7.5},
            {"hs_code": "8528.72.64", "description": "TV reception apparatus", "mfn": 3.9, "section_301": 7.5},
            
            # Textiles
            {"hs_code": "6109.10.00", "description": "T-shirts, cotton, knitted", "mfn": 16.5, "section_301": 7.5},
            {"hs_code": "6203.42.11", "description": "Men's trousers, cotton", "mfn": 16.6, "section_301": 7.5},
            
            # Machinery
            {"hs_code": "8451.10.00", "description": "Dry-cleaning machines", "mfn": 0.0, "section_301": 25.0},
            {"hs_code": "8467.21.00", "description": "Drills, electric, hand-held", "mfn": 0.0, "section_301": 25.0},
        ]
        
        imported = 0
        
        for item in real_tariffs:
            hs_code = item["hs_code"]
            
            # Check if HS code exists, if not create it
            result = await db.execute(select(HSCode).where(HSCode.code == hs_code))
            existing = result.scalar_one_or_none()
            
            if not existing:
                hs = HSCode(
                    code=hs_code,
                    description=item["description"],
                    level="tariff",
                    country="US"
                )
                db.add(hs)
            
            # Check if MFN tariff already exists
            result = await db.execute(
                select(Tariff).where(
                    and_(
                        Tariff.hs_code == hs_code,
                        Tariff.country_origin == "CN",
                        Tariff.country_destination == "US",
                        Tariff.rate_type == "MFN"
                    )
                )
            )
            if not result.scalar_one_or_none():
                # Add MFN rate
                if item["mfn"] > 0:
                    tariff_mfn = Tariff(
                        hs_code=hs_code,
                        country_origin="CN",
                        country_destination="US",
                        rate_type="MFN",
                        duty_rate=Decimal(str(item["mfn"])),
                        unit="%",
                        notes=f"MFN rate for {item['description']}"
                    )
                    db.add(tariff_mfn)
                    imported += 1
            
            # Check if Section 301 tariff already exists
            result = await db.execute(
                select(Tariff).where(
                    and_(
                        Tariff.hs_code == hs_code,
                        Tariff.country_origin == "CN",
                        Tariff.country_destination == "US",
                        Tariff.rate_type == "Section 301"
                    )
                )
            )
            if not result.scalar_one_or_none():
                # Add Section 301 rate
                if item["section_301"] > 0:
                    tariff_301 = Tariff(
                        hs_code=hs_code,
                        country_origin="CN",
                        country_destination="US",
                        rate_type="Section 301",
                        duty_rate=Decimal(str(item["mfn"] + item["section_301"])),
                        unit="%",
                        notes=f"MFN + Section 301 additional duty ({item['section_301']}%)"
                    )
                    db.add(tariff_301)
                    imported += 1
        
        await db.commit()
        return imported


async def import_usitc_data():
    async with async_session() as db:
        importer = USITCImporter()
        count = await importer.import_sample_data(db)
        print(f"Imported {count} real tariff rates from USITC data")


if __name__ == "__main__":
    asyncio.run(import_usitc_data())
