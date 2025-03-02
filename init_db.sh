#!/bin/bash
echo "Initializing database..."
cd "$(dirname "$0")"
python server/database/init_db.py
echo ""
echo "If the database initialization was successful, you can now start the application."
echo ""
read -p "Press Enter to continue..."
