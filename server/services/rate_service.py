import os
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from collections import OrderedDict
from pathlib import Path
from ..models.rate_models import RateRequest, RateResponse, LocationCoordinates

class RateService:
    def __init__(self):
        # Directory where Excel rate sheets are stored
        self.rate_sheets_dir = "./rate_sheets/"
        
        # In-memory cache for fast retrieval (storing recent calculations)
        self.cache = OrderedDict()
        self.cache_size = 100  # Store last 100 calculations
        
        # Cache for distance calculations
        self.distance_cache = {}
        
        # Cache for coordinates
        self.coordinates_cache = {}
        
        # Default coordinates for major cities (fallback if not found in rate sheets)
        self.default_coordinates = {
            "Winnipeg": (49.8951, -97.1384),
            "Calgary": (51.0447, -114.0719),
            "Edmonton": (53.5461, -113.4938),
            "Vancouver": (49.2827, -123.1207),
            "Toronto": (43.6532, -79.3832),
            "Montreal": (45.5017, -73.5673),
            "Regina": (50.4452, -104.6189)
        }

    def get_rates(self, manufacturer: str, warehouse: str) -> Optional[pd.DataFrame]:
        """
        Loads the latest rate sheet for the given manufacturer and warehouse dynamically from the Excel files.
        """
        file_path = os.path.join(self.rate_sheets_dir, f"{manufacturer}.xlsx")
        if not os.path.exists(file_path):
            return None
        
        try:
            df = pd.read_excel(file_path, sheet_name=warehouse)
            df = df.dropna(how="all").dropna(axis=1, how="all")  # Clean empty rows and columns
            return df
        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")
            return None

    def get_available_manufacturers(self) -> List[str]:
        """Get list of available manufacturers based on Excel files"""
        return [f.replace(".xlsx", "") for f in os.listdir(self.rate_sheets_dir) if f.endswith(".xlsx")]

    def get_warehouses(self, manufacturer: str) -> List[str]:
        """Get list of warehouses for a manufacturer"""
        file_path = os.path.join(self.rate_sheets_dir, f"{manufacturer}.xlsx")
        if not os.path.exists(file_path):
            return []
        
        try:
            xls = pd.ExcelFile(file_path)
            return xls.sheet_names
        except Exception as e:
            print(f"Error reading sheets: {str(e)}")
            return []

    def get_destinations(self, manufacturer: str, warehouse: str) -> List[str]:
        """Get list of destinations for a manufacturer and warehouse"""
        df = self.get_rates(manufacturer, warehouse)
        if df is None or not isinstance(df, pd.DataFrame):
            return []
        return df.iloc[:, 0].dropna().unique().tolist()  # Assume first column is 'City'

    def calculate_rate(self, request: RateRequest) -> float:
        """Calculate freight rate based on manufacturer, warehouse, destination, and weight"""
        key = (request.manufacturer, request.warehouse, request.destination, request.weight)
        
        # Check cache first
        if key in self.cache:
            return self.cache[key]
        
        df = self.get_rates(request.manufacturer, request.warehouse)
        if df is None or not isinstance(df, pd.DataFrame):
            return 0.0
        
        matching_row = df[df.iloc[:, 0].str.lower() == request.destination.lower()]  # First column assumed as 'City'
        if matching_row.empty:
            return 0.0
        
        min_rate = matching_row.iloc[0, 3]  # 0-1999 lbs column
        rate_brackets = matching_row.iloc[0, 3:10].values  # Extract rate columns (0-1999 to 40000+ lbs)
        
        if request.weight <= 1999.99:
            rate = max(min_rate, min(request.weight / 100 * rate_brackets[0], 20 * rate_brackets[2]))
        elif request.weight <= 4999.99:
            rate = max(min_rate, min(request.weight / 100 * rate_brackets[1], 50 * rate_brackets[3]))
        elif request.weight <= 9999.99:
            rate = max(min_rate, min(request.weight / 100 * rate_brackets[2], 100 * rate_brackets[4]))
        elif request.weight <= 19999.99:
            rate = max(min_rate, min(request.weight / 100 * rate_brackets[3], 200 * rate_brackets[5]))
        else:
            rate = min(request.weight / 100 * rate_brackets[4], rate_brackets[6])
        
        final_rate = round(rate, 2)
        
        # Store in cache
        if len(self.cache) >= self.cache_size:
            self.cache.popitem(last=False)  # Remove oldest entry
        self.cache[key] = final_rate
        
        return final_rate

    def get_cached_rate(self, manufacturer: str, warehouse: str, destination: str, weight: float) -> Optional[float]:
        """Get cached rate if available"""
        key = (manufacturer, warehouse, destination, weight)
        if key in self.cache:
            return self.cache[key]
        return None

    # Methods for compatibility with optimization engine
    def _get_location_coordinates(self, location: str) -> Optional[Tuple[float, float]]:
        """Get coordinates for a location"""
        # Check cache first
        if location in self.coordinates_cache:
            return self.coordinates_cache[location]
            
        # Check default coordinates
        if location in self.default_coordinates:
            coords = self.default_coordinates[location]
            self.coordinates_cache[location] = coords
            return coords
            
        # If not found, return None
        return None

    def _calculate_distance(self, loc1: str, loc2: str) -> float:
        """Calculate distance between two locations using Haversine formula"""
        # Get coordinates
        coord1 = self._get_location_coordinates(loc1)
        coord2 = self._get_location_coordinates(loc2)
        
        if not coord1 or not coord2:
            return float("inf")
            
        # Haversine formula implementation
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        R = 6371  # Earth radius in km
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        a = np.sin(dlat/2) * np.sin(dlat/2) + np.cos(np.radians(lat1)) * \
            np.cos(np.radians(lat2)) * np.sin(dlon/2) * np.sin(dlon/2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        return R * c

    async def get_distance_matrix(self, locations: List[str]) -> np.ndarray:
        """Get distance matrix between locations (for optimization engine)"""
        if tuple(locations) in self.distance_cache:
            return self.distance_cache[tuple(locations)]
            
        # Calculate distances using Haversine formula
        matrix = np.zeros((len(locations), len(locations)))
        for i, loc1 in enumerate(locations):
            for j, loc2 in enumerate(locations):
                if i == j:
                    matrix[i][j] = 0
                else:
                    matrix[i][j] = self._calculate_distance(loc1, loc2)
                    
        self.distance_cache[tuple(locations)] = matrix
        return matrix
