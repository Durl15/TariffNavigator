import asyncio
import uuid
from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def create_user():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto").hash("Admin2026!")
    user_id = str(uuid.uuid4())
    async with async_session() as db:
        await db.execute(text("""
            INSERT INTO users (id, email, hashed_password, full_name, role, is_active, is_email_verified)
            VALUES (:id, :email, :pw, :name, :role, :active, :verified)
            ON CONFLICT (email) DO UPDATE SET
            hashed_password = EXCLUDED.hashed_password,
            role = EXCLUDED.role,
            is_active = EXCLUDED.is_active
        """), {
            "id": user_id,
            "email": "don@djaibc.com",
            "pw": pwd,
            "name": "Don Johnson",
            "role": "admin",
            "active": True,
            "verified": True
        })
        await db.commit()
        print("Admin user created: don@djaibc.com / Admin2026!")

asyncio.run(create_user())