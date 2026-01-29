# Render Build Hook for Automatic Database Migration

# This script runs automatically when you deploy to Render
# It ensures the database schema is up-to-date

echo "🚀 Starting automatic database migration..."

# Check if we're in production
if [ "$RENDER_ENVIRONMENT" = "production" ]; then
    echo "📡 Production environment detected"
    
    # Wait for database to be ready (important for PostgreSQL)
    echo "⏳ Waiting for database to be ready..."
    sleep 10
    
    # Run database migration
    echo "🔄 Running database migration..."
    python -c "
import os
from app import app, db
from sqlalchemy import inspect

with app.app_context():
    try:
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        required_tables = ['users', 'delivery', 'audit_log']
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if missing_tables:
            print(f'Creating missing tables: {missing_tables}')
            db.create_all()
            print('✅ Database migration completed successfully!')
        else:
            print('✅ All tables already exist')
            
    except Exception as e:
        print(f'❌ Migration failed: {e}')
        raise
"
    
    echo "✅ Migration completed successfully!"
else
    echo "🔧 Development environment - skipping automatic migration"
fi

echo "🎉 Ready to start the application!"
