# Transportation Dashboard

A comprehensive transportation logistics management system with route optimization, fleet tracking, and rate management. The system includes both a backend API and a React-based frontend interface.

## Features

- **Order Management**: Create, track, and manage transportation orders
- **Route Optimization**: Optimize order assignments using Google OR-Tools and Google Maps API
- **Cost/Revenue Optimization**: Maximize profitability with intelligent route planning
- **Weather-Aware Routing**: Adjust travel times based on weather conditions
- **Fleet Tracking**: Real-time tracking of trucks and trailers via Samsara API
- **Rate Management**: Compare carrier rates and calculate shipping costs
- **PDF Processing**: Extract order information from PDF documents
- **Schedule Planning**: Plan and optimize orders across multiple days to maximize revenue
- **RESTful API**: FastAPI-based backend with comprehensive documentation
- **React Frontend**: Modern UI with Material-UI components

## System Architecture

The system consists of the following components:

- **Backend API**: FastAPI application with SQLAlchemy ORM
- **Frontend**: React application with Material-UI components
- **Database**: SQLite for development, PostgreSQL for production
- **Integration Services**: 
  - Samsara API for fleet tracking
  - Google Maps API for accurate route planning and distance calculations
  - Weather API for weather-aware routing
  - Rate service for pricing calculations
  - Optimization engine for cost/revenue-optimized route planning
- **PDF Processing**: Extraction of order data from PDF documents
- **Excel-Based Rate Calculator**: Dynamic rate calculation from Excel rate sheets

## Getting Started

### Prerequisites

- Python 3.13+ (or Python 3.9+ with the compatibility notes in PYTHON_3_13_COMPATIBILITY.md)
- Node.js 14+ and npm
- Samsara API key (for fleet tracking)
- Google Maps API key (for route optimization)
- Weather API key (optional, for weather-aware routing)
- PostgreSQL (for production)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/transportation-dashboard.git
   cd transportation-dashboard
   ```

2. Install backend dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:
   ```
   cd client
   npm install
   cd ..
   ```

4. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add the following variables:
     ```
     # Environment configuration
     ENVIRONMENT=development
     DATABASE_URL=sqlite:///./transportation.db
     
     # API Keys
     SAMSARA_API_KEY=your_samsara_api_key_here
     GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
     WEATHER_API_KEY=your_weather_api_key_here
     
     # Optimization Settings
     MAX_OPTIMIZATION_TIME=30
     REVENUE_WEIGHT=0.5
     COST_WEIGHT=0.3
     TIME_WEIGHT=0.2
     ```

5. Run the start script:
   ```
   # On Linux/macOS
   chmod +x start.sh
   ./start.sh
   
   # On Windows
   start.bat
   ```

6. Access the application:
   - Frontend: Open your browser and navigate to `http://localhost:3000`
   - API documentation: Open your browser and navigate to `http://localhost:8000/docs`

## API Endpoints

The API provides the following main endpoints:

### Orders

- `GET /orders`: List all orders
- `POST /orders`: Create a new order
- `GET /orders/{order_id}`: Get order details
- `PUT /orders/{order_id}`: Update order details
- `DELETE /orders/{order_id}`: Delete an order
- `POST /orders/filter`: Filter orders by criteria
- `POST /orders/{order_id}/optimize`: Optimize a single order
- `POST /orders/batch-optimize`: Optimize multiple orders
- `GET /orders/stats/daily`: Get daily order statistics

### Rates

- `POST /rates/calculate`: Calculate rate for a route
- `POST /rates/bulk-calculate`: Calculate rates for multiple routes
- `GET /rates/carriers`: List available carriers
- `GET /rates/carriers/{carrier}`: Get carrier rates
- `GET /rates/routes`: List available routes
- `GET /rates/locations`: List available locations

### Fleet

- `GET /fleet/locations`: Get real-time fleet locations
- `GET /fleet/vehicles/{vehicle_id}/stats`: Get vehicle stats
- `GET /fleet/trucks/available`: List available trucks
- `GET /fleet/trailers/available`: List available trailers
- `GET /fleet/status/{order_id}`: Get order status
- `GET /fleet/utilization`: Get fleet utilization metrics
- `GET /fleet/warehouses`: List warehouse locations

## Development

### Project Structure

```
transportation-dashboard/
├── server/                  # Backend application
│   ├── api/                 # API endpoints
│   ├── core/                # Core functionality
│   │   └── pdf_processor/   # PDF processing
│   ├── crud/                # Database operations
│   ├── database/            # Database models and config
│   ├── models/              # Pydantic models
│   ├── services/            # Business logic services
│   └── main.py              # Application entry point
├── client/                  # Frontend application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API service modules
│   │   └── utils/           # Utility functions
│   └── package.json         # Frontend dependencies
├── rate_sheets/             # Excel rate sheets
├── .env                     # Environment variables
├── requirements.txt         # Backend dependencies
├── start.sh                 # Linux/macOS startup script
└── start.bat                # Windows startup script
```

### Running Tests

```
pytest
```

### Database Migrations

```
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Production Deployment

For production deployment:

1. Update the `.env` file with production settings:
   ```
   # Environment configuration
   ENVIRONMENT=production
   DATABASE_URL=postgresql://user:password@localhost/transportation
   
   # API Keys
   SAMSARA_API_KEY=your_samsara_api_key_here
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
   WEATHER_API_KEY=your_weather_api_key_here
   
   # Optimization Settings
   MAX_OPTIMIZATION_TIME=60  # Longer optimization time for production
   REVENUE_WEIGHT=0.5
   COST_WEIGHT=0.3
   TIME_WEIGHT=0.2
   ```

2. Run the application with multiple workers:
   ```
   uvicorn server.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

3. Consider using a process manager like Supervisor or systemd

## License

This project is licensed under the MIT License - see the LICENSE file for details.
