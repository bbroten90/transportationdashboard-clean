import React from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions, Button, Box, Tabs, Tab,
  Grid, TextField, FormControl, InputLabel, Select, MenuItem, Chip
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { format } from 'date-fns';

const OrderDialog = ({
  open,
  onClose,
  selectedOrder,
  orderFormData,
  handleFormChange,
  handleDateChange,
  handleSaveOrder,
  dialogTab,
  handleDialogTabChange,
  handleSpecialRequirementChange,
  manufacturers,
  warehouseLocations,
  specialRequirementOptions
}) => {
  // Render basic information tab
  const renderBasicInfoTab = () => (
    <Grid container spacing={2} sx={{ mt: 1 }}>
      <Grid item xs={12} md={6}>
        <TextField
          label="Customer ID"
          value={orderFormData.customer_id}
          onChange={handleFormChange('customer_id')}
          fullWidth
          disabled={!!selectedOrder}
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          label="Customer Name"
          value={orderFormData.customer_name}
          onChange={handleFormChange('customer_name')}
          fullWidth
          disabled={!!selectedOrder}
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          label="Ship From"
          value={orderFormData.ship_from}
          onChange={handleFormChange('ship_from')}
          fullWidth
          disabled={!!selectedOrder}
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          label="Ship To"
          value={orderFormData.ship_to}
          onChange={handleFormChange('ship_to')}
          fullWidth
          disabled={!!selectedOrder}
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <DatePicker
          label="Pickup Date"
          value={orderFormData.pickup_date}
          onChange={handleDateChange}
          renderInput={(params) => <TextField {...params} fullWidth />}
          disabled={!!selectedOrder}
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          label="Weight (kg)"
          type="number"
          value={orderFormData.weight_kg}
          onChange={handleFormChange('weight_kg')}
          fullWidth
          disabled={!!selectedOrder}
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Priority</InputLabel>
          <Select
            value={orderFormData.priority}
            onChange={handleFormChange('priority')}
            label="Priority"
          >
            <MenuItem value="low">Low</MenuItem>
            <MenuItem value="medium">Medium</MenuItem>
            <MenuItem value="high">High</MenuItem>
          </Select>
        </FormControl>
      </Grid>
    </Grid>
  );

  // Render enhanced information tab
  const renderEnhancedInfoTab = () => (
    <Grid container spacing={2} sx={{ mt: 1 }}>
      <Grid item xs={12} md={6}>
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Manufacturer</InputLabel>
          <Select
            value={orderFormData.manufacturer}
            onChange={handleFormChange('manufacturer')}
            label="Manufacturer"
          >
            <MenuItem value="">None</MenuItem>
            {manufacturers.map(mfr => (
              <MenuItem key={mfr} value={mfr}>{mfr}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      <Grid item xs={12} md={6}>
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Ship From Location</InputLabel>
          <Select
            value={orderFormData.ship_from_location}
            onChange={handleFormChange('ship_from_location')}
            label="Ship From Location"
          >
            <MenuItem value="">None</MenuItem>
            {warehouseLocations.map(loc => (
              <MenuItem key={loc} value={loc}>{loc}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          label="Ship To City"
          value={orderFormData.ship_to_city}
          onChange={handleFormChange('ship_to_city')}
          fullWidth
          sx={{ mb: 2 }}
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          label="Ship To Company"
          value={orderFormData.ship_to_company}
          onChange={handleFormChange('ship_to_company')}
          fullWidth
          sx={{ mb: 2 }}
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          label="Purchase Order"
          value={orderFormData.purchase_order}
          onChange={handleFormChange('purchase_order')}
          fullWidth
          sx={{ mb: 2 }}
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          label="Weight (lbs)"
          type="number"
          value={orderFormData.weight_lbs}
          onChange={handleFormChange('weight_lbs')}
          fullWidth
          sx={{ mb: 2 }}
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          label="Gross Weight (kg)"
          type="number"
          value={orderFormData.gross_weight_kg}
          onChange={handleFormChange('gross_weight_kg')}
          fullWidth
          sx={{ mb: 2 }}
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          label="Net Quantity"
          value={orderFormData.net_quantity}
          onChange={handleFormChange('net_quantity')}
          fullWidth
          sx={{ mb: 2 }}
        />
      </Grid>
    </Grid>
  );

  // Render special requirements tab
  const renderSpecialReqTab = () => (
    <Box sx={{ mt: 2 }}>
      <Grid container spacing={2}>
        {specialRequirementOptions.map(option => (
          <Grid item xs={12} sm={6} key={option.key}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Chip
                icon={option.icon}
                label={option.label}
                onClick={() => handleSpecialRequirementChange(option.key)}
                color={orderFormData.special_requirements[option.key] ? 'secondary' : 'default'}
                variant={orderFormData.special_requirements[option.key] ? 'filled' : 'outlined'}
                sx={{ mr: 1 }}
              />
            </Box>
          </Grid>
        ))}
      </Grid>
      <Box sx={{ mt: 3 }}>
        <TextField
          label="Notes"
          value={orderFormData.notes}
          onChange={handleFormChange('notes')}
          fullWidth
          multiline
          rows={4}
        />
      </Box>
    </Box>
  );

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>{selectedOrder ? 'Edit Order' : 'New Order'}</DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 2 }}>
          <Tabs 
            value={dialogTab} 
            onChange={handleDialogTabChange}
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab label="Basic Information" value="basic" />
            <Tab label="Enhanced Information" value="enhanced" />
            <Tab label="Special Requirements" value="special" />
          </Tabs>
          
          {dialogTab === 'basic' && renderBasicInfoTab()}
          {dialogTab === 'enhanced' && renderEnhancedInfoTab()}
          {dialogTab === 'special' && renderSpecialReqTab()}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSaveOrder} color="primary">
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default OrderDialog;
