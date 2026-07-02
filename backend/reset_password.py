# Reset password for existing admin user
# Just run: python reset_password.py

from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# Step 1: Setup password hasher
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Step 2: Production database connection
DATABASE_URL = 'postgresql://tariffnavigator:REDACTED_DB_PASSWORD@dpg-d6a8l7h4tr6s73d48dd0-a.oregon-postgres.render.com/tariffnavigator'

# Step 3: User to update
EMAIL = 'admin@test.com'
NEW_PASSWORD = 'password123'

# Step 4: Connect to database
print('Connecting to database...')
engine = create_engine(DATABASE_URL)

# Step 5: Hash the new password
print('Hashing new password...')
hashed_password = pwd_context.hash(NEW_PASSWORD)

# Step 6: Update user password and make sure user is active
print('Updating user...')
with engine.begin() as conn:
    result = conn.execute(
        text("UPDATE users SET hashed_password = :password, is_active = true, is_email_verified = true WHERE email = :email"),
        {
            'email': EMAIL,
            'password': hashed_password
        }
    )

    if result.rowcount == 0:
        print('❌ ERROR: User not found!')
    else:
        print('')
        print('✅ SUCCESS! Password reset!')
        print('')
        print('Login credentials:')
        print(f'  Email: {EMAIL}')
        print(f'  Password: {NEW_PASSWORD}')
        print('')
        print('Go to: https://tariffnavigator-frontend.onrender.com')
        print('Click login and use these credentials')
