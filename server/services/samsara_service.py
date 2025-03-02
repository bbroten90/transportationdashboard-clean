import httpx
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import List, Optional
from ..models.order_models import Truck, Trailer, OrderAssignment

load_dotenv()

class SamsaraService:
    def __init__(self):
        self.api_key = os.getenv("SAMSARA_API_KEY")
        self.base_url = "https://api.samsara.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient()

    async def get_fleet_locations(self) -> List[dict]:
        """Get real-time locations of all vehicles"""
        url = f"{self.base_url}/fleet/locations"
        response = await self.client.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()["data"]

    async def get_vehicle_stats(self, vehicle_id: str) -> dict:
        """Get detailed stats for a specific vehicle"""
        url = f"{self.base_url}/fleet/vehicles/{vehicle_id}/stats"
        params = {
            "types": "gps,engineState,fuelPercents",
            "startTime": (datetime.utcnow() - timedelta(hours=24)).isoformat(),
            "endTime": datetime.utcnow().isoformat()
        }
        response = await self.client.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()["data"]

    async def get_available_trucks(self) -> List[Truck]:
        """Get list of available trucks"""
        url = f"{self.base_url}/fleet/vehicles"
        params = {
            "vehicleStatus": "available",
            "types": "truck"
        }
        response = await self.client.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        trucks = []
        for vehicle in response.json()["data"]:
            trucks.append(Truck(
                id=vehicle["id"],
                name=vehicle["name"],
                driver=vehicle["driver"]["name"],
                current_hours=vehicle["engineHours"],
                max_hours=10.0,  # Default max hours
                warehouse=vehicle["location"]["warehouse"] if "warehouse" in vehicle["location"] else "Unknown"
            ))
            
        return trucks

    async def get_available_trailers(self) -> List[Trailer]:
        """Get list of available trailers"""
        url = f"{self.base_url}/fleet/vehicles"
        params = {
            "vehicleStatus": "available",
            "types": "trailer"
        }
        response = await self.client.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        trailers = []
        for vehicle in response.json()["data"]:
            trailers.append(Trailer(
                id=vehicle["id"],
                name=vehicle["name"],
                max_weight_kg=vehicle["maxWeightKg"],
                has_pallet_jack=vehicle["hasPalletJack"],
                current_weight_kg=vehicle["currentWeightKg"],
                warehouse=vehicle["location"]["warehouse"] if "warehouse" in vehicle["location"] else "Unknown"
            ))
            
        return trailers

    async def assign_order(self, assignment: OrderAssignment) -> bool:
        """Assign an order to a truck and trailer"""
        url = f"{self.base_url}/fleet/dispatch/assignments"
        payload = {
            "orderId": assignment.order_id,
            "truckId": assignment.truck_id,
            "trailerId": assignment.trailer_id,
            "sequence": assignment.sequence,
            "assignedBy": assignment.assigned_by
        }
        response = await self.client.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.status_code == 200

    async def update_order_status(self, order_id: str, status: str) -> bool:
        """Update order status in Samsara"""
        url = f"{self.base_url}/fleet/dispatch/orders/{order_id}/status"
        payload = {
            "status": status
        }
        response = await self.client.patch(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.status_code == 200

    async def get_order_status(self, order_id: str) -> Optional[str]:
        """Get current status of an order"""
        url = f"{self.base_url}/fleet/dispatch/orders/{order_id}"
        response = await self.client.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()["data"]["status"]

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
