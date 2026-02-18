#!/usr/bin/env python3
"""Add all missing HS codes - with proper error handling"""
import asyncio
from sqlalchemy import text
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db.session import engine

async def add_codes():
    codes = [
        # CN Electronics
        ('8517', 'Telephone sets, smartphones', 'heading', 'CN', 0.0, 13.0),
        ('8517.12', 'Smartphones', 'subheading', 'CN', 0.0, 13.0),

        # CN Clothing
        ('6109', 'T-shirts, knitted', 'heading', 'CN', 16.0, 13.0),
        ('6109.10', 'T-shirts of cotton', 'subheading', 'CN', 16.0, 13.0),
        ('6203', 'Mens suits, jackets', 'heading', 'CN', 17.5, 13.0),
        ('6204', 'Womens suits, dresses', 'heading', 'CN', 17.5, 13.0),

        # CN Other
        ('9403', 'Furniture', 'heading', 'CN', 0.0, 13.0),
        ('4901', 'Books', 'heading', 'CN', 0.0, 13.0),
        ('9503', 'Toys', 'heading', 'CN', 0.0, 13.0),
        ('0901', 'Coffee', 'heading', 'CN', 8.0, 13.0),

        # EU Electronics
        ('8517', 'Telephone sets, smartphones', 'heading', 'EU', 0.0, 19.0),
        ('8517.12', 'Smartphones', 'subheading', 'EU', 0.0, 19.0),

        # EU Vehicles
        ('8703', 'Motor cars and vehicles', 'heading', 'EU', 10.0, 19.0),
        ('8703.23', 'Cars 1500-3000cc', 'subheading', 'EU', 10.0, 19.0),
        ('8703.24', 'Cars over 3000cc', 'subheading', 'EU', 10.0, 19.0),

        # EU Other
        ('8471', 'Computers', 'heading', 'EU', 0.0, 19.0),
        ('6109', 'T-shirts knitted', 'heading', 'EU', 12.0, 19.0),
        ('6109.10', 'T-shirts cotton', 'subheading', 'EU', 12.0, 19.0),
        ('6203', 'Mens suits', 'heading', 'EU', 12.0, 19.0),
        ('6204', 'Womens suits', 'heading', 'EU', 12.0, 19.0),
        ('9403', 'Furniture', 'heading', 'EU', 0.0, 19.0),
        ('4901', 'Books', 'heading', 'EU', 0.0, 19.0),
        ('9503', 'Toys', 'heading', 'EU', 4.7, 19.0),
        ('0901', 'Coffee', 'heading', 'EU', 7.5, 19.0),
    ]

    print(f"Attempting to add {len(codes)} HS codes...")
    added = 0
    skipped = 0
    errors = 0

    async with engine.begin() as conn:
        for code, desc, level, country, mfn, vat in codes:
            try:
                # First check if exists
                check = await conn.execute(
                    text("SELECT code FROM hs_codes WHERE code = :code AND country = :country"),
                    {"code": code, "country": country}
                )
                exists = check.fetchone()

                if exists:
                    print(f"  ⊘ {code} ({country}) - already exists")
                    skipped += 1
                    continue

                # Insert new code
                await conn.execute(
                    text("""
                        INSERT INTO hs_codes (code, description, level, country, mfn_rate, vat_rate, unit)
                        VALUES (:code, :desc, :level, :country, :mfn, :vat, 'unit')
                    """),
                    {"code": code, "desc": desc, "level": level, "country": country, "mfn": mfn, "vat": vat}
                )
                print(f"  ✓ {code} ({country}) - {desc}")
                added += 1

            except Exception as e:
                print(f"  ✗ {code} ({country}) - ERROR: {e}")
                errors += 1

    print(f"\n{'='*60}")
    print(f"✅ Successfully added: {added}")
    print(f"⊘  Already existed: {skipped}")
    print(f"✗  Errors: {errors}")
    print(f"{'='*60}")

    if added > 0:
        print("\n🎉 Test your calculator now!")
        print("   CN: Search for 'smartphone', 'shirt', 'furniture', 'toy', 'coffee'")
        print("   EU: Search for 'smartphone', 'car', 'shirt', 'furniture'")

if __name__ == "__main__":
    asyncio.run(add_codes())
