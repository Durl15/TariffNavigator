#!/usr/bin/env python3
"""Create admin user for TariffNavigator"""
import asyncio
import asyncpg
from passlib.context import CryptContext
import uuid
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def create_admin():
    """Create admin user in database"""
    db_url = 'postgresql://tariffnavigator:HPoHAkHCAnO43hu8n1AZKkCQp3gea5LL@dpg-d6a8l7h4tr6s73d48dd0-a/tariffnavigator'

    conn = await asyncpg.connect(db_url)

    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    hashed_password = pwd_context.hash('admin123')
    user_id = str(uuid.uuid4())
    org_id = '00000000-0000-0000-0000-000000000001'  # Default org

    try:
        await conn.execute(
            '''
            INSERT INTO users (
                id, email, hashed_password, full_name, role,
                organization_id, is_active, is_superuser, is_email_verified
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ''',
            user_id, 'admin@test.com', hashed_password, 'Admin User', 'admin',
            org_id, True, True, True
        )
        print('✅ Admin user created successfully!')
        print('')
        print('Login credentials:')
        print('  Email: admin@test.com')
        print('  Password: admin123')
        print('')
        print('Go to: https://tariffnavigator.vercel.app/login')

    except Exception as e:
        error_msg = str(e)
        if 'duplicate' in error_msg or 'unique' in error_msg:
            print('⚠️  Admin user already exists')
            print('Email: admin@test.com')
            print('Password: admin123')
        else:
            print(f'❌ Error creating admin user: {e}')
            raise
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(create_admin())
