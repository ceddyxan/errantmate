#!/usr/bin/env python3
"""
Direct Login Test Script
Test login functionality directly without browser
"""

from app import app, db, User
from flask import session
import sys

def test_login(username, password):
    """Test login functionality directly"""
    with app.test_request_context():
        try:
            print(f"Testing login for: {username}")
            
            # Find user
            user = User.query.filter_by(username=username).first()
            if not user:
                print(f"User '{username}' not found")
                return False
            
            print(f"User found: {user.username} (Role: {user.role})")
            
            # Check password
            if not user.check_password(password):
                print(f"Password incorrect for '{username}'")
                return False
            
            print(f"Password verified for '{username}'")
            
            # Check if user is active
            if not user.is_active:
                print(f"User '{username}' is not active")
                return False
            
            print(f"User '{username}' is active")
            
            # Simulate login session creation
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_role'] = user.role
            session.permanent = True
            
            print(f"Session created for '{username}'")
            print(f"   - user_id: {session.get('user_id')}")
            print(f"   - username: {session.get('username')}")
            print(f"   - user_role: {session.get('user_role')}")
            
            return True
            
        except Exception as e:
            print(f"Error during login test: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("Direct Login Test")
    print("=" * 50)
    
    # Test admin login
    print("\nTesting Admin Login:")
    admin_success = test_login('admin', 'ErrantMate@24!')
    
    print("\nTesting Regular User Login:")
    user_success = test_login('directtest2', 'User123@')
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Admin Login: {'SUCCESS' if admin_success else 'FAILED'}")
    print(f"User Login: {'SUCCESS' if user_success else 'FAILED'}")
    
    if admin_success and user_success:
        print("\nBoth logins should work! Check browser issues or form submission.")
    else:
        print("\nLogin verification failed - check user data or passwords.")
