#!/usr/bin/env python
"""
Extract PDF Text

This script extracts raw text from all PDFs in the SampleOrders directory,
saves the text to individual files, and creates a summary of the current
extraction results.
"""

import os
import json
import fitz  # PyMuPDF
from datetime import datetime
from server.core.pdf_processor.pdf_extractor import PDFExtractor

def extract_text_from_pdf(pdf_path):
    """Extract raw text from a PDF file"""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def extract_data_with_current_patterns(pdf_path):
    """Extract data using current regex patterns"""
    extractor = PDFExtractor()
    try:
        return extractor.extract_order_data(pdf_path)
    except Exception as e:
        return {"error": str(e)}

def main():
    """Main function"""
    # Create output directory
    output_dir = "pdf_extraction_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get list of PDF files
    sample_dir = "SampleOrders"
    pdf_files = [f for f in os.listdir(sample_dir) if f.lower().endswith(('.pdf', '.PDF'))]
    
    if not pdf_files:
        print("No PDF files found in SampleOrders directory")
        return
    
    # Create summary file
    summary_file = os.path.join(output_dir, "extraction_summary.txt")
    with open(summary_file, "w") as f:
        f.write("PDF EXTRACTION SUMMARY\n")
        f.write("=====================\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total PDFs processed: {len(pdf_files)}\n\n")
    
    # Process each PDF
    for pdf_file in pdf_files:
        pdf_path = os.path.join(sample_dir, pdf_file)
        print(f"Processing: {pdf_file}")
        
        # Extract raw text
        raw_text = extract_text_from_pdf(pdf_path)
        
        # Save raw text to file
        text_file = os.path.join(output_dir, f"{os.path.splitext(pdf_file)[0]}_text.txt")
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(raw_text)
        
        # Extract data with current patterns
        extracted_data = extract_data_with_current_patterns(pdf_path)
        
        # Save extracted data to file
        data_file = os.path.join(output_dir, f"{os.path.splitext(pdf_file)[0]}_data.json")
        with open(data_file, "w", encoding="utf-8") as f:
            # Convert datetime objects to strings for JSON serialization
            serializable_data = {}
            for key, value in extracted_data.items():
                if isinstance(value, datetime):
                    serializable_data[key] = value.isoformat()
                else:
                    serializable_data[key] = value
            
            json.dump(serializable_data, f, indent=2)
        
        # Append to summary file
        with open(summary_file, "a") as f:
            f.write(f"\n{'-' * 80}\n")
            f.write(f"File: {pdf_file}\n")
            f.write(f"Size: {os.path.getsize(pdf_path) / 1024:.2f} KB\n")
            f.write(f"Text extracted: {len(raw_text)} characters\n\n")
            
            f.write("Current extraction results:\n")
            for key, value in extracted_data.items():
                if isinstance(value, datetime):
                    value = value.isoformat()
                elif isinstance(value, dict) and not value:
                    value = "{}"
                f.write(f"  {key}: {value}\n")
            
            # Check if required fields are present
            required_fields = ["ship_from", "ship_to", "weight_kg"]
            missing_fields = [field for field in required_fields if not extracted_data.get(field)]
            
            if missing_fields:
                f.write("\nMissing required fields:\n")
                for field in missing_fields:
                    f.write(f"  - {field}\n")
            else:
                f.write("\nAll required fields present.\n")
    
    # Create all-in-one text file
    all_text_file = os.path.join(output_dir, "all_pdf_text.txt")
    with open(all_text_file, "w", encoding="utf-8") as f:
        f.write("ALL PDF TEXT\n")
        f.write("===========\n\n")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(sample_dir, pdf_file)
            raw_text = extract_text_from_pdf(pdf_path)
            
            f.write(f"\n{'-' * 80}\n")
            f.write(f"File: {pdf_file}\n")
            f.write(f"{'-' * 80}\n\n")
            f.write(raw_text)
            f.write("\n\n")
    
    print(f"\nExtraction complete. Results saved to {output_dir} directory.")
    print(f"Summary file: {summary_file}")
    print(f"All text file: {all_text_file}")

if __name__ == "__main__":
    main()
