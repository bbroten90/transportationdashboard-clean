import os
import httpx
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv
import json
import asyncio

load_dotenv()

class GoogleMapsService:
    """Service for interacting with Google Maps APIs"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.base_url = "https://maps.googleapis.com/maps/api"
        self.client = httpx.AsyncClient(timeout=30.0)  # Longer timeout for route calculations
        
        # Cache for API responses to minimize API calls
        self.distance_matrix_cache = {}
        self.geocode_cache = {}
        self.route_cache = {}
        
    async def get_distance_matrix(self, origins: List[str], destinations: List[str]) -> Dict[str, Any]:
        """
        Get distance matrix between origins and destinations
        
        Args:
            origins: List of origin addresses or coordinates
            destinations: List of destination addresses or coordinates
            
        Returns:
            Distance matrix with travel times and distances
        """
        # Check cache first
        cache_key = (tuple(origins), tuple(destinations))
        if cache_key in self.distance_matrix_cache:
            return self.distance_matrix_cache[cache_key]
        
        # Prepare API request
        url = f"{self.base_url}/distancematrix/json"
        params = {
            "origins": "|".join(origins),
            "destinations": "|".join(destinations),
            "mode": "driving",
            "units": "metric",
            "key": self.api_key
        }
        
        # Make API request
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Cache the result
        self.distance_matrix_cache[cache_key] = data
        
        return data
    
    async def get_optimized_route(self, origin: str, destination: str, waypoints: List[str]) -> Dict[str, Any]:
        """
        Get optimized route using the Directions API with waypoint optimization
        
        Args:
            origin: Starting location
            destination: Final destination
            waypoints: List of waypoints to visit
            
        Returns:
            Optimized route with directions
        """
        # Check cache first
        cache_key = (origin, destination, tuple(waypoints))
        if cache_key in self.route_cache:
            return self.route_cache[cache_key]
        
        # Prepare API request
        url = f"{self.base_url}/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "waypoints": f"optimize:true|{('|').join(waypoints)}",
            "mode": "driving",
            "units": "metric",
            "key": self.api_key
        }
        
        # Make API request
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Cache the result
        self.route_cache[cache_key] = data
        
        return data
    
    async def geocode_address(self, address: str) -> Optional[Dict[str, float]]:
        """
        Geocode an address to get coordinates
        
        Args:
            address: Address to geocode
            
        Returns:
            Dictionary with lat and lng keys
        """
        # Check cache first
        if address in self.geocode_cache:
            return self.geocode_cache[address]
        
        # Prepare API request
        url = f"{self.base_url}/geocode/json"
        params = {
            "address": address,
            "key": self.api_key
        }
        
        # Make API request
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data["status"] == "OK" and data["results"]:
            location = data["results"][0]["geometry"]["location"]
            result = {"lat": location["lat"], "lng": location["lng"]}
            
            # Cache the result
            self.geocode_cache[address] = result
            
            return result
        
        return None
    
    async def get_route_matrix(self, locations: List[str]) -> Tuple[List[List[float]], List[List[float]]]:
        """
        Get distance and time matrices for a list of locations
        
        Args:
            locations: List of locations
            
        Returns:
            Tuple of (distance_matrix, time_matrix)
        """
        n = len(locations)
        distance_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        time_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        # Get distance matrix from Google Maps API
        matrix_data = await self.get_distance_matrix(locations, locations)
        
        if matrix_data["status"] == "OK":
            rows = matrix_data["rows"]
            for i in range(n):
                elements = rows[i]["elements"]
                for j in range(n):
                    element = elements[j]
                    if element["status"] == "OK":
                        # Distance in meters
                        distance_matrix[i][j] = element["distance"]["value"]
                        # Duration in seconds
                        time_matrix[i][j] = element["duration"]["value"]
        
        return distance_matrix, time_matrix
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
