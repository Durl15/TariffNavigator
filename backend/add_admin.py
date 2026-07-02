# Simple script to add admin user to production database
# Just run: python add_admin.py

import uuid
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# Step 1: Setup password hasher
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Step 2: Production database connection
DATABASE_URL = 'postgresql://tariffnavigator:REDACTED_DB_PASSWORD@dpg-d6a8l7h4tr6s73d48dd0-a.oregon-postgres.render.com/tariffnavigator'

# Step 3: User credentials to create
EMAIL = 'admin@test.com'
PASSWORD = 'password123'
FULL_NAME = 'Admin User'

# Step 4: Connect to database
print('Connecting to database...')
engine = create_engine(DATABASE_URL)

# Step 5: Hash the password
print('Hashing password...')
hashed_password = pwd_context.hash(PASSWORD)

# Step 6: Generate unique ID
user_id = str(uuid.uuid4())

# Step 7: Insert user into database
print('Creating user...')
with engine.begin() as conn:
    conn.execute(
        text("INSERT INTO users (id, email, hashed_password, full_name, is_active, is_email_verified) VALUES (:id, :email, :password, :name, true, true)"),
        {
            'id': user_id,
            'email': EMAIL,
            'password': hashed_password,
            'name': FULL_NAME
        }
    )

# Step 8: Success!
print('')
print('✅ SUCCESS! Admin user created!')
print('')
print('Login credentials:')
print(f'  Email: {EMAIL}')
print(f'  Password: {PASSWORD}')
print('')
print('Go to: https://tariffnavigator-frontend.onrender.com')
print('Click login and use these credentials')
