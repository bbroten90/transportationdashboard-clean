import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  CardHeader,
  Divider,
  List,
  ListItem,
  ListItemText,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { fleetService } from '../../services';

const FleetManagement = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [warehouses, setWarehouses] = useState([]);
  const [selectedWarehouse, setSelectedWarehouse] = useState('');
  const [trucks, setTrucks] = useState([]);
  const [trailers, setTrailers] = useState([]);
  const [utilization, setUtilization] = useState(null);

  useEffect(() => {
    const fetchWarehouses = async () => {
      try {
        setLoading(true);
        const warehouseList = await fleetService.getWarehouseLocations();
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

    fetchWarehouses();
  }, []);

  useEffect(() => {
    const fetchFleetData = async () => {
      if (!selectedWarehouse) return;
      
      try {
        setLoading(true);
        
        // Fetch trucks and trailers for the selected warehouse
        const [truckList, trailerList, utilizationData] = await Promise.all([
          fleetService.getAvailableTrucksByWarehouse(selectedWarehouse),
          fleetService.getAvailableTrailersByWarehouse(selectedWarehouse),
          fleetService.getFleetUtilization()
        ]);
        
        setTrucks(truckList);
        setTrailers(trailerList);
        setUtilization(utilizationData);
        setLoading(false);
      } catch (err) {
        setError('Failed to load fleet data: ' + err.message);
        setLoading(false);
      }
    };

    fetchFleetData();
  }, [selectedWarehouse]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleWarehouseChange = (event) => {
    setSelectedWarehouse(event.target.value);
  };

  if (loading && !selectedWarehouse) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error && !selectedWarehouse) {
    return (
      <Box sx={{ mt: 2 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Fleet Management
      </Typography>

      <Paper sx={{ mb: 3, p: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel id="warehouse-select-label">Warehouse</InputLabel>
              <Select
                labelId="warehouse-select-label"
                id="warehouse-select"
                value={selectedWarehouse}
                label="Warehouse"
                onChange={handleWarehouseChange}
              >
                {warehouses.map((warehouse) => (
                  <MenuItem key={warehouse} value={warehouse}>
                    {warehouse}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          {utilization && selectedWarehouse && utilization[selectedWarehouse] && (
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Utilization
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Trucks: {utilization[selectedWarehouse].assignedTrucks} / {utilization[selectedWarehouse].totalTrucks}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Trailers: {utilization[selectedWarehouse].assignedTrailers} / {utilization[selectedWarehouse].totalTrailers}
                      </Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="body1">
                        Utilization: {utilization[selectedWarehouse].utilization.toFixed(1)}%
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      </Paper>

      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          centered
        >
          <Tab label="Trucks" />
          <Tab label="Trailers" />
        </Tabs>
        
        <Box sx={{ p: 3 }}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <CircularProgress />
            </Box>
          ) : error ? (
            <Alert severity="error">{error}</Alert>
          ) : (
            <>
              {tabValue === 0 && (
                <Grid container spacing={3}>
                  {trucks.length === 0 ? (
                    <Grid item xs={12}>
                      <Alert severity="info">No trucks available at this warehouse.</Alert>
                    </Grid>
                  ) : (
                    trucks.map((truck) => (
                      <Grid item xs={12} sm={6} md={4} key={truck.id}>
                        <Card>
                          <CardHeader
                            title={truck.name}
                            subheader={`Driver: ${truck.driver}`}
                          />
                          <Divider />
                          <CardContent>
                            <List dense>
                              <ListItem>
                                <ListItemText
                                  primary="Current Hours"
                                  secondary={`${truck.current_hours} / ${truck.max_hours}`}
                                />
                              </ListItem>
                              <ListItem>
                                <ListItemText
                                  primary="Warehouse"
                                  secondary={truck.warehouse}
                                />
                              </ListItem>
                            </List>
                            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                              <Chip
                                label="Available"
                                color="success"
                                size="small"
                              />
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))
                  )}
                </Grid>
              )}
              
              {tabValue === 1 && (
                <Grid container spacing={3}>
                  {trailers.length === 0 ? (
                    <Grid item xs={12}>
                      <Alert severity="info">No trailers available at this warehouse.</Alert>
                    </Grid>
                  ) : (
                    trailers.map((trailer) => (
                      <Grid item xs={12} sm={6} md={4} key={trailer.id}>
                        <Card>
                          <CardHeader
                            title={trailer.name}
                            subheader={`Max Weight: ${trailer.max_weight_kg} kg`}
                          />
                          <Divider />
                          <CardContent>
                            <List dense>
                              <ListItem>
                                <ListItemText
                                  primary="Current Weight"
                                  secondary={`${trailer.current_weight_kg} / ${trailer.max_weight_kg} kg`}
                                />
                              </ListItem>
                              <ListItem>
                                <ListItemText
                                  primary="Warehouse"
                                  secondary={trailer.warehouse}
                                />
                              </ListItem>
                              <ListItem>
                                <ListItemText
                                  primary="Has Pallet Jack"
                                  secondary={trailer.has_pallet_jack ? 'Yes' : 'No'}
                                />
                              </ListItem>
                            </List>
                            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                              <Chip
                                label="Available"
                                color="success"
                                size="small"
                              />
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))
                  )}
                </Grid>
              )}
            </>
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default FleetManagement;
