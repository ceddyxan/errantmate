#!/usr/bin/env python3
"""
Migration script to add new fields to the Shelf table
Run this script to update the database schema with new management fields
"""

import os
import sys
from datetime import datetime

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Shelf

def migrate_shelf_fields():
    """Add new fields to the Shelf table if they don't exist"""
    
    with app.app_context():
        try:
            print("Starting shelf fields migration...")
            
            # Check if the table exists
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('shelf')
            column_names = [col['name'] for col in columns]
            
            print(f"Current columns in shelf table: {column_names}")
            
            # Add customer_email column if it doesn't exist
            if 'customer_email' not in column_names:
                print("Adding customer_email column...")
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE shelf ADD COLUMN customer_email VARCHAR(100)'))
                    conn.commit()
                print("✅ customer_email column added")
            else:
                print("✅ customer_email column already exists")
            
            # Add card_number column if it doesn't exist
            if 'card_number' not in column_names:
                print("Adding card_number column...")
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE shelf ADD COLUMN card_number VARCHAR(50)'))
                    conn.commit()
                print("✅ card_number column added")
            else:
                print("✅ card_number column already exists")
            
            # Add discount column if it doesn't exist
            if 'discount' not in column_names:
                print("Adding discount column...")
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE shelf ADD COLUMN discount FLOAT DEFAULT 0.0'))
                    conn.commit()
                print("✅ discount column added")
            else:
                print("✅ discount column already exists")
            
            # Verify the migration
            updated_columns = inspector.get_columns('shelf')
            updated_column_names = [col['name'] for col in updated_columns]
            print(f"Updated columns in shelf table: {updated_column_names}")
            
            # Test the Shelf model
            test_shelf = Shelf.query.first()
            if test_shelf:
                print(f"✅ Migration successful! Test shelf {test_shelf.id} has:")
                print(f"   - customer_email: {getattr(test_shelf, 'customer_email', 'Not set')}")
                print(f"   - card_number: {getattr(test_shelf, 'card_number', 'Not set')}")
                print(f"   - discount: {getattr(test_shelf, 'discount', 'Not set')}")
            
            print("🎉 Shelf fields migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        return True

if __name__ == '__main__':
    success = migrate_shelf_fields()
    if success:
        print("\n✅ Migration completed successfully!")
        print("You can now restart your application.")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above and fix any issues.")
        sys.exit(1)
