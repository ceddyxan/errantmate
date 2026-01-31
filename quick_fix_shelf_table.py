#!/usr/bin/env python3
"""
Quick fix for shelf table missing error
Run this script to immediately resolve the "relation shelf does not exist" error
"""

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def quick_fix():
    """Quick fix for missing shelf table"""
    try:
        print("🔧 Applying quick fix for shelf table...")
        
        from app import app, db
        
        with app.app_context():
            # Create the shelf table
            print("📋 Creating shelf table...")
            db.create_all()
            print("✅ Shelf table created successfully!")
            
            # Check if shelf table exists and has data
            from app import Shelf
            shelf_count = Shelf.query.count()
            print(f"📊 Found {shelf_count} shelves in database")
            
            if shelf_count == 0:
                print("⚠️  No shelves found. Running initialization...")
                os.system("python init_shelves.py")
            else:
                print("✅ Shelves already exist in database")
            
            print("\n🎉 Quick fix completed!")
            print("🌐 The shelf rental system should now work without errors.")
            
    except Exception as e:
        print(f"❌ Quick fix failed: {str(e)}")
        print("🔧 Please run: python setup_production_db.py")
        sys.exit(1)

if __name__ == '__main__':
    quick_fix()
