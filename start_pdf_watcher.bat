@echo off
echo Installing required packages...
pip install watchdog pdfminer.six pytesseract Pillow

echo Starting PDF Watcher Service...
cd /d %~dp0
python server/start_pdf_watcher.py
