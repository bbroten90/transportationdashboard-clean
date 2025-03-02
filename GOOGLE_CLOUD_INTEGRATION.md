# Google Cloud Integration for Transportation Dashboard

This document describes how to set up and use the Google Cloud integration for the Transportation Dashboard application. The integration uses Google Cloud services for PDF processing, file storage, and database operations.

## Overview

The Transportation Dashboard application can be integrated with Google Cloud services to enhance its capabilities:

1. **Document AI**: Extract order information from PDF documents automatically
2. **Cloud Storage**: Store and manage PDF files in the cloud
3. **Cloud SQL**: Use a managed PostgreSQL database for storing orders and other data

## Prerequisites

Before setting up the integration, you need:

1. A Google Cloud Platform account
2. A Google Cloud project with the following APIs enabled:
   - Document AI API
   - Cloud Storage API
   - Cloud SQL Admin API
3. A service account with appropriate permissions
4. The Google Cloud SDK installed on your machine

## Setting Up Google Cloud Services

### 1. Create a Google Cloud Project

If you don't already have a Google Cloud project:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on "New Project"
3. Enter a name for your project (e.g., "transportation-dashboard")
4. Click "Create"

### 2. Enable Required APIs

1. Go to the [API Library](https://console.cloud.google.com/apis/library)
2. Search for and enable the following APIs:
   - Document AI API
   - Cloud Storage API
   - Cloud SQL Admin API

### 3. Create a Service Account

1. Go to [IAM & Admin > Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Click "Create Service Account"
3. Enter a name and description for the service account
4. Grant the following roles:
   - Document AI Editor
   - Storage Admin
   - Cloud SQL Admin
5. Click "Create Key" and select JSON
6. Save the key file as `credentials.json` in the root directory of the application

### 4. Set Up Document AI

1. Go to the [Document AI Console](https://console.cloud.google.com/ai/document-ai)
2. Click "Create Processor"
3. Select "Form Parser" as the processor type
4. Enter a name for the processor
5. Select a region (e.g., "us")
6. Click "Create"
7. Note the processor ID for later use

### 5. Set Up Cloud Storage

1. Go to the [Cloud Storage Console](https://console.cloud.google.com/storage/browser)
2. Click "Create Bucket"
3. Enter a name for the bucket (e.g., "transportation-incoming-pdfs")
4. Select a region
5. Click "Create"
6. Repeat for "transportation-processed-pdfs" and "transportation-error-pdfs" buckets

### 6. Set Up Cloud SQL

1. Go to the [Cloud SQL Console](https://console.cloud.google.com/sql)
2. Click "Create Instance"
3. Select PostgreSQL
4. Enter a name for the instance
5. Set a password for the postgres user
6. Select a region
7. Click "Create"
8. Once the instance is created, click on it
9. Go to "Databases" and click "Create Database"
10. Enter "transportation" as the database name
11. Click "Create"

## Setting Up the MCP Server

The Google Cloud integration is implemented as an MCP (Model Context Protocol) server that can be used with Claude. To set up the MCP server:

1. Clone the MCP server repository:
   ```
   git clone https://github.com/your-username/google-cloud-mcp.git
   cd google-cloud-mcp
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Build the server:
   ```
   npm run build
   ```

4. Configure the server by editing the `.env` file:
   ```
   # Google Cloud Project Configuration
   GCP_PROJECT_ID=your-project-id
   GCP_CREDENTIALS_FILE=path/to/credentials.json

   # Document AI Configuration
   DOCUMENT_AI_LOCATION=us
   DOCUMENT_AI_PROCESSOR_ID=your-processor-id

   # Storage Configuration
   GCP_BUCKET_INCOMING=transportation-incoming-pdfs
   GCP_BUCKET_PROCESSED=transportation-processed-pdfs
   GCP_BUCKET_ERROR=transportation-error-pdfs

   # Database Configuration
   DB_TYPE=postgres
   DB_HOST=localhost
   DB_PORT=5432
   DB_USERNAME=postgres
   DB_PASSWORD=postgres
   DB_NAME=transportation
   # Alternatively, use a connection string
   # DATABASE_URL=postgresql://postgres:postgres@localhost:5432/transportation
   ```

5. Install the MCP server in Claude:
   ```
   npm run install-mcp
   ```

## Using the Google Cloud Integration

### Processing PDFs with Document AI

You can use the MCP server to process PDF files with Document AI:

```
process_pdf(pdf_path="path/to/file.pdf")
```

This will extract order information from the PDF and return it as structured data.

### Uploading Files to Cloud Storage

You can upload files to Cloud Storage:

```
upload_to_storage(file_path="path/to/file.pdf", bucket_name="transportation-incoming-pdfs", destination_path="file.pdf")
```

### Creating Orders in the Database

You can create orders in the database:

```
create_order(order_data={
  "id": "ORD-12345",
  "customer_id": "CUST-001",
  "customer_name": "ACME Corp",
  "ship_from": "Winnipeg, MB",
  "ship_to": "Calgary, AB",
  "pickup_date": "2025-03-15T12:00:00Z",
  "weight_kg": 1500,
  "special_requirements": {
    "requires_refrigeration": true
  },
  "notes": "Handle with care"
})
```

### Getting Orders from the Database

You can get orders from the database:

```
get_orders(limit=10, offset=0, status="PENDING")
```

## Troubleshooting

### Document AI Issues

- Make sure the Document AI API is enabled
- Check that the service account has the Document AI Editor role
- Verify that the processor ID is correct
- Ensure the PDF file is in a format that Document AI can process

### Cloud Storage Issues

- Make sure the Cloud Storage API is enabled
- Check that the service account has the Storage Admin role
- Verify that the bucket names are correct
- Ensure the file paths are correct

### Database Issues

- Make sure the Cloud SQL Admin API is enabled
- Check that the service account has the Cloud SQL Admin role
- Verify that the database connection parameters are correct
- Ensure the database and tables exist

## Additional Resources

- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Document AI Documentation](https://cloud.google.com/document-ai/docs)
- [Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [MCP Server Documentation](https://github.com/your-username/google-cloud-mcp)
