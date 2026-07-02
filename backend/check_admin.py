import sqlite3
import uuid
from datetime import datetime
import bcrypt

conn = sqlite3.connect('tariffnavigator.db')
cursor = conn.cursor()

# Check for admin user
cursor.execute("SELECT id, email FROM users WHERE email = 'admin@test.com'")
admin = cursor.fetchone()

if admin:
    print(f'[OK] Admin user exists: {admin[1]} (ID: {admin[0]})')
else:
    # Create admin user
    user_id = str(uuid.uuid4())
    password = 'admin123'
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    cursor.execute('''
        INSERT INTO users (id, email, hashed_password, full_name, role, is_email_verified, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, 'admin@test.com', hashed, 'Admin User', 'admin', 1, datetime.utcnow().isoformat() + 'Z'))

    conn.commit()
    print(f'[CREATED] Admin user: admin@test.com / admin123')

conn.close()
print('\nLogin at: http://localhost:3007/login')
print('Email: admin@test.com')
print('Password: admin123')
