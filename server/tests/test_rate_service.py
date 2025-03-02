import pytest
import os
import pandas as pd
from unittest.mock import patch, MagicMock
from server.services.rate_service import RateService
from server.models.rate_models import RateRequest

# Mock Excel data
mock_excel_data = pd.DataFrame({
    'City': ['Winnipeg', 'Calgary', 'Edmonton'],
    'Province': ['MB', 'AB', 'AB'],
    '0-1999 lbs': [10.0, 15.0, 12.0],
    '2000-4999 lbs': [8.0, 12.0, 10.0],
    '5000-9999 lbs': [6.0, 10.0, 8.0],
    '10000-19999 lbs': [5.0, 8.0, 6.0],
    '20000-39999 lbs': [4.0, 6.0, 5.0],
    '40000+ lbs': [3.0, 5.0, 4.0],
    'Min Charge': [100.0, 150.0, 120.0]
})

class TestRateService:
    @pytest.fixture
    def rate_service(self):
        service = RateService()
        # Override rate_sheets_dir to use test directory
        service.rate_sheets_dir = "./rate_sheets/"
        return service
    
    @patch('pandas.read_excel')
    def test_get_rates(self, mock_read_excel, rate_service):
        # Setup mock
        mock_read_excel.return_value = mock_excel_data
        
        # Test
        df = rate_service.get_rates('IPCO', 'Winnipeg')
        
        # Verify
        assert df is not None
        assert len(df) == 3
        assert 'City' in df.columns
        assert '0-1999 lbs' in df.columns
    
    @patch('os.listdir')
    def test_get_available_manufacturers(self, mock_listdir, rate_service):
        # Setup mock
        mock_listdir.return_value = ['IPCO.xlsx', 'Cargill.xlsx', 'BASF.xlsx']
        
        # Test
        manufacturers = rate_service.get_available_manufacturers()
        
        # Verify
        assert len(manufacturers) == 3
        assert 'IPCO' in manufacturers
        assert 'Cargill' in manufacturers
        assert 'BASF' in manufacturers
    
    @patch('pandas.ExcelFile')
    def test_get_warehouses(self, mock_excel_file, rate_service):
        # Setup mock
        mock_excel = MagicMock()
        mock_excel.sheet_names = ['Winnipeg', 'Calgary', 'Edmonton']
        mock_excel_file.return_value = mock_excel
        
        # Test
        warehouses = rate_service.get_warehouses('IPCO')
        
        # Verify
        assert len(warehouses) == 3
        assert 'Winnipeg' in warehouses
        assert 'Calgary' in warehouses
        assert 'Edmonton' in warehouses
    
    @patch('pandas.read_excel')
    def test_get_destinations(self, mock_read_excel, rate_service):
        # Setup mock
        mock_read_excel.return_value = mock_excel_data
        
        # Test
        destinations = rate_service.get_destinations('IPCO', 'Winnipeg')
        
        # Verify
        assert len(destinations) == 3
        assert 'Winnipeg' in destinations
        assert 'Calgary' in destinations
        assert 'Edmonton' in destinations
    
    @patch('pandas.read_excel')
    def test_calculate_rate(self, mock_read_excel, rate_service):
        # Setup mock
        mock_read_excel.return_value = mock_excel_data
        
        # Test different weight brackets
        # 0-1999 lbs
        request = RateRequest(manufacturer='IPCO', warehouse='Winnipeg', destination='Calgary', weight=1000)
        rate = rate_service.calculate_rate(request)
        assert rate == 150.0  # Min charge
        
        # 2000-4999 lbs
        request = RateRequest(manufacturer='IPCO', warehouse='Winnipeg', destination='Calgary', weight=3000)
        rate = rate_service.calculate_rate(request)
        assert rate == 360.0  # 3000/100 * 12.0
        
        # 5000-9999 lbs
        request = RateRequest(manufacturer='IPCO', warehouse='Winnipeg', destination='Calgary', weight=8000)
        rate = rate_service.calculate_rate(request)
        assert rate == 800.0  # 8000/100 * 10.0
        
        # 10000-19999 lbs
        request = RateRequest(manufacturer='IPCO', warehouse='Winnipeg', destination='Calgary', weight=15000)
        rate = rate_service.calculate_rate(request)
        assert rate == 1200.0  # 15000/100 * 8.0
        
        # 20000+ lbs
        request = RateRequest(manufacturer='IPCO', warehouse='Winnipeg', destination='Calgary', weight=25000)
        rate = rate_service.calculate_rate(request)
        assert rate == 1500.0  # 25000/100 * 6.0
    
    def test_get_location_coordinates(self, rate_service):
        # Test with known location
        coords = rate_service._get_location_coordinates('Winnipeg')
        assert coords is not None
        assert coords[0] == 49.8951
        assert coords[1] == -97.1384
        
        # Test with unknown location
        coords = rate_service._get_location_coordinates('Unknown')
        assert coords is None
    
    def test_calculate_distance(self, rate_service):
        # Test with known locations
        distance = rate_service._calculate_distance('Winnipeg', 'Calgary')
        assert distance > 0
        assert distance < 1500  # Reasonable distance in km
        
        # Test with unknown location
        distance = rate_service._calculate_distance('Winnipeg', 'Unknown')
        assert distance == float('inf')
    
    @pytest.mark.asyncio
    async def test_get_distance_matrix(self, rate_service):
        # Test with known locations
        locations = ['Winnipeg', 'Calgary', 'Edmonton']
        matrix = await rate_service.get_distance_matrix(locations)
        
        # Verify matrix dimensions
        assert matrix.shape == (3, 3)
        
        # Verify diagonal is zero
        assert matrix[0, 0] == 0
        assert matrix[1, 1] == 0
        assert matrix[2, 2] == 0
        
        # Verify distances are reasonable
        assert matrix[0, 1] > 0  # Winnipeg to Calgary
        assert matrix[0, 2] > 0  # Winnipeg to Edmonton
        assert matrix[1, 2] > 0  # Calgary to Edmonton
