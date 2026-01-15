#!/usr/bin/env python3
"""
Production database migration script for revenue column
Run this script in your production environment
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_production_migration():
    """Run migration for production database"""
    
    # Force production environment
    os.environ['FLASK_ENV'] = 'production'
    
    # Import app after setting environment
    from app import app, db
    
    with app.app_context():
        try:
            print("=== Production Database Migration ===")
            print(f"Database URL: {db.engine.url}")
            
            # Check if column already exists
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('delivery')
            column_names = [col['name'] for col in columns]
            
            print(f"Current columns in delivery table: {column_names}")
            
            if 'revenue' in column_names:
                print("✅ Revenue column already exists in delivery table")
                return
            
            print("🔄 Adding revenue column to delivery table...")
            
            # Add revenue column with PostgreSQL syntax
            db.session.execute(text("ALTER TABLE delivery ADD COLUMN revenue FLOAT DEFAULT 50.0"))
            db.session.commit()
            print("✅ Revenue column added successfully!")
            
            # Update existing records to have revenue = 50.0
            print("🔄 Updating existing delivery records...")
            result = db.session.execute(text("UPDATE delivery SET revenue = 50.0 WHERE revenue IS NULL"))
            db.session.commit()
            print(f"✅ Updated {result.rowcount} existing records!")
            
            # Verify the column was added
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('delivery')
            column_names = [col['name'] for col in columns]
            
            if 'revenue' in column_names:
                print("✅ Migration completed successfully!")
                print("✅ Revenue column is now available in production database")
            else:
                print("❌ Migration failed - revenue column not found after creation")
                
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    run_production_migration()
