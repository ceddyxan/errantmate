#!/usr/bin/env python3
"""
Render.com migration script for adding new shelf management fields
This script will be executed during deployment to update the database schema
"""

import os
import sys
from datetime import datetime

def migrate_database():
    """Run database migrations for Render.com deployment"""
    
    try:
        # Import after setting up the environment
        from app import app, db, Shelf
        
        with app.app_context():
            print("Starting database migration for shelf management fields...")
            
            # Check current database state
            inspector = db.inspect(db.engine)
            table_exists = inspector.has_table('shelf')
            
            if not table_exists:
                print("❌ Shelf table doesn't exist. Please run init_render_db.py first.")
                return False
            
            # Get current columns
            columns = inspector.get_columns('shelf')
            column_names = [col['name'] for col in columns]
            
            print(f"Current shelf table columns: {column_names}")
            
            # Add missing columns
            migrations = [
                ('customer_email', 'VARCHAR(100)', None),
                ('card_number', 'VARCHAR(50)', None),
                ('discount', 'FLOAT', '0.0')
            ]
            
            for column_name, column_type, default_value in migrations:
                if column_name not in column_names:
                    print(f"Adding {column_name} column...")
                    if default_value:
                        sql = f'ALTER TABLE shelf ADD COLUMN {column_name} {column_type} DEFAULT {default_value}'
                    else:
                        sql = f'ALTER TABLE shelf ADD COLUMN {column_name} {column_type}'
                    
                    with db.engine.connect() as conn:
                        conn.execute(db.text(sql))
                        conn.commit()
                    print(f"✅ {column_name} column added")
                else:
                    print(f"✅ {column_name} column already exists")
            
            # Verify migration
            updated_columns = inspector.get_columns('shelf')
            updated_column_names = [col['name'] for col in updated_columns]
            
            required_columns = ['customer_email', 'card_number', 'discount']
            missing_columns = [col for col in required_columns if col not in updated_column_names]
            
            if missing_columns:
                print(f"❌ Missing columns after migration: {missing_columns}")
                return False
            
            print("✅ All required columns are present!")
            print(f"Final shelf table columns: {updated_column_names}")
            
            # Test a query to make sure everything works
            try:
                shelf_count = Shelf.query.count()
                print(f"✅ Database query successful! Found {shelf_count} shelves")
                
                # Test new fields on first shelf if available
                if shelf_count > 0:
                    test_shelf = Shelf.query.first()
                    print(f"✅ Test shelf {test_shelf.id} - new fields accessible")
            except Exception as query_error:
                print(f"❌ Database query failed: {query_error}")
                return False
            
            print("🎉 Database migration completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = migrate_database()
    if not success:
        print("❌ Migration failed - exiting with error")
        sys.exit(1)
    else:
        print("✅ Migration completed successfully")
