#!/bin/bash

# Start Docker Compose for Transportation Dashboard
# This script helps to start the application locally using Docker Compose

# Display banner
echo "=================================================="
echo "  Transportation Dashboard - Docker Startup Tool  "
echo "=================================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed or not in PATH"
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "Error: Docker daemon is not running"
    echo "Please start Docker and try again"
    exit 1
fi

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "Error: docker-compose.yml not found in current directory"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check if .env file exists, create if not
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found, creating a default one"
    cat > .env << EOF
# Environment configuration
ENVIRONMENT=development
DATABASE_URL=postgresql://postgres:postgres@db:5432/transportation

# API Keys
SAMSARA_API_KEY=your_samsara_api_key_here
GOOGLE_MAPS_API_KEY=
WEATHER_API_KEY=placeholder_for_weather_api_key

# Optimization Settings
MAX_OPTIMIZATION_TIME=30
REVENUE_WEIGHT=0.5
COST_WEIGHT=0.3
TIME_WEIGHT=0.2
EOF
    echo "Created default .env file. Please edit it with your API keys if needed."
fi

# Function to check if containers are already running
check_running() {
    RUNNING=$(docker-compose ps --services --filter "status=running")
    if [ ! -z "$RUNNING" ]; then
        echo "The following services are already running:"
        echo "$RUNNING"
        read -p "Do you want to stop and restart them? (y/n): " RESTART
        if [[ $RESTART =~ ^[Yy]$ ]]; then
            echo "Stopping running containers..."
            docker-compose down
        else
            echo "Exiting without changes."
            exit 0
        fi
    fi
}

# Function to build and start containers
start_containers() {
    echo "Building and starting containers..."
    docker-compose up -d --build
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "Containers started successfully!"
        echo ""
        echo "Frontend: http://localhost"
        echo "Backend API: http://localhost:8000"
        echo "API Documentation: http://localhost:8000/docs"
        echo ""
        echo "To view logs:"
        echo "  docker-compose logs -f"
        echo ""
        echo "To stop the application:"
        echo "  docker-compose down"
        echo ""
    else
        echo "Error: Failed to start containers"
        echo "Check the logs for more information:"
        echo "  docker-compose logs"
        exit 1
    fi
}

# Function to initialize the database
init_database() {
    echo "Waiting for database to be ready..."
    sleep 5
    
    echo "Initializing database..."
    docker-compose exec backend python -m server.database.init_db
    
    if [ $? -eq 0 ]; then
        echo "Database initialized successfully!"
    else
        echo "Warning: Failed to initialize database"
        echo "You may need to initialize it manually:"
        echo "  docker-compose exec backend python -m server.database.init_db"
    fi
}

# Main execution
check_running
start_containers
init_database

echo "=================================================="
echo "  Transportation Dashboard is now running!        "
echo "=================================================="
