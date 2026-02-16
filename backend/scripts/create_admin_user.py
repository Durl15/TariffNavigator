"""
Create an admin user for the application.
Run this script once after running migrations.

Usage:
    python scripts/create_admin_user.py
"""
import asyncio
import sys
import os
from getpass import getpass

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import async_session
from app.models.user import User
from app.models.organization import Organization
from app.services.auth import get_password_hash
import uuid


async def create_admin():
    print("\n[*] Create Admin User\n")
    print("=" * 50)

    # Get admin details
    email = input("Admin Email: ").strip()
    if not email or '@' not in email:
        print("[!] Invalid email address")
        return

    full_name = input("Full Name: ").strip()
    password = getpass("Password: ")
    password_confirm = getpass("Confirm Password: ")

    if password != password_confirm:
        print("[!] Passwords do not match")
        return

    if len(password) < 8:
        print("[!] Password must be at least 8 characters")
        return

    print("\n[*] Creating admin user...")

    async with async_session() as db:
        # Check if user already exists
        result = await db.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"[!] User with email {email} already exists")
            return

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
            is_email_verified=True,
            login_count=0
        )

        db.add(admin_user)
        await db.commit()

        print("\n" + "=" * 50)
        print("[+] Admin user created successfully!")
        print("=" * 50)
        print(f"Email:        {admin_user.email}")
        print(f"Role:         {admin_user.role}")
        print(f"Organization: {org.name}")
        print(f"User ID:      {admin_user.id}")
        print("=" * 50)
        print("\n[*] You can now log in with these credentials\n")


if __name__ == "__main__":
    try:
        asyncio.run(create_admin())
    except KeyboardInterrupt:
        print("\n\n[!] Cancelled by user")
    except Exception as e:
        print(f"\n[!] Error: {str(e)}")
        import traceback
        traceback.print_exc()
