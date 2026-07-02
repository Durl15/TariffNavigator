"""
Create the demo account on the production database.
Run once: python create_demo_user.py
"""
import uuid
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

DATABASE_URL = 'postgresql://tariffnavigator:REDACTED_DB_PASSWORD@dpg-d6a8l7h4tr6s73d48dd0-a.oregon-postgres.render.com/tariffnavigator'

EMAIL    = 'demo@tariffnavigator.com'
PASSWORD = 'demo1234'
NAME     = 'Demo User'
ROLE     = 'pro'

print('Connecting to production database...')
engine = create_engine(DATABASE_URL)

with engine.begin() as conn:
    existing = conn.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {'email': EMAIL}
    ).fetchone()

    if existing:
        conn.execute(
            text("UPDATE users SET hashed_password = :pw, role = :role, is_active = true, is_email_verified = true WHERE email = :email"),
            {'pw': pwd_context.hash(PASSWORD), 'role': ROLE, 'email': EMAIL}
        )
        action = 'updated'
    else:
        conn.execute(
            text("""
                INSERT INTO users (id, email, hashed_password, full_name, role, is_active, is_email_verified)
                VALUES (:id, :email, :pw, :name, :role, true, true)
            """),
            {'id': str(uuid.uuid4()), 'email': EMAIL, 'pw': pwd_context.hash(PASSWORD),
             'name': NAME, 'role': ROLE}
        )
        action = 'created'

print('Demo account ' + action + ' successfully.')
print('Email:    ' + EMAIL)
print('Password: ' + PASSWORD)
print('Role:     ' + ROLE)
