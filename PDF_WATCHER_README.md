# PDF Watcher Service

The PDF Watcher Service is a component of the Transportation Dashboard that automatically processes PDF order documents and creates orders in the system.

## Overview

This service monitors a designated directory for new PDF files, extracts order information from them, and creates orders in the database. It's designed to handle high volumes of orders (400+ per day) without manual intervention.

## Directory Structure

The service uses the following directory structure:

- `server/data/incoming_pdfs/`: Place new PDF files here for processing
- `server/data/processed_pdfs/`: Successfully processed PDFs are moved here
- `server/data/error_pdfs/`: PDFs that couldn't be processed are moved here

## Processing PDFs

There are three ways to process PDFs:

### 1. As Part of the Main Application

The PDF Watcher Service starts automatically when you run the main application using:

```
.\start.bat
```

This will start both the backend API server and the frontend, and the PDF Watcher Service will run in the background.

### 2. As a Standalone Service

You can run the PDF Watcher Service as a standalone application:

**Windows:**
```
.\start_pdf_watcher.bat
```

**Linux/macOS:**
```
./start_pdf_watcher.sh
```

### 3. Batch Processing

For one-time processing of all PDFs in the incoming directory:

**Windows:**
```
.\process_pdfs.bat
```

**Linux/macOS:**
```
./process_pdfs.sh
```

This is useful for:
- Processing a batch of PDFs at once
- Scheduled processing via cron jobs or Task Scheduler
- Testing the PDF extraction without running the continuous watcher

## How It Works

1. **File Detection**: The service monitors the `incoming_pdfs` directory for new PDF files.
2. **Data Extraction**: When a new PDF is detected, the service extracts order information using pattern matching.
3. **Order Creation**: If the extracted data is valid, an order is created in the database.
4. **File Management**: Processed PDFs are moved to either the `processed_pdfs` or `error_pdfs` directory.

## Logging

The service logs all activities to `pdf_watcher.log` in the root directory. This log file contains information about:

- Service startup and shutdown
- PDF processing attempts
- Successful order creations
- Errors and exceptions

## Integration with External Systems

To integrate with your existing systems:

1. **Automated File Transfer**: Set up a script or scheduled task to copy PDF files from your existing system to the `incoming_pdfs` directory.
2. **Network Share**: Configure the `incoming_pdfs` directory as a network share that other systems can write to.
3. **Email Integration**: Set up email forwarding to save PDF attachments to the `incoming_pdfs` directory.

## Troubleshooting

If PDFs are not being processed correctly:

1. Check the `pdf_watcher.log` file for error messages.
2. Verify that the PDF format is compatible with the extractor.
3. Examine PDFs in the `error_pdfs` directory to identify patterns in files that fail processing.
4. Ensure the database is accessible and properly configured.

## Customizing PDF Extraction

The PDF extraction logic is defined in `server/core/pdf_processor/pdf_extractor.py`. You can modify this file to adapt to your specific PDF formats by:

1. Adding new regular expressions to match your document format
2. Adjusting field extraction logic
3. Adding support for additional special requirements or fields

## Requirements

The PDF Watcher Service requires the following Python packages:

- watchdog
- pdfminer.six
- pytesseract
- Pillow

These dependencies are included in the project's `requirements.txt` file.
