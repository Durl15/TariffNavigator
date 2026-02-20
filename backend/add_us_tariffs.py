#!/usr/bin/env python3
"""
Add US HTS (Harmonized Tariff Schedule) codes to database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import sqlite3
import uuid

# Sample US tariff rates for common product categories
# Data approximated from USITC HTS database (https://hts.usitc.gov/)
US_TARIFFS = [
    {
        'code': '8517130000',
        'description': 'Smartphones',
        'mfn_rate': 0.0,  # US: Duty-free for smartphones
        'fta_rate': 0.0,
        'fta_countries': 'MX,CA,KR,AU,SG,CL',  # USMCA, KORUS, etc.
        'category': 'Electronics',
        'unit': 'No.'
    },
    {
        'code': '8703230010',
        'description': 'Automobiles with spark-ignition internal combustion reciprocating piston engine, of a cylinder capacity exceeding 1,500 cc but not exceeding 3,000 cc',
        'mfn_rate': 2.5,  # US: 2.5% for passenger vehicles
        'fta_rate': 0.0,
        'fta_countries': 'MX,CA,KR',  # USMCA, KORUS FTA
        'category': 'Automotive',
        'unit': 'No.'
    },
    {
        'code': '8471300000',
        'description': 'Portable automatic data processing machines, weighing not more than 10 kg (laptops, tablets)',
        'mfn_rate': 0.0,  # US: Duty-free under ITA
        'fta_rate': 0.0,
        'fta_countries': 'MX,CA,KR,JP,AU,SG,CL',
        'category': 'Electronics',
        'unit': 'No.'
    },
    {
        'code': '6203420010',
        'description': 'Men\'s or boys\' trousers, bib and brace overalls, breeches and shorts, of cotton',
        'mfn_rate': 16.6,  # US: Typical apparel rate
        'fta_rate': 0.0,
        'fta_countries': 'MX,CA,PE,CL',
        'category': 'Apparel',
        'unit': 'doz.'
    },
    {
        'code': '6402190000',
        'description': 'Sports footwear; other than ski-boots, snowboard boots, or cross-country ski footwear',
        'mfn_rate': 20.0,  # US: High tariff on footwear
        'fta_rate': 0.0,
        'fta_countries': 'MX,CA,PE,CL',
        'category': 'Footwear',
        'unit': 'prs.'
    },
    {
        'code': '6110200010',
        'description': 'Sweaters, pullovers, sweatshirts, waistcoats and similar articles, of cotton, knitted or crocheted',
        'mfn_rate': 16.5,
        'fta_rate': 0.0,
        'fta_countries': 'MX,CA,PE,CL',
        'category': 'Apparel',
        'unit': 'doz.'
    },
    {
        'code': '9403600000',
        'description': 'Other wooden furniture',
        'mfn_rate': 0.0,  # US: Duty-free
        'fta_rate': 0.0,
        'fta_countries': 'MX,CA,KR,AU,SG,CL',
        'category': 'Furniture',
        'unit': 'No.'
    },
    {
        'code': '8528720000',
        'description': 'Reception apparatus for television, color, LCD',
        'mfn_rate': 5.0,
        'fta_rate': 0.0,
        'fta_countries': 'MX,CA,KR,AU,SG,CL',
        'category': 'Electronics',
        'unit': 'No.'
    },
    {
        'code': '4202920000',
        'description': 'Traveling bags, toiletry bags, knapsacks and backpacks, with outer surface of textile materials',
        'mfn_rate': 17.6,
        'fta_rate': 0.0,
        'fta_countries': 'MX,CA,PE,CL',
        'category': 'Bags',
        'unit': 'No.'
    },
    {
        'code': '9503000000',
        'description': 'Tricycles, scooters, pedal cars and similar wheeled toys; dolls\' carriages; dolls; other toys',
        'mfn_rate': 0.0,  # US: Duty-free for most toys
        'fta_rate': 0.0,
        'fta_countries': 'MX,CA,KR,AU,SG,CL',
        'category': 'Toys',
        'unit': 'No.'
    }
]

def add_us_tariffs():
    conn = sqlite3.connect('tariffnavigator.db')
    cursor = conn.cursor()

    # Check if US codes already exist
    cursor.execute("SELECT COUNT(*) FROM hs_codes WHERE country = 'US'")
    existing_count = cursor.fetchone()[0]

    if existing_count > 0:
        print(f"[WARN] Found {existing_count} existing US HS codes. Deleting...")
        cursor.execute("DELETE FROM hs_codes WHERE country = 'US'")
        conn.commit()

    print(f"Adding {len(US_TARIFFS)} US HTS codes...")

    inserted = 0
    for tariff in US_TARIFFS:
        try:
            cursor.execute("""
                INSERT INTO hs_codes (
                    code, description, level, country, mfn_rate, general_rate,
                    vat_rate, consumption_tax, unit, fta_rate, fta_name, fta_countries
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tariff['code'],
                tariff['description'],
                '10',  # 10-digit HTS level
                'US',  # United States
                tariff['mfn_rate'],
                tariff['mfn_rate'],  # general_rate same as mfn_rate
                0.0,  # US has no VAT
                0.0,  # No consumption tax
                tariff['unit'],
                tariff['fta_rate'],
                'USMCA, KORUS, etc.',  # FTA name
                tariff['fta_countries']
            ))
            inserted += 1
            print(f"  [OK] {tariff['code']}: {tariff['description'][:50]}... ({tariff['mfn_rate']}% MFN)")
        except sqlite3.IntegrityError as e:
            print(f"  [SKIP] {tariff['code']}: {e}")

    conn.commit()
    conn.close()

    print(f"\n[SUCCESS] Added {inserted} US HTS codes successfully!")
    print(f"  Country: United States (US)")
    print(f"  Total US codes in database: {inserted}")
    print()
    print("You can now test US tariff calculations:")
    print("  - Navigate to catalog impact page")
    print("  - Select 'Import to USA (US)' in dropdown")
    print("  - View calculated tariff costs")

if __name__ == "__main__":
    add_us_tariffs()
