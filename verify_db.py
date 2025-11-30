from app import app, db, Delivery, User
from sqlalchemy import inspect

print("Verifying database state...")

with app.app_context():
    try:
        # Check if tables exist
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables found: {tables}")
        
        # Test queries
        users = User.query.all()
        deliveries = Delivery.query.all()
        
        print(f"Users in database: {len(users)}")
        print(f"Deliveries in database: {len(deliveries)}")
        
        # Test dashboard query
        deliveries_for_dashboard = Delivery.query.order_by(Delivery.created_at.desc()).all()
        print(f"Dashboard query successful: {len(deliveries_for_dashboard)} deliveries")
        
        print("Database verification PASSED!")
        
    except Exception as e:
        print(f"Database verification FAILED: {e}")
        import traceback
        traceback.print_exc()
