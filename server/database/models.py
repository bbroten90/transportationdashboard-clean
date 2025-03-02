from sqlalchemy import Column, String, Float, DateTime, JSON, Boolean, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class OrderModel(Base):
    """SQLAlchemy model for orders"""
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    customer_name = Column(String)
    ship_from = Column(String, index=True)
    ship_to = Column(String, index=True)
    pickup_date = Column(DateTime, index=True)
    delivery_date = Column(DateTime, nullable=True)  # Make sure this column is created
    status = Column(String, index=True)
    priority = Column(String, index=True)
    weight_kg = Column(Float)
    volume_m3 = Column(Float, nullable=True)  # Make sure this column is created
    special_requirements = Column(JSON, default={})
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignments = relationship("OrderAssignmentModel", back_populates="order")

class TruckModel(Base):
    """SQLAlchemy model for trucks"""
    __tablename__ = "trucks"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    driver = Column(String)
    current_hours = Column(Float)
    max_hours = Column(Float)
    warehouse = Column(String, index=True)
    
    # Relationships
    assignments = relationship("OrderAssignmentModel", back_populates="truck")

class TrailerModel(Base):
    """SQLAlchemy model for trailers"""
    __tablename__ = "trailers"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    max_weight_kg = Column(Float)
    has_pallet_jack = Column(Boolean, default=False)
    current_weight_kg = Column(Float, default=0.0)
    warehouse = Column(String, index=True)
    
    # Relationships
    assignments = relationship("OrderAssignmentModel", back_populates="trailer")

class OrderAssignmentModel(Base):
    """SQLAlchemy model for order assignments"""
    __tablename__ = "order_assignments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, ForeignKey("orders.id"), index=True)
    truck_id = Column(String, ForeignKey("trucks.id"), index=True)
    trailer_id = Column(String, ForeignKey("trailers.id"), index=True)
    sequence = Column(Integer)
    assigned_by = Column(String)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("OrderModel", back_populates="assignments")
    truck = relationship("TruckModel", back_populates="assignments")
    trailer = relationship("TrailerModel", back_populates="assignments")
