#!/bin/bash

# Production Database Migration Script
# This script will create the necessary tables in your PostgreSQL database

echo "🚀 Starting production database migration..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL environment variable is not set!"
    echo "Please set it to your PostgreSQL connection string:"
    echo "export DATABASE_URL='postgresql://username:password@host:port/database'"
    exit 1
fi

echo "📡 Using database: $DATABASE_URL"

# Run the table creation script
python create_production_tables.py

echo "✅ Migration completed!"
