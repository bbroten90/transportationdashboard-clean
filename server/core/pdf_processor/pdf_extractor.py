import os
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import tempfile

class PDFExtractor:
    """Extract order information from PDF documents"""
    
    def __init__(self, tesseract_path: Optional[str] = None):
        """Initialize PDF extractor"""
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def extract_order_data(self, pdf_path: str) -> Dict[str, Any]:
        """Extract order data from PDF file"""
        # Extract text from PDF using PyMuPDF
        text = ""
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
        
        # Extract order information
        order_data = {
            "id": self._extract_order_id(text),
            "customer_id": self._extract_customer_id(text),
            "customer_name": self._extract_customer_name(text),
            "ship_from": self._extract_ship_from(text),
            "ship_to": self._extract_ship_to(text),
            "pickup_date": self._extract_pickup_date(text),
            "weight_kg": self._extract_weight(text),
            "special_requirements": self._extract_special_requirements(text),
            "notes": self._extract_notes(text)
        }
        
        return order_data
    
    def extract_from_image(self, image_path: str) -> Dict[str, Any]:
        """Extract order data from image file"""
        # Open image and extract text
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        
        # Extract order information (same as PDF)
        order_data = {
            "id": self._extract_order_id(text),
            "customer_id": self._extract_customer_id(text),
            "customer_name": self._extract_customer_name(text),
            "ship_from": self._extract_ship_from(text),
            "ship_to": self._extract_ship_to(text),
            "pickup_date": self._extract_pickup_date(text),
            "weight_kg": self._extract_weight(text),
            "special_requirements": self._extract_special_requirements(text),
            "notes": self._extract_notes(text)
        }
        
        return order_data
    
    def extract_from_bytes(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extract order data from PDF bytes"""
        # Extract text directly from bytes using PyMuPDF
        text = ""
        try:
            # Create a memory stream from the bytes
            stream = io.BytesIO(pdf_bytes)
            # Open the PDF from the memory stream
            doc = fitz.open(stream=stream, filetype="pdf")
            # Extract text from each page
            for page in doc:
                text += page.get_text()
            doc.close()
            
            # Extract order information
            order_data = {
                "id": self._extract_order_id(text),
                "customer_id": self._extract_customer_id(text),
                "customer_name": self._extract_customer_name(text),
                "ship_from": self._extract_ship_from(text),
                "ship_to": self._extract_ship_to(text),
                "pickup_date": self._extract_pickup_date(text),
                "weight_kg": self._extract_weight(text),
                "special_requirements": self._extract_special_requirements(text),
                "notes": self._extract_notes(text)
            }
            
            return order_data
        except Exception as e:
            raise Exception(f"Error extracting text from PDF bytes: {str(e)}")
    
    def _extract_order_id(self, text: str) -> str:
        """Extract order ID from text"""
        # Look for patterns like "Order #12345" or "Order ID: 12345"
        order_id_match = re.search(r'Order\s+(?:#|ID|Number|No\.?)[:\s]*([A-Z0-9-]+)', text, re.IGNORECASE)
        if order_id_match:
            return order_id_match.group(1).strip()
        return ""
    
    def _extract_customer_id(self, text: str) -> str:
        """Extract customer ID from text"""
        # Look for patterns like "Customer #12345" or "Customer ID: 12345"
        customer_id_match = re.search(r'Customer\s+(?:#|ID|Number|No\.?)[:\s]*([A-Z0-9-]+)', text, re.IGNORECASE)
        if customer_id_match:
            return customer_id_match.group(1).strip()
        return ""
    
    def _extract_customer_name(self, text: str) -> str:
        """Extract customer name from text"""
        # Look for patterns like "Customer Name: ABC Corp" or "Bill To: ABC Corp"
        customer_name_match = re.search(r'(?:Customer\s+Name|Bill\s+To)[:\s]*([A-Za-z0-9\s\.,&]+)(?:\r|\n|$)', text, re.IGNORECASE)
        if customer_name_match:
            return customer_name_match.group(1).strip()
        return ""
    
    def _extract_ship_from(self, text: str) -> str:
        """Extract ship from location from text"""
        # Look for patterns like "Ship From: Location" or "Origin: Location"
        ship_from_patterns = [
            r'(?:Ship\s+From|Origin|Pickup)[:\s]*([A-Za-z0-9\s\.,&-]+)(?:\r|\n|$)',
            r'(?:Shipper|Expediteur)[:\s]*([A-Za-z0-9\s\.,&-]+)(?:\r|\n|$)',
            r'(?:From|De)[:\s]*([A-Za-z0-9\s\.,&-]+)(?:\r|\n|$)',
            r'C/O\s+([A-Za-z0-9\s\.,&-]+)(?:\r|\n|$)'
        ]
        
        for pattern in ship_from_patterns:
            ship_from_match = re.search(pattern, text, re.IGNORECASE)
            if ship_from_match:
                return ship_from_match.group(1).strip()
        
        # Look for BASF specific pattern
        if "BASF" in text:
            basf_match = re.search(r'BASF[^,\n\r]*(?:,|\n|\r)([^,\n\r]+)', text, re.IGNORECASE)
            if basf_match:
                return f"BASF, {basf_match.group(1).strip()}"
        
        return ""
    
    def _extract_ship_to(self, text: str) -> str:
        """Extract ship to location from text"""
        # Look for patterns like "Ship To: Location" or "Destination: Location"
        ship_to_patterns = [
            r'(?:Ship\s+To|Destination|Delivery)[:\s]*([A-Za-z0-9\s\.,&-]+)(?:\r|\n|$)',
            r'(?:Consignee|Destinataire)[:\s]*([A-Za-z0-9\s\.,&-]+)(?:\r|\n|$)',
            r'(?:To|À)[:\s]*([A-Za-z0-9\s\.,&-]+)(?:\r|\n|$)',
            r'(?:Ship\s+to|Expedie\s+à)[:\s]*(?:[0-9]+\s+)?([A-Za-z0-9\s\.,&-]+)(?:\r|\n|$)'
        ]
        
        for pattern in ship_to_patterns:
            ship_to_match = re.search(pattern, text, re.IGNORECASE)
            if ship_to_match:
                return ship_to_match.group(1).strip()
        
        return ""
    
    def _extract_pickup_date(self, text: str) -> Optional[datetime]:
        """Extract pickup date from text"""
        # Look for patterns like "Pickup Date: 2023-01-01" or "Date: 01/01/2023"
        date_patterns = [
            r'(?:Pickup|Collection)\s+Date[:\s]*(\d{4}-\d{1,2}-\d{1,2})',  # YYYY-MM-DD
            r'(?:Pickup|Collection)\s+Date[:\s]*(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY or DD/MM/YYYY
            r'(?:Pickup|Collection)\s+Date[:\s]*(\d{1,2}-\d{1,2}-\d{4})',  # MM-DD-YYYY or DD-MM-YYYY
            r'(?:Pickup|Collection)\s+Date[:\s]*(\w+\s+\d{1,2},\s*\d{4})'  # Month DD, YYYY
        ]
        
        for pattern in date_patterns:
            date_match = re.search(pattern, text, re.IGNORECASE)
            if date_match:
                date_str = date_match.group(1).strip()
                try:
                    # Try different date formats
                    for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y', '%d-%m-%Y', '%B %d, %Y'):
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
                except Exception:
                    pass
        
        return None
    
    def _extract_weight(self, text: str) -> float:
        """Extract weight in kg from text"""
        # Look for patterns like "Weight: 1000 kg" or "1000 kg"
        weight_patterns = [
            r'Weight[:\s]*(\d+(?:\.\d+)?)\s*(?:kg|kilograms)',  # Weight: 1000 kg
            r'(?:Gross\s+)?Weight[:\s]*(\d+(?:\.\d+)?)\s*(?:kg|kilograms)',  # Gross Weight: 1000 kg
            r'(?:Net\s+)?Weight[:\s]*(\d+(?:\.\d+)?)\s*(?:kg|kilograms)',  # Net Weight: 1000 kg
            r'(?:Total\s+)?Weight[:\s]*(\d+(?:\.\d+)?)\s*(?:kg|kilograms)',  # Total Weight: 1000 kg
            r'(?:Poids\s+)?(?:Brut|Net|Total)[:\s]*(\d+(?:\.\d+)?)\s*(?:kg|kilograms)',  # French: Poids Brut: 1000 kg
            r'(\d+(?:\.\d+)?)\s*(?:kg|kilograms)',  # 1000 kg
            r'Weight[:\s]*(\d+(?:\.\d+)?)\s*(?:lbs|pounds)',  # Weight: 1000 lbs
            r'(?:Gross\s+)?Weight[:\s]*(\d+(?:\.\d+)?)\s*(?:lbs|pounds)',  # Gross Weight: 1000 lbs
            r'(?:Net\s+)?Weight[:\s]*(\d+(?:\.\d+)?)\s*(?:lbs|pounds)',  # Net Weight: 1000 lbs
            r'(?:Total\s+)?Weight[:\s]*(\d+(?:\.\d+)?)\s*(?:lbs|pounds)',  # Total Weight: 1000 lbs
            r'(?:Poids\s+)?(?:Brut|Net|Total)[:\s]*(\d+(?:\.\d+)?)\s*(?:lbs|pounds)',  # French: Poids Brut: 1000 lbs
            r'(\d+(?:\.\d+)?)\s*(?:lbs|pounds)'  # 1000 lbs
        ]
        
        for pattern in weight_patterns:
            weight_match = re.search(pattern, text, re.IGNORECASE)
            if weight_match:
                weight = float(weight_match.group(1).strip())
                # Convert lbs to kg if needed
                if 'lbs' in pattern or 'pounds' in pattern:
                    weight *= 0.453592  # lbs to kg conversion
                return weight
        
        # Look for weight patterns with KG suffix
        kg_match = re.search(r'(\d+(?:\.\d+)?)\s*KG', text)
        if kg_match:
            return float(kg_match.group(1).strip())
        
        return 0.0
    
    def _extract_special_requirements(self, text: str) -> Dict[str, bool]:
        """Extract special requirements from text"""
        special_requirements = {}
        
        # Check for common special requirements
        if re.search(r'refrigerated|temperature\s+controlled|cooling', text, re.IGNORECASE):
            special_requirements["requires_refrigeration"] = True
        
        if re.search(r'heated|heating|warm', text, re.IGNORECASE):
            special_requirements["requires_heating"] = True
        
        if re.search(r'fragile|handle\s+with\s+care', text, re.IGNORECASE):
            special_requirements["fragile"] = True
        
        if re.search(r'hazardous|dangerous|hazmat', text, re.IGNORECASE):
            special_requirements["hazardous_materials"] = True
        
        if re.search(r'rush|urgent|expedited|priority', text, re.IGNORECASE):
            special_requirements["rush_delivery"] = True
        
        return special_requirements
    
    def _extract_notes(self, text: str) -> Optional[str]:
        """Extract notes from text"""
        # Look for patterns like "Notes: ..." or "Comments: ..."
        notes_match = re.search(r'(?:Notes|Comments)[:\s]*(.+?)(?:\r|\n\r|\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
        if notes_match:
            return notes_match.group(1).strip()
        return None
