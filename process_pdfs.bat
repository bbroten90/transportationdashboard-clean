@echo off
echo Processing PDF files...
cd /d %~dp0
python server/process_pdfs.py
echo PDF processing complete.
