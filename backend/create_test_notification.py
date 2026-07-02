"""
Create test notification for testing Module 2 frontend.
"""
import sqlite3
import uuid
from datetime import datetime

# Connect to database
conn = sqlite3.connect('tariffnavigator.db')
cursor = conn.cursor()

# Get a test user (use the first user in the database)
cursor.execute("SELECT id, email FROM users LIMIT 1")
user = cursor.fetchone()

if not user:
    print("[ERROR] No users found in database. Please create a user first.")
    conn.close()
    exit(1)

user_id, user_email = user
print(f"[OK] Found user: {user_email} (ID: {user_id})")

# Create test notification
notification_id = str(uuid.uuid4())
notification_data = {
    'id': notification_id,
    'user_id': user_id,
    'type': 'rate_change',
    'title': 'Test: Tariff Rate Change Detected',
    'message': 'HS Code 8703.23 (CN): Rate increased from 5% to 7.5%',
    'link': '/tariff/8703.23?country=CN',
    'data': '{"hs_code": "8703.23", "country": "CN", "old_rate": 5.0, "new_rate": 7.5}',
    'is_read': 0,  # False
    'created_at': datetime.utcnow().isoformat() + 'Z'
}

try:
    cursor.execute("""
        INSERT INTO notifications (id, user_id, type, title, message, link, data, is_read, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        notification_data['id'],
        notification_data['user_id'],
        notification_data['type'],
        notification_data['title'],
        notification_data['message'],
        notification_data['link'],
        notification_data['data'],
        notification_data['is_read'],
        notification_data['created_at']
    ))

    conn.commit()
    print(f"\n[SUCCESS] Created test notification!")
    print(f"  ID: {notification_id}")
    print(f"  Title: {notification_data['title']}")
    print(f"  User: {user_email}")

    # Create a second notification for better testing
    notification_id2 = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO notifications (id, user_id, type, title, message, link, data, is_read, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        notification_id2,
        user_id,
        'deadline',
        'Test: Compliance Deadline Approaching',
        'Section 301 tariff review deadline: March 1, 2026',
        None,
        '{"deadline": "2026-03-01", "program": "Section 301"}',
        0,
        datetime.utcnow().isoformat() + 'Z'
    ))

    conn.commit()
    print(f"\n[SUCCESS] Created second test notification!")
    print(f"  ID: {notification_id2}")

    # Count total notifications for this user
    cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    print(f"\n[INFO] Total notifications for {user_email}: {count}")

except sqlite3.IntegrityError as e:
    print(f"\n[ERROR] Failed to create notification: {e}")
except Exception as e:
    print(f"\n[ERROR] Unexpected error: {e}")
finally:
    conn.close()

print("\n[NEXT STEPS]")
print("1. Login to the application with: " + user_email)
print("2. Check the notification bell in the header")
print("3. Navigate to /notifications to see the full list")
print("4. Navigate to /watchlists to create a watchlist")
