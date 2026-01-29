#!/usr/bin/env python3
"""
Production Database Table Checker
Run this script to check what tables exist in production database
"""

import os
from app import app, db, User
from sqlalchemy import inspect, text

def check_production_tables():
    """Check what tables exist in production database"""
    with app.app_context():
        try:
            print(f"Database URL: {os.environ.get('DATABASE_URL', 'Not set')}")
            
            # Get table inspector
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            print(f"\nExisting tables in database: {sorted(existing_tables)}")
            
            # Check for both 'user' and 'users' tables
            has_user_table = 'user' in existing_tables
            has_users_table = 'users' in existing_tables
            
            print(f"\nTable Status:")
            print(f"- 'user' table exists: {has_user_table}")
            print(f"- 'users' table exists: {has_users_table}")
            
            # Check which table the User model is using
            print(f"\nUser model table name: {User.__tablename__}")
            
            # Try to query admin user from both tables
            print(f"\nChecking for admin user:")
            
            if has_users_table:
                try:
                    result = db.session.execute(text("SELECT COUNT(*) FROM users WHERE username = 'admin'"))
                    admin_count_users = result.scalar()
                    print(f"- Admin users in 'users' table: {admin_count_users}")
                except Exception as e:
                    print(f"- Error querying 'users' table: {e}")
            
            if has_user_table:
                try:
                    result = db.session.execute(text("SELECT COUNT(*) FROM \"user\" WHERE username = 'admin'"))
                    admin_count_user = result.scalar()
                    print(f"- Admin users in 'user' table: {admin_count_user}")
                except Exception as e:
                    print(f"- Error querying 'user' table: {e}")
            
            # Check foreign key references
            print(f"\nForeign Key References:")
            if has_users_table:
                try:
                    columns = inspector.get_columns('users')
                    print(f"- 'users' table columns: {[col['name'] for col in columns]}")
                except Exception as e:
                    print(f"- Error getting 'users' columns: {e}")
                    
            if has_user_table:
                try:
                    columns = inspector.get_columns('user')
                    print(f"- 'user' table columns: {[col['name'] for col in columns]}")
                except Exception as e:
                    print(f"- Error getting 'user' columns: {e}")
            
            # Recommendation
            print(f"\nRecommendation:")
            if has_users_table and not has_user_table:
                print("CORRECT: Only 'users' table exists - this matches the User model")
            elif has_user_table and not has_users_table:
                print("WARNING: Only 'user' table exists - this doesn't match the User model")
                print("   The User model expects 'users' table. You may need to migrate.")
            elif has_user_table and has_users_table:
                print("WARNING: Both 'user' and 'users' tables exist")
                print("   This could cause confusion. Consider migrating data to 'users' table only.")
            else:
                print("ERROR: Neither 'user' nor 'users' table exists")
                print("   Run database migration to create the required tables.")
                
        except Exception as e:
            print(f"Error checking database: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("Checking production database tables...")
    check_production_tables()
