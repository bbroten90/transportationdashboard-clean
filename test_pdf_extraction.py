#!/usr/bin/env python
"""
Test PDF Extraction with PyMuPDF

This script tests the updated PDF extractor with PyMuPDF on a sample PDF file.
It prints the extracted text and structured data to verify the extraction works correctly.
"""

import os
import sys
import json
from server.core.pdf_processor.pdf_extractor import PDFExtractor

def test_pdf_extraction(pdf_path):
    """Test PDF extraction on a single file"""
    print(f"Testing PDF extraction on: {pdf_path}")
    
    # Create PDF extractor
    extractor = PDFExtractor()
    
    try:
        # Extract data from PDF
        print("Extracting data...")
        order_data = extractor.extract_order_data(pdf_path)
        
        # Print extracted data
        print("\nExtracted Order Data:")
        print(json.dumps(
            {k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v 
             for k, v in order_data.items()}, 
            indent=2
        ))
        
        # Print validation result
        is_valid = all([
            order_data.get("ship_from"),
            order_data.get("ship_to"),
            order_data.get("weight_kg")
        ])
        
        print(f"\nValidation result: {'Valid' if is_valid else 'Invalid'} order data")
        
        if not is_valid:
            print("Missing required fields:")
            if not order_data.get("ship_from"):
                print("- ship_from")
            if not order_data.get("ship_to"):
                print("- ship_to")
            if not order_data.get("weight_kg"):
                print("- weight_kg")
        
        return is_valid
    except Exception as e:
        print(f"Error extracting data: {str(e)}")
        return False

def main():
    """Main function"""
    # Check if PDF path is provided
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Use a default sample PDF
        sample_dir = "SampleOrders"
        sample_files = [f for f in os.listdir(sample_dir) if f.lower().endswith('.pdf')]
        
        if not sample_files:
            print("No sample PDFs found in SampleOrders directory")
            return
        
        pdf_path = os.path.join(sample_dir, sample_files[0])
    
    # Test PDF extraction
    success = test_pdf_extraction(pdf_path)
    
    # Print result
    if success:
        print("\nPDF extraction test successful!")
    else:
        print("\nPDF extraction test failed!")

if __name__ == "__main__":
    main()
