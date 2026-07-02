import sqlite3
import uuid
from datetime import datetime

conn = sqlite3.connect('tariffnavigator.db')
cursor = conn.cursor()

# Get test@test.com user
cursor.execute("SELECT id FROM users WHERE email = 'test@test.com'")
user = cursor.fetchone()

if user:
    user_id = user[0]

    # Check if notifications already exist
    cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]

    if count == 0:
        # Create test notifications
        cursor.execute("""
            INSERT INTO notifications (id, user_id, type, title, message, link, data, is_read, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            user_id,
            'rate_change',
            'Tariff Rate Change Detected',
            'HS Code 8703.23 (CN): Rate increased from 5% to 7.5%',
            '/tariff/8703.23?country=CN',
            '{"hs_code": "8703.23", "country": "CN", "old_rate": 5.0, "new_rate": 7.5}',
            0,
            datetime.utcnow().isoformat() + 'Z'
        ))

        cursor.execute("""
            INSERT INTO notifications (id, user_id, type, title, message, is_read, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            user_id,
            'deadline',
            'Compliance Deadline Approaching',
            'Section 301 tariff review deadline: March 1, 2026',
            0,
            datetime.utcnow().isoformat() + 'Z'
        ))

        conn.commit()
        print('[SUCCESS] Created 2 test notifications for test@test.com')
    else:
        print(f'[INFO] User already has {count} notifications')

conn.close()
