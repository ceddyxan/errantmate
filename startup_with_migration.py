#!/usr/bin/env python3
"""
Production startup script with automatic migration
This will run migrations before starting the app
"""

import os
import sys

def run_startup_migration():
    """Run migration before starting the app"""
    
    try:
        from app import app, db, Shelf
        
        with app.app_context():
            print("🚀 Running startup migration...")
            
            # Check if we need to migrate
            try:
                # Test if new fields exist
                test_shelf = Shelf.query.first()
                if test_shelf:
                    # Try to access new fields
                    _ = test_shelf.customer_email
                    _ = test_shelf.card_number  
                    _ = test_shelf.discount
                    print("✅ Migration already completed")
                    return True
            except:
                print("🔧 Migration needed - running now...")
            
            # Run migration
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('shelf')
            column_names = [col['name'] for col in columns]
            
            migrations = [
                ('customer_email', 'VARCHAR(100)', None),
                ('card_number', 'VARCHAR(50)', None),
                ('discount', 'FLOAT', '0.0')
            ]
            
            for column_name, column_type, default_value in migrations:
                if column_name not in column_names:
                    print(f"Adding {column_name}...")
                    
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
                    
                    with db.engine.connect() as conn:
                        conn.execute(db.text(sql))
                        conn.commit()
                    print(f"✅ {column_name} added")
            
            print("🎉 Startup migration completed!")
            return True
            
    except Exception as e:
        print(f"❌ Startup migration failed: {e}")
        return False

if __name__ == '__main__':
    # Run migration first
    migration_success = run_startup_migration()
    
    if migration_success:
        print("✅ Starting application...")
        # Start the Flask app
        from app import app
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    else:
        print("❌ Migration failed - cannot start application")
        sys.exit(1)
