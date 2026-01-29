#!/usr/bin/env python3
"""
Reset User Password Script
Run this script to reset password for any user
"""

import os
from app import app, db, User

def reset_user_password(username, new_password):
    """Reset password for a specific user"""
    with app.app_context():
        try:
            user = User.query.filter_by(username=username).first()
            if user:
                user.set_password(new_password)
                db.session.commit()
                print(f"Password reset successfully for user: {user.username}")
                print(f"New login credentials:")
                print(f"  Username: {user.username}")
                print(f"  Password: {new_password}")
                print(f"  Role: {user.role}")
                print(f"  Email: {user.email}")
            else:
                print(f"User '{username}' not found in database")
                
        except Exception as e:
            print(f"Error resetting password: {e}")
            db.session.rollback()

if __name__ == '__main__':
    print("Reset user password...")
    
    # Reset directtest2 user password to a known value
    reset_user_password('directtest2', 'User123@')
    
    print("\nAlso available admin credentials:")
    print("Username: admin")
    print("Password: ErrantMate@24!")
