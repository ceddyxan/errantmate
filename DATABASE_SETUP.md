# Database Setup for Shelf Rental System

## Overview
The shelf rental system requires proper database setup to function correctly. This document provides instructions for initializing the database with the shelf table and sample data.

## Database Tables Required

### Shelf Table
The `shelf` table stores all shelf information including:
- Shelf ID (A-01, B-02, etc.)
- Status (available, occupied, maintenance)
- Size and pricing
- Customer information for occupied shelves
- Rental details and timestamps

## Setup Instructions

### 1. Create Database Tables
Run the following command to create all required database tables:

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database tables created successfully')"
```

### 2. Initialize Shelf Data
Run the shelf initialization script to populate the database with sample data:

```bash
python init_shelves.py
```

### 3. Verify Setup
After running the initialization, you should see output similar to:

```
Successfully initialized 12 shelves in the database

Initialized Shelves:
------------------------------------------------------------
A-01   | Small  | KSh  800 | available
A-02   | Small  | KSh  800 | occupied - John Doe
A-03   | Small  | KSh  800 | available
A-04   | Small  | KSh  800 | maintenance - Repair needed
B-01   | Large  | KSh 1000 | occupied - Jane Smith
B-02   | Large  | KSh 1000 | available
B-03   | Large  | KSh 1000 | occupied - Mike Johnson
C-01   | Small  | KSh  800 | available
C-02   | Small  | KSh  800 | occupied - Sarah Wilson
C-03   | Large  | KSh 1000 | available
D-01   | Large  | KSh 1000 | maintenance - Cleaning
D-02   | Large  | KSh 1000 | occupied - Tom Brown
```

## Troubleshooting

### Error: "relation 'shelf' does not exist"
This error occurs when the shelf table hasn't been created in the database.

**Solution:**
1. Run the table creation command above
2. Run the initialization script
3. Restart the application

### Error: "Missing required fields"
This error was caused by field name mismatch between frontend and backend.

**Solution:**
- Fixed in commit fd88d63 - API now expects camelCase field names matching frontend

## Production Deployment

For production deployment:

1. **Database Migration**: Ensure the shelf table exists in production database
2. **Data Initialization**: Run init_shelves.py to populate initial data
3. **Verification**: Test shelf rental functionality
4. **Backup**: Create database backup after initialization

## API Endpoints

After setup, the following endpoints should work:

- `GET /api/shelves` - Fetch all shelves
- `POST /api/shelves/rent` - Rent a shelf
- `GET /api/shelves/stats` - Get shelf statistics

## Sample Data Summary

- **Total Shelves**: 12
- **Available**: 6 shelves (A-01, A-03, B-02, C-01, C-03, D-01)
- **Occupied**: 5 shelves (A-02, B-01, B-03, C-02, D-02)
- **Maintenance**: 1 shelf (A-04)
- **Monthly Revenue**: KSh 4,600 from occupied shelves

## Support

If you encounter database-related issues:
1. Check that the shelf table exists
2. Verify database connection
3. Run initialization scripts
4. Check application logs for detailed error messages
