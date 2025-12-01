# Local PostgreSQL Development Setup

Since the application now uses PostgreSQL only, you'll need a local PostgreSQL instance for development.

## Option 1: Docker (Recommended)
```bash
# Start PostgreSQL container
docker run --name errantmate-postgres -e POSTGRES_PASSWORD=errantmate -e POSTGRES_DB=errantmate_db -p 5432:5432 -d postgres:15

# Set environment variable
export DATABASE_URL="postgresql://postgres:errantmate@localhost:5432/errantmate_db"

# Run the application
python start.py
```

## Option 2: Local PostgreSQL Installation
1. Install PostgreSQL on your system
2. Create a database:
```sql
CREATE DATABASE errantmate_db;
CREATE USER errantmate WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE errantmate_db TO errantmate;
```

3. Set environment variable:
```bash
export DATABASE_URL="postgresql://errantmate:your_password@localhost:5432/errantmate_db"
```

## Option 3: Cloud PostgreSQL (ElephantSQL, Supabase, etc.)
1. Sign up for a free PostgreSQL service
2. Get the connection string
3. Set DATABASE_URL environment variable

## Testing the Connection
```bash
# Test database initialization
python init_db.py

# Check database status
curl http://localhost:5001/check-db
```

## Environment Variables for Development
Create a `.env` file:
```
DATABASE_URL=postgresql://postgres:errantmate@localhost:5432/errantmate_db
SECRET_KEY=your-development-secret-key
FLASK_ENV=development
```

## Notes
- The application will NOT start without a valid DATABASE_URL
- SQLite support has been completely removed
- All database operations now use PostgreSQL
- Tables are automatically created on first run
