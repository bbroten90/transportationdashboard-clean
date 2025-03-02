#!/usr/bin/env python
"""
Add Missing Columns Script

This script adds missing columns to the orders table.
"""

import os
import sys
import logging
import psycopg2
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AddColumns")

# Load environment variables
load_dotenv()

# Get database connection parameters from environment variables
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    logger.error("DATABASE_URL environment variable not set")
    sys.exit(1)

logger.info(f"Connecting to database: {DB_URL}")

try:
    # Connect to the database
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    
    # Add missing columns
    logger.info("Adding missing columns to orders table...")
    cursor.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS delivery_date TIMESTAMP;")
    cursor.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS volume_m3 DECIMAL(10, 2);")
    
    # Commit the changes
    conn.commit()
    logger.info("Columns added successfully")
    
    # Verify columns
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'orders';")
    columns = cursor.fetchall()
    logger.info("Columns in orders table:")
    for column in columns:
        logger.info(f"  {column[0]}")
    
    # Close the connection
    cursor.close()
    conn.close()
    logger.info("Database connection closed")
    
except Exception as e:
    logger.error(f"Error: {str(e)}")
    sys.exit(1)
