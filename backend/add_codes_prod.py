 import asyncio                                                                                                                  from sqlalchemy import create_engine, text

  DATABASE_URL = "postgresql+asyncpg://tariffnavigator:REDACTED_DB_PASSWORD@dpg-d6a8l7h4tr6s73d48dd0-a/tariffnavigator"

  engine = create_engine(DATABASE_URL.replace('postgresql+asyncpg', 'postgresql'))

  sql = """
  INSERT INTO hs_codes (code, description, level, country, mfn_rate, general_rate, vat_rate, created_at) VALUES
  ('8703', 'Motor cars', 'tariff', 'CN', 0.15, 0.15, 0.13, NOW()),
  ('8517.12', 'Smartphones', 'tariff', 'CN', 0.0, 0.0, 0.13, NOW()),
  ('8471.30', 'Laptops', 'tariff', 'CN', 0.0, 0.0, 0.13, NOW()),
  ('8703', 'Motor cars', 'tariff', 'EU', 0.1, 0.1, 0.2, NOW()),
  ('8517.12', 'Smartphones', 'tariff', 'EU', 0.0, 0.0, 0.2, NOW()),
  ('8471.30', 'Laptops', 'tariff', 'EU', 0.0, 0.0, 0.2, NOW())
  ON CONFLICT (code, country) DO NOTHING;
  """

  with engine.connect() as conn:
      conn.execute(text(sql))
      conn.commit()
  print("✅ Done!")