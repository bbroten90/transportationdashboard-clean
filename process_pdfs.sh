#!/bin/bash
echo "Processing PDF files..."
cd "$(dirname "$0")"
python server/process_pdfs.py
echo "PDF processing complete."
