#!/usr/bin/env python3
"""Add comprehensive HS codes for various product categories"""
import asyncio
import asyncpg
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def add_comprehensive_codes():
    """Add 50+ HS codes across multiple categories"""
    db_url = 'postgresql://tariffnavigator:HPoHAkHCAnO43hu8n1AZKkCQp3gea5LL@dpg-d6a8l7h4tr6s73d48dd0-a/tariffnavigator'
    conn = await asyncpg.connect(db_url)

    # Format: (code, description, level, country, mfn_rate, vat_rate)
    codes = [
        # Electronics & Technology
        ('8525', 'Video cameras and recorders', 'heading', 'CN', 0.0, 13.0),
        ('8525', 'Video cameras and recorders', 'heading', 'EU', 0.0, 19.0),
        ('8517.62', 'Wireless network equipment', 'subheading', 'CN', 0.0, 13.0),
        ('8517.62', 'Wireless network equipment', 'subheading', 'EU', 0.0, 19.0),
        ('8519', 'Audio players and recorders', 'heading', 'CN', 0.0, 13.0),
        ('8519', 'Audio players and recorders', 'heading', 'EU', 0.0, 19.0),
        ('8529', 'Parts for phones and cameras', 'heading', 'CN', 0.0, 13.0),
        ('8529', 'Parts for phones and cameras', 'heading', 'EU', 0.0, 19.0),
        ('8523', 'USB drives and memory cards', 'heading', 'CN', 0.0, 13.0),
        ('8523', 'USB drives and memory cards', 'heading', 'EU', 0.0, 19.0),

        # Home Appliances
        ('8509', 'Vacuum cleaners and appliances', 'heading', 'CN', 10.0, 13.0),
        ('8509', 'Vacuum cleaners and appliances', 'heading', 'EU', 6.5, 19.0),
        ('8516', 'Electric heaters and dryers', 'heading', 'CN', 8.0, 13.0),
        ('8516', 'Electric heaters and dryers', 'heading', 'EU', 6.7, 19.0),
        ('8418', 'Refrigerators and freezers', 'heading', 'CN', 8.0, 13.0),
        ('8418', 'Refrigerators and freezers', 'heading', 'EU', 2.5, 19.0),
        ('8450', 'Washing machines', 'heading', 'CN', 8.0, 13.0),
        ('8450', 'Washing machines', 'heading', 'EU', 2.5, 19.0),

        # Footwear
        ('6403', 'Leather footwear', 'heading', 'CN', 13.0, 13.0),
        ('6403', 'Leather footwear', 'heading', 'EU', 8.0, 19.0),
        ('6404', 'Textile footwear', 'heading', 'CN', 13.0, 13.0),
        ('6404', 'Textile footwear', 'heading', 'EU', 12.0, 19.0),
        ('6402', 'Sports footwear', 'heading', 'CN', 13.0, 13.0),
        ('6402', 'Sports footwear', 'heading', 'EU', 16.9, 19.0),

        # Bags and Accessories
        ('4202', 'Leather bags and handbags', 'heading', 'CN', 8.0, 13.0),
        ('4202', 'Leather bags and handbags', 'heading', 'EU', 3.0, 19.0),
        ('6117', 'Scarves and accessories', 'heading', 'CN', 14.0, 13.0),
        ('6117', 'Scarves and accessories', 'heading', 'EU', 12.0, 19.0),
        ('7113', 'Jewelry of precious metal', 'heading', 'CN', 15.0, 13.0),
        ('7113', 'Jewelry of precious metal', 'heading', 'EU', 2.5, 19.0),

        # Cosmetics & Personal Care
        ('3304', 'Beauty and makeup products', 'heading', 'CN', 10.0, 13.0),
        ('3304', 'Beauty and makeup products', 'heading', 'EU', 0.0, 19.0),
        ('3305', 'Hair care products', 'heading', 'CN', 6.5, 13.0),
        ('3305', 'Hair care products', 'heading', 'EU', 0.0, 19.0),
        ('3307', 'Perfumes and fragrances', 'heading', 'CN', 10.0, 13.0),
        ('3307', 'Perfumes and fragrances', 'heading', 'EU', 0.0, 19.0),
        ('3401', 'Soap and cleaning products', 'heading', 'CN', 6.5, 13.0),
        ('3401', 'Soap and cleaning products', 'heading', 'EU', 0.0, 19.0),

        # Sports Equipment
        ('9506', 'Sports equipment', 'heading', 'CN', 8.0, 13.0),
        ('9506', 'Sports equipment', 'heading', 'EU', 2.7, 19.0),
        ('6506', 'Hats and headgear', 'heading', 'CN', 14.0, 13.0),
        ('6506', 'Hats and headgear', 'heading', 'EU', 2.7, 19.0),

        # Kitchenware & Tableware
        ('6911', 'Ceramic tableware', 'heading', 'CN', 7.0, 13.0),
        ('6911', 'Ceramic tableware', 'heading', 'EU', 12.0, 19.0),
        ('7323', 'Steel kitchen utensils', 'heading', 'CN', 8.0, 13.0),
        ('7323', 'Steel kitchen utensils', 'heading', 'EU', 2.7, 19.0),
        ('8211', 'Knives and cutting blades', 'heading', 'CN', 7.0, 13.0),
        ('8211', 'Knives and cutting blades', 'heading', 'EU', 0.0, 19.0),

        # Lighting
        ('9405', 'Lamps and lighting fixtures', 'heading', 'CN', 8.0, 13.0),
        ('9405', 'Lamps and lighting fixtures', 'heading', 'EU', 3.0, 19.0),
        ('8539', 'Light bulbs and LED lamps', 'heading', 'CN', 5.0, 13.0),
        ('8539', 'Light bulbs and LED lamps', 'heading', 'EU', 2.7, 19.0),

        # Textiles & Bedding
        ('6302', 'Bed linen and table linen', 'heading', 'CN', 8.0, 13.0),
        ('6302', 'Bed linen and table linen', 'heading', 'EU', 12.0, 19.0),
        ('6304', 'Curtains and interior blinds', 'heading', 'CN', 8.0, 13.0),
        ('6304', 'Curtains and interior blinds', 'heading', 'EU', 12.0, 19.0),

        # Baby Products
        ('9503.00', 'Toys for children', 'subheading', 'CN', 0.0, 13.0),
        ('9503.00', 'Toys for children', 'subheading', 'EU', 4.7, 19.0),
        ('9404', 'Mattresses and cushions', 'heading', 'CN', 8.0, 13.0),
        ('9404', 'Mattresses and cushions', 'heading', 'EU', 2.7, 19.0),

        # Watches & Clocks
        ('9102', 'Wristwatches', 'heading', 'CN', 11.0, 13.0),
        ('9102', 'Wristwatches', 'heading', 'EU', 4.5, 19.0),

        # Musical Instruments
        ('9207', 'Musical instruments', 'heading', 'CN', 0.0, 13.0),
        ('9207', 'Musical instruments', 'heading', 'EU', 0.0, 19.0),

        # Stationery
        ('9608', 'Pens and markers', 'heading', 'CN', 0.0, 13.0),
        ('9608', 'Pens and markers', 'heading', 'EU', 0.0, 19.0),
        ('4820', 'Notebooks and stationery', 'heading', 'CN', 0.0, 13.0),
        ('4820', 'Notebooks and stationery', 'heading', 'EU', 0.0, 19.0),

        # Luggage & Travel
        ('4202.92', 'Travel bags and suitcases', 'subheading', 'CN', 8.0, 13.0),
        ('4202.92', 'Travel bags and suitcases', 'subheading', 'EU', 3.7, 19.0),

        # Eyewear
        ('9004', 'Sunglasses and eyeglasses', 'heading', 'CN', 7.0, 13.0),
        ('9004', 'Sunglasses and eyeglasses', 'heading', 'EU', 2.0, 19.0),

        # Beverages
        ('2202', 'Soft drinks and juices', 'heading', 'CN', 15.0, 13.0),
        ('2202', 'Soft drinks and juices', 'heading', 'EU', 9.6, 19.0),
        ('2203', 'Beer', 'heading', 'CN', 0.0, 13.0),
        ('2203', 'Beer', 'heading', 'EU', 0.0, 19.0),
        ('2204', 'Wine', 'heading', 'CN', 14.0, 13.0),
        ('2204', 'Wine', 'heading', 'EU', 13.5, 19.0),

        # Food Products
        ('1806', 'Chocolate and cocoa products', 'heading', 'CN', 8.0, 13.0),
        ('1806', 'Chocolate and cocoa products', 'heading', 'EU', 8.3, 19.0),
        ('1905', 'Bread, pastry, biscuits', 'heading', 'CN', 15.0, 13.0),
        ('1905', 'Bread, pastry, biscuits', 'heading', 'EU', 9.0, 19.0),
        ('0802', 'Nuts (almonds, cashews)', 'heading', 'CN', 10.0, 13.0),
        ('0802', 'Nuts (almonds, cashews)', 'heading', 'EU', 3.5, 19.0),
        ('2008', 'Canned fruits and vegetables', 'heading', 'CN', 15.0, 13.0),
        ('2008', 'Canned fruits and vegetables', 'heading', 'EU', 20.0, 19.0),
    ]

    added = 0
    skipped = 0

    print(f'Adding {len(codes)} HS codes...\n')

    for code, desc, level, country, mfn, vat in codes:
        try:
            await conn.execute(
                'INSERT INTO hs_codes (code, description, level, country, mfn_rate, vat_rate, unit) '
                'VALUES ($1, $2, $3, $4, $5, $6, $7)',
                code, desc, level, country, mfn, vat, 'unit'
            )
            print(f'✓ {code} ({country}) - {desc}')
            added += 1
        except Exception as e:
            if 'unique' in str(e) or 'duplicate' in str(e):
                skipped += 1
            else:
                print(f'✗ {code} ({country}) - Error: {e}')

    await conn.close()

    print(f'\n{"="*70}')
    print(f'✅ Successfully added: {added} codes')
    print(f'⊘  Already existed: {skipped} codes')
    print(f'{"="*70}')
    print('\n📦 New product categories:')
    print('  • Electronics: cameras, audio, network equipment')
    print('  • Home appliances: vacuum cleaners, fridges, washing machines')
    print('  • Footwear: leather shoes, sports shoes, textile footwear')
    print('  • Fashion accessories: bags, jewelry, scarves')
    print('  • Cosmetics: makeup, hair care, perfumes, soap')
    print('  • Sports equipment & hats')
    print('  • Kitchenware: tableware, utensils, knives')
    print('  • Lighting: lamps, LED bulbs')
    print('  • Textiles: bed linen, curtains')
    print('  • Baby products & toys')
    print('  • Watches & musical instruments')
    print('  • Stationery: pens, notebooks')
    print('  • Luggage & eyewear')
    print('  • Beverages: soft drinks, beer, wine')
    print('  • Food: chocolate, biscuits, nuts, canned goods')

if __name__ == '__main__':
    asyncio.run(add_comprehensive_codes())
