from app import app, db

def init_database():
    """Initialize the database with the new schema."""
    with app.app_context():
        # Drop all tables to ensure clean schema
        db.drop_all()
        # Create all tables with new schema including expenses field
        db.create_all()
        print("Database initialized successfully with expenses field!")

if __name__ == '__main__':
    init_database()
