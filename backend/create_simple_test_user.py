"""
Create a simple test user for Module 2 testing.
"""
import sqlite3
import uuid
from datetime import datetime
import bcrypt

# Connect to database
conn = sqlite3.connect('tariffnavigator.db')
cursor = conn.cursor()

# Check if user already exists
cursor.execute("SELECT email FROM users WHERE email = 'test@test.com'")
existing = cursor.fetchone()

if existing:
    print("[INFO] User test@test.com already exists")
else:
    # Create test user
    user_id = str(uuid.uuid4())
    password = "password123"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    cursor.execute("""
        INSERT INTO users (id, email, hashed_password, full_name, role, is_email_verified, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        'test@test.com',
        hashed_password,
        'Test User',
        'user',
        1,  # True
        datetime.utcnow().isoformat() + 'Z'
    ))

    conn.commit()
    print(f"[SUCCESS] Created test user!")
    print(f"  Email: test@test.com")
    print(f"  Password: password123")
    print(f"  ID: {user_id}")

conn.close()

print("\n[LOGIN]")
print("Navigate to: http://localhost:3006/login")
print("Email: test@test.com")
print("Password: password123")
