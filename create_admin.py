#!/usr/bin/env python3
"""
Admin User Creation Script
Run this script to create or reset the admin user
"""

from app import app, db, User

def create_admin_user():
    """Create or reset the admin user"""
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
                
                print("\nLogin Credentials:")
                print("Username: admin")
                print("Password: ErrantMate@24!")
            else:
                print("Admin user creation failed!")
                
        except Exception as e:
            print(f"Error creating admin user: {e}")
            db.session.rollback()

if __name__ == '__main__':
    print("Creating admin user...")
    create_admin_user()
