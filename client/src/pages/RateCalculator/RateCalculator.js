import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Button,
  CircularProgress,
  Alert,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  Divider,
  List,
  ListItem,
  ListItemText,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  Calculate as CalculateIcon,
  Refresh as RefreshIcon,
  Save as SaveIcon,
} from '@mui/icons-material';
import { rateService } from '../../services';

const RateCalculator = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [manufacturers, setManufacturers] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [destinations, setDestinations] = useState([]);
  const [selectedManufacturer, setSelectedManufacturer] = useState('');
  const [selectedWarehouse, setSelectedWarehouse] = useState('');
  const [selectedDestination, setSelectedDestination] = useState('');
  const [weight, setWeight] = useState(1000);
  const [calculatedRate, setCalculatedRate] = useState(null);
  const [recentCalculations, setRecentCalculations] = useState([]);
  const [bulkRateRequests, setBulkRateRequests] = useState([]);
  const [bulkRateResults, setBulkRateResults] = useState([]);
  const [calculating, setCalculating] = useState(false);

  useEffect(() => {
    fetchManufacturers();
  }, []);

  useEffect(() => {
    if (selectedManufacturer) {
      fetchWarehouses(selectedManufacturer);
    } else {
      setWarehouses([]);
      setSelectedWarehouse('');
    }
  }, [selectedManufacturer]);

  useEffect(() => {
    if (selectedManufacturer && selectedWarehouse) {
      fetchDestinations(selectedManufacturer, selectedWarehouse);
    } else {
      setDestinations([]);
      setSelectedDestination('');
    }
  }, [selectedManufacturer, selectedWarehouse]);

  const fetchManufacturers = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const manufacturerList = await rateService.getManufacturers();
      setManufacturers(manufacturerList);
      
      setLoading(false);
    } catch (err) {
      setError('Failed to load manufacturers: ' + err.message);
      setLoading(false);
    }
  };

  const fetchWarehouses = async (manufacturer) => {
    try {
      setLoading(true);
      setError(null);
      
      const warehouseList = await rateService.getWarehouses(manufacturer);
      setWarehouses(warehouseList);
      
      if (warehouseList.length > 0) {
        setSelectedWarehouse(warehouseList[0]);
      }
      
      setLoading(false);
    } catch (err) {
      setError('Failed to load warehouses: ' + err.message);
      setLoading(false);
    }
  };

  const fetchDestinations = async (manufacturer, warehouse) => {
    try {
      setLoading(true);
      setError(null);
      
      const destinationList = await rateService.getDestinations(manufacturer, warehouse);
      setDestinations(destinationList);
      
      setLoading(false);
    } catch (err) {
      setError('Failed to load destinations: ' + err.message);
      setLoading(false);
    }
  };

  const handleManufacturerChange = (event) => {
    setSelectedManufacturer(event.target.value);
  };

  const handleWarehouseChange = (event) => {
    setSelectedWarehouse(event.target.value);
  };

  const handleDestinationChange = (event) => {
    setSelectedDestination(event.target.value);
  };

  const handleWeightChange = (event) => {
    setWeight(Number(event.target.value));
  };

  const handleCalculateRate = async () => {
    if (!selectedManufacturer || !selectedWarehouse || !selectedDestination || !weight) {
      setError('Please fill in all fields');
      return;
    }
    
    try {
      setCalculating(true);
      setError(null);
      
      const request = {
        manufacturer: selectedManufacturer,
        warehouse: selectedWarehouse,
        destination: selectedDestination,
        weight: weight
      };
      
      const response = await rateService.calculateRate(request);
      setCalculatedRate(response);
      
      // Add to recent calculations
      setRecentCalculations([
        {
          ...request,
          rate: response.rate,
          timestamp: new Date()
        },
        ...recentCalculations.slice(0, 4) // Keep only the 5 most recent
      ]);
      
      setCalculating(false);
    } catch (err) {
      setError('Failed to calculate rate: ' + err.message);
      setCalculating(false);
    }
  };

  const handleAddToBulk = () => {
    if (!selectedManufacturer || !selectedWarehouse || !selectedDestination || !weight) {
      setError('Please fill in all fields');
      return;
    }
    
    const request = {
      manufacturer: selectedManufacturer,
      warehouse: selectedWarehouse,
      destination: selectedDestination,
      weight: weight
    };
    
    setBulkRateRequests([...bulkRateRequests, request]);
  };

  const handleRemoveFromBulk = (index) => {
    const newRequests = [...bulkRateRequests];
    newRequests.splice(index, 1);
    setBulkRateRequests(newRequests);
  };

  const handleCalculateBulkRates = async () => {
    if (bulkRateRequests.length === 0) {
      setError('No bulk requests to calculate');
      return;
    }
    
    try {
      setCalculating(true);
      setError(null);
      
      const response = await rateService.calculateBulkRates({ requests: bulkRateRequests });
      
      // Combine requests with results
      const results = bulkRateRequests.map((request, index) => ({
        ...request,
        rate: response.rates[index]
      }));
      
      setBulkRateResults(results);
      setCalculating(false);
    } catch (err) {
      setError('Failed to calculate bulk rates: ' + err.message);
      setCalculating(false);
    }
  };

  const formatCurrency = (amount) => {
    return `$${amount.toFixed(2)}`;
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Rate Calculator
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Calculate Rate
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <FormControl fullWidth disabled={loading}>
                  <InputLabel>Manufacturer</InputLabel>
                  <Select
                    value={selectedManufacturer}
                    onChange={handleManufacturerChange}
                    label="Manufacturer"
                  >
                    {manufacturers.map((manufacturer) => (
                      <MenuItem key={manufacturer} value={manufacturer}>
                        {manufacturer}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth disabled={loading || !selectedManufacturer}>
                  <InputLabel>Warehouse</InputLabel>
                  <Select
                    value={selectedWarehouse}
                    onChange={handleWarehouseChange}
                    label="Warehouse"
                  >
                    {warehouses.map((warehouse) => (
                      <MenuItem key={warehouse} value={warehouse}>
                        {warehouse}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth disabled={loading || !selectedWarehouse}>
                  <InputLabel>Destination</InputLabel>
                  <Select
                    value={selectedDestination}
                    onChange={handleDestinationChange}
                    label="Destination"
                  >
                    {destinations.map((destination) => (
                      <MenuItem key={destination} value={destination}>
                        {destination}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Weight (kg)"
                  type="number"
                  value={weight}
                  onChange={handleWeightChange}
                  fullWidth
                  disabled={loading}
                  InputProps={{ inputProps: { min: 1 } }}
                />
              </Grid>
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<CalculateIcon />}
                    onClick={handleCalculateRate}
                    disabled={calculating || !selectedDestination}
                  >
                    Calculate
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<SaveIcon />}
                    onClick={handleAddToBulk}
                    disabled={!selectedDestination}
                  >
                    Add to Bulk
                  </Button>
                </Box>
              </Grid>
            </Grid>

            {calculating && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                <CircularProgress />
              </Box>
            )}

            {calculatedRate && (
              <Card sx={{ mt: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Rate Result
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        From:
                      </Typography>
                      <Typography variant="body1">
                        {selectedWarehouse}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        To:
                      </Typography>
                      <Typography variant="body1">
                        {selectedDestination}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Weight:
                      </Typography>
                      <Typography variant="body1">
                        {weight} kg
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Rate:
                      </Typography>
                      <Typography variant="h5" color="primary">
                        {formatCurrency(calculatedRate.rate)}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Calculations
            </Typography>
            {recentCalculations.length === 0 ? (
              <Alert severity="info">No recent calculations.</Alert>
            ) : (
              <List>
                {recentCalculations.map((calc, index) => (
                  <React.Fragment key={index}>
                    <ListItem>
                      <ListItemText
                        primary={`${calc.manufacturer} - ${calc.warehouse} to ${calc.destination}`}
                        secondary={`Weight: ${calc.weight} kg | Rate: ${formatCurrency(calc.rate)}`}
                      />
                    </ListItem>
                    {index < recentCalculations.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            )}
          </Paper>

          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Bulk Rate Calculator
            </Typography>
            {bulkRateRequests.length === 0 ? (
              <Alert severity="info" sx={{ mb: 2 }}>
                Add routes to calculate bulk rates.
              </Alert>
            ) : (
              <TableContainer sx={{ mb: 2 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Manufacturer</TableCell>
                      <TableCell>From</TableCell>
                      <TableCell>To</TableCell>
                      <TableCell>Weight (kg)</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {bulkRateRequests.map((request, index) => (
                      <TableRow key={index}>
                        <TableCell>{request.manufacturer}</TableCell>
                        <TableCell>{request.warehouse}</TableCell>
                        <TableCell>{request.destination}</TableCell>
                        <TableCell>{request.weight}</TableCell>
                        <TableCell>
                          <Button
                            size="small"
                            color="error"
                            onClick={() => handleRemoveFromBulk(index)}
                          >
                            Remove
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}

            <Button
              variant="contained"
              color="primary"
              startIcon={<CalculateIcon />}
              onClick={handleCalculateBulkRates}
              disabled={calculating || bulkRateRequests.length === 0}
              fullWidth
            >
              Calculate Bulk Rates
            </Button>

            {bulkRateResults.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Bulk Rate Results
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>From</TableCell>
                        <TableCell>To</TableCell>
                        <TableCell>Weight (kg)</TableCell>
                        <TableCell>Rate</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {bulkRateResults.map((result, index) => (
                        <TableRow key={index}>
                          <TableCell>{result.warehouse}</TableCell>
                          <TableCell>{result.destination}</TableCell>
                          <TableCell>{result.weight}</TableCell>
                          <TableCell>{formatCurrency(result.rate)}</TableCell>
                        </TableRow>
                      ))}
                      <TableRow>
                        <TableCell colSpan={3} align="right">
                          <Typography variant="subtitle1">Total:</Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="subtitle1" color="primary">
                            {formatCurrency(
                              bulkRateResults.reduce((sum, result) => sum + result.rate, 0)
                            )}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default RateCalculator;
