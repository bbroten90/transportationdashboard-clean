@echo off
echo Starting Transportation Dashboard...

REM Start the backend server
echo Starting backend server...
start cmd /k "python -m uvicorn server.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait for backend to start
timeout /t 2 /nobreak > nul
echo Backend server started on http://localhost:8000

REM Start the frontend server
echo Starting frontend server...
start cmd /k "cd client && npm start"

REM Wait for frontend to start
timeout /t 2 /nobreak > nul
echo Frontend server started on http://localhost:3000

echo.
echo Transportation Dashboard is now running.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Close the command windows to stop the servers.
