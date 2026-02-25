import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

db_url = os.getenv('DATABASE_URL')
print('Connecting to PostgreSQL...')

try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Get all users
    cursor.execute('SELECT id, username, role, is_active, created_at FROM "user" ORDER BY username')
    users = cursor.fetchall()
    
    print(f'Found {len(users)} users in PostgreSQL:')
    print('=' * 50)
    
    for user in users:
        user_id, username, role, is_active, created_at = user
        status = 'Active' if is_active else 'Inactive'
        print(f'ID: {user_id} | {username} | {role} | {status} | {created_at}')
    
    print('=' * 50)
    
    # Check for problem users
    problem_users = []
    for user in users:
        username = user[1]
        if username in ['Datox', 'mary']:
            problem_users.append(username)
    
    if problem_users:
        print(f'PROBLEM: Found SQLite users in PostgreSQL: {problem_users}')
    else:
        print('GOOD: No SQLite users found')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'Error: {e}')
