#!/usr/bin/env python3
import sys
sys.path.append('.')
from app import app, db

with app.app_context():
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print('Current tables:', tables)
    required_tables = ['users', 'delivery', 'audit_log', 'shelf']
    missing = [t for t in required_tables if t not in tables]
    print('Missing tables:', missing)
    
    # Try to create missing tables
    if missing:
        print(f'Attempting to create missing tables: {missing}')
        try:
            db.create_all()
            print('db.create_all() executed successfully')
            
            # Check again
            inspector = db.inspect(db.engine)
            new_tables = inspector.get_table_names()
            print('Tables after create_all():', new_tables)
            
            still_missing = [t for t in required_tables if t not in new_tables]
            if still_missing:
                print('Still missing:', still_missing)
            else:
                print('All required tables now exist!')
                
        except Exception as e:
            print(f'Error creating tables: {e}')
            import traceback
            traceback.print_exc()
