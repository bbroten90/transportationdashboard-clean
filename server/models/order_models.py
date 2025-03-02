from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    """Enum for order status"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderPriority(str, Enum):
    """Enum for order priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Order(BaseModel):
    """Model for a transportation order"""
    id: str
    customer_id: str
    customer_name: str
    ship_from: str
    ship_to: str
    pickup_date: datetime
    delivery_date: Optional[datetime] = Field(default=None)
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    priority: OrderPriority = Field(default=OrderPriority.MEDIUM)
    weight_kg: float
    volume_m3: Optional[float] = Field(default=None)
    special_requirements: Dict[str, bool] = Field(default_factory=dict)
    notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Truck(BaseModel):
    """Model for a truck"""
    id: str
    name: str
    driver: str
    current_hours: float
    max_hours: float
    warehouse: str

class Trailer(BaseModel):
    """Model for a trailer"""
    id: str
    name: str
    max_weight_kg: float
    has_pallet_jack: bool
    current_weight_kg: float = Field(default=0.0)
    warehouse: str

class OrderAssignment(BaseModel):
    """Model for an order assignment"""
    order_id: str
    truck_id: str
    trailer_id: str
    sequence: int
    assigned_by: str
    assigned_at: datetime = Field(default_factory=datetime.utcnow)

class OrderUpdateRequest(BaseModel):
    """Model for an order update request"""
    status: Optional[OrderStatus] = Field(default=None)
    priority: Optional[OrderPriority] = Field(default=None)
    delivery_date: Optional[datetime] = Field(default=None)
    notes: Optional[str] = Field(default=None)

class OrderFilterRequest(BaseModel):
    """Model for filtering orders"""
    status: Optional[List[OrderStatus]] = Field(default=None)
    priority: Optional[List[OrderPriority]] = Field(default=None)
    customer_id: Optional[str] = Field(default=None)
    from_date: Optional[datetime] = Field(default=None)
    to_date: Optional[datetime] = Field(default=None)
    ship_from: Optional[str] = Field(default=None)
    ship_to: Optional[str] = Field(default=None)
