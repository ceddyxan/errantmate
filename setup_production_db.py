#!/usr/bin/env python3
"""
Production database setup for shelf rental system
This script will create the shelf table in the production database
"""

import sys
import os
from datetime import datetime, date

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Shelf

def setup_production_database():
    """Setup the production database with shelf table and sample data"""
    
    print("🔧 Setting up production database...")
    
    with app.app_context():
        try:
            # Create all database tables
            print("📋 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Check if shelves already exist
            existing_shelves = Shelf.query.count()
            if existing_shelves > 0:
                print(f"ℹ️  Found {existing_shelves} existing shelves")
                choice = input("Do you want to reset shelf data? (y/N): ").lower().strip()
                if choice == 'y':
                    print("🗑️  Clearing existing shelf data...")
                    Shelf.query.delete()
                    db.session.commit()
                    print("✅ Existing shelf data cleared")
                else:
                    print("📋 Keeping existing shelf data")
                    return
            
            # Sample shelf data
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
            print("📦 Adding sample shelf data...")
            for data in shelf_data:
                shelf = Shelf(**data)
                db.session.add(shelf)
            
            db.session.commit()
            
            print(f"✅ Successfully initialized {len(shelf_data)} shelves in production database")
            
            # Display the initialized shelves
            shelves = Shelf.query.all()
            print("\n📋 Initialized Shelves:")
            print("-" * 60)
            for shelf in shelves:
                status_info = shelf.status
                if shelf.status == 'occupied':
                    status_info += f" - {shelf.customer_name}"
                elif shelf.status == 'maintenance':
                    status_info += f" - {shelf.maintenance_reason}"
                
                print(f"{shelf.id:6} | {shelf.size:6} | KSh {shelf.price:4} | {status_info}")
            
            # Verify API endpoints
            print("\n🔍 Verifying API endpoints...")
            from app import Shelf
            
            available_count = Shelf.query.filter_by(status='available').count()
            occupied_count = Shelf.query.filter_by(status='occupied').count()
            maintenance_count = Shelf.query.filter_by(status='maintenance').count()
            
            print(f"📊 Database Statistics:")
            print(f"   Available: {available_count}")
            print(f"   Occupied: {occupied_count}")
            print(f"   Maintenance: {maintenance_count}")
            
            revenue = sum(shelf.price for shelf in Shelf.query.filter_by(status='occupied').all())
            print(f"   Monthly Revenue: KSh {revenue}")
            
            print("\n🎉 Production database setup completed successfully!")
            print("🌐 The shelf rental system should now work correctly.")
            
        except Exception as e:
            print(f"\n❌ Error setting up production database: {str(e)}")
            print("🔧 Please check your database connection and permissions.")
            sys.exit(1)

if __name__ == '__main__':
    setup_production_database()
