#!/usr/bin/env python
"""
Database Initialization Script

This script initializes the database with the schema defined in schema.sql.
It creates the necessary tables, indexes, and views for the Transportation Dashboard.

Usage:
    python init_db.py
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
        logging.FileHandler("db_init.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DBInit")

# Load environment variables
load_dotenv()

# Get database connection parameters from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "transportation")
DB_USER = os.getenv("DB_USERNAME", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_URL = os.getenv("DATABASE_URL")

def get_connection():
    """Get a connection to the database"""
    if DB_URL:
        return psycopg2.connect(DB_URL)
    else:
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

def init_db():
    """Initialize the database with the schema"""
    logger.info("Initializing database...")
    
    # Get the path to the schema file
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    
    # Read the schema file
    with open(schema_path, "r") as f:
        schema_sql = f.read()
    
    # Connect to the database
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Execute the schema SQL
        cursor.execute(schema_sql)
        
        # Commit the changes
        conn.commit()
        
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def create_database():
    """Create the database if it doesn't exist"""
    logger.info(f"Creating database {DB_NAME} if it doesn't exist...")
    
    # Connect to the postgres database to create the new database
    try:
        # Connect to the default postgres database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if the database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            # Create the database
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            logger.info(f"Database {DB_NAME} created")
        else:
            logger.info(f"Database {DB_NAME} already exists")
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def main():
    """Main function"""
    try:
        # Skip creating the database for Google Cloud SQL
        # Just initialize the database with the schema
        init_db()
        
        logger.info("Database setup complete")
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
