@echo off
echo Initializing database...
cd /d %~dp0
python server/database/init_db.py
echo.
echo If the database initialization was successful, you can now start the application.
echo.
pause
