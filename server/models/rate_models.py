from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from collections import OrderedDict

# Models for Excel-based rate calculator
class RateRequest(BaseModel):
    """Model for a rate request"""
    manufacturer: str
    warehouse: str
    destination: str
    weight: float
    special_requirements: Optional[List[str]] = Field(default=None)

class RateResponse(BaseModel):
    """Model for a rate response"""
    rate: float

class BulkRateRequest(BaseModel):
    """Model for a bulk rate request"""
    requests: List[RateRequest]

class BulkRateResponse(BaseModel):
    """Model for a bulk rate response"""
    rates: List[float]

# Legacy models for compatibility with optimization engine
class LocationCoordinates(BaseModel):
    """Model for location coordinates"""
    lat: float
    lon: float

class DistanceMatrix(BaseModel):
    """Model for distance matrix"""
    locations: List[str]
    matrix: List[List[float]]
