import React from 'react';
import {
  Box, Typography, Grid, Card, CardContent,
} from '@mui/material';
import {
  LocalShipping as LocalShippingIcon,
  Description as DescriptionIcon,
  Inventory as InventoryIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';

const OrderDetailPanel = ({ order, specialRequirementChips }) => {
  return (
    <Box sx={{ margin: 2 }}>
      <Typography variant="h6" gutterBottom component="div">
        Order Details
      </Typography>
      
      <Grid container spacing={3}>
        {/* Shipping Information */}
        <Grid item xs={12} md={4}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" color="primary" gutterBottom>
                <LocalShippingIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Shipping Information
              </Typography>
              
              <Typography variant="body2" color="text.secondary">
                Ship From Location:
              </Typography>
              <Typography variant="body1" gutterBottom>
                {order.ship_from_location || order.ship_from || 'N/A'}
              </Typography>
              
              <Typography variant="body2" color="text.secondary">
                Ship To Company:
              </Typography>
              <Typography variant="body1" gutterBottom>
                {order.ship_to_company || 'N/A'}
              </Typography>
              
              <Typography variant="body2" color="text.secondary">
                Ship To City:
              </Typography>
              <Typography variant="body1" gutterBottom>
                {order.ship_to_city || order.ship_to || 'N/A'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Order Information */}
        <Grid item xs={12} md={4}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" color="primary" gutterBottom>
                <DescriptionIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Order Information
              </Typography>
              
              <Typography variant="body2" color="text.secondary">
                Manufacturer:
              </Typography>
              <Typography variant="body1" gutterBottom>
                {order.manufacturer || 'N/A'}
              </Typography>
              
              <Typography variant="body2" color="text.secondary">
                Purchase Order:
              </Typography>
              <Typography variant="body1" gutterBottom>
                {order.purchase_order || 'N/A'}
              </Typography>
              
              <Typography variant="body2" color="text.secondary">
                Net Quantity:
              </Typography>
              <Typography variant="body1" gutterBottom>
                {order.net_quantity || 'N/A'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Weight Information */}
        <Grid item xs={12} md={4}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" color="primary" gutterBottom>
                <InventoryIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Weight Information
              </Typography>
              
              <Typography variant="body2" color="text.secondary">
                Weight (kg):
              </Typography>
              <Typography variant="body1" gutterBottom>
                {order.weight_kg || 'N/A'}
              </Typography>
              
              <Typography variant="body2" color="text.secondary">
                Weight (lbs):
              </Typography>
              <Typography variant="body1" gutterBottom>
                {order.weight_lbs || (order.weight_kg ? Math.round(order.weight_kg * 2.20462) : 'N/A')}
              </Typography>
              
              <Typography variant="body2" color="text.secondary">
                Gross Weight (kg):
              </Typography>
              <Typography variant="body1" gutterBottom>
                {order.gross_weight_kg || 'N/A'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Special Requirements */}
        {order.special_requirements && Object.values(order.special_requirements).some(v => v) && (
          <Grid item xs={12}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="subtitle1" color="primary" gutterBottom>
                  <WarningIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Special Requirements
                </Typography>
                
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                  {specialRequirementChips(order.special_requirements)}
                </Box>
                
                {order.notes && (
                  <>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                      Notes:
                    </Typography>
                    <Typography variant="body1">
                      {order.notes}
                    </Typography>
                  </>
                )}
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default OrderDetailPanel;
