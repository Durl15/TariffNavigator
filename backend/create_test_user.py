"""Create test user directly in database"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from passlib.context import CryptContext
import uuid
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database setup
import sqlite3

def create_test_user():
    conn = sqlite3.connect('tariffnavigator.db')
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT email FROM users WHERE email = ?", ("test@test.com",))
    if cursor.fetchone():
        print("✓ Test user already exists!")
        print("  Email: test@test.com")
        print("  Password: test123")
        conn.close()
        return

    # Create user
    user_id = str(uuid.uuid4())
    hashed_password = pwd_context.hash("test123")

    cursor.execute("""
        INSERT INTO users (id, email, hashed_password, full_name, role, is_active, is_email_verified)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        "test@test.com",
        hashed_password,
        "Test User",
        "admin",  # Admin role for full access
        1,  # is_active
        1   # is_email_verified
    ))

    conn.commit()
    conn.close()

    print("✓ Test user created successfully!")
    print("  Email: test@test.com")
    print("  Password: test123")
    print("  Tier: enterprise (unlimited SKUs)")
    print()
    print("Login at: http://localhost:3003/login")

if __name__ == "__main__":
    create_test_user()
