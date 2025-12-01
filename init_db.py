#!/usr/bin/env python3
"""
Database Initialization Script
Creates database tables and default admin user
"""

import os
import sys
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_database():
    """Initialize database tables and create admin user."""
    try:
        # Import Flask and SQLAlchemy
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from werkzeug.security import generate_password_hash
        
        # Create Flask app
        app = Flask(__name__)
        
        # Database configuration - PostgreSQL only
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        # Ensure it's a PostgreSQL connection
        if not database_url.startswith('postgres'):
            raise ValueError("DATABASE_URL must be a PostgreSQL connection string")
        
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        print("Using PostgreSQL database")
        
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db = SQLAlchemy(app)
        
        # Define User model
        class User(db.Model):
            __tablename__ = 'user'
            id = db.Column(db.Integer, primary_key=True)
            username = db.Column(db.String(80), unique=True, nullable=False)
            password_hash = db.Column(db.String(255), nullable=False)
            role = db.Column(db.String(20), default='user')
            created_at = db.Column(db.DateTime, default=datetime.now)
            is_active = db.Column(db.Boolean, default=True)
            
            def set_password(self, password):
                self.password_hash = generate_password_hash(password)
            
            def __repr__(self):
                return f'<User {self.username} ({self.role})>'
        
        # Define Delivery model
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
            payment_by = db.Column(db.String(50), nullable=False)
            status = db.Column(db.String(20), default='Pending')
            created_at = db.Column(db.DateTime, default=datetime.now)
            created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
            
            creator = db.relationship('User', backref='deliveries')
            
            def __repr__(self):
                return f'<Delivery {self.display_id}>'
        
        # Define AuditLog model
        class AuditLog(db.Model):
            __tablename__ = 'audit_log'
            id = db.Column(db.Integer, primary_key=True)
            user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
            username = db.Column(db.String(80), nullable=False)
            action = db.Column(db.String(100), nullable=False)
            resource_type = db.Column(db.String(50), nullable=True)
            resource_id = db.Column(db.String(50), nullable=True)
            details = db.Column(db.Text, nullable=True)
            ip_address = db.Column(db.String(45), nullable=True)
            user_agent = db.Column(db.String(500), nullable=True)
            timestamp = db.Column(db.DateTime, default=datetime.now)
            
            user = db.relationship('User', backref='audit_logs')
            
            def __repr__(self):
                return f'<AuditLog {self.action} by {self.username} at {self.timestamp}>'
        
        # Create tables
        print("Creating database tables...")
        with app.app_context():
            db.create_all()
            print("Database tables created successfully")
            
            # Check if admin user exists
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                print("Creating default admin user...")
                admin_user = User(
                    username='admin',
                    role='admin',
                    is_active=True
                )
                admin_user.set_password('ErrantMate@24!')
                db.session.add(admin_user)
                db.session.commit()
                print("Default admin user created: admin / ErrantMate@24!")
            else:
                print("Admin user already exists")
            
            # Verify tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Tables created: {tables}")
            
            required_tables = ['user', 'delivery', 'audit_log']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                print(f"Missing tables: {missing_tables}")
                return False
            else:
                print("All required tables are present")
                return True
                
    except Exception as e:
        print(f"Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting database initialization...")
    if init_database():
        print("Database initialization completed successfully!")
        print("\nLogin credentials:")
        print("   Username: admin")
        print("   Password: ErrantMate@24!")
    else:
        print("Database initialization failed!")
        sys.exit(1)
