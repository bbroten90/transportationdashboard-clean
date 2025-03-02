import React, { useState, useEffect, useCallback } from 'react';
import {
  Box, Typography, Paper, Button, CircularProgress, Alert, Tabs, Tab,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TablePagination,
  Chip, IconButton, Tooltip, Collapse
} from '@mui/material';
import {
  Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon, Refresh as RefreshIcon,
  Assignment as AssignmentIcon, ExpandMore as ExpandMoreIcon, ExpandLess as ExpandLessIcon,
  LocationOn as LocationIcon, AcUnit as AcUnitIcon, Dangerous as DangerousIcon,
  Warning as WarningIcon, Inventory as InventoryIcon
} from '@mui/icons-material';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { format } from 'date-fns';
import { orderService } from '../../services';

// Import components
import OrderDetailPanel from './components/OrderDetailPanel';
import OrderFilterBar from './components/OrderFilterBar';
import OrderDialog from './components/OrderDialog';

const OrderManagement = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [orders, setOrders] = useState([]);
  const [tabValue, setTabValue] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [openOrderDialog, setOpenOrderDialog] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [orderFormData, setOrderFormData] = useState({
    customer_id: '',
    customer_name: '',
    ship_from: '',
    ship_to: '',
    pickup_date: new Date(),
    weight_kg: 0,
    priority: 'medium',
    special_requirements: {},
    notes: '',
    // Enhanced fields
    manufacturer: '',
    ship_from_location: '',
    ship_to_city: '',
    ship_to_company: '',
    purchase_order: '',
    gross_weight_kg: 0,
    weight_lbs: 0,
    gross_weight_lbs: 0,
    net_quantity: '',
  });
  const [optimizing, setOptimizing] = useState(false);
  const [expandedRows, setExpandedRows] = useState({});
  const [dialogTab, setDialogTab] = useState('basic');
  const [filterManufacturer, setFilterManufacturer] = useState('');
  const [filterWarehouse, setFilterWarehouse] = useState('');
  const [filterSpecialReq, setFilterSpecialReq] = useState('');

  const statusTabs = ['all', 'pending', 'assigned', 'in_transit', 'delivered', 'cancelled'];
  
  // Available warehouse locations
  const warehouseLocations = [
    'CWS Edmonton', 
    'CWS Winnipeg', 
    'CWS Regina', 
    'CWS Calgary - 5625 61 Ave SE #3, Calgary, AB T2C 5K8', 
    'CWS Saskatoon'
  ];
  
  // Available manufacturers
  const manufacturers = ['BASF', 'Bayer', 'Cargill', 'FCL', 'IPCO'];
  
  // Special requirements options
  const specialRequirementOptions = [
    { key: 'refrigerated', label: 'Refrigerated', icon: <AcUnitIcon /> },
    { key: 'hazardous', label: 'Hazardous Materials', icon: <DangerousIcon /> },
    { key: 'fragile', label: 'Fragile', icon: <WarningIcon /> },
    { key: 'oversized', label: 'Oversized', icon: <InventoryIcon /> }
  ];

  const fetchOrders = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const status = tabValue === 0 ? undefined : statusTabs[tabValue];
      
      // Create filter request if any filters are applied
      if (filterManufacturer || filterWarehouse || filterSpecialReq) {
        const filterRequest = {};
        
        if (status) {
          filterRequest.status = [status];
        }
        
        // Apply additional filters
        if (filterManufacturer) {
          filterRequest.manufacturer = filterManufacturer;
        }
        
        if (filterWarehouse) {
          filterRequest.ship_from_location = filterWarehouse;
        }
        
        if (filterSpecialReq) {
          filterRequest.special_requirements = { [filterSpecialReq]: true };
        }
        
        const filteredData = await orderService.filterOrders(filterRequest);
        setOrders(filteredData);
      } else {
        // Use standard getOrders if no additional filters
        const orderData = await orderService.getOrders({ status });
        setOrders(orderData);
      }
      
      setLoading(false);
    } catch (err) {
      setError('Failed to load orders: ' + err.message);
      setLoading(false);
    }
  }, [tabValue, filterManufacturer, filterWarehouse, filterSpecialReq, statusTabs]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleOpenOrderDialog = (order = null) => {
    if (order) {
      setSelectedOrder(order);
      setOrderFormData({
        customer_id: order.customer_id,
        customer_name: order.customer_name,
        ship_from: order.ship_from,
        ship_to: order.ship_to,
        pickup_date: new Date(order.pickup_date),
        weight_kg: order.weight_kg,
        priority: order.priority,
        special_requirements: order.special_requirements || {},
        notes: order.notes || '',
        // Enhanced fields
        manufacturer: order.manufacturer || '',
        ship_from_location: order.ship_from_location || '',
        ship_to_city: order.ship_to_city || '',
        ship_to_company: order.ship_to_company || '',
        purchase_order: order.purchase_order || '',
        gross_weight_kg: order.gross_weight_kg || 0,
        weight_lbs: order.weight_lbs || 0,
        gross_weight_lbs: order.gross_weight_lbs || 0,
        net_quantity: order.net_quantity || '',
      });
    } else {
      setSelectedOrder(null);
      setOrderFormData({
        customer_id: '',
        customer_name: '',
        ship_from: '',
        ship_to: '',
        pickup_date: new Date(),
        weight_kg: 0,
        priority: 'medium',
        special_requirements: {},
        notes: '',
        // Enhanced fields
        manufacturer: '',
        ship_from_location: '',
        ship_to_city: '',
        ship_to_company: '',
        purchase_order: '',
        gross_weight_kg: 0,
        weight_lbs: 0,
        gross_weight_lbs: 0,
        net_quantity: '',
      });
    }
    setDialogTab('basic');
    setOpenOrderDialog(true);
  };

  const handleCloseOrderDialog = () => {
    setOpenOrderDialog(false);
    setSelectedOrder(null);
  };

  const handleFormChange = (field) => (event) => {
    setOrderFormData({
      ...orderFormData,
      [field]: event.target.value,
    });
  };

  const handleDateChange = (date) => {
    setOrderFormData({
      ...orderFormData,
      pickup_date: date,
    });
  };

  const handleSaveOrder = async () => {
    try {
      setLoading(true);
      
      if (selectedOrder) {
        // Update existing order
        await orderService.updateOrder(selectedOrder.id, {
          status: selectedOrder.status,
          priority: orderFormData.priority,
          notes: orderFormData.notes,
          special_requirements: orderFormData.special_requirements,
          // Include enhanced fields in update
          manufacturer: orderFormData.manufacturer,
          ship_from_location: orderFormData.ship_from_location,
          ship_to_city: orderFormData.ship_to_city,
          ship_to_company: orderFormData.ship_to_company,
          purchase_order: orderFormData.purchase_order,
          gross_weight_kg: orderFormData.gross_weight_kg,
          weight_lbs: orderFormData.weight_lbs,
          gross_weight_lbs: orderFormData.gross_weight_lbs,
          net_quantity: orderFormData.net_quantity,
        });
      } else {
        // Create new order
        await orderService.createOrder({
          ...orderFormData,
          status: 'pending',
        });
      }
      
      // Refresh orders
      await fetchOrders();
      
      handleCloseOrderDialog();
    } catch (err) {
      setError('Failed to save order: ' + err.message);
      setLoading(false);
    }
  };

  const handleDeleteOrder = async (orderId) => {
    if (!window.confirm('Are you sure you want to delete this order?')) {
      return;
    }
    
    try {
      setLoading(true);
      await orderService.deleteOrder(orderId);
      
      // Refresh orders
      await fetchOrders();
      
      setLoading(false);
    } catch (err) {
      setError('Failed to delete order: ' + err.message);
      setLoading(false);
    }
  };

  const handleOptimizeOrder = async (orderId) => {
    try {
      setOptimizing(true);
      const result = await orderService.optimizeOrder(orderId);
      
      if (result) {
        // Refresh orders
        await fetchOrders();
      }
      
      setOptimizing(false);
    } catch (err) {
      setError('Failed to optimize order: ' + err.message);
      setOptimizing(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'assigned': return 'info';
      case 'in_transit': return 'primary';
      case 'delivered': return 'success';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };
  
  // Toggle expanded row
  const toggleRowExpand = (orderId) => {
    setExpandedRows(prev => ({
      ...prev,
      [orderId]: !prev[orderId]
    }));
  };
  
  // Handle dialog tab change
  const handleDialogTabChange = (event, newValue) => {
    setDialogTab(newValue);
  };
  
  // Handle special requirement toggle
  const handleSpecialRequirementChange = (key) => {
    setOrderFormData(prev => ({
      ...prev,
      special_requirements: {
        ...prev.special_requirements,
        [key]: !prev.special_requirements[key]
      }
    }));
  };
  
  // Render special requirement chips
  const renderSpecialRequirementChips = (specialRequirements) => {
    if (!specialRequirements) return null;
    
    return specialRequirementOptions
      .filter(option => specialRequirements[option.key])
      .map(option => (
        <Tooltip key={option.key} title={option.label}>
          <Chip
            icon={option.icon}
            label={option.label}
            size="small"
            color="secondary"
            sx={{ mr: 0.5, mb: 0.5 }}
          />
        </Tooltip>
      ));
  };
  
  // Reset all filters
  const handleResetFilters = () => {
    setFilterManufacturer('');
    setFilterWarehouse('');
    setFilterSpecialReq('');
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">
            Order Management
          </Typography>
          <Box>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={() => handleOpenOrderDialog()}
              sx={{ mr: 1 }}
            >
              New Order
            </Button>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={fetchOrders}
            >
              Refresh
            </Button>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Paper sx={{ width: '100%', mb: 3 }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            indicatorColor="primary"
            textColor="primary"
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab label="All Orders" />
            <Tab label="Pending" />
            <Tab label="Assigned" />
            <Tab label="In Transit" />
            <Tab label="Delivered" />
            <Tab label="Cancelled" />
          </Tabs>
          
          {/* Filter controls */}
          <OrderFilterBar
            filterManufacturer={filterManufacturer}
            setFilterManufacturer={setFilterManufacturer}
            filterWarehouse={filterWarehouse}
            setFilterWarehouse={setFilterWarehouse}
            filterSpecialReq={filterSpecialReq}
            setFilterSpecialReq={setFilterSpecialReq}
            handleResetFilters={handleResetFilters}
            manufacturers={manufacturers}
            warehouseLocations={warehouseLocations}
            specialRequirementOptions={specialRequirementOptions}
          />
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox"></TableCell>
                  <TableCell>Order ID</TableCell>
                  <TableCell>Customer</TableCell>
                  <TableCell>From</TableCell>
                  <TableCell>To</TableCell>
                  <TableCell>Pickup Date</TableCell>
                  <TableCell>Manufacturer</TableCell>
                  <TableCell>PO #</TableCell>
                  <TableCell>Weight</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Priority</TableCell>
                  <TableCell>Special Req.</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={13} align="center">
                      <CircularProgress />
                    </TableCell>
                  </TableRow>
                ) : orders.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={13} align="center">
                      <Alert severity="info">No orders found.</Alert>
                    </TableCell>
                  </TableRow>
                ) : (
                  orders
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    .map((order) => (
                      <React.Fragment key={order.id}>
                        <TableRow>
                          <TableCell padding="checkbox">
                            <IconButton
                              size="small"
                              onClick={() => toggleRowExpand(order.id)}
                            >
                              {expandedRows[order.id] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                            </IconButton>
                          </TableCell>
                          <TableCell>{order.id}</TableCell>
                          <TableCell>{order.customer_name}</TableCell>
                          <TableCell>
                            <Tooltip title={order.ship_from_location || order.ship_from}>
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <LocationIcon fontSize="small" sx={{ mr: 0.5, color: 'primary.main' }} />
                                {order.ship_from_location || order.ship_from}
                              </Box>
                            </Tooltip>
                          </TableCell>
                          <TableCell>
                            <Tooltip title={order.ship_to_city || order.ship_to}>
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <LocationIcon fontSize="small" sx={{ mr: 0.5, color: 'secondary.main' }} />
                                {order.ship_to_city || order.ship_to}
                              </Box>
                            </Tooltip>
                          </TableCell>
                          <TableCell>{format(new Date(order.pickup_date), 'MMM d, yyyy')}</TableCell>
                          <TableCell>
                            {order.manufacturer && (
                              <Chip
                                label={order.manufacturer}
                                size="small"
                                color="default"
                                variant="outlined"
                              />
                            )}
                          </TableCell>
                          <TableCell>{order.purchase_order || '-'}</TableCell>
                          <TableCell>
                            <Tooltip title={`${order.weight_lbs || Math.round(order.weight_kg * 2.20462)} lbs`}>
                              <span>{order.weight_kg} kg</span>
                            </Tooltip>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={order.status}
                              color={getStatusColor(order.status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={order.priority}
                              color={order.priority === 'high' ? 'error' : order.priority === 'medium' ? 'warning' : 'default'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap' }}>
                              {renderSpecialRequirementChips(order.special_requirements)}
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex' }}>
                              <Tooltip title="Edit">
                                <IconButton
                                  size="small"
                                  onClick={() => handleOpenOrderDialog(order)}
                                >
                                  <EditIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                              {order.status === 'pending' && (
                                <Tooltip title="Optimize">
                                  <IconButton
                                    size="small"
                                    onClick={() => handleOptimizeOrder(order.id)}
                                    disabled={optimizing}
                                  >
                                    <AssignmentIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              )}
                              <Tooltip title="Delete">
                                <IconButton
                                  size="small"
                                  onClick={() => handleDeleteOrder(order.id)}
                                >
                                  <DeleteIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </TableCell>
                        </TableRow>
                        
                        {/* Expanded row with additional details */}
                        <TableRow>
                          <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={13}>
                            <Collapse in={expandedRows[order.id]} timeout="auto" unmountOnExit>
                              <OrderDetailPanel 
                                order={order} 
                                specialRequirementChips={renderSpecialRequirementChips} 
                              />
                            </Collapse>
                          </TableCell>
                        </TableRow>
                      </React.Fragment>
                    ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
          
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={orders.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Paper>

        {/* Order Dialog */}
        <OrderDialog
          open={openOrderDialog}
          onClose={handleCloseOrderDialog}
          selectedOrder={selectedOrder}
          orderFormData={orderFormData}
          handleFormChange={handleFormChange}
          handleDateChange={handleDateChange}
          handleSaveOrder={handleSaveOrder}
          dialogTab={dialogTab}
          handleDialogTabChange={handleDialogTabChange}
          handleSpecialRequirementChange={handleSpecialRequirementChange}
          manufacturers={manufacturers}
          warehouseLocations={warehouseLocations}
          specialRequirementOptions={specialRequirementOptions}
        />
      </Box>
    </LocalizationProvider>
  );
};

export default OrderManagement;
