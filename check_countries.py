import sqlite3

conn = sqlite3.connect('backend/tariffnavigator.db')
cursor = conn.cursor()

cursor.execute('SELECT DISTINCT country FROM hs_codes ORDER BY country')
countries = cursor.fetchall()
print('Available countries in hs_codes table:')
for c in countries:
    print(f'  - {c[0]}')

cursor.execute('SELECT COUNT(*) FROM hs_codes WHERE country = "CN"')
print(f'\nTotal CN HS codes: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM hs_codes WHERE country = "US"')
print(f'Total US HS codes: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM hs_codes WHERE country = "EU"')
print(f'Total EU HS codes: {cursor.fetchone()[0]}')

conn.close()
