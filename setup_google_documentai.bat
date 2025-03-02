@echo off
REM Setup Google Document AI Integration
REM This script installs the required dependencies and sets up the environment variables

echo Setting up Google Document AI Integration...

REM Install required Python packages
echo Installing required Python packages...
pip install -r requirements.txt

REM Check if credentials file exists
set CREDENTIALS_FILE=C:\Users\Brent\Documents\Cline\MCP\google-cloud-mcp\credentials.json
if not exist "%CREDENTIALS_FILE%" (
    echo.
    echo WARNING: Credentials file not found at %CREDENTIALS_FILE%
    echo Please make sure to create a service account key file and save it to this location.
    echo You can follow the instructions in GOOGLE_CLOUD_INTEGRATION.md to set up a service account.
    echo.
)

REM Check if processor ID is set
set PROCESSOR_ID_PLACEHOLDER=your-processor-id
for /f "tokens=1,* delims==" %%a in ('type .env ^| findstr /C:"DOCUMENT_AI_PROCESSOR_ID"') do (
    set PROCESSOR_ID=%%b
)

if "%PROCESSOR_ID%"=="%PROCESSOR_ID_PLACEHOLDER%" (
    echo.
    echo WARNING: Document AI processor ID is not set in .env file
    echo Please update the DOCUMENT_AI_PROCESSOR_ID value in the .env file with your processor ID.
    echo You can follow the instructions in GOOGLE_CLOUD_INTEGRATION.md to create a processor.
    echo.
)

REM Run the test script
echo.
echo Setup complete. Running test script...
python test_google_documentai.py

echo.
echo Setup and test complete.
echo If the test was successful, you can now use the Google Document AI integration.
echo If the test failed, please check the error messages and make sure the credentials and processor ID are set correctly.
