#!/usr/bin/env python3
"""
Production User Count Script
Run this script to count all users in production database
"""

import os
from app import app, db, User

def count_production_users():
    """Count and display all users in production database"""
    with app.app_context():
        try:
            print(f"Database URL: {os.environ.get('DATABASE_URL', 'Not set')}")
            
            # Count all users in the database
            total_users = User.query.count()
            print(f'\nTotal users in database: {total_users}')
            
            # Get all users with details
            users = User.query.all()
            print(f'\nUser details:')
            for user in users:
                print(f'  - {user.username} (ID: {user.id}, Role: {user.role}, Email: {user.email}, Phone: {user.phone_number}, Active: {user.is_active})')
            
            # Count by role
            admin_count = User.query.filter_by(role='admin').count()
            user_count = User.query.filter_by(role='user').count()
            staff_count = User.query.filter_by(role='staff').count()
            
            print(f'\nUsers by role:')
            print(f'  Admin: {admin_count}')
            print(f'  User: {user_count}')
            print(f'  Staff: {staff_count}')
            
            # Active vs inactive
            active_count = User.query.filter_by(is_active=True).count()
            inactive_count = User.query.filter_by(is_active=False).count()
            
            print(f'\nUsers by status:')
            print(f'  Active: {active_count}')
            print(f'  Inactive: {inactive_count}')
            
            # Recent users (created in last 7 days)
            from datetime import datetime, timedelta
            week_ago = datetime.now() - timedelta(days=7)
            recent_users = User.query.filter(User.created_at >= week_ago).count()
            print(f'\nRecent signups (last 7 days): {recent_users}')
            
            # Users with complete profiles
            complete_profiles = User.query.filter(
                User.email.isnot(None),
                User.phone_number.isnot(None)
            ).count()
            print(f'Users with complete profiles: {complete_profiles}')
            
        except Exception as e:
            print(f"Error counting users: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("Counting production users...")
    count_production_users()
