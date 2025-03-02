# Database Setup Guide

This guide explains how to set up the database for the Transportation Dashboard application.

## Database Configuration

The application is configured to use a PostgreSQL database hosted on Google Cloud SQL. However, it will automatically fall back to a local SQLite database if the PostgreSQL connection fails.

## Current Configuration

The database connection is configured in the `.env` file:

```
# Google Cloud SQL connection
DATABASE_URL=postgresql://transportation-user:cwsseel1664@34.60.46.45:5432/transportation
DB_HOST=34.60.46.45
DB_PORT=5432
DB_NAME=transportation
DB_USERNAME=transportation-user
DB_PASSWORD=cwsseel1664
```

## Database Initialization

To initialize the database tables, run:

```
.\create_tables.bat  # Windows
./create_tables.sh   # Linux/Mac
```

This will:
1. Connect to the Google Cloud SQL database
2. Create all the necessary tables based on the SQLAlchemy models
3. If the connection fails, it will fall back to a local SQLite database

## Google Cloud SQL Setup

The Google Cloud SQL instance has been set up successfully. The application is now using the cloud database for all operations.

## Adding Data to the Database

Currently, the database is empty, which is why you see the "Failed to load dashboard data" error. You can add data to the database in several ways:

1. **Through the application UI**: Use the Order Management, Fleet Management, and other pages to add data.
2. **By uploading PDFs**: Use the PDF Processor page to upload and process order PDFs.
3. **Directly through the API**: Use the API endpoints to add data programmatically.

## Troubleshooting

### Connection Timeout

If you see a connection timeout error when trying to connect to the Google Cloud SQL instance:

```
Error connecting to database: connection to server at "34.60.46.45" port 5432 failed: Connection timed out
```

This could be due to:
1. The Google Cloud SQL instance is still being created
2. Your IP address is not allowed in the Google Cloud SQL instance's firewall rules
3. The Google Cloud SQL instance is not running

### Using SQLite Instead

If you want to use SQLite instead of PostgreSQL, you can modify the `.env` file:

```
# Environment configuration
ENVIRONMENT=development
DATABASE_URL=sqlite:///./transportation.db
```

## Machine Learning PDF Processing

The application uses Google Document AI for machine learning-based PDF processing. This is configured in the `.env` file:

```
# Google Cloud Document AI Configuration
GCP_PROJECT_ID=transportation-dashboard
DOCUMENT_AI_LOCATION=us
DOCUMENT_AI_PROCESSOR_ID=84f9d8f793949d8e
GCP_CREDENTIALS_FILE=C:/Users/Brent/Documents/Cline/MCP/google-cloud-mcp/credentials.json
```

The PDF processing functionality is implemented in:
- `server/core/pdf_processor/google_documentai_extractor.py` - Main ML-powered extractor
- `server/services/google_documentai_service.py` - Service for interacting with Google Document AI
