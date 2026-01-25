import sqlite3
from datetime import datetime

def create_staff_user():
    conn = sqlite3.connect('deliveries.db')
    cursor = conn.cursor()
    
    # Create a staff user for testing
    staff_username = 'staff1'
    password_hash = 'pbkdf2:sha256:260000$staff_salt$staff_hash'  # Placeholder hash
    
    # Check if staff user already exists
    cursor.execute('SELECT id FROM user WHERE username = ?', (staff_username,))
    existing = cursor.fetchone()
    
    if existing:
        print(f"Staff user '{staff_username}' already exists (ID: {existing[0]})")
    else:
        # Add the staff user
        cursor.execute('''
            INSERT INTO user (username, password_hash, role, created_at, is_active)
            VALUES (?, ?, ?, ?, 1)
        ''', (staff_username, password_hash, 'staff', datetime.now()))
        
        print(f"Created staff user: {staff_username} (role: staff)")
    
    conn.commit()
    
    # Show all users after creating staff
    cursor.execute('SELECT id, username, role, created_at, is_active FROM user ORDER BY created_at DESC')
    users = cursor.fetchall()
    print('\nAll users in database:')
    for user in users:
        print(f'  ID: {user[0]}, Username: {user[1]}, Role: {user[2]}, Created: {user[3]}, Active: {user[4]}')
    
    conn.close()

if __name__ == '__main__':
    create_staff_user()
