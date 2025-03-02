@echo off
echo Setting up Transportation Dashboard for Python 3.13...

REM Install setuptools and wheel first
echo Installing setuptools and wheel...
pip install setuptools wheel

REM Install the requirements
echo Installing requirements...
pip install -r requirements.txt

REM Install frontend dependencies
echo Installing frontend dependencies...
cd client
npm install
cd ..

echo.
echo Setup complete! You can now run the application using start.bat
echo.
