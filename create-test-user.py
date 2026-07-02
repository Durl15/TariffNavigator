#!/usr/bin/env python3
"""
Create a test user for TariffNavigator
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from app.db.session import AsyncSessionLocal
from app.models.user import User
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_test_user():
    async with AsyncSessionLocal() as db:
        # Check if user exists
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.email == "test@example.com"))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("✓ Test user already exists!")
            print(f"  Email: test@example.com")
            print(f"  Password: test123")
            print(f"  Tier: {existing_user.subscription_tier}")
            return

        # Create new user
        hashed_password = pwd_context.hash("test123")
        new_user = User(
            id=str(uuid.uuid4()),
            email="test@example.com",
            hashed_password=hashed_password,
            full_name="Test User",
            subscription_tier="enterprise",  # Give full access for testing
            is_active=True,
            is_verified=True
        )

        db.add(new_user)
        await db.commit()

        print("✓ Test user created successfully!")
        print(f"  Email: test@example.com")
        print(f"  Password: test123")
        print(f"  Tier: enterprise (unlimited SKUs)")
        print()
        print("You can now login at: http://localhost:3003/login")

if __name__ == "__main__":
    asyncio.run(create_test_user())
