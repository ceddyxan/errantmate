import sqlite3
from datetime import datetime

def add_users():
    conn = sqlite3.connect('deliveries.db')
    cursor = conn.cursor()
    
    users_to_add = [
        ('bravin', 'user', '2026-01-23 11:27:00'),
        ('mary', 'user', '2026-01-23 11:28:00'), 
        ('frank', 'user', '2026-01-23 11:31:00')
    ]
    
    for username, role, created_at in users_to_add:
        # Check if user already exists
        cursor.execute('SELECT id FROM user WHERE username = ?', (username,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"User '{username}' already exists (ID: {existing[0]})")
        else:
            # Add the user with simple password hash
            password_hash = 'pbkdf2:sha256:260000$salt$hash'  # Placeholder hash
            cursor.execute('''
                INSERT INTO user (username, password_hash, role, created_at, is_active)
                VALUES (?, ?, ?, ?, 1)
            ''', (username, password_hash, role, created_at))
            
            print(f"Added user: {username} (role: {role})")
    
    conn.commit()
    
    # Show all users after adding
    cursor.execute('SELECT id, username, role, created_at, is_active FROM user ORDER BY created_at DESC')
    users = cursor.fetchall()
    print('\nAll users in database:')
    for user in users:
        print(f'  ID: {user[0]}, Username: {user[1]}, Role: {user[2]}, Created: {user[3]}, Active: {user[4]}')
    
    conn.close()

if __name__ == '__main__':
    add_users()
