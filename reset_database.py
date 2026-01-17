#!/usr/bin/env python3
"""
Database Reset Script for ErrantMate
This script will:
1. Delete all deliveries and audit logs
2. Reset auto-increment sequences to start from 1
3. Keep users table intact
"""

import os
import sys
from datetime import datetime

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Delivery, AuditLog, User

def reset_database():
    """Reset the database to start fresh from ID 1."""
    
    with app.app_context():
        print("🔄 Starting database reset...")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Count current records
        delivery_count = Delivery.query.count()
        audit_count = AuditLog.query.count()
        user_count = User.query.count()
        
        print(f"📊 Current state:")
        print(f"   - Deliveries: {delivery_count}")
        print(f"   - Audit logs: {audit_count}")
        print(f"   - Users: {user_count}")
        
        if delivery_count == 0:
            print("✅ Database is already empty. No reset needed.")
            return
        
        # Confirm deletion
        confirm = input("\n⚠️  This will permanently delete ALL deliveries and audit logs. Continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Reset cancelled.")
            return
        
        try:
            # For SQLite - simplest approach: delete and recreate
            if 'sqlite' in str(db.engine.url):
                print("🔄 SQLite detected - using file reset approach...")
                
                # Get database file path
                db_path = str(db.engine.url).replace('sqlite:///', '')
                
                # Close all connections
                db.session.close()
                db.engine.dispose()
                
                # Delete database file
                if os.path.exists(db_path):
                    os.remove(db_path)
                    print(f"🗑️  Deleted database file: {db_path}")
                
                # Recreate all tables
                print("🏗️  Recreating database tables...")
                db.create_all()
                
            # For PostgreSQL
            elif 'postgresql' in str(db.engine.url):
                print("🔄 PostgreSQL detected - using sequence reset...")
                # Delete all deliveries and audit logs
                Delivery.query.delete()
                AuditLog.query.delete()
                
                # Reset sequences
                db.session.execute("ALTER SEQUENCE delivery_id_seq RESTART WITH 1")
                db.session.execute("ALTER SEQUENCE audit_log_id_seq RESTART WITH 1")
                db.session.commit()
            
            print("\n✅ Database reset successfully!")
            print("📊 New state:")
            print(f"   - Deliveries: 0")
            print(f"   - Audit logs: 0")
            print(f"   - Users: {user_count} (preserved)")
            print("\n🎯 Next delivery will be: 2501170001 (today's date + 0001)")
            
        except Exception as e:
            print(f"❌ Error during reset: {e}")
            db.session.rollback()
            sys.exit(1)

if __name__ == "__main__":
    reset_database()
