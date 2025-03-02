from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.rate_models import RateRequest, RateResponse, BulkRateRequest, BulkRateResponse
from ..services.rate_service import RateService

router = APIRouter(prefix="/rates", tags=["rates"])
rate_service = RateService()

@router.get("/manufacturers")
def get_manufacturers():
    """Get list of available manufacturers"""
    return {"manufacturers": rate_service.get_available_manufacturers()}

@router.get("/warehouses")
def get_warehouses(manufacturer: str):
    """Get list of warehouses for a manufacturer"""
    warehouses = rate_service.get_warehouses(manufacturer)
    if not warehouses:
        raise HTTPException(status_code=404, detail="Manufacturer not found.")
    return {"warehouses": warehouses}

@router.get("/destinations")
def get_destinations(manufacturer: str, warehouse: str):
    """Get list of destinations for a manufacturer and warehouse"""
    destinations = rate_service.get_destinations(manufacturer, warehouse)
    if not destinations:
        raise HTTPException(status_code=404, detail="Warehouse data not found.")
    return {"destinations": destinations}

@router.post("/calculate", response_model=RateResponse)
async def calculate_freight_rate(request: RateRequest):
    """Calculate rate for a single route"""
    rate = rate_service.calculate_rate(request)
    if rate == 0.0:
        raise HTTPException(status_code=404, detail="Rate data not found.")
    return RateResponse(rate=rate)

@router.post("/bulk-calculate", response_model=BulkRateResponse)
async def calculate_bulk_rates(request: BulkRateRequest):
    """Calculate rates for multiple routes"""
    rates = []
    for req in request.requests:
        try:
            rate = rate_service.calculate_rate(req)
            rates.append(rate)
        except Exception:
            # Skip routes with errors
            rates.append(0.0)
    
    return BulkRateResponse(rates=rates)

@router.get("/rate")
def get_cached_rate(manufacturer: str, warehouse: str, destination: str, weight: float):
    """Get cached rate if available"""
    rate = rate_service.get_cached_rate(manufacturer, warehouse, destination, weight)
    if rate is None:
        raise HTTPException(status_code=404, detail="Rate not found in cache.")
    return {"rate": rate}

# Legacy endpoints for compatibility with optimization engine
@router.get("/distance")
async def calculate_distance(origin: str, destination: str):
    """Calculate distance between two locations"""
    distance = rate_service._calculate_distance(origin, destination)
    if distance == float("inf"):
        raise HTTPException(status_code=404, detail="Location coordinates not found")
    return {"distance_km": distance}

@router.get("/coordinates")
def get_location_coordinates(location: str):
    """Get coordinates for a location"""
    coords = rate_service._get_location_coordinates(location)
    if not coords:
        raise HTTPException(status_code=404, detail="Location coordinates not found")
    return {"lat": coords[0], "lon": coords[1]}
