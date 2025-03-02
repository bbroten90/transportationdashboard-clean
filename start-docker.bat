@echo off
REM Start Docker Compose for Transportation Dashboard
REM This script helps to start the application locally using Docker Compose on Windows

echo ==================================================
echo   Transportation Dashboard - Docker Startup Tool  
echo ==================================================
echo.

REM Check if Docker is installed
where docker >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Docker is not installed or not in PATH
    echo Please install Docker first: https://docs.docker.com/get-docker/
    exit /b 1
)

REM Check if Docker Compose is installed
where docker-compose >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Docker Compose is not installed or not in PATH
    echo Please install Docker Compose first: https://docs.docker.com/compose/install/
    exit /b 1
)

REM Check if Docker daemon is running
docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Docker daemon is not running
    echo Please start Docker Desktop and try again
    exit /b 1
)

REM Check if docker-compose.yml exists
if not exist "docker-compose.yml" (
    echo Error: docker-compose.yml not found in current directory
    echo Please run this script from the project root directory
    exit /b 1
)

REM Check if .env file exists, create if not
if not exist ".env" (
    echo Warning: .env file not found, creating a default one
    (
        echo # Environment configuration
        echo ENVIRONMENT=development
        echo DATABASE_URL=postgresql://postgres:postgres@db:5432/transportation
        echo.
        echo # API Keys
        echo SAMSARA_API_KEY=your_samsara_api_key_here
        echo GOOGLE_MAPS_API_KEY=
        echo WEATHER_API_KEY=placeholder_for_weather_api_key
        echo.
        echo # Optimization Settings
        echo MAX_OPTIMIZATION_TIME=30
        echo REVENUE_WEIGHT=0.5
        echo COST_WEIGHT=0.3
        echo TIME_WEIGHT=0.2
    ) > .env
    echo Created default .env file. Please edit it with your API keys if needed.
)

REM Check if containers are already running
docker-compose ps --services --filter "status=running" > running_services.tmp
set /p RUNNING=<running_services.tmp
del running_services.tmp

if not "%RUNNING%"=="" (
    echo The following services are already running:
    echo %RUNNING%
    set /p RESTART="Do you want to stop and restart them? (y/n): "
    if /i "%RESTART%"=="y" (
        echo Stopping running containers...
        docker-compose down
    ) else (
        echo Exiting without changes.
        exit /b 0
    )
)

REM Build and start containers
echo Building and starting containers...
docker-compose up -d --build

if %ERRORLEVEL% equ 0 (
    echo.
    echo Containers started successfully!
    echo.
    echo Frontend: http://localhost
    echo Backend API: http://localhost:8000
    echo API Documentation: http://localhost:8000/docs
    echo.
    echo To view logs:
    echo   docker-compose logs -f
    echo.
    echo To stop the application:
    echo   docker-compose down
    echo.
) else (
    echo Error: Failed to start containers
    echo Check the logs for more information:
    echo   docker-compose logs
    exit /b 1
)

REM Initialize the database
echo Waiting for database to be ready...
timeout /t 5 /nobreak >nul

echo Initializing database...
docker-compose exec backend python -m server.database.init_db

if %ERRORLEVEL% equ 0 (
    echo Database initialized successfully!
) else (
    echo Warning: Failed to initialize database
    echo You may need to initialize it manually:
    echo   docker-compose exec backend python -m server.database.init_db
)

echo ==================================================
echo   Transportation Dashboard is now running!        
echo ==================================================
