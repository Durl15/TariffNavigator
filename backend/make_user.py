import os
import uuid
import argparse
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

#!/usr/bin/env python3

pwd = CryptContext(schemes=['bcrypt'], deprecated='auto')

def main():
    parser = argparse.ArgumentParser(description='Create a user in the PostgreSQL users table.')
    parser.add_argument('--db-url', required=bool(os.environ.get('DATABASE_URL') is None),
                        default=os.environ.get('DATABASE_URL'),
                        help='Database URL (or set DATABASE_URL env var)')
    parser.add_argument('--email', default='admin@test.com')
    parser.add_argument('--password', default='password123')
    parser.add_argument('--name', default='Admin')
    parser.add_argument('--active', action='store_true', help='Mark user as active')
    parser.add_argument('--verified', action='store_true', help='Mark email as verified')
    args = parser.parse_args()

    if not args.db_url:
        raise SystemExit('DATABASE_URL not provided (use --db-url or set DATABASE_URL env var).')

    engine = create_engine(args.db_url)
    hashed = pwd.hash(args.password)
    user_id = str(uuid.uuid4())

    insert_sql = text("""
        INSERT INTO users (id, email, hashed_password, full_name, is_active, is_email_verified)
        VALUES (:id, :email, :p, :full_name, :is_active, :is_email_verified)
    """)

    with engine.begin() as conn:
        conn.execute(insert_sql, {
            'id': user_id,
            'email': args.email,
            'p': hashed,
            'full_name': args.name,
            'is_active': args.active,
            'is_email_verified': args.verified
        })

    print('✅ User created!')
    print(f'Email: {args.email}')
    print(f'Password: {args.password}')
    print('Remember to secure your DATABASE_URL and avoid committing secrets to source control.')

if __name__ == '__main__':
    main()