#!/usr/bin/env python
"""
PDF Watcher Service Starter

This script starts the PDF watcher service that monitors the incoming_pdfs directory
for new PDF files and processes them automatically.

Usage:
    python start_pdf_watcher.py
"""

import os
import sys
import time
import logging

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.services.pdf_watcher_service import PDFWatcherService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pdf_watcher.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PDFWatcherStarter")

def main():
    """Main function to start the PDF watcher service"""
    logger.info("Starting PDF watcher service...")
    
    # Create PDF watcher service
    service = PDFWatcherService()
    
    try:
        # Start the service
        service.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Stopping service...")
        service.stop()
    except Exception as e:
        logger.error(f"Error in PDF watcher service: {str(e)}")
        service.stop()
        sys.exit(1)
    
    logger.info("PDF watcher service stopped")
    sys.exit(0)

if __name__ == "__main__":
    main()
