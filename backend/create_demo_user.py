"""Create demo user for the login page"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from passlib.context import CryptContext
import uuid
import sqlite3

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_demo_user():
    conn = sqlite3.connect('tariffnavigator.db')
    cursor = conn.cursor()

    email = "demo@tariffnavigator.com"
    password = "demo1234"

    cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        # Update password in case it changed
        hashed = pwd_context.hash(password)
        cursor.execute("UPDATE users SET hashed_password = ?, role = ?, is_active = 1, is_email_verified = 1 WHERE email = ?",
                       (hashed, "pro", email))
        conn.commit()
        print(f"✓ Demo user updated: {email} / {password}")
        conn.close()
        return

    user_id = str(uuid.uuid4())
    hashed = pwd_context.hash(password)

    cursor.execute("""
        INSERT INTO users (id, email, hashed_password, full_name, role, is_active, is_email_verified)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, email, hashed, "Demo User", "pro", 1, 1))

    conn.commit()
    conn.close()

    print(f"✓ Demo user created!")
    print(f"  Email:    {email}")
    print(f"  Password: {password}")
    print(f"  Role:     pro")

if __name__ == "__main__":
    create_demo_user()
