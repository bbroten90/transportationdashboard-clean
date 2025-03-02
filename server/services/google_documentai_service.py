import os
import json
from typing import Dict, Any, Optional, List
import base64
import tempfile
from datetime import datetime
import requests

class GoogleDocumentAIService:
    """Service for interacting with Google Document AI"""
    
    def __init__(self, project_id: str = None, location: str = None, processor_id: str = None):
        """Initialize the Google Document AI service"""
        # Try to load environment variables from .env file if dotenv is available
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("Loaded environment variables from .env file")
        except ImportError:
            print("dotenv package not available, skipping .env loading")
        
        # Set parameters from arguments or environment variables
        self.project_id = project_id or os.environ.get('GCP_PROJECT_ID')
        self.location = location or os.environ.get('DOCUMENT_AI_LOCATION', 'us')
        self.processor_id = processor_id or os.environ.get('DOCUMENT_AI_PROCESSOR_ID')
        self.credentials_path = os.environ.get('GCP_CREDENTIALS_FILE')
        
        # Print debug information
        print(f"Google Document AI Service initialization:")
        print(f"  Project ID: {self.project_id}")
        print(f"  Location: {self.location}")
        print(f"  Processor ID: {self.processor_id}")
        print(f"  Credentials Path: {self.credentials_path}")
        
        # Validate required parameters
        if not self.project_id:
            raise ValueError("GCP_PROJECT_ID is required")
        if not self.processor_id:
            raise ValueError("DOCUMENT_AI_PROCESSOR_ID is required")
        
        # Set GOOGLE_APPLICATION_CREDENTIALS environment variable
        if self.credentials_path:
            if os.path.exists(self.credentials_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path
                print(f"Set GOOGLE_APPLICATION_CREDENTIALS to {self.credentials_path}")
            else:
                print(f"Warning: Credentials file not found at {self.credentials_path}")
        
        # Load credentials for REST API
        self.credentials = None
        if self.credentials_path and os.path.exists(self.credentials_path):
            try:
                with open(self.credentials_path, 'r') as f:
                    self.credentials = json.load(f)
                print("Successfully loaded credentials from file")
            except Exception as e:
                print(f"Error loading credentials: {str(e)}")
                # Don't raise here, we'll try to use the SDK which uses GOOGLE_APPLICATION_CREDENTIALS
    
    def process_document(self, content: bytes, mime_type: str = 'application/pdf') -> Dict[str, Any]:
        """Process a document using Google Document AI"""
        try:
            # If we have the google-cloud-documentai package installed, use it
            try:
                from google.cloud import documentai
                return self._process_with_sdk(content, mime_type)
            except ImportError:
                # Fall back to using the REST API
                return self._process_with_rest_api(content, mime_type)
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            raise
    
    def _process_with_sdk(self, content: bytes, mime_type: str) -> Dict[str, Any]:
        """Process a document using the Google Cloud Document AI SDK"""
        from google.cloud import documentai
        
        # Create a client
        client_options = {"api_endpoint": f"{self.location}-documentai.googleapis.com"}
        client = documentai.DocumentProcessorServiceClient(client_options=client_options)
        
        # The full resource name of the processor
        name = f"projects/{self.project_id}/locations/{self.location}/processors/{self.processor_id}"
        
        # Create the document object
        document = documentai.RawDocument(content=content, mime_type=mime_type)
        
        # Process the document
        request = documentai.ProcessRequest(name=name, raw_document=document)
        response = client.process_document(request=request)
        
        # Convert the response to a dictionary
        document = response.document
        
        # Extract entities
        entities = []
        if hasattr(document, 'entities') and document.entities:
            for entity in document.entities:
                entities.append({
                    'type': entity.type_,
                    'mention_text': entity.mention_text,
                    'confidence': entity.confidence,
                })
        
        # Extract form fields (key-value pairs)
        form_fields = []
        if hasattr(document, 'pages'):
            for page in document.pages:
                if hasattr(page, 'form_fields') and page.form_fields:
                    for field in page.form_fields:
                        # Get the field name (key)
                        key_text = ""
                        if field.field_name and field.field_name.text_anchor:
                            key_text = self._get_text_from_layout(field.field_name.text_anchor, document.text)
                        
                        # Get the field value
                        value_text = ""
                        if field.field_value and field.field_value.text_anchor:
                            value_text = self._get_text_from_layout(field.field_value.text_anchor, document.text)
                        
                        # Add to form fields
                        form_field = {
                            'key': key_text.strip(),
                            'value': value_text.strip(),
                            'page': page.page_number
                        }
                        
                        # Add confidence if available
                        if hasattr(field, 'confidence'):
                            form_field['confidence'] = field.confidence
                        
                        form_fields.append(form_field)
        
        # Extract tables
        tables = []
        if hasattr(document, 'pages'):
            for page in document.pages:
                if hasattr(page, 'tables') and page.tables:
                    for table in page.tables:
                        table_data = {
                            'page': page.page_number,
                            'rows': []
                        }
                        
                        # Add confidence if available
                        if hasattr(table, 'confidence'):
                            table_data['confidence'] = table.confidence
                        
                        # Process table rows
                        for row_idx, row in enumerate(table.body_rows):
                            row_data = []
                            for cell_idx, cell in enumerate(row.cells):
                                cell_text = ""
                                if hasattr(cell, 'text_anchor') and cell.text_anchor:
                                    cell_text = self._get_text_from_layout(cell.text_anchor, document.text)
                                
                                cell_data = {
                                    'text': cell_text.strip(),
                                    'row_span': cell.row_span,
                                    'col_span': cell.col_span
                                }
                                
                                # Add confidence if available
                                if hasattr(cell, 'confidence'):
                                    cell_data['confidence'] = cell.confidence
                                
                                row_data.append(cell_data)
                            
                            table_data['rows'].append(row_data)
                        
                        # Process header rows if available
                        if hasattr(table, 'header_rows') and table.header_rows:
                            table_data['headers'] = []
                            for row in table.header_rows:
                                header_row = []
                                for cell in row.cells:
                                    cell_text = ""
                                    if hasattr(cell, 'text_anchor') and cell.text_anchor:
                                        cell_text = self._get_text_from_layout(cell.text_anchor, document.text)
                                    
                                    cell_data = {
                                        'text': cell_text.strip(),
                                        'row_span': cell.row_span,
                                        'col_span': cell.col_span
                                    }
                                    
                                    # Add confidence if available
                                    if hasattr(cell, 'confidence'):
                                        cell_data['confidence'] = cell.confidence
                                    
                                    header_row.append(cell_data)
                                
                                table_data['headers'].append(header_row)
                        
                        tables.append(table_data)
        
        # Extract text
        text = document.text
        
        return {
            'text': text,
            'entities': entities,
            'form_fields': form_fields,
            'tables': tables,
        }
    
    def _get_text_from_layout(self, text_anchor, text: str) -> str:
        """Extract text from a text anchor"""
        result = ""
        for segment in text_anchor.text_segments:
            start_index = segment.start_index
            end_index = segment.end_index
            result += text[start_index:end_index]
        return result
    
    def _process_with_rest_api(self, content: bytes, mime_type: str) -> Dict[str, Any]:
        """Process a document using the Google Cloud Document AI REST API"""
        # Get access token
        access_token = self._get_access_token()
        
        # Encode the document content
        encoded_content = base64.b64encode(content).decode('utf-8')
        
        # Prepare the request
        url = f"https://{self.location}-documentai.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/processors/{self.processor_id}:process"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        data = {
            'rawDocument': {
                'content': encoded_content,
                'mimeType': mime_type,
            }
        }
        
        # Send the request
        response = requests.post(url, headers=headers, json=data)
        
        # Check for errors
        if response.status_code != 200:
            raise Exception(f"Error processing document: {response.text}")
        
        # Parse the response
        result = response.json()
        
        # Extract entities
        entities = []
        if 'document' in result and 'entities' in result['document']:
            for entity in result['document']['entities']:
                entities.append({
                    'type': entity.get('type', ''),
                    'mention_text': entity.get('mentionText', ''),
                    'confidence': entity.get('confidence', 0.0),
                })
        
        # Extract text
        text = result.get('document', {}).get('text', '')
        
        # Extract form fields (key-value pairs)
        form_fields = []
        if 'document' in result and 'pages' in result['document']:
            for page in result['document']['pages']:
                if 'formFields' in page:
                    for field in page['formFields']:
                        # Get the field name (key)
                        key_text = ""
                        if 'fieldName' in field and 'textAnchor' in field['fieldName']:
                            key_text = self._get_text_from_rest_text_anchor(field['fieldName']['textAnchor'], text)
                        
                        # Get the field value
                        value_text = ""
                        if 'fieldValue' in field and 'textAnchor' in field['fieldValue']:
                            value_text = self._get_text_from_rest_text_anchor(field['fieldValue']['textAnchor'], text)
                        
                        # Add to form fields
                        form_field = {
                            'key': key_text.strip(),
                            'value': value_text.strip(),
                            'page': page.get('pageNumber', 1)
                        }
                        
                        # Add confidence if available
                        if 'confidence' in field:
                            form_field['confidence'] = field.get('confidence', 0.0)
                        
                        form_fields.append(form_field)
        
        # Extract tables
        tables = []
        if 'document' in result and 'pages' in result['document']:
            for page in result['document']['pages']:
                if 'tables' in page:
                    for table in page['tables']:
                        table_data = {
                            'page': page.get('pageNumber', 1),
                            'rows': []
                        }
                        
                        # Add confidence if available
                        if 'confidence' in table:
                            table_data['confidence'] = table.get('confidence', 0.0)
                        
                        # Process table rows
                        if 'bodyRows' in table:
                            for row in table['bodyRows']:
                                row_data = []
                                if 'cells' in row:
                                    for cell in row['cells']:
                                        cell_text = ""
                                        if 'textAnchor' in cell:
                                            cell_text = self._get_text_from_rest_text_anchor(cell['textAnchor'], text)
                                        
                                        cell_data = {
                                            'text': cell_text.strip(),
                                            'row_span': cell.get('rowSpan', 1),
                                            'col_span': cell.get('colSpan', 1)
                                        }
                                        
                                        # Add confidence if available
                                        if 'confidence' in cell:
                                            cell_data['confidence'] = cell.get('confidence', 0.0)
                                        
                                        row_data.append(cell_data)
                                
                                table_data['rows'].append(row_data)
                        
                        # Process header rows if available
                        if 'headerRows' in table:
                            table_data['headers'] = []
                            for row in table['headerRows']:
                                header_row = []
                                if 'cells' in row:
                                    for cell in row['cells']:
                                        cell_text = ""
                                        if 'textAnchor' in cell:
                                            cell_text = self._get_text_from_rest_text_anchor(cell['textAnchor'], text)
                                        
                                        cell_data = {
                                            'text': cell_text.strip(),
                                            'row_span': cell.get('rowSpan', 1),
                                            'col_span': cell.get('colSpan', 1)
                                        }
                                        
                                        # Add confidence if available
                                        if 'confidence' in cell:
                                            cell_data['confidence'] = cell.get('confidence', 0.0)
                                        
                                        header_row.append(cell_data)
                                
                                table_data['headers'].append(header_row)
                        
                        tables.append(table_data)
        
        return {
            'text': text,
            'entities': entities,
            'form_fields': form_fields,
            'tables': tables,
        }
    
    def _get_text_from_rest_text_anchor(self, text_anchor: Dict[str, Any], text: str) -> str:
        """Extract text from a REST API text anchor"""
        result = ""
        if 'textSegments' in text_anchor:
            for segment in text_anchor['textSegments']:
                start_index = int(segment.get('startIndex', 0))
                end_index = int(segment.get('endIndex', 0))
                if start_index < end_index and end_index <= len(text):
                    result += text[start_index:end_index]
        return result
    
    def _get_access_token(self) -> str:
        """Get an access token for the Google Cloud API"""
        if not self.credentials:
            raise ValueError("Credentials are required for REST API access")
        
        # Use the service account credentials to get an access token
        auth_url = "https://oauth2.googleapis.com/token"
        scope = "https://www.googleapis.com/auth/cloud-platform"
        
        # Prepare the request
        payload = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'assertion': self._create_jwt(scope),
        }
        
        # Send the request
        response = requests.post(auth_url, data=payload)
        
        # Check for errors
        if response.status_code != 200:
            raise Exception(f"Error getting access token: {response.text}")
        
        # Parse the response
        result = response.json()
        
        return result.get('access_token', '')
    
    def _create_jwt(self, scope: str) -> str:
        """Create a JWT for authentication"""
        import jwt
        import time
        
        # Get the service account email and private key
        service_account_email = self.credentials.get('client_email')
        private_key = self.credentials.get('private_key')
        
        # Create the JWT
        now = int(time.time())
        payload = {
            'iss': service_account_email,
            'sub': service_account_email,
            'aud': 'https://oauth2.googleapis.com/token',
            'iat': now,
            'exp': now + 3600,  # 1 hour
            'scope': scope,
        }
        
        # Sign the JWT
        token = jwt.encode(payload, private_key, algorithm='RS256')
        
        return token
