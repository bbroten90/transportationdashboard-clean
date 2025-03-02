#!/usr/bin/env python
"""
Test Enhanced PDF Extraction

This script tests the enhanced PDF extractor with sample PDF files.
"""

import os
import json
from datetime import datetime
from server.core.pdf_processor.enhanced_pdf_extractor import EnhancedPDFExtractor

def test_enhanced_extraction(pdf_path):
    """Test enhanced PDF extraction on a single file"""
    print(f"\n\nTesting enhanced PDF extraction on: {pdf_path}")
    
    # Create enhanced PDF extractor
    extractor = EnhancedPDFExtractor()
    
    try:
        # Extract data from PDF
        print("Extracting data...")
        order_data = extractor.extract_order_data(pdf_path)
        
        # Convert datetime objects to strings for display
        serializable_data = {}
        for key, value in order_data.items():
            if isinstance(value, datetime):
                serializable_data[key] = value.isoformat()
            else:
                serializable_data[key] = value
        
        # Print extracted data
        print("\nExtracted Order Data:")
        print(json.dumps(serializable_data, indent=2))
        
        # Print specific fields of interest
        print("\nSpecific Fields of Interest:")
        print(f"Manufacturer: {order_data.get('manufacturer', '')}")
        print(f"Ship From Location: {order_data.get('ship_from_location', '')}")
        print(f"Ship To City: {order_data.get('ship_to_city', '')}")
        print(f"Ship To Company: {order_data.get('ship_to_company', '')}")
        print(f"Purchase Order: {order_data.get('purchase_order', '')}")
        print(f"Weight (kg): {order_data.get('weight_kg', 0)}")
        print(f"Weight (lbs): {order_data.get('weight_lbs', 0)}")
        print(f"Gross Weight (kg): {order_data.get('gross_weight_kg', 0)}")
        print(f"Gross Weight (lbs): {order_data.get('gross_weight_lbs', 0)}")
        print(f"Net Quantity: {order_data.get('net_quantity', '')}")
        print(f"Notes: {order_data.get('notes', '')}")
        
        # Save extracted data to JSON file
        output_dir = "pdf_extraction_results"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = os.path.basename(pdf_path)
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(output_dir, f"{base_name}_data.json")
        
        with open(output_path, 'w') as f:
            json.dump(serializable_data, f, indent=2)
        
        print(f"\nExtracted data saved to: {output_path}")
        
        return True
    except Exception as e:
        print(f"Error extracting data: {str(e)}")
        return False

def main():
    """Main function"""
    # Test with multiple PDF files
    pdf_files = [
        "SampleOrders/BOL_ 0834881732.PDF",  # BAYER
        "SampleOrders/CWS Picking Ticket Document.pdf",  # FCL
        "SampleOrders/FNDWRR.pdf",  # Nufarm
        "SampleOrders/GC1487243 CWS Winnipeg to Winkler.pdf",  # Gowan
        "SampleOrders/BASF Carrier Conf 6106947_0148976682 RICHARDSON -.pdf",  # BASF
        "SampleOrders/143777181 LAMONT.pdf"  # Additional test
    ]
    
    success_count = 0
    
    for pdf_path in pdf_files:
        if not os.path.exists(pdf_path):
            print(f"Error: File not found: {pdf_path}")
            continue
        
        # Test enhanced extraction
        if test_enhanced_extraction(pdf_path):
            success_count += 1
    
    # Print overall result
    print(f"\n\nEnhanced PDF extraction test completed!")
    print(f"Successfully processed {success_count} out of {len(pdf_files)} files.")

if __name__ == "__main__":
    main()
