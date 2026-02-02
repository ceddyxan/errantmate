#!/usr/bin/env python3
"""
Emergency production migration script
This can be run directly to fix the production database
"""

import os
import sys

def emergency_migration():
    """Emergency migration for production database"""
    
    try:
        # Import after environment setup
        from app import app, db, Shelf
        
        with app.app_context():
            print("🚨 EMERGENCY PRODUCTION MIGRATION")
            print("=" * 50)
            
            # Check database connection
            try:
                # Test basic database connection
                db.engine.execute("SELECT 1")
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                return False
            
            # Check if shelf table exists
            try:
                result = db.engine.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shelf'")
                table_exists = result.fetchone() is not None
                print(f"✅ Shelf table exists: {table_exists}")
            except:
                # For PostgreSQL
                try:
                    result = db.engine.execute("SELECT table_name FROM information_schema.tables WHERE table_name = 'shelf'")
                    table_exists = result.fetchone() is not None
                    print(f"✅ Shelf table exists: {table_exists}")
                except Exception as e:
                    print(f"❌ Cannot check shelf table: {e}")
                    return False
            
            if not table_exists:
                print("❌ Shelf table doesn't exist!")
                return False
            
            # Get current columns
            try:
                if 'sqlite' in str(db.engine.url).lower():
                    # SQLite
                    result = db.engine.execute("PRAGMA table_info(shelf)")
                    columns = [row[1] for row in result.fetchall()]
                else:
                    # PostgreSQL
                    result = db.engine.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'shelf'")
                    columns = [row[0] for row in result.fetchall()]
                
                print(f"✅ Current columns: {columns}")
            except Exception as e:
                print(f"❌ Cannot get columns: {e}")
                return False
            
            # Add missing columns
            migrations = [
                ('customer_email', 'VARCHAR(100)', None),
                ('card_number', 'VARCHAR(50)', None),
                ('discount', 'FLOAT', '0.0')
            ]
            
            for column_name, column_type, default_value in migrations:
                if column_name not in columns:
                    print(f"🔧 Adding {column_name}...")
                    try:
                        if 'sqlite' in str(db.engine.url).lower():
                            # SQLite
                            if default_value:
                                sql = f'ALTER TABLE shelf ADD COLUMN {column_name} {column_type} DEFAULT {default_value}'
                            else:
                                sql = f'ALTER TABLE shelf ADD COLUMN {column_name} {column_type}'
                        else:
                            # PostgreSQL
                            if default_value:
                                sql = f'ALTER TABLE shelf ADD COLUMN {column_name} {column_type} DEFAULT {default_value}'
                            else:
                                sql = f'ALTER TABLE shelf ADD COLUMN {column_name} {column_type}'
                        
                        db.engine.execute(sql)
                        print(f"✅ {column_name} added successfully")
                    except Exception as e:
                        print(f"❌ Failed to add {column_name}: {e}")
                        return False
                else:
                    print(f"✅ {column_name} already exists")
            
            # Verify migration
            try:
                # Test Shelf model
                test_shelf = Shelf.query.first()
                if test_shelf:
                    print(f"✅ Migration verified! Test shelf: {test_shelf.id}")
                    print(f"   customer_email: {getattr(test_shelf, 'customer_email', 'N/A')}")
                    print(f"   card_number: {getattr(test_shelf, 'card_number', 'N/A')}")
                    print(f"   discount: {getattr(test_shelf, 'discount', 'N/A')}")
                
                # Test shelves API
                shelves = Shelf.query.all()
                print(f"✅ Can query {len(shelves)} shelves successfully")
                
            except Exception as e:
                print(f"❌ Migration verification failed: {e}")
                return False
            
            print("🎉 EMERGENCY MIGRATION COMPLETED SUCCESSFULLY!")
            return True
            
    except Exception as e:
        print(f"❌ Emergency migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = emergency_migration()
    if success:
        print("\n✅ Production database is now ready!")
        print("🔄 Please restart the application.")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
