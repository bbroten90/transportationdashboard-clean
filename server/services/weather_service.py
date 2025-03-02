import os
import httpx
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta

load_dotenv()

class WeatherService:
    """Service for retrieving weather data for locations"""
    
    def __init__(self):
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"  # Default to OpenWeatherMap
        self.client = httpx.AsyncClient()
        
        # Cache for weather data to minimize API calls
        self.weather_cache = {}
        self.forecast_cache = {}
        self.cache_expiry = 3600  # Cache expires after 1 hour
        self.last_cache_cleanup = datetime.now()
        
    async def get_current_weather(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Get current weather for a location
        
        Args:
            location: City name or coordinates
            
        Returns:
            Weather data or None if not available
        """
        # Check if we have a valid API key
        if not self.api_key or self.api_key == "placeholder_for_weather_api_key":
            return self._get_placeholder_weather(location)
        
        # Check cache first
        current_time = datetime.now()
        cache_key = f"current_{location}"
        
        if cache_key in self.weather_cache:
            cached_data, timestamp = self.weather_cache[cache_key]
            if (current_time - timestamp).total_seconds() < self.cache_expiry:
                return cached_data
        
        # Clean up cache if needed
        if (current_time - self.last_cache_cleanup).total_seconds() > self.cache_expiry:
            self._cleanup_cache()
        
        try:
            # Prepare API request
            url = f"{self.base_url}/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric"
            }
            
            # Make API request
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Cache the result
            self.weather_cache[cache_key] = (data, current_time)
            
            return data
        except Exception as e:
            print(f"Error getting weather for {location}: {str(e)}")
            return self._get_placeholder_weather(location)
    
    async def get_forecast(self, location: str, days: int = 1) -> Optional[Dict[str, Any]]:
        """
        Get weather forecast for a location
        
        Args:
            location: City name or coordinates
            days: Number of days to forecast (1-5)
            
        Returns:
            Forecast data or None if not available
        """
        # Check if we have a valid API key
        if not self.api_key or self.api_key == "placeholder_for_weather_api_key":
            return self._get_placeholder_forecast(location, days)
        
        # Check cache first
        current_time = datetime.now()
        cache_key = f"forecast_{location}_{days}"
        
        if cache_key in self.forecast_cache:
            cached_data, timestamp = self.forecast_cache[cache_key]
            if (current_time - timestamp).total_seconds() < self.cache_expiry:
                return cached_data
        
        try:
            # Prepare API request
            url = f"{self.base_url}/forecast"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric",
                "cnt": min(days * 8, 40)  # 8 forecasts per day, max 5 days (40 timestamps)
            }
            
            # Make API request
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Cache the result
            self.forecast_cache[cache_key] = (data, current_time)
            
            return data
        except Exception as e:
            print(f"Error getting forecast for {location}: {str(e)}")
            return self._get_placeholder_forecast(location, days)
    
    def _get_placeholder_weather(self, location: str) -> Dict[str, Any]:
        """
        Get placeholder weather data when API key is not available
        
        Args:
            location: City name
            
        Returns:
            Placeholder weather data
        """
        return {
            "name": location,
            "main": {
                "temp": 20.0,  # Default temperature in Celsius
                "feels_like": 20.0,
                "humidity": 50
            },
            "weather": [
                {
                    "main": "Clear",
                    "description": "clear sky",
                    "icon": "01d"
                }
            ],
            "wind": {
                "speed": 5.0,
                "deg": 180
            },
            "clouds": {
                "all": 0
            },
            "sys": {
                "country": "CA"
            },
            "is_placeholder": True
        }
    
    def _get_placeholder_forecast(self, location: str, days: int) -> Dict[str, Any]:
        """
        Get placeholder forecast data when API key is not available
        
        Args:
            location: City name
            days: Number of days
            
        Returns:
            Placeholder forecast data
        """
        forecast_list = []
        current_time = datetime.now()
        
        for day in range(days):
            for hour in [6, 12, 18, 0]:  # 4 timestamps per day
                forecast_time = current_time + timedelta(days=day, hours=hour)
                forecast_list.append({
                    "dt": int(forecast_time.timestamp()),
                    "main": {
                        "temp": 20.0,  # Default temperature in Celsius
                        "feels_like": 20.0,
                        "humidity": 50
                    },
                    "weather": [
                        {
                            "main": "Clear",
                            "description": "clear sky",
                            "icon": "01d"
                        }
                    ],
                    "wind": {
                        "speed": 5.0,
                        "deg": 180
                    },
                    "clouds": {
                        "all": 0
                    },
                    "dt_txt": forecast_time.strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return {
            "city": {
                "name": location,
                "country": "CA"
            },
            "list": forecast_list,
            "is_placeholder": True
        }
    
    def _cleanup_cache(self):
        """Clean up expired cache entries"""
        current_time = datetime.now()
        self.last_cache_cleanup = current_time
        
        # Clean up weather cache
        for key in list(self.weather_cache.keys()):
            _, timestamp = self.weather_cache[key]
            if (current_time - timestamp).total_seconds() > self.cache_expiry:
                del self.weather_cache[key]
        
        # Clean up forecast cache
        for key in list(self.forecast_cache.keys()):
            _, timestamp = self.forecast_cache[key]
            if (current_time - timestamp).total_seconds() > self.cache_expiry:
                del self.forecast_cache[key]
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
