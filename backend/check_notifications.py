import sqlite3

conn = sqlite3.connect('tariffnavigator.db')
cursor = conn.cursor()

# Check notifications
cursor.execute('SELECT id, user_id, title, is_read FROM notifications')
notifications = cursor.fetchall()

print("Notifications in database:")
for notif in notifications:
    print(f"  ID: {notif[0]}, User: {notif[1]}, Title: {notif[2]}, Read: {notif[3]}")

# Check admin user ID
cursor.execute('SELECT id, email FROM users WHERE email = ?', ('admin@test.com',))
user = cursor.fetchone()
print(f"\nAdmin user ID: {user[0] if user else 'NOT FOUND'}")

conn.close()
