import os
import sys
import json
from datetime import datetime
from server.core.pdf_processor.google_documentai_extractor import GoogleDocumentAIExtractor

def test_format_shipping_fields():
    """Test the _format_shipping_fields method"""
    # Initialize the extractor
    extractor = GoogleDocumentAIExtractor()
    
    # Test case 1: Ship from location with address that matches warehouse
    order_data = {
        "ship_from_location": "1664 Seel Avenue, Winnipeg, MB",
        "manufacturer": "BASF",
        "ship_to_city": "Brandon",
        "ship_to": "Farmer John\n123 Main St\nBrandon MB R7A 1A1"
    }
    extractor._format_shipping_fields(order_data)
    print("Test case 1 - Ship from location with address that matches warehouse:")
    print(f"  ship_from_location: {order_data['ship_from_location']}")
    print(f"  ship_to_city: {order_data['ship_to_city']}")
    print()
    
    # Test case 2: No ship from location but manufacturer is set
    order_data = {
        "ship_from_location": "",
        "manufacturer": "BAYER",
        "ship_to_city": "Saskatoon",
        "ship_to": "Farmer Bob\n456 Oak St\nSaskatoon SK S7K 1J5"
    }
    extractor._format_shipping_fields(order_data)
    print("Test case 2 - No ship from location but manufacturer is set:")
    print(f"  ship_from_location: {order_data['ship_from_location']}")
    print(f"  ship_to_city: {order_data['ship_to_city']}")
    print()
    
    # Test case 3: Ship to city without province code
    order_data = {
        "ship_from_location": "CWS Edmonton",
        "manufacturer": "Nufarm",
        "ship_to_city": "Winnipeg",
        "ship_to": "Farmer Alice\n789 Pine St\nWinnipeg MB R3C 1T5"
    }
    extractor._format_shipping_fields(order_data)
    print("Test case 3 - Ship to city without province code:")
    print(f"  ship_from_location: {order_data['ship_from_location']}")
    print(f"  ship_to_city: {order_data['ship_to_city']}")
    print()
    
    # Test case 4: Ship to city already has province code
    order_data = {
        "ship_from_location": "CWS Calgary",
        "manufacturer": "FCL",
        "ship_to_city": "Edmonton, AB",
        "ship_to": "Farmer Charlie\n101 Spruce St\nEdmonton AB T5J 0K7"
    }
    extractor._format_shipping_fields(order_data)
    print("Test case 4 - Ship to city already has province code:")
    print(f"  ship_from_location: {order_data['ship_from_location']}")
    print(f"  ship_to_city: {order_data['ship_to_city']}")
    print()

def test_extract_order_data():
    """Test the extract_order_data method with a sample PDF"""
    # Initialize the extractor
    extractor = GoogleDocumentAIExtractor()
    
    # Check if we have sample PDFs
    sample_dir = "SampleOrders"
    if not os.path.exists(sample_dir):
        print(f"Sample directory {sample_dir} not found. Skipping PDF extraction test.")
        return
    
    # Find a sample PDF
    sample_files = os.listdir(sample_dir)
    pdf_files = [f for f in sample_files if f.endswith('.pdf') or f.endswith('.PDF')]
    
    if not pdf_files:
        print(f"No PDF files found in {sample_dir}. Skipping PDF extraction test.")
        return
    
    # Test with the first PDF
    sample_pdf = os.path.join(sample_dir, pdf_files[0])
    print(f"Testing extraction with {sample_pdf}")
    
    try:
        # Extract order data
        order_data = extractor.extract_order_data(sample_pdf)
        
        # Print the extracted data
        print("Extracted order data:")
        print(json.dumps(order_data, indent=2, default=str))
    except Exception as e:
        print(f"Error extracting order data: {str(e)}")

if __name__ == "__main__":
    # Test the _format_shipping_fields method
    test_format_shipping_fields()
    
    # Test the extract_order_data method
    test_extract_order_data()
