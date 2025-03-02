# Google Document AI Integration

This document provides instructions on how to set up and use the Google Document AI integration for the Transportation Dashboard application. The integration uses Google Cloud Document AI to extract order information from PDF documents with higher accuracy and confidence scores.

## Overview

The Google Document AI integration enhances the PDF extraction capabilities of the Transportation Dashboard application by:

1. **Improved Accuracy**: Using machine learning to extract information from PDFs with higher accuracy
2. **Confidence Scores**: Providing confidence scores for extracted fields to identify potential issues
3. **Automatic Review Flagging**: Automatically flagging fields that need human review
4. **Manufacturer-Specific Processing**: Applying manufacturer-specific processing to the extracted data
5. **Hybrid Approach**: Combining the strengths of Google Document AI and the enhanced PDF extractor
6. **Fallback Mechanism**: Falling back to the enhanced PDF extractor if Google Document AI is not available

## Prerequisites

Before setting up the integration, you need:

1. A Google Cloud Platform account
2. A Google Cloud project with the Document AI API enabled
3. A service account with appropriate permissions
4. A Document AI processor configured for form parsing

## Setting Up Google Document AI

### 1. Create a Google Cloud Project

If you don't already have a Google Cloud project:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on "New Project"
3. Enter a name for your project (e.g., "transportation-dashboard")
4. Click "Create"

### 2. Enable the Document AI API

1. Go to the [API Library](https://console.cloud.google.com/apis/library)
2. Search for "Document AI API"
3. Click on "Document AI API"
4. Click "Enable"

### 3. Create a Service Account

1. Go to [IAM & Admin > Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Click "Create Service Account"
3. Enter a name and description for the service account
4. Grant the "Document AI Editor" role
5. Click "Create Key" and select JSON
6. Save the key file as `credentials.json` in the `C:/Users/Brent/Documents/Cline/MCP/google-cloud-mcp/` directory (or the equivalent path on your system)

### 4. Create a Document AI Processor

1. Go to the [Document AI Console](https://console.cloud.google.com/ai/document-ai)
2. Click "Create Processor"
3. Select "Form Parser" as the processor type
4. Enter a name for the processor
5. Select a region (e.g., "us")
6. Click "Create"
7. Note the processor ID for later use

### 5. Configure Environment Variables

Update the `.env` file with your Google Cloud configuration:

```
# Google Cloud Document AI Configuration
GCP_PROJECT_ID=your-project-id
DOCUMENT_AI_LOCATION=us
DOCUMENT_AI_PROCESSOR_ID=your-processor-id
GCP_CREDENTIALS_FILE=path/to/credentials.json
```

Replace the placeholder values with your actual values.

## Installation

1. Run the setup script to install the required dependencies:

   On Windows:
   ```
   setup_google_documentai.bat
   ```

   On Linux/macOS:
   ```
   ./setup_google_documentai.sh
   ```

2. The setup script will:
   - Install the required Python packages
   - Check if the credentials file exists
   - Check if the processor ID is set
   - Run a test to verify the integration is working

## Testing the Integration

You can test the Google Document AI integration by running:

```
python test_google_documentai.py [pdf_path]
```

Where `[pdf_path]` is the path to a PDF file to process. If not provided, the script will try to use a sample PDF from the `SampleOrders` directory.

To compare the results with the enhanced PDF extractor, add the `--compare` flag:

```
python test_google_documentai.py [pdf_path] --compare
```

## Using the Integration

The integration is automatically used by the Transportation Dashboard application when available. If Google Document AI is not available (e.g., due to missing credentials or API errors), the application will fall back to the enhanced PDF extractor.

### Hybrid Approach

The system uses a hybrid approach to extract data from PDFs:

1. **Google Document AI First**: The system first tries to extract data using Google Document AI, which is particularly good at extracting structured data from forms.

2. **Manufacturer-Specific Processing**: After extraction, the system applies manufacturer-specific processing to the data based on the detected manufacturer (BASF, Bayer, FCL, Nufarm, or Gowan).

3. **Enhanced Extractor Fallback**: If Google Document AI fails to extract certain fields or is not available, the system falls back to the enhanced PDF extractor.

4. **Special Handling for Known PDFs**: The system applies special handling for known problematic PDFs to ensure accurate extraction.

This hybrid approach combines the strengths of both Google Document AI and the enhanced PDF extractor to provide the most accurate extraction possible.

### Manufacturer-Specific Processing

The system includes specialized processing for different manufacturers:

1. **BASF**: 
   - Sets ship_from_location to "CWS Edmonton"
   - Extracts Richardson International information from filenames
   - Handles specific weight and quantity formats

2. **Bayer**:
   - Sets ship_from_location to "CWS Regina"
   - Extracts ACROPOLIS WAREHOUSING information
   - Handles BOL document formats

3. **FCL (Federated Co-Op)**:
   - Extracts Swan Lake information
   - Handles specific address formats

4. **Nufarm**:
   - Handles Edmonton warehouse information
   - Processes special instructions

5. **Gowan**:
   - Extracts Winnipeg and Regina location information
   - Processes Winfield United Canada information
   - Handles GC-prefixed order numbers

The manufacturer is detected automatically from the PDF content or filename, and the appropriate processing is applied to ensure accurate extraction.

### PDF API Endpoints

The PDF API endpoints now use Google Document AI when available:

- `POST /pdf/extract`: Extract order data from a PDF file
- `POST /pdf/extract-to-order`: Extract PDF data and convert to an order object
- `POST /pdf/upload`: Upload a PDF file and save to disk

### PDF Processor Script

The PDF processor script (`process_pdfs.py`) now uses Google Document AI when available to process PDF files in batch mode.

### Confidence Scores and Review Flags

The extracted order data now includes confidence scores and review flags for each field:

```json
{
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
  "notes": "Handle with care",
  "confidence_scores": {
    "id": 0.95,
    "customer_id": 0.85,
    "customer_name": 0.92,
    "ship_from": 0.78,
    "ship_to": 0.82,
    "pickup_date": 0.88,
    "weight_kg": 0.75
  },
  "needs_review": {
    "id": false,
    "customer_id": false,
    "customer_name": false,
    "ship_from": false,
    "ship_to": false,
    "pickup_date": false,
    "weight_kg": false
  }
}
```

Fields with confidence scores below 0.5 are automatically flagged for review.

## Troubleshooting

### Document AI Issues

- Make sure the Document AI API is enabled
- Check that the service account has the Document AI Editor role
- Verify that the processor ID is correct
- Ensure the PDF file is in a format that Document AI can process

### Credentials Issues

- Make sure the credentials file exists at the specified path
- Check that the service account has the necessary permissions
- Verify that the project ID is correct

### API Issues

- Check the logs for error messages
- Make sure the Document AI API is enabled and not hitting quota limits
- Verify that the processor is in the correct region

## Additional Resources

- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Document AI Documentation](https://cloud.google.com/document-ai/docs)
- [Document AI Pricing](https://cloud.google.com/document-ai/pricing)
- [Document AI Quotas](https://cloud.google.com/document-ai/quotas)
