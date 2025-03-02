from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.order_models import Order, OrderStatus, OrderPriority, OrderUpdateRequest, OrderFilterRequest
from ..services.optimization_engine import OptimizationEngine
from ..services.samsara_service import SamsaraService
from ..crud.order_crud import (
    create_order,
    get_order,
    get_orders,
    update_order,
    delete_order,
    filter_orders
)

router = APIRouter(prefix="/orders", tags=["orders"])
optimization_engine = OptimizationEngine()
samsara_service = SamsaraService()

@router.post("/", response_model=Order)
async def create_new_order(order: Order, db: Session = Depends(get_db)):
    """Create a new transportation order"""
    return create_order(db, order)

@router.get("/{order_id}", response_model=Order)
async def get_order_by_id(order_id: str, db: Session = Depends(get_db)):
    """Get order by ID"""
    db_order = get_order(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@router.get("/", response_model=List[Order])
async def get_all_orders(
    skip: int = 0, 
    limit: int = 100,
    status: Optional[OrderStatus] = None,
    db: Session = Depends(get_db)
):
    """Get all orders with optional filtering"""
    return get_orders(db, skip=skip, limit=limit, status=status)

@router.put("/{order_id}", response_model=Order)
async def update_order_details(
    order_id: str, 
    order_update: OrderUpdateRequest, 
    db: Session = Depends(get_db)
):
    """Update order details"""
    db_order = get_order(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    updated_order = update_order(db, order_id, order_update)
    
    # If status is updated to assigned or in_transit, update in Samsara
    if order_update.status in [OrderStatus.ASSIGNED, OrderStatus.IN_TRANSIT]:
        await samsara_service.update_order_status(order_id, order_update.status.value)
        
    return updated_order

@router.delete("/{order_id}", response_model=bool)
async def delete_order_by_id(order_id: str, db: Session = Depends(get_db)):
    """Delete an order"""
    db_order = get_order(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return delete_order(db, order_id)

@router.post("/filter", response_model=List[Order])
async def filter_orders_by_criteria(filter_request: OrderFilterRequest, db: Session = Depends(get_db)):
    """Filter orders by various criteria"""
    return filter_orders(db, filter_request)

@router.post("/{order_id}/optimize", response_model=bool)
async def optimize_order(order_id: str, db: Session = Depends(get_db)):
    """Optimize a single order assignment"""
    db_order = get_order(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Run optimization for this order
    assignments = await optimization_engine.optimize_assignments([db_order])
    
    if not assignments:
        raise HTTPException(status_code=400, detail="Could not find optimal assignment")
    
    # Assign the order in Samsara
    assignment_success = await samsara_service.assign_order(assignments[0])
    
    if assignment_success:
        # Update order status to assigned
        order_update = OrderUpdateRequest(status=OrderStatus.ASSIGNED)
        update_order(db, order_id, order_update)
        
    return assignment_success

@router.post("/batch-optimize", response_model=int)
async def optimize_pending_orders(
    priority: Optional[OrderPriority] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Optimize multiple pending orders"""
    # Get pending orders
    filter_req = OrderFilterRequest(
        status=[OrderStatus.PENDING],
        priority=[priority] if priority else None
    )
    pending_orders = filter_orders(db, filter_req)[:limit]
    
    if not pending_orders:
        return 0
    
    # Run optimization
    assignments = await optimization_engine.optimize_assignments(pending_orders)
    
    # Assign orders in Samsara and update status
    assigned_count = 0
    for assignment in assignments:
        assignment_success = await samsara_service.assign_order(assignment)
        
        if assignment_success:
            # Update order status to assigned
            order_update = OrderUpdateRequest(status=OrderStatus.ASSIGNED)
            update_order(db, assignment.order_id, order_update)
            assigned_count += 1
            
    return assigned_count

@router.get("/stats/daily", response_model=dict)
async def get_daily_order_stats(
    date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get daily order statistics"""
    target_date = date or datetime.utcnow().date()
    
    # Get orders for the day
    filter_req = OrderFilterRequest(
        from_date=datetime.combine(target_date, datetime.min.time()),
        to_date=datetime.combine(target_date, datetime.max.time())
    )
    daily_orders = filter_orders(db, filter_req)
    
    # Calculate statistics
    total_orders = len(daily_orders)
    pending_orders = sum(1 for order in daily_orders if order.status == OrderStatus.PENDING)
    assigned_orders = sum(1 for order in daily_orders if order.status == OrderStatus.ASSIGNED)
    in_transit_orders = sum(1 for order in daily_orders if order.status == OrderStatus.IN_TRANSIT)
    delivered_orders = sum(1 for order in daily_orders if order.status == OrderStatus.DELIVERED)
    cancelled_orders = sum(1 for order in daily_orders if order.status == OrderStatus.CANCELLED)
    
    # Calculate total weight
    total_weight = sum(order.weight_kg for order in daily_orders)
    
    return {
        "date": target_date.isoformat(),
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "assigned_orders": assigned_orders,
        "in_transit_orders": in_transit_orders,
        "delivered_orders": delivered_orders,
        "cancelled_orders": cancelled_orders,
        "total_weight_kg": total_weight
    }
