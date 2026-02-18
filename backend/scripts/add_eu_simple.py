#!/usr/bin/env python3
import asyncio
import asyncpg

async def add_eu_codes():
    conn = await asyncpg.connect(
        'postgresql://tariffnavigator:HPoHAkHCAnO43hu8n1AZKkCQp3gea5LL@dpg-d6a8l7h4tr6s73d48dd0-a/tariffnavigator'
    )

    codes = [
        ('8517', 'Smartphones', 'heading', 'EU', 0.0, 19.0),
        ('8703', 'Cars', 'heading', 'EU', 10.0, 19.0),
        ('8471', 'Computers', 'heading', 'EU', 0.0, 19.0),
        ('6109', 'T-shirts', 'heading', 'EU', 12.0, 19.0),
        ('6203', 'Mens suits', 'heading', 'EU', 12.0, 19.0),
        ('6204', 'Womens suits', 'heading', 'EU', 12.0, 19.0),
        ('9403', 'Furniture', 'heading', 'EU', 0.0, 19.0),
        ('4901', 'Books', 'heading', 'EU', 0.0, 19.0),
        ('9503', 'Toys', 'heading', 'EU', 4.7, 19.0),
        ('0901', 'Coffee', 'heading', 'EU', 7.5, 19.0),
    ]

    added = 0
    for code, desc, level, country, mfn, vat in codes:
        try:
            await conn.execute(
                'INSERT INTO hs_codes (code, description, level, country, mfn_rate, vat_rate, unit) '
                'VALUES ($1, $2, $3, $4, $5, $6, $7)',
                code, desc, level, country, mfn, vat, 'unit'
            )
            print(f'✓ {code} ({country})')
            added += 1
        except Exception as e:
            print(f'⊘ {code} ({country})')

    await conn.close()
    print(f'\n✅ Added {added} EU codes!')

if __name__ == '__main__':
    asyncio.run(add_eu_codes())
