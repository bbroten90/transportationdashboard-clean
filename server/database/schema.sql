-- Database schema for Transportation Dashboard

-- Create orders table if it doesn't exist
CREATE TABLE IF NOT EXISTS orders (
  id VARCHAR(255) PRIMARY KEY,
  customer_id VARCHAR(255) NOT NULL,
  customer_name VARCHAR(255) NOT NULL,
  ship_from TEXT NOT NULL,
  ship_to TEXT NOT NULL,
  pickup_date TIMESTAMP,
  delivery_date TIMESTAMP,
  status VARCHAR(50) DEFAULT 'PENDING',
  priority VARCHAR(50) DEFAULT 'MEDIUM',
  weight_kg DECIMAL(10, 2) DEFAULT 0,
  volume_m3 DECIMAL(10, 2),
  special_requirements JSONB DEFAULT '{}',
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create trucks table if it doesn't exist
CREATE TABLE IF NOT EXISTS trucks (
  id VARCHAR(255) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  driver VARCHAR(255) NOT NULL,
  current_hours DECIMAL(10, 2) DEFAULT 0,
  max_hours DECIMAL(10, 2) DEFAULT 0,
  warehouse VARCHAR(255) NOT NULL
);

-- Create trailers table if it doesn't exist
CREATE TABLE IF NOT EXISTS trailers (
  id VARCHAR(255) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  max_weight_kg DECIMAL(10, 2) DEFAULT 0,
  has_pallet_jack BOOLEAN DEFAULT FALSE,
  current_weight_kg DECIMAL(10, 2) DEFAULT 0,
  warehouse VARCHAR(255) NOT NULL
);

-- Create order_assignments table if it doesn't exist
CREATE TABLE IF NOT EXISTS order_assignments (
  id SERIAL PRIMARY KEY,
  order_id VARCHAR(255) REFERENCES orders(id),
  truck_id VARCHAR(255) REFERENCES trucks(id),
  trailer_id VARCHAR(255) REFERENCES trailers(id),
  sequence INTEGER DEFAULT 0,
  assigned_by VARCHAR(255) NOT NULL,
  assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on status for faster queries
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

-- Create index on customer_id for faster queries
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);

-- Create index on pickup_date for faster queries
CREATE INDEX IF NOT EXISTS idx_orders_pickup_date ON orders(pickup_date);

-- Create view for pending orders
CREATE OR REPLACE VIEW pending_orders AS
SELECT * FROM orders WHERE status = 'PENDING';

-- Create view for in-transit orders
CREATE OR REPLACE VIEW in_transit_orders AS
SELECT * FROM orders WHERE status = 'IN_TRANSIT';

-- Create view for delivered orders
CREATE OR REPLACE VIEW delivered_orders AS
SELECT * FROM orders WHERE status = 'DELIVERED';

-- Create view for cancelled orders
CREATE OR REPLACE VIEW cancelled_orders AS
SELECT * FROM orders WHERE status = 'CANCELLED';

-- Create view for high priority orders
CREATE OR REPLACE VIEW high_priority_orders AS
SELECT * FROM orders WHERE priority = 'HIGH';
