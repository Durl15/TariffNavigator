from sqlalchemy import create_engine, text

url = "postgresql://tariffnavigator:YOURPASS@YOURHOST:5432/tariffnavigator"
engine = create_engine(url, future=True)

sql = text("""
INSERT INTO hs_codes (code, description, level, country, mfn_rate, general_rate, vat_rate, created_at) VALUES
('8703',    'Motor cars',  'tariff', 'CN', 0.15, 0.15, 0.13, NOW()),
('8517.12', 'Smartphones', 'tariff', 'CN', 0.00, 0.00, 0.13, NOW()),
('8471.30', 'Laptops',     'tariff', 'CN', 0.00, 0.00, 0.13, NOW()),
('8703',    'Motor cars',  'tariff', 'EU', 0.10, 0.10, 0.20, NOW()),
('8517.12', 'Smartphones', 'tariff', 'EU', 0.00, 0.00, 0.20, NOW()),
('8471.30', 'Laptops',     'tariff', 'EU', 0.00, 0.00, 0.20, NOW())
ON CONFLICT (code, country) DO NOTHING
""")

with engine.begin() as conn:
    conn.execute(sql)

print("✅ HS codes added!")