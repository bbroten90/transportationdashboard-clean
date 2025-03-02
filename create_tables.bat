@echo off
echo Creating database tables...
cd /d %~dp0
python server/database/create_tables.py
echo.
echo If the database tables were created successfully, you can now start the application.
echo.
pause
