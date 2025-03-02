#!/bin/bash
echo "Creating database tables..."
python server/database/create_tables.py
echo ""
echo "If the database tables were created successfully, you can now start the application."
echo ""
read -p "Press Enter to continue..."
