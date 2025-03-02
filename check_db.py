import os
import sys
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Float, DateTime, JSON, Boolean, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CheckDB")

# Load environment variables
load_dotenv()

# Get database connection parameters from environment variables
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    logger.error("DATABASE_URL environment variable not set")
    sys.exit(1)

logger.info(f"Connecting to database: {DB_URL}")

# Create SQLAlchemy engine
engine = create_engine(DB_URL)

# Create a base class for declarative models
Base = declarative_base()

# Define a simple test model
class TestModel(Base):
    """Test SQLAlchemy model"""
    __tablename__ = "test_table"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create the tables
try:
    from sqlalchemy import inspect
    inspector = inspect(engine)
    
    logger.info("Dropping test_table if it exists...")
    if inspector.has_table("test_table"):
        TestModel.__table__.drop(engine)
    
    logger.info("Creating test_table...")
    TestModel.__table__.create(engine)
    logger.info("Test table created successfully")
    
    # Create a session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # Create a test record
    test_record = TestModel(id="test-1", name="Test Record")
    db.add(test_record)
    db.commit()
    logger.info("Test record created successfully")
    
    # Query the test record
    result = db.query(TestModel).filter(TestModel.id == "test-1").first()
    logger.info(f"Test record retrieved: {result.id}, {result.name}")
    
    # Clean up
    db.delete(result)
    db.commit()
    logger.info("Test record deleted successfully")
    
    # Drop the test table
    TestModel.__table__.drop(engine)
    logger.info("Test table dropped successfully")
    
    logger.info("Database connection and operations successful")
except Exception as e:
    logger.error(f"Error: {str(e)}")
    sys.exit(1)
