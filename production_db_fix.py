#!/usr/bin/env python3
"""
Production Database Fix Script
This script will fix the database table issues in production.

Usage:
1. Deploy this script to your Render.com instance
2. Access the /fix-production-db endpoint to fix the database
3. The script will create missing tables and fix table name inconsistencies
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

# Define models matching the main app
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    actual_password = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=get_current_time)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        if self.role in ['user', 'staff']:
            self.actual_password = password
        else:
            self.actual_password = None

class Delivery(db.Model):
    __tablename__ = 'delivery'
    id = db.Column(db.Integer, primary_key=True)
    display_id = db.Column(db.String(20), unique=True, nullable=False)
    sender_name = db.Column(db.String(100), nullable=False)
    sender_phone = db.Column(db.String(20), nullable=False)
    recipient_name = db.Column(db.String(100), nullable=False)
    recipient_phone = db.Column(db.String(20), nullable=False)
    recipient_address = db.Column(db.String(200), nullable=False)
    delivery_person = db.Column(db.String(100), nullable=True)
    goods_type = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    expenses = db.Column(db.Float, default=0.0)
    payment_by = db.Column(db.String(50), nullable=False, default='M-Pesa')
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=get_current_time)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=True)
    resource_id = db.Column(db.String(50), nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    timestamp = db.Column(db.DateTime, default=get_current_time)

class Shelf(db.Model):
    __tablename__ = 'shelf'
    id = db.Column(db.String(10), primary_key=True)
    status = db.Column(db.String(20), default='available')
    size = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    customer_name = db.Column(db.String(100), nullable=True)
    customer_phone = db.Column(db.String(20), nullable=True)
    customer_email = db.Column(db.String(100), nullable=True)
    card_number = db.Column(db.String(50), nullable=True)
    rented_date = db.Column(db.Date, nullable=True)
    items_description = db.Column(db.Text, nullable=True)
    rental_period = db.Column(db.Integer, nullable=True)
    discount = db.Column(db.Float, default=0.0)
    maintenance_reason = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=get_current_time)
    updated_at = db.Column(db.DateTime, default=get_current_time, onupdate=get_current_time)

@app.route('/fix-production-db')
def fix_production_database():
    """Fix production database by creating missing tables"""
    try:
        with app.app_context():
            print("🔧 Starting production database fix...")
            
            # Check current tables
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            print(f"📋 Current tables: {existing_tables}")
            
            # Required tables
            required_tables = ['users', 'delivery', 'audit_log', 'shelf']
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
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
            
            # Create admin user if not exists
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    role='admin',
                    is_active=True
                )
                admin_user.set_password('ErrantMate@24!')
                db.session.add(admin_user)
                db.session.commit()
                print("👤 Default admin user created")
            else:
                print("👤 Admin user already exists")
            
            return jsonify({
                'status': 'success',
                'message': 'Production database fixed successfully',
                'tables': inspector.get_table_names(),
                'admin_user_exists': User.query.filter_by(username='admin').first() is not None,
                'database_url': str(app.config['SQLALCHEMY_DATABASE_URI']).split('@')[1] if '@' in str(app.config['SQLALCHEMY_DATABASE_URI']) else 'local'
            }), 200
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Database fix failed: {e}")
        print(f"❌ Error details: {error_details}")
        
        return jsonify({
            'status': 'error',
            'message': str(e),
            'error_details': error_details
        }), 500

@app.route('/check-production-db')
def check_production_database():
    """Check production database status"""
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['users', 'delivery', 'audit_log', 'shelf']
            missing_tables = [t for t in required_tables if t not in tables]
            
            # Test basic queries
            user_count = User.query.count() if 'users' in tables else 0
            delivery_count = Delivery.query.count() if 'delivery' in tables else 0
            
            return jsonify({
                'status': 'ready' if not missing_tables else 'incomplete',
                'tables': tables,
                'missing_tables': missing_tables,
                'users_count': user_count,
                'deliveries_count': delivery_count,
                'database_url': str(app.config['SQLALCHEMY_DATABASE_URI']).split('@')[1] if '@' in str(app.config['SQLALCHEMY_DATABASE_URI']) else 'local'
            }), 200
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # For local testing
    with app.app_context():
        print("🔧 Testing database fix locally...")
        result = fix_production_database()
        print(f"Result: {result}")
