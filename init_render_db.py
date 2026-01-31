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
        from app import app, db, Shelf
        
        with app.app_context():
            # Create tables
            print("📋 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Check if shelves already exist
            existing_count = Shelf.query.count()
            if existing_count > 0:
                print(f"ℹ️  Found {existing_count} existing shelves")
                print("✅ Database already initialized")
                return True
            
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
            for data in shelf_data:
                shelf = Shelf(**data)
                db.session.add(shelf)
            
            db.session.commit()
            
            print(f"✅ Successfully initialized {len(shelf_data)} shelves")
            
            # Display statistics
            available = Shelf.query.filter_by(status='available').count()
            occupied = Shelf.query.filter_by(status='occupied').count()
            maintenance = Shelf.query.filter_by(status='maintenance').count()
            revenue = sum(shelf.price for shelf in Shelf.query.filter_by(status='occupied').all())
            
            print(f"📊 Database Statistics:")
            print(f"   Available: {available}")
            print(f"   Occupied: {occupied}")
            print(f"   Maintenance: {maintenance}")
            print(f"   Monthly Revenue: KSh {revenue}")
            
            print("🎉 Render.com database initialization completed!")
            return True
            
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return False

if __name__ == '__main__':
    success = init_render_database()
    sys.exit(0 if success else 1)
