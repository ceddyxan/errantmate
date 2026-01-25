import sqlite3

conn = sqlite3.connect('deliveries.db')
cursor = conn.cursor()

# Check tables
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Tables:', tables)

# Check users if table exists
if ('user',) in tables:
    cursor.execute('SELECT id, username, role, created_at, is_active FROM user ORDER BY created_at DESC')
    users = cursor.fetchall()
    print('\nUsers:')
    for user in users:
        print(f'  ID: {user[0]}, Username: {user[1]}, Role: {user[2]}, Created: {user[3]}, Active: {user[4]}')
else:
    print('No user table found')

conn.close()
