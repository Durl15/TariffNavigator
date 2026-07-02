import sqlite3

conn = sqlite3.connect('tariffnavigator.db')
cursor = conn.cursor()
cursor.execute('SELECT email, role, is_superuser, is_active FROM users WHERE email = ?', ('admin@test.com',))
result = cursor.fetchone()

if result:
    print(f'Email: {result[0]}')
    print(f'Role: {result[1]}')
    print(f'is_superuser: {result[2]}')
    print(f'is_active: {result[3]}')
else:
    print('User not found')

conn.close()
