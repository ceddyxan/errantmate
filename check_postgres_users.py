import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

# Get PostgreSQL connection details
db_url = os.getenv('DATABASE_URL')
print(f'Database URL: {db_url[:50]}...' if db_url else 'No DATABASE_URL found')

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    print('✅ Connected to PostgreSQL database')
    
    # Check if users table exists
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'user';
    """)
    
    table_exists = cursor.fetchone()
    if table_exists:
        print('✅ Users table found')
        
        # Get all users
        cursor.execute("""
            SELECT id, username, role, is_active, created_at 
            FROM "user" 
            ORDER BY username;
        """)
        
        users = cursor.fetchall()
        
        print(f'\n📊 Found {len(users)} users in PostgreSQL:')
        print('=' * 60)
        
        for user in users:
            user_id, username, role, is_active, created_at = user
            status = '✅ Active' if is_active else '❌ Inactive'
            print(f'ID: {user_id:3} | Username: {username:12} | Role: {role:8} | {status} | Created: {created_at}')
        
        print('=' * 60)
        
        # Check for any SQLite users that shouldn't be there
        sqlite_users = ['Datox', 'mary']
        found_sqlite_users = [user[1] for user in users if user[1] in sqlite_users]
        
        if found_sqlite_users:
            print(f'\n⚠️  Found SQLite users in PostgreSQL: {found_sqlite_users}')
        else:
            print('\n✅ No SQLite users found in PostgreSQL')
            
    else:
        print('❌ Users table not found in PostgreSQL')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Error connecting to PostgreSQL: {str(e)}')
