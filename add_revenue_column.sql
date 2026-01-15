-- PostgreSQL migration script to add revenue column to delivery table
-- Run this directly in your PostgreSQL database

-- Check if column exists (optional - for safety)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name='delivery' 
        AND column_name='revenue'
    ) THEN
        -- Add the revenue column
        ALTER TABLE delivery ADD COLUMN revenue FLOAT DEFAULT 50.0;
        
        -- Update existing records
        UPDATE delivery SET revenue = 50.0 WHERE revenue IS NULL;
        
        RAISE NOTICE 'Revenue column added successfully to delivery table';
    ELSE
        RAISE NOTICE 'Revenue column already exists in delivery table';
    END IF;
END $$;

-- Verify the column was added
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'delivery' AND column_name = 'revenue';
