#!/usr/bin/env python3
"""
Database migration script to add revenue column to delivery table
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the app
from app import app, db

def add_revenue_column():
    """Add revenue column to delivery table"""
    with app.app_context():
        try:
            # Check if column already exists
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('delivery')
            column_names = [col['name'] for col in columns]
            
            if 'revenue' in column_names:
                print("Revenue column already exists in delivery table")
                return
            
            print("Adding revenue column to delivery table...")
            
            # Add the revenue column
            if 'postgresql' in str(db.engine.url).lower():
                # PostgreSQL syntax
                db.session.execute(text("ALTER TABLE delivery ADD COLUMN revenue FLOAT DEFAULT 50.0"))
            else:
                # SQLite syntax
                db.session.execute(text("ALTER TABLE delivery ADD COLUMN revenue FLOAT DEFAULT 50.0"))
            
            db.session.commit()
            print("Revenue column added successfully!")
            
            # Update existing records to have revenue = 50.0
            print("Updating existing delivery records...")
            db.session.execute(text("UPDATE delivery SET revenue = 50.0 WHERE revenue IS NULL"))
            db.session.commit()
            print("Existing records updated successfully!")
            
        except Exception as e:
            print(f"Error adding revenue column: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    add_revenue_column()
