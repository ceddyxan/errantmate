#!/usr/bin/env python3
"""
Temporary script to check production users and roles
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def check_production_users():
    """Check users in production database"""
    try:
        # Get production database URL from environment
        database_url = os.environ.get('DATABASE_URL')
        
        if not database_url:
            print("DATABASE_URL environment variable not found")
            print("This script needs to be run in the production environment")
            return
        
        print(f"Connecting to production database...")
        
        # Connect to production database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if Peter exists
        cursor.execute("""
            SELECT username, role, is_active, created_at 
            FROM "user" 
            WHERE username ILIKE %s
        """, ('%peter%',))
        
        peter_users = cursor.fetchall()
        
        if peter_users:
            print("\n=== Found Peter users ===")
            for user in peter_users:
                print(f"Username: {user['username']}")
                print(f"Role: {user['role']}")
                print(f"Active: {user['is_active']}")
                print(f"Created: {user['created_at']}")
                print("-" * 30)
        else:
            print("\n=== No Peter users found ===")
        
        # Show all users for context
        cursor.execute("""
            SELECT username, role, is_active, created_at 
            FROM "user" 
            ORDER BY username
        """)
        
        all_users = cursor.fetchall()
        
        print(f"\n=== All Production Users ({len(all_users)} total) ===")
        for user in all_users:
            print(f"{user['username']} ({user['role']}) - {'Active' if user['is_active'] else 'Inactive'}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error checking production users: {e}")
        print("Make sure you're running this in the production environment")

if __name__ == "__main__":
    check_production_users()
