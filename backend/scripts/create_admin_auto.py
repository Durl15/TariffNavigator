"""
Create an admin user automatically (non-interactive).
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import async_session
from app.models.user import User
from app.models.organization import Organization
from app.services.auth import get_password_hash
import uuid


async def create_admin(email: str, full_name: str, password: str):
    print("\n[*] Create Admin User")
    print("=" * 50)

    async with async_session() as db:
        # Check if user already exists
        result = await db.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"[!] User with email {email} already exists")
            print(f"    User ID: {existing_user.id}")
            print(f"    Role: {existing_user.role}")
            print(f"    Is Superuser: {existing_user.is_superuser}")
            return existing_user

        # Get or create default organization
        result = await db.execute(
            select(Organization).where(Organization.slug == 'default')
        )
        org = result.scalar_one_or_none()

        if not org:
            org = Organization(
                id=str(uuid.uuid4()),
                name='Default Organization',
                slug='default',
                plan='enterprise',
                status='active',
                max_users=999,
                max_calculations_per_month=999999
            )
            db.add(org)
            await db.flush()
            print(f"[+] Created organization: {org.name}")

        # Create admin user
        hashed_password = get_password_hash(password)
        admin_user = User(
            id=str(uuid.uuid4()),
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role='admin',
            organization_id=org.id,
            is_active=True,
            is_superuser=True,
            is_email_verified=True
        )

        db.add(admin_user)
        await db.commit()

        print("\n" + "=" * 50)
        print("[+] Admin user created successfully!")
        print("=" * 50)
        print(f"Email:        {admin_user.email}")
        print(f"Name:         {admin_user.full_name}")
        print(f"Role:         {admin_user.role}")
        print(f"Superuser:    {admin_user.is_superuser}")
        print(f"Organization: {org.name}")
        print(f"User ID:      {admin_user.id}")
        print("=" * 50)
        print("\n[*] You can now log in with these credentials")
        print(f"    Email: {email}")
        print(f"    Password: {password}\n")

        return admin_user


if __name__ == "__main__":
    # Default credentials
    DEFAULT_EMAIL = "admin@test.com"
    DEFAULT_NAME = "Admin User"
    DEFAULT_PASSWORD = "admin123"

    # Get from command line args or use defaults
    email = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_EMAIL
    full_name = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_NAME
    password = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_PASSWORD

    try:
        asyncio.run(create_admin(email, full_name, password))
    except KeyboardInterrupt:
        print("\n[!] Cancelled by user")
    except Exception as e:
        print(f"\n[!] Error: {str(e)}")
        import traceback
        traceback.print_exc()
