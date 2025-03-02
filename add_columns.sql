-- Add missing columns to orders table
ALTER TABLE orders ADD COLUMN IF NOT EXISTS delivery_date TIMESTAMP;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS volume_m3 DECIMAL(10, 2);
