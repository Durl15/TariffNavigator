import asyncio
from sqlalchemy import text
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db.session import engine

async def seed_more():
    async with engine.begin() as conn:
        await conn.execute(text('''
            INSERT INTO hs_codes (code, description, level, country, mfn_rate, vat_rate, unit)
            VALUES
            -- Electronics
            ('8517', 'Telephone sets, smartphones', 'heading', 'CN', 0.0, 13.0, 'unit'),
            ('8517.12', 'Smartphones', 'subheading', 'CN', 0.0, 13.0, 'unit'),
            ('8528', 'Monitors and televisions', 'heading', 'CN', 5.0, 13.0, 'unit'),
            ('8528.72', 'Flat panel displays', 'subheading', 'CN', 5.0, 13.0, 'unit'),

            -- Clothing
            ('6109', 'T-shirts, singlets and vests, knitted', 'heading', 'CN', 16.0, 13.0, 'unit'),
            ('6109.10', 'T-shirts of cotton', 'subheading', 'CN', 16.0, 13.0, 'unit'),
            ('6203', 'Mens suits, jackets, trousers', 'heading', 'CN', 17.5, 13.0, 'unit'),
            ('6204', 'Womens suits, jackets, dresses', 'heading', 'CN', 17.5, 13.0, 'unit'),

            -- Furniture
            ('9403', 'Furniture and parts thereof', 'heading', 'CN', 0.0, 13.0, 'unit'),
            ('9403.60', 'Wooden furniture', 'subheading', 'CN', 0.0, 13.0, 'unit'),

            -- Books and toys
            ('4901', 'Printed books, brochures, leaflets', 'heading', 'CN', 0.0, 13.0, 'unit'),
            ('9503', 'Toys, scale models', 'heading', 'CN', 0.0, 13.0, 'unit'),

            -- Food
            ('0901', 'Coffee, roasted or not', 'heading', 'CN', 8.0, 13.0, 'kg'),
            ('1704', 'Sugar confectionery', 'heading', 'CN', 15.0, 13.0, 'kg'),

            -- Same for EU
            ('8517', 'Telephone sets, smartphones', 'heading', 'EU', 0.0, 19.0, 'unit'),
            ('8517.12', 'Smartphones', 'subheading', 'EU', 0.0, 19.0, 'unit'),
            ('8528', 'Monitors and televisions', 'heading', 'EU', 14.0, 19.0, 'unit'),
            ('8528.72', 'Flat panel displays', 'subheading', 'EU', 14.0, 19.0, 'unit'),

            ('6109', 'T-shirts, singlets and vests, knitted', 'heading', 'EU', 12.0, 19.0, 'unit'),
            ('6109.10', 'T-shirts of cotton', 'subheading', 'EU', 12.0, 19.0, 'unit'),
            ('6203', 'Mens suits, jackets, trousers', 'heading', 'EU', 12.0, 19.0, 'unit'),
            ('6204', 'Womens suits, jackets, dresses', 'heading', 'EU', 12.0, 19.0, 'unit'),

            ('9403', 'Furniture and parts thereof', 'heading', 'EU', 0.0, 19.0, 'unit'),
            ('9403.60', 'Wooden furniture', 'subheading', 'EU', 0.0, 19.0, 'unit'),

            ('4901', 'Printed books, brochures, leaflets', 'heading', 'EU', 0.0, 19.0, 'unit'),
            ('9503', 'Toys, scale models', 'heading', 'EU', 4.7, 19.0, 'unit'),

            ('0901', 'Coffee, roasted or not', 'heading', 'EU', 7.5, 19.0, 'kg'),
            ('1704', 'Sugar confectionery', 'heading', 'EU', 8.3, 19.0, 'kg')
        '''))
        print('✅ Added 28 more HS codes!')
        print('📱 Electronics: smartphones, computers, TVs')
        print('👕 Clothing: t-shirts, suits, dresses')
        print('🪑 Furniture: wooden furniture')
        print('📚 Books and toys')
        print('☕ Food: coffee, candy')

if __name__ == "__main__":
    asyncio.run(seed_more())
