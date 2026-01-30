#!/usr/bin/env python3
"""
Production Migration for Audit Log User ID
Run this script in production to update the audit_log table schema
"""

import os
from app import app, db
from sqlalchemy import text

def migrate_audit_log_production():
    """Update audit_log table to make user_id nullable"""
    with app.app_context():
        try:
            print("Starting production audit_log migration...")
            
            # Check current database
            database_url = os.environ.get('DATABASE_URL', 'Unknown')
            print(f"Database URL: {database_url}")
            
            # For PostgreSQL production
            if database_url.startswith('postgres'):
                print("Running PostgreSQL migration...")
                
                # Make user_id nullable
                db.session.execute(text("""
                    ALTER TABLE audit_log 
                    ALTER COLUMN user_id DROP NOT NULL
                """))
                
                db.session.commit()
                print("✅ Successfully made user_id nullable in audit_log table")
                
            else:
                print("SQLite detected - recreating audit_log table...")
                
                # For SQLite, drop and recreate
                db.session.execute(text('DROP TABLE IF EXISTS audit_log'))
                db.session.commit()
                
                db.session.execute(text('''
                    CREATE TABLE audit_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        username VARCHAR(80) NOT NULL,
                        action VARCHAR(100) NOT NULL,
                        resource_type VARCHAR(50),
                        resource_id VARCHAR(50),
                        details TEXT,
                        ip_address VARCHAR(45),
                        user_agent VARCHAR(500),
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                '''))
                
                db.session.commit()
                print("✅ Successfully recreated audit_log table with nullable user_id")
            
            # Verify the change
            result = db.session.execute(text("""
                SELECT column_name, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'audit_log' AND column_name = 'user_id'
            """))
            
            row = result.fetchone()
            if row:
                print(f"✅ Verification: user_id nullable = {row[1]}")
            else:
                print("⚠️  Could not verify schema change")
                
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            return False
            
    return True

if __name__ == '__main__':
    print("Production Audit Log Migration")
    print("=" * 50)
    
    success = migrate_audit_log_production()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("Login functionality should now work in production.")
    else:
        print("\n❌ Migration failed. Please check the error above.")
        print("You may need to run this manually in your production database.")
