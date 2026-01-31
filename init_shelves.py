#!/usr/bin/env python3
"""
Initialize shelves table with sample data
Run this script to populate the database with initial shelf data
"""

import sys
import os
from datetime import datetime, date

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Shelf

def init_shelves():
    """Initialize the shelves table with sample data"""
    
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
    
    with app.app_context():
        # Create the table if it doesn't exist
        db.create_all()
        
        # Clear existing shelves
        Shelf.query.delete()
        db.session.commit()
        
        # Add new shelves
        for data in shelf_data:
            shelf = Shelf(**data)
            db.session.add(shelf)
        
        db.session.commit()
        
        print(f"Successfully initialized {len(shelf_data)} shelves in the database")
        
        # Display the initialized shelves
        shelves = Shelf.query.all()
        print("\nInitialized Shelves:")
        print("-" * 60)
        for shelf in shelves:
            status_info = shelf.status
            if shelf.status == 'occupied':
                status_info += f" - {shelf.customer_name}"
            elif shelf.status == 'maintenance':
                status_info += f" - {shelf.maintenance_reason}"
            
            print(f"{shelf.id:6} | {shelf.size:6} | KSh {shelf.price:4} | {status_info}")

if __name__ == '__main__':
    try:
        init_shelves()
        print("\n✅ Shelves initialized successfully!")
    except Exception as e:
        print(f"\n❌ Error initializing shelves: {str(e)}")
        sys.exit(1)
