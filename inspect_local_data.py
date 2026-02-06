#!/usr/bin/env python3
"""
SQLite Database Data Inspector
This script will show all existing data in the local SQLite database.
"""

import sys
sys.path.append('.')
from app import app, db, User, Delivery, AuditLog, Shelf
from datetime import datetime

def inspect_database():
    """Inspect and display all data in the database"""
    with app.app_context():
        print("📊 SQLite Database Data Inspection")
        print("=" * 60)
        print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🗄️  Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"📁 Actual file location: instance/deliveries.db")
        print()
        
        # Check tables first
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📋 Available tables: {tables}")
        print()
        
        # Users table
        print("👥 USERS TABLE")
        print("-" * 40)
        users = User.query.all()
        if users:
            print(f"Total users: {len(users)}")
            for user in users:
                print(f"  ID: {user.id}")
                print(f"  Username: {user.username}")
                print(f"  Email: {user.email or 'N/A'}")
                print(f"  Phone: {user.phone_number or 'N/A'}")
                print(f"  Role: {user.role}")
                print(f"  Active: {user.is_active}")
                print(f"  Created: {user.created_at}")
                print(f"  Has actual password: {'Yes' if user.actual_password else 'No'}")
                print("  ---")
        else:
            print("❌ No users found")
        print()
        
        # Deliveries table
        print("📦 DELIVERIES TABLE")
        print("-" * 40)
        deliveries = Delivery.query.all()
        if deliveries:
            print(f"Total deliveries: {len(deliveries)}")
            for delivery in deliveries[:10]:  # Show first 10 to avoid too much output
                print(f"  ID: {delivery.id}")
                print(f"  Display ID: {delivery.display_id}")
                print(f"  Sender: {delivery.sender_name} ({delivery.sender_phone})")
                print(f"  Recipient: {delivery.recipient_name} ({delivery.recipient_phone})")
                print(f"  Address: {delivery.recipient_address}")
                print(f"  Goods: {delivery.goods_type} (Qty: {delivery.quantity})")
                print(f"  Amount: KSh {delivery.amount}")
                print(f"  Expenses: KSh {delivery.expenses}")
                print(f"  Payment: {delivery.payment_by}")
                print(f"  Status: {delivery.status}")
                print(f"  Delivery Person: {delivery.delivery_person or 'N/A'}")
                print(f"  Created by: User ID {delivery.created_by}")
                print(f"  Created at: {delivery.created_at}")
                print("  ---")
            
            if len(deliveries) > 10:
                print(f"  ... and {len(deliveries) - 10} more deliveries")
        else:
            print("❌ No deliveries found")
        print()
        
        # Audit Log table
        print("📋 AUDIT LOG TABLE")
        print("-" * 40)
        audit_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(20).all()
        if audit_logs:
            print(f"Total audit logs (showing latest 20): {AuditLog.query.count()}")
            for log in audit_logs:
                print(f"  ID: {log.id}")
                print(f"  User: {log.username} (ID: {log.user_id})")
                print(f"  Action: {log.action}")
                print(f"  Resource: {log.resource_type or 'N/A'} ({log.resource_id or 'N/A'})")
                print(f"  Details: {log.details or 'N/A'}")
                print(f"  IP: {log.ip_address or 'N/A'}")
                print(f"  Timestamp: {log.timestamp}")
                print("  ---")
        else:
            print("❌ No audit logs found")
        print()
        
        # Shelf table
        print("🗄️  SHELF TABLE")
        print("-" * 40)
        shelves = Shelf.query.all()
        if shelves:
            print(f"Total shelves: {len(shelves)}")
            for shelf in shelves:
                print(f"  ID: {shelf.id}")
                print(f"  Status: {shelf.status}")
                print(f"  Size: {shelf.size}")
                print(f"  Price: KSh {shelf.price}/month")
                print(f"  Customer: {shelf.customer_name or 'N/A'}")
                print(f"  Customer Phone: {shelf.customer_phone or 'N/A'}")
                print(f"  Customer Email: {shelf.customer_email or 'N/A'}")
                print(f"  Card Number: {shelf.card_number or 'N/A'}")
                print(f"  Rented Date: {shelf.rented_date or 'N/A'}")
                print(f"  Items: {shelf.items_description or 'N/A'}")
                print(f"  Rental Period: {shelf.rental_period or 'N/A'} months")
                print(f"  Discount: {shelf.discount}%")
                print(f"  Maintenance: {shelf.maintenance_reason or 'N/A'}")
                print(f"  Created: {shelf.created_at}")
                print(f"  Updated: {shelf.updated_at}")
                print("  ---")
        else:
            print("❌ No shelves found")
        print()
        
        # Summary statistics
        print("📈 SUMMARY STATISTICS")
        print("-" * 40)
        print(f"Total Users: {User.query.count()}")
        print(f"Total Deliveries: {Delivery.query.count()}")
        print(f"Total Audit Logs: {AuditLog.query.count()}")
        print(f"Total Shelves: {Shelf.query.count()}")
        
        # Delivery status breakdown
        if deliveries:
            print("\nDelivery Status Breakdown:")
            status_counts = {}
            for delivery in deliveries:
                status_counts[delivery.status] = status_counts.get(delivery.status, 0) + 1
            for status, count in status_counts.items():
                print(f"  {status}: {count}")
        
        # User role breakdown
        if users:
            print("\nUser Role Breakdown:")
            role_counts = {}
            for user in users:
                role_counts[user.role] = role_counts.get(user.role, 0) + 1
            for role, count in role_counts.items():
                print(f"  {role}: {count}")
        
        # Shelf status breakdown
        if shelves:
            print("\nShelf Status Breakdown:")
            status_counts = {}
            for shelf in shelves:
                status_counts[shelf.status] = status_counts.get(shelf.status, 0) + 1
            for status, count in status_counts.items():
                print(f"  {status}: {count}")

if __name__ == "__main__":
    inspect_database()
