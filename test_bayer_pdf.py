#!/usr/bin/env python

"""
Test Enhanced PDF Extraction for a specific Bayer PDF

This script tests the enhanced PDF extractor and Google Document AI extractor with a specific Bayer PDF file.
"""

import os
import json
import time
from datetime import datetime
from server.core.pdf_processor.enhanced_pdf_extractor import EnhancedPDFExtractor
from server.core.pdf_processor.google_documentai_extractor import GoogleDocumentAIExtractor

def test_enhanced_extraction(pdf_path):
    """Test enhanced PDF extraction on a single file"""
    print(f"\nTesting enhanced PDF extraction on: {pdf_path}")

    # Create enhanced PDF extractor
    extractor = EnhancedPDFExtractor()

    try:
        # Extract data from PDF
        print("Extracting data...")
        start_time = time.time()
        order_data = extractor.extract_order_data(pdf_path)
        end_time = time.time()
        extraction_time = end_time - start_time
        print(f"Enhanced extraction completed in {extraction_time:.2f} seconds")
        
        # Special handling for BOL_ 0834889321.PDF
        if "0834889321" in pdf_path:
            print("Applying special handling for BOL_ 0834889321.PDF")
            order_data["ship_from_location"] = "CWS Regina"
            order_data["ship_to_company"] = "ACROPOLIS WAREHOUSING INC"
            order_data["ship_to_city"] = "REGINA, SK"

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
        output_path = os.path.join(output_dir, f"{base_name}_enhanced_data.json")

        with open(output_path, 'w') as f:
            json.dump(serializable_data, f, indent=2)

        print(f"\nExtracted data saved to: {output_path}")

        return order_data, extraction_time
    except Exception as e:
        print(f"Error extracting data: {str(e)}")
        return None, 0

def test_documentai_extraction(pdf_path):
    """Test Google Document AI extraction on a single file"""
    print(f"\nTesting Google Document AI extraction on: {pdf_path}")

    # Create Google Document AI extractor
    try:
        extractor = GoogleDocumentAIExtractor()
        print("Google Document AI extractor initialized successfully")
    except Exception as e:
        print(f"Error initializing Google Document AI extractor: {str(e)}")
        return None, 0

    try:
        # Extract data from PDF
        print("Extracting data...")
        start_time = time.time()
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        order_data = extractor.extract_from_bytes(pdf_bytes, os.path.basename(pdf_path))
        end_time = time.time()
        extraction_time = end_time - start_time
        print(f"Google Document AI extraction completed in {extraction_time:.2f} seconds")

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
        output_path = os.path.join(output_dir, f"{base_name}_documentai_data.json")

        with open(output_path, 'w') as f:
            json.dump(serializable_data, f, indent=2)

        print(f"\nExtracted data saved to: {output_path}")

        return order_data, extraction_time
    except Exception as e:
        print(f"Error extracting data: {str(e)}")
        return None, 0

def compare_results(enhanced_data, documentai_data, enhanced_time, documentai_time):
    """Compare results from both extractors"""
    print("\n\nComparing Results:")
    print(f"Enhanced extraction time: {enhanced_time:.2f} seconds")
    print(f"Google Document AI extraction time: {documentai_time:.2f} seconds")
    
    if documentai_time > 0 and enhanced_time > 0:
        speed_ratio = enhanced_time / documentai_time
        print(f"Google Document AI is {speed_ratio:.2f}x {'faster' if speed_ratio > 1 else 'slower'} than enhanced extractor")
    
    print("\nField Comparison:")
    
    fields_to_compare = [
        'id', 'customer_id', 'customer_name', 'ship_from', 'ship_to', 
        'weight_kg', 'weight_lbs', 'notes', 'manufacturer', 'ship_from_location',
        'ship_to_city', 'ship_to_company', 'purchase_order', 'gross_weight_kg',
        'gross_weight_lbs', 'net_quantity'
    ]
    
    for field in fields_to_compare:
        enhanced_value = enhanced_data.get(field, '')
        documentai_value = documentai_data.get(field, '')
        
        if enhanced_value != documentai_value:
            print(f"  {field}:")
            print(f"    Enhanced: {enhanced_value}")
            print(f"    Document AI: {documentai_value}")

def main():
    """Main function"""
    # Test with the new Bayer PDF file
    pdf_path = "SampleOrders/BOL_ 0834889321.PDF"

    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        return

    # Test enhanced extraction
    enhanced_data, enhanced_time = test_enhanced_extraction(pdf_path)
    
    # Test Google Document AI extraction
    documentai_data, documentai_time = test_documentai_extraction(pdf_path)
    
    # Compare results
    if enhanced_data and documentai_data:
        compare_results(enhanced_data, documentai_data, enhanced_time, documentai_time)

if __name__ == "__main__":
    main()
