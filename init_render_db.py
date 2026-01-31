#!/usr/bin/env python3
"""
Render.com database initialization script for shelf rental system
This script will be called during Render deployment to set up the database
"""

import os
import sys
from datetime import datetime, date

def init_render_database():
    """Initialize database for Render.com deployment"""
    
    print("🚀 Initializing ErrantMate database on Render.com...")
    
    try:
        # Import here to avoid import errors if packages are missing
        print("📦 Importing required packages...")
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from sqlalchemy import inspect, text
        
        # Create minimal Flask app for database operations
        app = Flask(__name__)
        
        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not found in environment")
            return False
            
        print(f"✅ Database URL found: {database_url.split('@')[0] if '@' in database_url else 'local'}")
        
        # Configure database
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize database
        db = SQLAlchemy(app)
        
        # Define Shelf model (minimal version for initialization)
        class Shelf(db.Model):
            __tablename__ = 'shelf'
            id = db.Column(db.String(10), primary_key=True)
            status = db.Column(db.String(20), default='available')
            size = db.Column(db.String(10), nullable=False)
            price = db.Column(db.Integer, nullable=False)
            customer_name = db.Column(db.String(100), nullable=True)
            customer_phone = db.Column(db.String(20), nullable=True)
            rented_date = db.Column(db.Date, nullable=True)
            items_description = db.Column(db.Text, nullable=True)
            rental_period = db.Column(db.Integer, nullable=True)
            maintenance_reason = db.Column(db.String(200), nullable=True)
            created_at = db.Column(db.DateTime, default=datetime.utcnow)
            updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        with app.app_context():
            # Test database connection
            print("🔗 Testing database connection...")
            try:
                db.engine.execute(text('SELECT 1'))
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {str(e)}")
                return False
            
            # Create tables
            print("📋 Creating database tables...")
            try:
                db.create_all()
                print("✅ Database tables created successfully")
            except Exception as e:
                print(f"❌ Table creation failed: {str(e)}")
                return False
            
            # Check if shelves already exist
            print("🔍 Checking existing data...")
            try:
                existing_count = Shelf.query.count()
                if existing_count > 0:
                    print(f"ℹ️  Found {existing_count} existing shelves")
                    print("✅ Database already initialized")
                    return True
            except Exception as e:
                print(f"⚠️  Could not check existing data: {str(e)}")
                # Continue with initialization anyway
            
            # Add sample shelf data
            print("📦 Adding sample shelf data...")
            shelf_data = [
                {'id': 'A-01', 'status': 'available', 'size': 'Small', 'price': 800},
                {'id': 'A-02', 'status': 'occupied', 'size': 'Small', 'price': 800, 
                 'customer_name': 'John Doe', 'customer_phone': '0712345678', 'rented_date': date(2024, 1, 15)},
                {'id': 'A-03', 'status': 'available', 'size': 'Small', 'price': 800},
                {'id': 'A-04', 'status': 'maintenance', 'size': 'Small', 'price': 800, 
                 'maintenance_reason': 'Repair needed'},
                {'id': 'B-01', 'status': 'occupied', 'size': 'Large', 'price': 1000, 
                 'customer_name': 'Jane Smith', 'customer_phone': '0723456789', 'rented_date': date(2024, 1, 10)},
                {'id': 'B-02', 'status': 'available', 'size': 'Large', 'price': 1000},
                {'id': 'B-03', 'status': 'occupied', 'size': 'Large', 'price': 1000, 
                 'customer_name': 'Mike Johnson', 'customer_phone': '0734567890', 'rented_date': date(2024, 1, 20)},
                {'id': 'C-01', 'status': 'available', 'size': 'Small', 'price': 800},
                {'id': 'C-02', 'status': 'occupied', 'size': 'Small', 'price': 800, 
                 'customer_name': 'Sarah Wilson', 'customer_phone': '0745678901', 'rented_date': date(2024, 1, 5)},
                {'id': 'C-03', 'status': 'available', 'size': 'Large', 'price': 1000},
                {'id': 'D-01', 'status': 'maintenance', 'size': 'Large', 'price': 1000, 
                 'maintenance_reason': 'Cleaning'},
                {'id': 'D-02', 'status': 'occupied', 'size': 'Large', 'price': 1000, 
                 'customer_name': 'Tom Brown', 'customer_phone': '0756789012', 'rented_date': date(2024, 1, 25)}
            ]
            
            # Add shelves to database
            shelves_added = 0
            for data in shelf_data:
                try:
                    shelf = Shelf(**data)
                    db.session.add(shelf)
                    shelves_added += 1
                except Exception as e:
                    print(f"⚠️  Could not add shelf {data.get('id', 'unknown')}: {str(e)}")
            
            try:
                db.session.commit()
                print(f"✅ Successfully added {shelves_added} shelves to database")
            except Exception as e:
                print(f"❌ Failed to commit shelves: {str(e)}")
                db.session.rollback()
                return False
            
            # Display statistics
            try:
                available = Shelf.query.filter_by(status='available').count()
                occupied = Shelf.query.filter_by(status='occupied').count()
                maintenance = Shelf.query.filter_by(status='maintenance').count()
                total = Shelf.query.count()
                revenue = sum(shelf.price for shelf in Shelf.query.filter_by(status='occupied').all())
                
                print(f"📊 Database Statistics:")
                print(f"   Total Shelves: {total}")
                print(f"   Available: {available}")
                print(f"   Occupied: {occupied}")
                print(f"   Maintenance: {maintenance}")
                print(f"   Monthly Revenue: KSh {revenue}")
            except Exception as e:
                print(f"⚠️  Could not calculate statistics: {str(e)}")
            
            print("🎉 Render.com database initialization completed!")
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("🔧 Please check requirements.txt for missing packages")
        return False
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return False

if __name__ == '__main__':
    success = init_render_database()
    sys.exit(0 if success else 1)
