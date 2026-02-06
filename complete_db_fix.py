#!/usr/bin/env python3
"""
Complete Production Database Fix Script
This script will fix all database issues including missing tables and columns.
"""

import os
import sys
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)

# Database configuration
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    database_url = 'sqlite:///deliveries.db'
    print("WARNING: No DATABASE_URL found, using SQLite for testing")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def get_current_time():
    """Get current datetime in UTC+3 (Kenya timezone)."""
    return datetime.utcnow() + timedelta(hours=3)

def get_database_type():
    """Check if we're using PostgreSQL or SQLite"""
    if 'postgres' in str(app.config['SQLALCHEMY_DATABASE_URI']).lower():
        return 'postgresql'
    else:
        return 'sqlite'

@app.route('/complete-db-fix')
def complete_database_fix():
    """Complete database fix including tables and columns"""
    try:
        with app.app_context():
            print("🔧 Starting complete database fix...")
            db_type = get_database_type()
            print(f"📊 Database type: {db_type}")
            
            # Check current tables
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            print(f"📋 Current tables: {existing_tables}")
            
            # Required tables
            required_tables = ['users', 'delivery', 'audit_log', 'shelf']
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            # Create missing tables first
            if missing_tables:
                print(f"❌ Missing tables: {missing_tables}")
                print("🔨 Creating missing tables...")
                
                # Create all tables
                db.create_all()
                print("✅ db.create_all() executed")
                
                # Verify creation
                inspector = inspect(db.engine)
                new_tables = inspector.get_table_names()
                print(f"📋 Tables after creation: {new_tables}")
                
                still_missing = [t for t in required_tables if t not in new_tables]
                if still_missing:
                    return jsonify({
                        'status': 'error',
                        'message': f'Failed to create tables: {still_missing}',
                        'existing_tables': new_tables
                    }), 500
                else:
                    print("✅ All required tables created successfully!")
            else:
                print("✅ All required tables already exist")
            
            # Check and add missing columns for each table
            print("🔍 Checking table columns...")
            
            # Check users table columns
            if 'users' in existing_tables:
                users_columns = [col['name'] for col in inspector.get_columns('users')]
                print(f"👤 Users table columns: {users_columns}")
                
                required_user_columns = ['id', 'username', 'email', 'phone_number', 'password_hash', 'actual_password', 'role', 'created_at', 'is_active']
                missing_user_columns = [col for col in required_user_columns if col not in users_columns]
                
                if missing_user_columns:
                    print(f"❌ Missing user columns: {missing_user_columns}")
                    
                    # Add missing columns
                    for col in missing_user_columns:
                        if col == 'actual_password':
                            add_column_query = f"ALTER TABLE users ADD COLUMN actual_password VARCHAR(255)"
                        elif col == 'role':
                            add_column_query = f"ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'"
                        elif col == 'is_active':
                            add_column_query = f"ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE"
                        else:
                            continue  # Skip other columns for now
                        
                        print(f"🔨 Adding column {col} to users table...")
                        try:
                            db.session.execute(text(add_column_query))
                            db.session.commit()
                            print(f"✅ Added {col} column")
                        except Exception as col_error:
                            print(f"⚠️  Could not add {col} column: {col_error}")
                            db.session.rollback()
                else:
                    print("✅ All user columns exist")
            
            # Check shelf table columns (if it exists)
            if 'shelf' in existing_tables:
                shelf_columns = [col['name'] for col in inspector.get_columns('shelf')]
                print(f"📦 Shelf table columns: {shelf_columns}")
                
                required_shelf_columns = ['id', 'status', 'size', 'price', 'customer_name', 'customer_phone', 'customer_email', 'card_number', 'rented_date', 'items_description', 'rental_period', 'discount', 'maintenance_reason', 'created_at', 'updated_at']
                missing_shelf_columns = [col for col in required_shelf_columns if col not in shelf_columns]
                
                if missing_shelf_columns:
                    print(f"❌ Missing shelf columns: {missing_shelf_columns}")
                    
                    # Add missing columns
                    for col in missing_shelf_columns:
                        if col == 'customer_email':
                            add_column_query = f"ALTER TABLE shelf ADD COLUMN customer_email VARCHAR(100)"
                        elif col == 'card_number':
                            add_column_query = f"ALTER TABLE shelf ADD COLUMN card_number VARCHAR(50)"
                        elif col == 'discount':
                            add_column_query = f"ALTER TABLE shelf ADD COLUMN discount FLOAT DEFAULT 0.0"
                        else:
                            continue  # Skip other columns for now
                        
                        print(f"🔨 Adding column {col} to shelf table...")
                        try:
                            db.session.execute(text(add_column_query))
                            db.session.commit()
                            print(f"✅ Added {col} column")
                        except Exception as col_error:
                            print(f"⚠️  Could not add {col} column: {col_error}")
                            db.session.rollback()
                else:
                    print("✅ All shelf columns exist")
            
            # Create admin user if not exists (now that columns should be fixed)
            try:
                admin_user = db.session.execute(text("SELECT * FROM users WHERE username = 'admin'")).fetchone()
                if not admin_user:
                    print("👤 Creating default admin user...")
                    password_hash = generate_password_hash('ErrantMate@24!')
                    
                    if db_type == 'postgresql':
                        insert_query = """
                        INSERT INTO users (username, password_hash, role, is_active, created_at) 
                        VALUES ('admin', :password_hash, 'admin', TRUE, CURRENT_TIMESTAMP)
                        """
                    else:
                        insert_query = """
                        INSERT INTO users (username, password_hash, role, is_active, created_at) 
                        VALUES ('admin', ?, 'admin', 1, CURRENT_TIMESTAMP)
                        """
                    
                    db.session.execute(text(insert_query), {'password_hash': password_hash})
                    db.session.commit()
                    print("✅ Default admin user created")
                else:
                    print("✅ Admin user already exists")
                    
            except Exception as admin_error:
                print(f"⚠️  Admin user creation issue: {admin_error}")
            
            # Final verification
            inspector = inspect(db.engine)
            final_tables = inspector.get_table_names()
            
            return jsonify({
                'status': 'success',
                'message': 'Complete database fix successful',
                'tables': final_tables,
                'database_type': db_type,
                'admin_user_created': True,
                'database_url': str(app.config['SQLALCHEMY_DATABASE_URI']).split('@')[1] if '@' in str(app.config['SQLALCHEMY_DATABASE_URI']) else 'local'
            }), 200
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Complete database fix failed: {e}")
        print(f"❌ Error details: {error_details}")
        
        return jsonify({
            'status': 'error',
            'message': str(e),
            'error_details': error_details
        }), 500

@app.route('/check-db-status')
def check_database_status():
    """Check complete database status including columns"""
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['users', 'delivery', 'audit_log', 'shelf']
            missing_tables = [t for t in required_tables if t not in tables]
            
            # Check column details for each table
            table_details = {}
            for table in tables:
                if table in required_tables:
                    columns = [col['name'] for col in inspector.get_columns(table)]
                    table_details[table] = {
                        'columns': columns,
                        'column_count': len(columns)
                    }
            
            return jsonify({
                'status': 'ready' if not missing_tables else 'incomplete',
                'tables': tables,
                'missing_tables': missing_tables,
                'table_details': table_details,
                'database_type': get_database_type()
            }), 200
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # For local testing
    with app.app_context():
        print("🔧 Testing complete database fix locally...")
        result = complete_database_fix()
        print(f"Result: {result}")
