#!/usr/bin/env python
"""
Database Table Creation Script

This script creates database tables using SQLAlchemy models.
It's an alternative to using the SQL schema directly.

Usage:
    python create_tables.py
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the server package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import the database models and engine
from server.database import engine, Base
from server.database.models import OrderModel, TruckModel, TrailerModel, OrderAssignmentModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("db_create_tables.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DBCreateTables")

def create_tables():
    """Create all tables defined in the models"""
    logger.info("Creating database tables...")
    try:
        # Drop all tables first
        Base.metadata.drop_all(bind=engine)
        logger.info("Dropped existing tables")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Tables in database: {tables}")
        
        # Verify columns in orders table
        columns = inspector.get_columns("orders")
        column_names = [column["name"] for column in columns]
        logger.info(f"Columns in orders table: {column_names}")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

def main():
    """Main function"""
    try:
        # Create the tables
        create_tables()
        logger.info("Database setup complete")
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
