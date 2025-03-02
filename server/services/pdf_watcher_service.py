import os
import time
import shutil
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from server.core.pdf_processor.enhanced_pdf_extractor import EnhancedPDFExtractor
from server.models.order_models import Order, OrderStatus, OrderPriority
from server.database import SessionLocal
from server.database.models import OrderModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pdf_watcher.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PDFWatcherService")

class PDFHandler(FileSystemEventHandler):
    """Handler for PDF file events"""
    
    def __init__(self, pdf_extractor: EnhancedPDFExtractor, incoming_dir: str, processed_dir: str, error_dir: str):
        """Initialize PDF handler"""
        self.pdf_extractor = pdf_extractor
        self.incoming_dir = incoming_dir
        self.processed_dir = processed_dir
        self.error_dir = error_dir
        
    def on_created(self, event):
        """Handle file created event"""
        if not event.is_directory and event.src_path.lower().endswith(('.pdf', '.PDF')):
            logger.info(f"New PDF detected: {event.src_path}")
            self.process_pdf(event.src_path)
    
    def process_pdf(self, pdf_path: str):
        """Process a PDF file and create an order"""
        filename = os.path.basename(pdf_path)
        
        try:
            # Extract order data from PDF
            logger.info(f"Extracting data from {filename}")
            order_data = self.pdf_extractor.extract_order_data(pdf_path)
            
            # Create order in database
            if self._is_valid_order_data(order_data):
                self._create_order(order_data)
                logger.info(f"Order created successfully from {filename}")
                
                # Move PDF to processed directory
                processed_path = os.path.join(self.processed_dir, filename)
                shutil.move(pdf_path, processed_path)
                logger.info(f"Moved {filename} to processed directory")
            else:
                logger.warning(f"Invalid order data extracted from {filename}")
                
                # Move PDF to error directory
                error_path = os.path.join(self.error_dir, filename)
                shutil.move(pdf_path, error_path)
                logger.warning(f"Moved {filename} to error directory")
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            
            # Move PDF to error directory
            try:
                error_path = os.path.join(self.error_dir, filename)
                shutil.move(pdf_path, error_path)
                logger.warning(f"Moved {filename} to error directory")
            except Exception as move_error:
                logger.error(f"Error moving {filename} to error directory: {str(move_error)}")
    
    def _is_valid_order_data(self, order_data: Dict[str, Any]) -> bool:
        """Check if order data is valid"""
        # Check required fields
        required_fields = ["ship_from", "ship_to", "weight_kg"]
        for field in required_fields:
            if not order_data.get(field):
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Generate ID if not present
        if not order_data.get("id"):
            order_data["id"] = f"ORD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Set default customer info if not present
        if not order_data.get("customer_id"):
            order_data["customer_id"] = "UNKNOWN"
        
        if not order_data.get("customer_name"):
            order_data["customer_name"] = "Unknown Customer"
        
        # Set pickup date if not present
        if not order_data.get("pickup_date"):
            order_data["pickup_date"] = datetime.utcnow()
        
        # Set default values for enhanced fields if not present
        if not order_data.get("manufacturer"):
            order_data["manufacturer"] = "UNKNOWN"
        
        if not order_data.get("ship_from_location"):
            order_data["ship_from_location"] = ""
        
        if not order_data.get("ship_to_city"):
            order_data["ship_to_city"] = ""
        
        if not order_data.get("ship_to_company"):
            order_data["ship_to_company"] = ""
        
        if not order_data.get("purchase_order"):
            order_data["purchase_order"] = ""
        
        if not order_data.get("gross_weight_kg"):
            order_data["gross_weight_kg"] = 0.0
        
        if not order_data.get("gross_weight_lbs"):
            order_data["gross_weight_lbs"] = 0.0
        
        if not order_data.get("weight_lbs"):
            order_data["weight_lbs"] = 0.0
        
        if not order_data.get("net_quantity"):
            order_data["net_quantity"] = ""
        
        return True
    
    def _create_order(self, order_data: Dict[str, Any]):
        """Create order in database"""
        # Store enhanced data in notes field as JSON
        import json
        enhanced_data = {
            "manufacturer": order_data.get("manufacturer", ""),
            "ship_from_location": order_data.get("ship_from_location", ""),
            "ship_to_city": order_data.get("ship_to_city", ""),
            "ship_to_company": order_data.get("ship_to_company", ""),
            "purchase_order": order_data.get("purchase_order", ""),
            "gross_weight_kg": order_data.get("gross_weight_kg", 0.0),
            "gross_weight_lbs": order_data.get("gross_weight_lbs", 0.0),
            "weight_lbs": order_data.get("weight_lbs", 0.0),
            "net_quantity": order_data.get("net_quantity", "")
        }
        
        # Combine existing notes with enhanced data
        notes = order_data.get("notes", "")
        if notes:
            notes += "\n\n"
        notes += f"Enhanced Data: {json.dumps(enhanced_data, indent=2)}"
        
        # Create Order object
        order = Order(
            id=order_data["id"],
            customer_id=order_data["customer_id"],
            customer_name=order_data["customer_name"],
            ship_from=order_data["ship_from"],
            ship_to=order_data["ship_to"],
            pickup_date=order_data["pickup_date"],
            weight_kg=order_data["weight_kg"],
            special_requirements=order_data.get("special_requirements", {}),
            notes=notes,
            status=OrderStatus.PENDING,
            priority=OrderPriority.MEDIUM,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Create database model
        db_order = OrderModel(
            id=order.id,
            customer_id=order.customer_id,
            customer_name=order.customer_name,
            ship_from=order.ship_from,
            ship_to=order.ship_to,
            pickup_date=order.pickup_date,
            status=order.status.value,
            priority=order.priority.value,
            weight_kg=order.weight_kg,
            special_requirements=order.special_requirements,
            notes=order.notes,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
        
        # Save to database
        db = SessionLocal()
        try:
            db.add(db_order)
            db.commit()
            db.refresh(db_order)
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

class PDFWatcherService:
    """Service for watching and processing PDF files"""
    
    def __init__(self):
        """Initialize PDF watcher service"""
        # Set up directories
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.incoming_dir = os.path.join(self.base_dir, "data", "incoming_pdfs")
        self.processed_dir = os.path.join(self.base_dir, "data", "processed_pdfs")
        self.error_dir = os.path.join(self.base_dir, "data", "error_pdfs")
        
        # Create directories if they don't exist
        os.makedirs(self.incoming_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.error_dir, exist_ok=True)
        
        # Initialize PDF extractor
        self.pdf_extractor = EnhancedPDFExtractor()
        
        # Initialize observer
        self.observer = Observer()
        self.event_handler = PDFHandler(
            self.pdf_extractor,
            self.incoming_dir,
            self.processed_dir,
            self.error_dir
        )
    
    def start(self):
        """Start watching for PDF files"""
        logger.info(f"Starting PDF watcher service")
        logger.info(f"Watching directory: {self.incoming_dir}")
        
        # Schedule observer
        self.observer.schedule(self.event_handler, self.incoming_dir, recursive=False)
        self.observer.start()
        
        # Process any existing files
        self._process_existing_files()
        
        logger.info("PDF watcher service started")
        
        try:
            # Keep the observer running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        
        self.observer.join()
    
    def stop(self):
        """Stop watching for PDF files"""
        logger.info("Stopping PDF watcher service")
        self.observer.stop()
        self.observer.join()
        logger.info("PDF watcher service stopped")
    
    def _process_existing_files(self):
        """Process any existing files in the incoming directory"""
        for filename in os.listdir(self.incoming_dir):
            if filename.lower().endswith(('.pdf', '.PDF')):
                pdf_path = os.path.join(self.incoming_dir, filename)
                logger.info(f"Processing existing file: {filename}")
                self.event_handler.process_pdf(pdf_path)
    
    async def process_batch(self, batch_size: int = 10):
        """Process a batch of PDF files"""
        logger.info(f"Processing batch of up to {batch_size} PDF files")
        
        # Get list of PDF files
        pdf_files = [f for f in os.listdir(self.incoming_dir) if f.lower().endswith(('.pdf', '.PDF'))]
        
        # Process up to batch_size files
        for i, filename in enumerate(pdf_files[:batch_size]):
            pdf_path = os.path.join(self.incoming_dir, filename)
            logger.info(f"Batch processing file {i+1}/{min(batch_size, len(pdf_files))}: {filename}")
            self.event_handler.process_pdf(pdf_path)
        
        logger.info(f"Batch processing complete. Processed {min(batch_size, len(pdf_files))} files")

# For running as a standalone script
if __name__ == "__main__":
    service = PDFWatcherService()
    service.start()
