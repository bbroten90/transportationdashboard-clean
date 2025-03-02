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
  Card,
  CardContent,
  Divider,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Tooltip,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  InputAdornment,
} from '@mui/material';
import {
  Upload as UploadIcon,
  Description as DescriptionIcon,
  Assignment as AssignmentIcon,
  Check as CheckIcon,
  Error as ErrorIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Warning as WarningIcon,
  LocationOn as LocationIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { pdfService, orderService } from '../../services';

const PDFProcessor = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeStep, setActiveStep] = useState(0);
  const [selectedFile, setSelectedFile] = useState(null);
  const [extractedData, setExtractedData] = useState(null);
  const [validationResult, setValidationResult] = useState(null);
  const [createdOrder, setCreatedOrder] = useState(null);
  const [orderFormData, setOrderFormData] = useState({
    customer_id: '',
    customer_name: '',
    ship_from: '',
    ship_to: '',
    pickup_date: new Date(),
    weight_kg: 0,
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
  
  // Available warehouse locations
  const [warehouseLocations, setWarehouseLocations] = useState([
    'CWS Edmonton',
    'CWS Winnipeg',
    'CWS Regina'
  ]);
  const [recentOrders, setRecentOrders] = useState([]);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setActiveStep(1);
      setError(null);
    } else {
      setError('Please select a valid PDF file');
    }
  };

  // Helper function to render confidence indicator
  const ConfidenceIndicator = ({ score }) => {
    let color = 'success';
    let icon = <CheckIcon />;
    
    if (score < 0.5) {
      color = 'error';
      icon = <ErrorIcon />;
    } else if (score < 0.8) {
      color = 'warning';
      icon = <WarningIcon />;
    }
    
    return (
      <Tooltip title={`Confidence: ${Math.round(score * 100)}%`}>
        <Chip 
          size="small" 
          color={color} 
          icon={icon} 
          label={`${Math.round(score * 100)}%`} 
          sx={{ ml: 1 }}
        />
      </Tooltip>
    );
  };

  const handleExtractData = async () => {
    if (!selectedFile) {
      setError('No file selected');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const data = await pdfService.extractPdfData(selectedFile);
      setExtractedData(data);
      
      // Validate extracted data
      const validation = pdfService.validateExtractedData(data);
      setValidationResult(validation);
      
      // Populate form data with both basic and enhanced fields
      setOrderFormData({
        // Basic fields
        customer_id: data.customer_id || '',
        customer_name: data.customer_name || '',
        ship_from: data.ship_from || '',
        ship_to: data.ship_to || '',
        pickup_date: data.pickup_date ? new Date(data.pickup_date) : new Date(),
        weight_kg: data.weight_kg || 0,
        special_requirements: data.special_requirements || {},
        notes: data.notes || '',
        
        // Enhanced fields
        manufacturer: data.manufacturer || '',
        ship_from_location: data.ship_from_location || '',
        ship_to_city: data.ship_to_city || '',
        ship_to_company: data.ship_to_company || '',
        purchase_order: data.purchase_order || '',
        gross_weight_kg: data.gross_weight_kg || 0,
        weight_lbs: data.weight_lbs || 0,
        gross_weight_lbs: data.gross_weight_lbs || 0,
        net_quantity: data.net_quantity || '',
      });
      
      setActiveStep(2);
      setLoading(false);
    } catch (err) {
      setError('Failed to extract data: ' + err.message);
      setLoading(false);
    }
  };

  const handleFormChange = (field) => (event) => {
    setOrderFormData({
      ...orderFormData,
      [field]: event.target.value,
    });
    
    // Update validation
    const updatedValidation = { ...validationResult };
    if (field in updatedValidation.errors) {
      delete updatedValidation.errors[field];
      updatedValidation.isValid = Object.keys(updatedValidation.errors).length === 0;
      setValidationResult(updatedValidation);
    }
  };

  const handleCreateOrder = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Create order
      const order = await orderService.createOrder({
        ...orderFormData,
        status: 'pending',
        priority: 'medium',
      });
      
      setCreatedOrder(order);
      
      // Add to recent orders
      setRecentOrders([order, ...recentOrders.slice(0, 4)]);
      
      setActiveStep(3);
      setLoading(false);
    } catch (err) {
      setError('Failed to create order: ' + err.message);
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setExtractedData(null);
    setValidationResult(null);
    setCreatedOrder(null);
    setOrderFormData({
      // Basic fields
      customer_id: '',
      customer_name: '',
      ship_from: '',
      ship_to: '',
      pickup_date: new Date(),
      weight_kg: 0,
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
    setActiveStep(0);
    setError(null);
  };

  const steps = [
    {
      label: 'Select PDF',
      description: 'Upload a PDF file containing order information',
      content: (
        <Box sx={{ mt: 2 }}>
          <Button
            variant="contained"
            component="label"
            startIcon={<UploadIcon />}
            disabled={loading}
          >
            Select PDF File
            <input
              type="file"
              accept=".pdf"
              hidden
              onChange={handleFileChange}
            />
          </Button>
          {selectedFile && (
            <Typography variant="body2" sx={{ mt: 1 }}>
              Selected file: {selectedFile.name}
            </Typography>
          )}
        </Box>
      ),
    },
    {
      label: 'Extract Data',
      description: 'Extract order information from the PDF',
      content: (
        <Box sx={{ mt: 2 }}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<DescriptionIcon />}
            onClick={handleExtractData}
            disabled={loading || !selectedFile}
          >
            Extract Data
          </Button>
          {loading && (
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
              <CircularProgress size={24} sx={{ mr: 1 }} />
              <Typography variant="body2">Extracting data...</Typography>
            </Box>
          )}
        </Box>
      ),
    },
    {
      label: 'Review & Edit',
      description: 'Review and edit the extracted order information',
      content: (
        <Box sx={{ mt: 2 }}>
          {extractedData && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Customer ID"
                  value={orderFormData.customer_id}
                  onChange={handleFormChange('customer_id')}
                  fullWidth
                  error={validationResult && !validationResult.isValid && 'customer_id' in validationResult.errors}
                  helperText={validationResult && !validationResult.isValid && validationResult.errors.customer_id}
                  sx={{ mb: 2 }}
                />
                <TextField
                  label="Customer Name"
                  value={orderFormData.customer_name}
                  onChange={handleFormChange('customer_name')}
                  fullWidth
                  error={validationResult && !validationResult.isValid && 'customer_name' in validationResult.errors}
                  helperText={validationResult && !validationResult.isValid && validationResult.errors.customer_name}
                  sx={{ mb: 2 }}
                />
                <TextField
                  label="Ship From"
                  value={orderFormData.ship_from}
                  onChange={handleFormChange('ship_from')}
                  fullWidth
                  error={validationResult && !validationResult.isValid && 'ship_from' in validationResult.errors}
                  helperText={validationResult && !validationResult.isValid && validationResult.errors.ship_from}
                  sx={{ mb: 2 }}
                />
                <TextField
                  label="Ship To"
                  value={orderFormData.ship_to}
                  onChange={handleFormChange('ship_to')}
                  fullWidth
                  error={validationResult && !validationResult.isValid && 'ship_to' in validationResult.errors}
                  helperText={validationResult && !validationResult.isValid && validationResult.errors.ship_to}
                  sx={{ mb: 2 }}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Pickup Date"
                  type="date"
                  value={orderFormData.pickup_date ? format(new Date(orderFormData.pickup_date), 'yyyy-MM-dd') : ''}
                  onChange={handleFormChange('pickup_date')}
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                  error={validationResult && !validationResult.isValid && 'pickup_date' in validationResult.errors}
                  helperText={validationResult && !validationResult.isValid && validationResult.errors.pickup_date}
                  sx={{ mb: 2 }}
                />
                <TextField
                  label="Weight (kg)"
                  type="number"
                  value={orderFormData.weight_kg}
                  onChange={handleFormChange('weight_kg')}
                  fullWidth
                  error={validationResult && !validationResult.isValid && 'weight_kg' in validationResult.errors}
                  helperText={validationResult && !validationResult.isValid && validationResult.errors.weight_kg}
                  sx={{ mb: 2 }}
                />
                <TextField
                  label="Notes"
                  value={orderFormData.notes}
                  onChange={handleFormChange('notes')}
                  fullWidth
                  multiline
                  rows={4}
                  sx={{ mb: 2 }}
                />
              </Grid>
              {/* Enhanced extraction information */}
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                  Enhanced Extraction Information
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      label="Manufacturer"
                      value={orderFormData.manufacturer}
                      onChange={handleFormChange('manufacturer')}
                      fullWidth
                      sx={{ mb: 2 }}
                      InputProps={{
                        endAdornment: extractedData?.confidence_scores?.manufacturer !== undefined && (
                          <InputAdornment position="end">
                            <ConfidenceIndicator score={extractedData.confidence_scores.manufacturer} />
                          </InputAdornment>
                        )
                      }}
                      helperText={extractedData?.needs_review?.manufacturer && "This field needs review"}
                      error={extractedData?.needs_review?.manufacturer}
                    />
                    
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <InputLabel>Ship From Location</InputLabel>
                      <Select
                        value={orderFormData.ship_from_location}
                        onChange={handleFormChange('ship_from_location')}
                        label="Ship From Location"
                        endAdornment={
                          extractedData?.confidence_scores?.ship_from_location !== undefined && (
                            <InputAdornment position="end">
                              <ConfidenceIndicator score={extractedData.confidence_scores.ship_from_location} />
                            </InputAdornment>
                          )
                        }
                      >
                        {warehouseLocations.map((location) => (
                          <MenuItem key={location} value={location}>
                            {location}
                          </MenuItem>
                        ))}
                      </Select>
                      {extractedData?.needs_review?.ship_from_location && (
                        <Typography variant="caption" color="error">
                          This location needs review
                        </Typography>
                      )}
                    </FormControl>
                    
                    <TextField
                      label="Ship To City"
                      value={orderFormData.ship_to_city}
                      onChange={handleFormChange('ship_to_city')}
                      fullWidth
                      sx={{ mb: 2 }}
                      InputProps={{
                        endAdornment: extractedData?.confidence_scores?.ship_to_city !== undefined && (
                          <InputAdornment position="end">
                            <ConfidenceIndicator score={extractedData.confidence_scores.ship_to_city} />
                          </InputAdornment>
                        )
                      }}
                      helperText={extractedData?.needs_review?.ship_to_city && "This field needs review"}
                      error={extractedData?.needs_review?.ship_to_city}
                    />
                    
                    <TextField
                      label="Ship To Company"
                      value={orderFormData.ship_to_company}
                      onChange={handleFormChange('ship_to_company')}
                      fullWidth
                      sx={{ mb: 2 }}
                      InputProps={{
                        endAdornment: extractedData?.confidence_scores?.ship_to_company !== undefined && (
                          <InputAdornment position="end">
                            <ConfidenceIndicator score={extractedData.confidence_scores.ship_to_company} />
                          </InputAdornment>
                        )
                      }}
                      helperText={extractedData?.needs_review?.ship_to_company && "This field needs review"}
                      error={extractedData?.needs_review?.ship_to_company}
                    />
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <TextField
                      label="Purchase Order"
                      value={orderFormData.purchase_order}
                      onChange={handleFormChange('purchase_order')}
                      fullWidth
                      sx={{ mb: 2 }}
                      InputProps={{
                        endAdornment: extractedData?.confidence_scores?.purchase_order !== undefined && (
                          <InputAdornment position="end">
                            <ConfidenceIndicator score={extractedData.confidence_scores.purchase_order} />
                          </InputAdornment>
                        )
                      }}
                      helperText={extractedData?.needs_review?.purchase_order && "This field needs review"}
                      error={extractedData?.needs_review?.purchase_order}
                    />
                    
                    <TextField
                      label="Gross Weight (kg)"
                      type="number"
                      value={orderFormData.gross_weight_kg}
                      onChange={handleFormChange('gross_weight_kg')}
                      fullWidth
                      sx={{ mb: 2 }}
                      InputProps={{
                        endAdornment: extractedData?.confidence_scores?.gross_weight_kg !== undefined && (
                          <InputAdornment position="end">
                            <ConfidenceIndicator score={extractedData.confidence_scores.gross_weight_kg} />
                          </InputAdornment>
                        )
                      }}
                      helperText={extractedData?.needs_review?.gross_weight_kg && "This field needs review"}
                      error={extractedData?.needs_review?.gross_weight_kg}
                    />
                    
                    <TextField
                      label="Weight (lbs)"
                      type="number"
                      value={orderFormData.weight_lbs}
                      onChange={handleFormChange('weight_lbs')}
                      fullWidth
                      sx={{ mb: 2 }}
                      InputProps={{
                        endAdornment: extractedData?.confidence_scores?.weight_lbs !== undefined && (
                          <InputAdornment position="end">
                            <ConfidenceIndicator score={extractedData.confidence_scores.weight_lbs} />
                          </InputAdornment>
                        )
                      }}
                      helperText={extractedData?.needs_review?.weight_lbs && "This field needs review"}
                      error={extractedData?.needs_review?.weight_lbs}
                    />
                    
                    <TextField
                      label="Net Quantity"
                      value={orderFormData.net_quantity}
                      onChange={handleFormChange('net_quantity')}
                      fullWidth
                      sx={{ mb: 2 }}
                      InputProps={{
                        endAdornment: extractedData?.confidence_scores?.net_quantity !== undefined && (
                          <InputAdornment position="end">
                            <ConfidenceIndicator score={extractedData.confidence_scores.net_quantity} />
                          </InputAdornment>
                        )
                      }}
                      helperText={extractedData?.needs_review?.net_quantity && "This field needs review"}
                      error={extractedData?.needs_review?.net_quantity}
                    />
                  </Grid>
                </Grid>
              </Grid>
              
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                  <Button
                    variant="outlined"
                    startIcon={<DeleteIcon />}
                    onClick={handleReset}
                  >
                    Reset
                  </Button>
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<AssignmentIcon />}
                    onClick={handleCreateOrder}
                    disabled={loading || (validationResult && !validationResult.isValid)}
                  >
                    Create Order
                  </Button>
                </Box>
              </Grid>
            </Grid>
          )}
        </Box>
      ),
    },
    {
      label: 'Order Created',
      description: 'Order has been successfully created',
      content: (
        <Box sx={{ mt: 2 }}>
          {createdOrder && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Order Created Successfully
                </Typography>
                {/* Basic information */}
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Order ID:
                    </Typography>
                    <Typography variant="body1">
                      {createdOrder.id}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Customer:
                    </Typography>
                    <Typography variant="body1">
                      {createdOrder.customer_name}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      From:
                    </Typography>
                    <Typography variant="body1">
                      {createdOrder.ship_from}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      To:
                    </Typography>
                    <Typography variant="body1">
                      {createdOrder.ship_to}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Pickup Date:
                    </Typography>
                    <Typography variant="body1">
                      {format(new Date(createdOrder.pickup_date), 'MMM d, yyyy')}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Weight:
                    </Typography>
                    <Typography variant="body1">
                      {createdOrder.weight_kg} kg
                    </Typography>
                  </Grid>
                </Grid>
                
                {/* Enhanced information */}
                <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                  Enhanced Information
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Manufacturer:
                    </Typography>
                    <Typography variant="body1">
                      {createdOrder.manufacturer || 'N/A'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Ship From Location:
                    </Typography>
                    <Typography variant="body1">
                      {createdOrder.ship_from_location || 'N/A'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Ship To City:
                    </Typography>
                    <Typography variant="body1">
                      {createdOrder.ship_to_city || 'N/A'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Ship To Company:
                    </Typography>
                    <Typography variant="body1">
                      {createdOrder.ship_to_company || 'N/A'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Purchase Order:
                    </Typography>
                    <Typography variant="body1">
                      {createdOrder.purchase_order || 'N/A'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Net Quantity:
                    </Typography>
                    <Typography variant="body1">
                      {createdOrder.net_quantity || 'N/A'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Weight (lbs):
                    </Typography>
                    <Typography variant="body1">
                      {createdOrder.weight_lbs || 'N/A'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Gross Weight (kg):
                    </Typography>
                    <Typography variant="body1">
                      {createdOrder.gross_weight_kg || 'N/A'}
                    </Typography>
                  </Grid>
                </Grid>
                <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<CheckIcon />}
                    onClick={handleReset}
                  >
                    Process Another PDF
                  </Button>
                </Box>
              </CardContent>
            </Card>
          )}
        </Box>
      ),
    },
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        PDF Processor
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Process Order PDF
            </Typography>
            <Stepper activeStep={activeStep} orientation="vertical">
              {steps.map((step, index) => (
                <Step key={step.label}>
                  <StepLabel
                    optional={
                      <Typography variant="caption">{step.description}</Typography>
                    }
                  >
                    {step.label}
                  </StepLabel>
                  <StepContent>
                    {step.content}
                  </StepContent>
                </Step>
              ))}
            </Stepper>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Orders
            </Typography>
            {recentOrders.length === 0 ? (
              <Alert severity="info">No recent orders.</Alert>
            ) : (
              <List>
                {recentOrders.map((order, index) => (
                  <React.Fragment key={order.id}>
                    <ListItem>
                      <ListItemText
                        primary={`${order.customer_name} - ${order.ship_from} to ${order.ship_to}`}
                        secondary={`Order ID: ${order.id} | Weight: ${order.weight_kg} kg | Pickup: ${format(new Date(order.pickup_date), 'MMM d, yyyy')}`}
                      />
                    </ListItem>
                    {index < recentOrders.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PDFProcessor;
