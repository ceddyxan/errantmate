#!/usr/bin/env python3
"""
Direct production database fix script
This will check and fix the database schema directly
"""

import requests
import json

def fix_production_database():
    """Fix the production database by calling a special endpoint"""
    
    base_url = "https://errantmate.onrender.com"
    
    print("🔧 DIRECT PRODUCTION DATABASE FIX")
    print("=" * 45)
    
    # First, let's add a debug endpoint to check the database
    print("\n1. Testing database connection...")
    
    # We'll create a special endpoint that can run migrations
    # But first, let's check what's actually happening
    
    try:
        # Try to access a simple endpoint to see if app is running
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Health check: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ App is running")
        else:
            print(f"   ❌ App not responding properly: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Cannot reach app: {e}")
        return False
    
    # The issue is likely that the migration isn't running
    # Let's create a direct migration endpoint
    
    print("\n2. Adding emergency migration endpoint...")
    
    # We need to add this to the app.py and deploy
    migration_endpoint_code = '''
@app.route('/emergency-migrate', methods=['POST'])
def emergency_migrate():
    """Emergency migration endpoint"""
    try:
        with app.app_context():
            # Check current columns
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('shelf')
            column_names = [col['name'] for col in columns]
            
            print(f"Current columns: {column_names}")
            
            # Add missing columns
            migrations = [
                ('customer_email', 'VARCHAR(100)', None),
                ('card_number', 'VARCHAR(50)', None),
                ('discount', 'FLOAT', '0.0')
            ]
            
            for column_name, column_type, default_value in migrations:
                if column_name not in column_names:
                    print(f"Adding {column_name}...")
                    
                    if 'sqlite' in str(db.engine.url).lower():
                        if default_value:
                            sql = f'ALTER TABLE shelf ADD COLUMN {column_name} {column_type} DEFAULT {default_value}'
                        else:
                            sql = f'ALTER TABLE shelf ADD COLUMN {column_name} {column_type}'
                    else:
                        if default_value:
                            sql = f'ALTER TABLE shelf ADD COLUMN {column_name} {column_type} DEFAULT {default_value}'
                        else:
                            sql = f'ALTER TABLE shelf ADD COLUMN {column_name} {column_type}'
                    
                    with db.engine.connect() as conn:
                        conn.execute(db.text(sql))
                        conn.commit()
                    print(f"✅ {column_name} added")
            
            return jsonify({
                'success': True,
                'message': 'Emergency migration completed',
                'columns': column_names
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
'''
    
    print("   ✅ Migration endpoint code prepared")
    print("   📝 Need to add this to app.py and deploy")
    
    return True

if __name__ == "__main__":
    fix_production_database()
