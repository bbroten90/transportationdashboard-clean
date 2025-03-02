from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import os
import threading
from dotenv import load_dotenv

from server.database import engine, Base, get_db
from server.database.models import OrderModel, TruckModel, TrailerModel
from server.api import orders, rates, fleet, pdf
from server.services.samsara_service import SamsaraService
from server.services.rate_service import RateService
from server.services.google_maps_service import GoogleMapsService
from server.services.weather_service import WeatherService
from server.services.optimization_engine import OptimizationEngine
from server.services.pdf_watcher_service import PDFWatcherService

# Load environment variables
load_dotenv()
print("Loaded environment variables from .env file in main.py")

# Set GOOGLE_APPLICATION_CREDENTIALS environment variable
credentials_path = os.environ.get('GCP_CREDENTIALS_FILE', 'C:/Users/Brent/Documents/Cline/MCP/google-cloud-mcp/credentials.json')
if os.path.exists(credentials_path):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    print(f"Set GOOGLE_APPLICATION_CREDENTIALS to {credentials_path} in main.py")
else:
    print(f"Warning: Credentials file not found at {credentials_path} in main.py")

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Transportation Dashboard API",
    description="API for transportation logistics optimization and tracking",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api prefix
app.include_router(orders.router, prefix="/api")
app.include_router(rates.router, prefix="/api")
app.include_router(fleet.router, prefix="/api")
app.include_router(pdf.router, prefix="/api")

# Initialize services
samsara_service = SamsaraService()
rate_service = RateService()
google_maps_service = GoogleMapsService()
weather_service = WeatherService()
optimization_engine = OptimizationEngine()

# Initialize PDF watcher service
pdf_watcher_service = None
pdf_watcher_thread = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("Initializing Transportation Dashboard API services...")
    
    # Check API keys
    samsara_api_key = os.getenv("SAMSARA_API_KEY")
    google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    weather_api_key = os.getenv("WEATHER_API_KEY")
    
    if not samsara_api_key or samsara_api_key == "your_samsara_api_key_here":
        print("WARNING: Samsara API key not configured. Fleet tracking features will be limited.")
    else:
        print("Samsara API key configured.")
        
    if not google_maps_api_key:
        print("WARNING: Google Maps API key not configured. Route optimization will use simplified distance calculations.")
    else:
        print("Google Maps API key configured.")
        
    if not weather_api_key or weather_api_key == "placeholder_for_weather_api_key":
        print("WARNING: Weather API key not configured. Weather data will be simulated.")
    else:
        print("Weather API key configured.")
    
    # Start PDF watcher service in a separate thread
    global pdf_watcher_service, pdf_watcher_thread
    pdf_watcher_service = PDFWatcherService()
    
    def run_pdf_watcher():
        try:
            pdf_watcher_service._process_existing_files()
            print("PDF Watcher Service: Processed existing files")
        except Exception as e:
            print(f"PDF Watcher Service Error: {str(e)}")
    
    pdf_watcher_thread = threading.Thread(target=run_pdf_watcher)
    pdf_watcher_thread.daemon = True
    pdf_watcher_thread.start()
    print("PDF Watcher Service started in background")
    
    print("All services initialized successfully.")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    print("Shutting down Transportation Dashboard API services...")
    
    # Stop PDF watcher service
    global pdf_watcher_service
    if pdf_watcher_service:
        try:
            pdf_watcher_service.stop()
            print("PDF Watcher Service stopped")
        except Exception as e:
            print(f"Error stopping PDF Watcher Service: {str(e)}")
    
    # Close other services
    await samsara_service.close()
    await google_maps_service.close()
    await weather_service.close()
    
    print("All services shut down successfully.")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Transportation Dashboard API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "api_prefix": "/api"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/api/config")
async def get_config():
    """Get configuration information"""
    return {
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database_type": "SQLite" if os.getenv("DATABASE_URL", "").startswith("sqlite") else "PostgreSQL",
        "api_status": {
            "samsara_api_enabled": bool(os.getenv("SAMSARA_API_KEY")) and os.getenv("SAMSARA_API_KEY") != "your_samsara_api_key_here",
            "google_maps_api_enabled": bool(os.getenv("GOOGLE_MAPS_API_KEY")),
            "weather_api_enabled": bool(os.getenv("WEATHER_API_KEY")) and os.getenv("WEATHER_API_KEY") != "placeholder_for_weather_api_key"
        },
        "optimization_settings": {
            "max_optimization_time": int(os.getenv("MAX_OPTIMIZATION_TIME", "30")),
            "revenue_weight": float(os.getenv("REVENUE_WEIGHT", "0.5")),
            "cost_weight": float(os.getenv("COST_WEIGHT", "0.3")),
            "time_weight": float(os.getenv("TIME_WEIGHT", "0.2"))
        }
    }

if __name__ == "__main__":
    # Run the application with uvicorn when script is executed directly
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)
