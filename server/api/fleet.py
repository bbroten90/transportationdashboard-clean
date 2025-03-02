from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from datetime import datetime

from ..services.samsara_service import SamsaraService
from ..models.order_models import Truck, Trailer

router = APIRouter(prefix="/fleet", tags=["fleet"])
samsara_service = SamsaraService()

@router.get("/locations", response_model=List[dict])
async def get_fleet_locations():
    """Get real-time locations of all vehicles"""
    try:
        locations = await samsara_service.get_fleet_locations()
        return locations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get fleet locations: {str(e)}")

@router.get("/vehicles/{vehicle_id}/stats", response_model=dict)
async def get_vehicle_stats(vehicle_id: str):
    """Get detailed stats for a specific vehicle"""
    try:
        stats = await samsara_service.get_vehicle_stats(vehicle_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get vehicle stats: {str(e)}")

@router.get("/trucks/available", response_model=List[Truck])
async def get_available_trucks():
    """Get list of available trucks"""
    try:
        trucks = await samsara_service.get_available_trucks()
        return trucks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available trucks: {str(e)}")

@router.get("/trailers/available", response_model=List[Trailer])
async def get_available_trailers():
    """Get list of available trailers"""
    try:
        trailers = await samsara_service.get_available_trailers()
        return trailers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available trailers: {str(e)}")

@router.get("/status/{order_id}", response_model=Optional[str])
async def get_order_status(order_id: str):
    """Get current status of an order in Samsara"""
    try:
        status = await samsara_service.get_order_status(order_id)
        if not status:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found in Samsara")
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get order status: {str(e)}")

@router.get("/utilization", response_model=Dict[str, float])
async def get_fleet_utilization():
    """Get fleet utilization metrics"""
    try:
        # Get all trucks
        trucks = await samsara_service.get_available_trucks()
        
        # Calculate utilization metrics
        total_trucks = len(trucks)
        if total_trucks == 0:
            return {
                "truck_utilization_percent": 0,
                "driver_hours_utilization_percent": 0,
                "average_driver_hours": 0
            }
            
        # Calculate truck utilization (available vs. total)
        truck_utilization = (total_trucks - len(trucks)) / total_trucks * 100
        
        # Calculate driver hours utilization
        total_hours = sum(truck.current_hours for truck in trucks)
        max_hours = sum(truck.max_hours for truck in trucks)
        driver_hours_utilization = (total_hours / max_hours * 100) if max_hours > 0 else 0
        
        # Calculate average driver hours
        average_driver_hours = total_hours / total_trucks if total_trucks > 0 else 0
        
        return {
            "truck_utilization_percent": truck_utilization,
            "driver_hours_utilization_percent": driver_hours_utilization,
            "average_driver_hours": average_driver_hours
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate fleet utilization: {str(e)}")

@router.get("/warehouses", response_model=List[str])
async def get_warehouse_locations():
    """Get list of warehouse locations"""
    try:
        # Get all trucks and trailers
        trucks = await samsara_service.get_available_trucks()
        trailers = await samsara_service.get_available_trailers()
        
        # Extract unique warehouse locations
        warehouses = set()
        for truck in trucks:
            warehouses.add(truck.warehouse)
        for trailer in trailers:
            warehouses.add(trailer.warehouse)
            
        return sorted(list(warehouses))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get warehouse locations: {str(e)}")
