#!/usr/bin/env python3
"""
SQLite Schema Inspector
This script will show the database schema and more detailed information.
"""

import sqlite3
import os

def inspect_sqlite_schema():
    """Inspect SQLite database schema and file info"""
    db_path = "instance/deliveries.db"
    
    print("🗄️  SQLite Database Schema Inspection")
    print("=" * 60)
    
    # Check if database file exists
    if os.path.exists(db_path):
        file_size = os.path.getsize(db_path)
        print(f"📁 Database file: {db_path}")
        print(f"📏 File size: {file_size} bytes")
        print(f"📅 Modified: {datetime.fromtimestamp(os.path.getmtime(db_path))}")
        print()
    else:
        print(f"❌ Database file {db_path} not found!")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("📋 Tables found:")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
        
        print("\n" + "=" * 60)
        
        # Show schema for each table
        for table in tables:
            table_name = table[0]
            print(f"\n🔍 Table: {table_name}")
            print("-" * 40)
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print("Columns:")
            for col in columns:
                col_id, name, type_, not_null, default_val, pk = col
                print(f"  {name}: {type_} {'(PK)' if pk else ''} {'NOT NULL' if not_null else ''} {'DEFAULT ' + str(default_val) if default_val else ''}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            print(f"Row count: {row_count}")
            
            # Show sample data if table has rows
            if row_count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                sample_rows = cursor.fetchall()
                
                # Get column names for header
                cursor.execute(f"PRAGMA table_info({table_name});")
                col_names = [col[1] for col in cursor.fetchall()]
                
                print("\nSample data (first 3 rows):")
                print("Columns:", " | ".join(col_names))
                for row in sample_rows:
                    print("Data:   ", " | ".join(str(val) for val in row))
        
        print("\n" + "=" * 60)
        print("📊 Database Statistics:")
        
        # Get database page info
        cursor.execute("PRAGMA page_size;")
        page_size = cursor.fetchone()[0]
        cursor.execute("PRAGMA page_count;")
        page_count = cursor.fetchone()[0]
        
        print(f"Page size: {page_size} bytes")
        print(f"Page count: {page_count}")
        print(f"Database size: {page_size * page_count} bytes")
        
        # Get SQLite version
        cursor.execute("SELECT sqlite_version();")
        sqlite_version = cursor.fetchone()[0]
        print(f"SQLite version: {sqlite_version}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error inspecting database: {e}")

if __name__ == "__main__":
    from datetime import datetime
    inspect_sqlite_schema()
