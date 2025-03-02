import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Button,
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
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  CalendarToday as CalendarIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import { format, addDays, isSameDay } from 'date-fns';
import { orderService, scheduleService } from '../../services';

const SchedulePlanner = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(addDays(new Date(), 7));
  const [scheduleData, setScheduleData] = useState([]);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedOrders, setSelectedOrders] = useState([]);
  const [openOrderDialog, setOpenOrderDialog] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [newDate, setNewDate] = useState(null);
  const [optimizing, setOptimizing] = useState(false);
  const [optimizationResult, setOptimizationResult] = useState(null);
  const [revenueData, setRevenueData] = useState({});

  useEffect(() => {
    fetchScheduleData();
  }, [startDate, endDate]);

  useEffect(() => {
    if (scheduleData.length > 0) {
      const dateData = scheduleData.find(data => 
        isSameDay(new Date(data.date), selectedDate)
      );
      
      if (dateData) {
        setSelectedOrders(dateData.orders);
      } else {
        setSelectedOrders([]);
      }
    }
  }, [selectedDate, scheduleData]);

  const fetchScheduleData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await scheduleService.getScheduleData(startDate, endDate);
      setScheduleData(data);
      
      // Calculate revenue for each date
      const revenues = {};
      for (const day of data) {
        const revenue = await scheduleService.calculateDateRevenue(day.date);
        revenues[format(new Date(day.date), 'yyyy-MM-dd')] = revenue;
      }
      setRevenueData(revenues);
      
      setLoading(false);
    } catch (err) {
      setError('Failed to load schedule data: ' + err.message);
      setLoading(false);
    }
  };

  const handleOptimizeSchedule = async () => {
    try {
      setOptimizing(true);
      setError(null);
      
      const result = await scheduleService.optimizeSchedule(startDate, endDate);
      setOptimizationResult(result);
      
      // Refresh schedule data after optimization
      await fetchScheduleData();
      
      setOptimizing(false);
    } catch (err) {
      setError('Failed to optimize schedule: ' + err.message);
      setOptimizing(false);
    }
  };

  const handleOptimizeRevenue = async () => {
    try {
      setOptimizing(true);
      setError(null);
      
      // Get all pending orders
      const pendingOrders = [];
      for (const day of scheduleData) {
        const dayPendingOrders = day.orders.filter(order => order.status === 'pending');
        pendingOrders.push(...dayPendingOrders);
      }
      
      if (pendingOrders.length === 0) {
        setError('No pending orders to optimize');
        setOptimizing(false);
        return;
      }
      
      // Calculate optimal schedule
      const result = await scheduleService.calculateOptimalSchedule(
        pendingOrders,
        startDate,
        Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1
      );
      
      // Reschedule orders based on optimization
      for (const day of result.schedule) {
        for (const order of day.orders) {
          await scheduleService.rescheduleOrder(order.id, day.date);
        }
      }
      
      // Refresh schedule data
      await fetchScheduleData();
      
      setOptimizationResult({
        startDate: result.startDate,
        endDate: result.endDate,
        totalRevenue: result.totalRevenue,
        message: `Optimized ${pendingOrders.length} orders for maximum revenue`
      });
      
      setOptimizing(false);
    } catch (err) {
      setError('Failed to optimize revenue: ' + err.message);
      setOptimizing(false);
    }
  };

  const handleDateClick = (date) => {
    setSelectedDate(date);
  };

  const handleRescheduleOrder = (order) => {
    setSelectedOrder(order);
    setNewDate(new Date(order.pickup_date));
    setOpenOrderDialog(true);
  };

  const handleCloseOrderDialog = () => {
    setOpenOrderDialog(false);
    setSelectedOrder(null);
    setNewDate(null);
  };

  const handleSaveReschedule = async () => {
    if (!selectedOrder || !newDate) return;
    
    try {
      setLoading(true);
      await scheduleService.rescheduleOrder(selectedOrder.id, newDate);
      
      // Refresh schedule data
      await fetchScheduleData();
      
      handleCloseOrderDialog();
      setLoading(false);
    } catch (err) {
      setError('Failed to reschedule order: ' + err.message);
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'warning';
      case 'assigned':
        return 'info';
      case 'in_transit':
        return 'primary';
      case 'delivered':
        return 'success';
      case 'cancelled':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Schedule Planner
        </Typography>

        <Paper sx={{ mb: 3, p: 2 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <DatePicker
                label="Start Date"
                value={startDate}
                onChange={(newValue) => setStartDate(newValue)}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <DatePicker
                label="End Date"
                value={endDate}
                onChange={(newValue) => setEndDate(newValue)}
                renderInput={(params) => <TextField {...params} fullWidth />}
                minDate={startDate}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <Button
                variant="contained"
                color="primary"
                startIcon={<RefreshIcon />}
                onClick={fetchScheduleData}
                fullWidth
              >
                Refresh
              </Button>
            </Grid>
            <Grid item xs={12} md={3}>
              <Button
                variant="contained"
                color="secondary"
                startIcon={<TrendingUpIcon />}
                onClick={handleOptimizeRevenue}
                disabled={optimizing}
                fullWidth
              >
                Optimize Revenue
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {optimizationResult && (
          <Alert severity="success" sx={{ mb: 3 }}>
            {optimizationResult.message || `Optimization complete. ${optimizationResult.totalAssigned || 0} orders assigned.`}
            {optimizationResult.totalRevenue && ` Estimated revenue: $${optimizationResult.totalRevenue.toFixed(2)}`}
          </Alert>
        )}

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                Schedule Overview
              </Typography>
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                  <CircularProgress />
                </Box>
              ) : (
                <List>
                  {scheduleData.map((day) => (
                    <ListItem
                      key={day.date}
                      button
                      selected={isSameDay(new Date(day.date), selectedDate)}
                      onClick={() => handleDateClick(new Date(day.date))}
                    >
                      <ListItemText
                        primary={format(new Date(day.date), 'EEEE, MMMM d, yyyy')}
                        secondary={`${day.orders.length} orders`}
                      />
                      <Box>
                        <Chip
                          size="small"
                          label={`$${revenueData[format(new Date(day.date), 'yyyy-MM-dd')] ? 
                            revenueData[format(new Date(day.date), 'yyyy-MM-dd')].toFixed(2) : '0.00'}`}
                          color="primary"
                        />
                      </Box>
                    </ListItem>
                  ))}
                </List>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Orders for {format(selectedDate, 'EEEE, MMMM d, yyyy')}
                </Typography>
                <Button
                  variant="outlined"
                  color="primary"
                  startIcon={<CalendarIcon />}
                  onClick={() => handleOptimizeSchedule()}
                  disabled={optimizing}
                >
                  Optimize Day
                </Button>
              </Box>
              
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                  <CircularProgress />
                </Box>
              ) : selectedOrders.length === 0 ? (
                <Alert severity="info">No orders scheduled for this date.</Alert>
              ) : (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Order ID</TableCell>
                        <TableCell>Customer</TableCell>
                        <TableCell>From</TableCell>
                        <TableCell>To</TableCell>
                        <TableCell>Weight (kg)</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {selectedOrders.map((order) => (
                        <TableRow key={order.id}>
                          <TableCell>{order.id}</TableCell>
                          <TableCell>{order.customer_name}</TableCell>
                          <TableCell>{order.ship_from}</TableCell>
                          <TableCell>{order.ship_to}</TableCell>
                          <TableCell>{order.weight_kg}</TableCell>
                          <TableCell>
                            <Chip
                              label={order.status}
                              color={getStatusColor(order.status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Tooltip title="Reschedule">
                              <IconButton
                                size="small"
                                onClick={() => handleRescheduleOrder(order)}
                              >
                                <EditIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Paper>
          </Grid>
        </Grid>

        <Dialog open={openOrderDialog} onClose={handleCloseOrderDialog}>
          <DialogTitle>Reschedule Order</DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 2 }}>
              {selectedOrder && (
                <>
                  <Typography variant="subtitle1" gutterBottom>
                    Order: {selectedOrder.id}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {selectedOrder.customer_name} - {selectedOrder.ship_from} to {selectedOrder.ship_to}
                  </Typography>
                  <Box sx={{ mt: 3 }}>
                    <DatePicker
                      label="New Pickup Date"
                      value={newDate}
                      onChange={(date) => setNewDate(date)}
                      renderInput={(params) => <TextField {...params} fullWidth />}
                    />
                  </Box>
                </>
              )}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseOrderDialog}>Cancel</Button>
            <Button onClick={handleSaveReschedule} color="primary">
              Save
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </LocalizationProvider>
  );
};

export default SchedulePlanner;
