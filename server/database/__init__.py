from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Database")

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./transportation.db")

# Create SQLAlchemy engine with fallback to SQLite if PostgreSQL connection fails
try:
    logger.info(f"Attempting to connect to database: {DATABASE_URL}")
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
        pool_pre_ping=True  # Check connection before using it
    )
    # Test the connection
    with engine.connect() as conn:
        from sqlalchemy import text
        conn.execute(text("SELECT 1"))
    logger.info("Database connection successful")
except Exception as e:
    logger.error(f"Error connecting to database: {str(e)}")
    logger.info("Falling back to SQLite database")
    # Fallback to SQLite
    sqlite_url = "sqlite:///./transportation.db"
    engine = create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False}
    )
    logger.info(f"Using SQLite database: {sqlite_url}")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
