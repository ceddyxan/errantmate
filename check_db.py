import sqlite3
import os

db_path = os.path.join('instance', 'deliveries.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print('Tables in database:', tables)

if not tables:
    print('No tables found. Creating tables...')
    from app import app, db
    with app.app_context():
        db.create_all()
        print('Tables created successfully')
        
        # Check again
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print('Tables after creation:', tables)

conn.close()
