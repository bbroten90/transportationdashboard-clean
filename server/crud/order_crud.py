from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime

from ..models.order_models import Order, OrderStatus, OrderPriority, OrderUpdateRequest, OrderFilterRequest
from ..database.models import OrderModel

def create_order(db: Session, order: Order) -> Order:
    """Create a new order in the database"""
    db_order = OrderModel(
        id=order.id,
        customer_id=order.customer_id,
        customer_name=order.customer_name,
        ship_from=order.ship_from,
        ship_to=order.ship_to,
        pickup_date=order.pickup_date,
        delivery_date=order.delivery_date,
        status=order.status.value,
        priority=order.priority.value,
        weight_kg=order.weight_kg,
        volume_m3=order.volume_m3,
        special_requirements=order.special_requirements,
        notes=order.notes,
        created_at=order.created_at,
        updated_at=order.updated_at
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    return _map_to_order(db_order)

def get_order(db: Session, order_id: str) -> Optional[Order]:
    """Get an order by ID"""
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    
    if db_order is None:
        return None
        
    return _map_to_order(db_order)

def get_orders(db: Session, skip: int = 0, limit: int = 100, status: Optional[OrderStatus] = None) -> List[Order]:
    """Get all orders with optional status filter"""
    query = db.query(OrderModel)
    
    if status:
        query = query.filter(OrderModel.status == status.value)
        
    db_orders = query.offset(skip).limit(limit).all()
    
    return [_map_to_order(db_order) for db_order in db_orders]

def update_order(db: Session, order_id: str, order_update: OrderUpdateRequest) -> Order:
    """Update an order"""
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    
    if db_order is None:
        return None
    
    # Update fields if provided
    if order_update.status is not None:
        db_order.status = order_update.status.value
    
    if order_update.priority is not None:
        db_order.priority = order_update.priority.value
    
    if order_update.delivery_date is not None:
        db_order.delivery_date = order_update.delivery_date
    
    if order_update.notes is not None:
        db_order.notes = order_update.notes
    
    # Update timestamp
    db_order.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_order)
    
    return _map_to_order(db_order)

def delete_order(db: Session, order_id: str) -> bool:
    """Delete an order"""
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    
    if db_order is None:
        return False
    
    db.delete(db_order)
    db.commit()
    
    return True

def filter_orders(db: Session, filter_request: OrderFilterRequest) -> List[Order]:
    """Filter orders by various criteria"""
    query = db.query(OrderModel)
    
    # Apply status filter
    if filter_request.status:
        status_values = [status.value for status in filter_request.status]
        query = query.filter(OrderModel.status.in_(status_values))
    
    # Apply priority filter
    if filter_request.priority:
        priority_values = [priority.value for priority in filter_request.priority]
        query = query.filter(OrderModel.priority.in_(priority_values))
    
    # Apply customer filter
    if filter_request.customer_id:
        query = query.filter(OrderModel.customer_id == filter_request.customer_id)
    
    # Apply date range filter
    if filter_request.from_date:
        query = query.filter(OrderModel.pickup_date >= filter_request.from_date)
    
    if filter_request.to_date:
        query = query.filter(OrderModel.pickup_date <= filter_request.to_date)
    
    # Apply location filters
    if filter_request.ship_from:
        query = query.filter(OrderModel.ship_from == filter_request.ship_from)
    
    if filter_request.ship_to:
        query = query.filter(OrderModel.ship_to == filter_request.ship_to)
    
    db_orders = query.all()
    
    return [_map_to_order(db_order) for db_order in db_orders]

def _map_to_order(db_order: OrderModel) -> Order:
    """Map database model to Pydantic model"""
    return Order(
        id=db_order.id,
        customer_id=db_order.customer_id,
        customer_name=db_order.customer_name,
        ship_from=db_order.ship_from,
        ship_to=db_order.ship_to,
        pickup_date=db_order.pickup_date,
        delivery_date=db_order.delivery_date,
        status=OrderStatus(db_order.status),
        priority=OrderPriority(db_order.priority),
        weight_kg=db_order.weight_kg,
        volume_m3=db_order.volume_m3,
        special_requirements=db_order.special_requirements,
        notes=db_order.notes,
        created_at=db_order.created_at,
        updated_at=db_order.updated_at
    )
