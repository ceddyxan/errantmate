#!/usr/bin/env python3
"""
Production Admin User Creation Script
Run this script in production to create the admin user
"""

import os
from app import app, db, User

def create_production_admin():
    """Create admin user in production database"""
    with app.app_context():
        try:
            # Check if admin user already exists
            admin_user = User.query.filter_by(username='admin').first()
            
            if admin_user:
                print(f"Admin user already exists: {admin_user.username} (ID: {admin_user.id})")
                # Reset password
                admin_user.set_password('ErrantMate@24!')
                db.session.commit()
                print("Admin password reset successfully!")
            else:
                # Create new admin user
                admin_user = User(
                    username='admin',
                    email='admin@errantmate.com',
                    phone_number='+1999999999',  # Unique phone number
                    role='admin',
                    is_active=True
                )
                admin_user.set_password('ErrantMate@24!')
                db.session.add(admin_user)
                db.session.commit()
                print(f"Admin user created successfully! ID: {admin_user.id}")
            
            # Verify the user was created
            admin_check = User.query.filter_by(username='admin').first()
            if admin_check:
                print(f"Admin user verified: {admin_check.username}")
                print(f"Email: {admin_check.email}")
                print(f"Role: {admin_check.role}")
                print(f"Active: {admin_check.is_active}")
                print(f"ID: {admin_check.id}")
                
                # Test password
                if admin_check.check_password('ErrantMate@24!'):
                    print("Password verification successful!")
                else:
                    print("Password verification failed!")
                
                print("\nProduction Login Credentials:")
                print("Username: admin")
                print("Password: ErrantMate@24!")
                print("\nDatabase URL:", os.environ.get('DATABASE_URL', 'Not set'))
            else:
                print("Admin user creation failed!")
                
        except Exception as e:
            print(f"Error creating admin user: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == '__main__':
    print("Creating production admin user...")
    create_production_admin()
