import asyncio
from sqlalchemy import text
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db.session import engine

async def seed_eu():
    """Add EU versions of existing HS codes"""
    codes = [
        # Electronics
        ('8517', 'Telephone sets, smartphones', 'heading', 'EU', 0.0, 19.0),
        ('8517.12', 'Smartphones', 'subheading', 'EU', 0.0, 19.0),
        ('8528', 'Monitors and televisions', 'heading', 'EU', 14.0, 19.0),
        ('8528.72', 'Flat panel displays', 'subheading', 'EU', 14.0, 19.0),
        ('8471', 'Computers and peripheral equipment', 'heading', 'EU', 0.0, 19.0),

        # Vehicles
        ('8703', 'Motor cars and vehicles', 'heading', 'EU', 10.0, 19.0),
        ('8703.23', 'Vehicles with spark-ignition engine 1500-3000cc', 'subheading', 'EU', 10.0, 19.0),
        ('8703.24', 'Vehicles with spark-ignition engine over 3000cc', 'subheading', 'EU', 10.0, 19.0),

        # Clothing
        ('6109', 'T-shirts, singlets and vests, knitted', 'heading', 'EU', 12.0, 19.0),
        ('6109.10', 'T-shirts of cotton', 'subheading', 'EU', 12.0, 19.0),
        ('6203', 'Mens suits, jackets, trousers', 'heading', 'EU', 12.0, 19.0),
        ('6204', 'Womens suits, jackets, dresses', 'heading', 'EU', 12.0, 19.0),

        # Furniture
        ('9403', 'Furniture and parts thereof', 'heading', 'EU', 0.0, 19.0),

        # Books and toys
        ('4901', 'Printed books, brochures, leaflets', 'heading', 'EU', 0.0, 19.0),
        ('9503', 'Toys, scale models', 'heading', 'EU', 4.7, 19.0),

        # Food
        ('0901', 'Coffee, roasted or not', 'heading', 'EU', 7.5, 19.0),
    ]

    async with engine.begin() as conn:
        added = 0
        for code, desc, level, country, mfn, vat in codes:
            try:
                await conn.execute(text(
                    "INSERT INTO hs_codes (code, description, level, country, mfn_rate, vat_rate, unit) "
                    "VALUES (:code, :desc, :level, :country, :mfn, :vat, 'unit')"
                ), {"code": code, "desc": desc, "level": level, "country": country, "mfn": mfn, "vat": vat})
                added += 1
                print(f"✓ Added {code} - {desc} (EU)")
            except Exception as e:
                print(f"✗ Skipped {code} (already exists or error)")

        print(f'\n✅ Successfully added {added} EU HS codes!')
        print('🇪🇺 EU codes now available for: smartphones, TVs, computers, cars, clothing, furniture, books, toys, coffee')

if __name__ == "__main__":
    asyncio.run(seed_eu())
