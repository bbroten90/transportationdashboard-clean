#!/bin/bash
# Setup Google Document AI Integration
# This script installs the required dependencies and sets up the environment variables

echo "Setting up Google Document AI Integration..."

# Install required Python packages
echo "Installing required Python packages..."
pip install -r requirements.txt

# Check if credentials file exists
CREDENTIALS_FILE="$HOME/Documents/Cline/MCP/google-cloud-mcp/credentials.json"
if [ ! -f "$CREDENTIALS_FILE" ]; then
    echo
    echo "WARNING: Credentials file not found at $CREDENTIALS_FILE"
    echo "Please make sure to create a service account key file and save it to this location."
    echo "You can follow the instructions in GOOGLE_CLOUD_INTEGRATION.md to set up a service account."
    echo
fi

# Check if processor ID is set
PROCESSOR_ID_PLACEHOLDER="your-processor-id"
PROCESSOR_ID=$(grep "DOCUMENT_AI_PROCESSOR_ID" .env | cut -d '=' -f2)

if [ "$PROCESSOR_ID" = "$PROCESSOR_ID_PLACEHOLDER" ]; then
    echo
    echo "WARNING: Document AI processor ID is not set in .env file"
    echo "Please update the DOCUMENT_AI_PROCESSOR_ID value in the .env file with your processor ID."
    echo "You can follow the instructions in GOOGLE_CLOUD_INTEGRATION.md to create a processor."
    echo
fi

# Run the test script
echo
echo "Setup complete. Running test script..."
python test_google_documentai.py

echo
echo "Setup and test complete."
echo "If the test was successful, you can now use the Google Document AI integration."
echo "If the test failed, please check the error messages and make sure the credentials and processor ID are set correctly."
