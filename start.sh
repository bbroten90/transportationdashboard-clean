#!/bin/bash

# Start the backend server
echo "Starting backend server..."
cd server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 2
echo "Backend server started on http://localhost:8000"

# Start the frontend server
echo "Starting frontend server..."
cd ../client
npm start &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 2
echo "Frontend server started on http://localhost:3000"

# Function to handle script termination
function cleanup {
  echo "Stopping servers..."
  kill $BACKEND_PID
  kill $FRONTEND_PID
  exit
}

# Trap SIGINT (Ctrl+C) and call cleanup
trap cleanup SIGINT

# Keep script running
echo "Press Ctrl+C to stop both servers"
wait
