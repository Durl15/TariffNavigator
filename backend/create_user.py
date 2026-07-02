from sqlalchemy import create_engine, text
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
url = 'postgresql://tariffnavigator:REDACTED_DB_PASSWORD@dpg-d6a8l7h4tr6s73d48dd0-a.oregon-postgres.render.com/tariffnavigator'
engine = create_engine(url)
hashed = pwd_context.hash('password123')
with engine.connect() as conn:
    conn.execute(text
        ("""
         INSERT INTO users (email, hashed_password, full_name, role, is_active, is_email_verified, created_at)
         VALUES ('admin@test.com', :pwd, 'Admin User', 'user', true, true, NOW())
         ON CONFLICT (email) DO NOTHING
      """), {'pwd': hashed})
    conn.commit()
print('✅ User created!')
print('Email: admin@test.com')
print('Password: password123')