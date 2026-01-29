# Production Database Migration

This directory contains scripts to migrate your production database to support the new signup functionality.

## Issue
The production environment is showing: `relation "users" does not exist` because the database schema needs to be updated.

## Solution

### Option 1: Automatic Migration (Recommended)
Run this command in your production environment:

```bash
# Set your database URL
export DATABASE_URL='postgresql://username:password@host:port/database'

# Run the migration script
python create_production_tables.py
```

### Option 2: Manual SQL Migration
If you prefer to run SQL directly:

```sql
-- Create the users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE,
    phone_number VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number);
```

### Option 3: Using Render Dashboard
1. Go to your Render dashboard
2. Navigate to your service
3. Click on "Shell" tab
4. Run the migration script

## Verification
After migration, verify the table exists:

```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name = 'users';
```

## Next Steps
1. Run the migration
2. Test the signup functionality
3. Verify users appear in User Management

The signup form will work correctly once the `users` table exists in your production database.
