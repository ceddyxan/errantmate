from app import app, db, Delivery, User
from sqlalchemy import text

print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

with app.app_context():
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        print("Database connection successful")
        
        # Test Delivery query
        deliveries = Delivery.query.all()
        print(f"Delivery query successful - Found {len(deliveries)} deliveries")
        
        # Test User query
        users = User.query.all()
        print(f"User query successful - Found {len(users)} users")
        
        # Test dashboard logic
        from app import index
        with app.test_request_context():
            try:
                response = index()
                print("Dashboard route works successfully")
            except Exception as e:
                print(f"Dashboard route error: {e}")
                
    except Exception as e:
        print(f"Database error: {e}")
