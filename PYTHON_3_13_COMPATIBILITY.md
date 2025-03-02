# Python 3.13 Compatibility

This document outlines the changes made to ensure compatibility with Python 3.13.

## Changes Made

1. **Updated requirements.txt**
   - Changed package versions to be compatible with Python 3.13
   - Used version ranges (>=) instead of pinned versions to allow for newer compatible versions

2. **Updated Pydantic Models**
   - Migrated from Pydantic v1 to Pydantic v2 syntax
   - Added `Field(default=None)` for Optional fields
   - Added `Field(default_factory=dict)` for dictionary defaults
   - Added `Field(default_factory=datetime.utcnow)` for datetime defaults

3. **Fixed Import Structure**
   - Changed relative imports (`.database`) to absolute imports (`server.database`)
   - Added `__init__.py` files to all directories to make them proper Python packages
   - Updated the start.bat script to use the correct module path

4. **Added React Frontend Files**
   - Created the missing public directory with required files (index.html, manifest.json, etc.)
   - Added placeholder favicon and logo files

5. **Added setup.bat**
   - Created a setup script to install dependencies in the correct order
   - Installs setuptools and wheel first to avoid distutils issues

## Known Issues

- Some packages may still have compatibility issues with Python 3.13
- If you encounter errors, consider using Python 3.10 in a virtual environment

## Troubleshooting

If you encounter issues with Python 3.13:

1. **Missing modules errors**
   ```
   pip install setuptools wheel
   ```

2. **C extension compilation errors**
   - These may require a C compiler or specific system libraries
   - Consider using a pre-built wheel if available

3. **API compatibility issues**
   - Some packages may use deprecated APIs
   - Check for newer versions of the package

## Alternative Setup

If you continue to have issues with Python 3.13, you can use Python 3.10 in a virtual environment:

```bash
# Install Python 3.10
# Create a virtual environment
python3.10 -m venv venv

# Activate the environment
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

After installing dependencies:

```bash
# Run the application
start.bat
```

This will start both the backend and frontend servers.
