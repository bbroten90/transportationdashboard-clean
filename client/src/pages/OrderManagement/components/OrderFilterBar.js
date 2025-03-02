import React from 'react';
import {
  Box, Typography, FormControl, InputLabel, Select, MenuItem, Button
} from '@mui/material';

const OrderFilterBar = ({ 
  filterManufacturer, 
  setFilterManufacturer, 
  filterWarehouse, 
  setFilterWarehouse, 
  filterSpecialReq, 
  setFilterSpecialReq, 
  handleResetFilters,
  manufacturers,
  warehouseLocations,
  specialRequirementOptions
}) => {
  return (
    <Box sx={{ p: 2, display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'center' }}>
      <Typography variant="subtitle1">Filters:</Typography>
      
      <FormControl sx={{ minWidth: 150 }}>
        <InputLabel>Manufacturer</InputLabel>
        <Select
          value={filterManufacturer}
          onChange={(e) => setFilterManufacturer(e.target.value)}
          label="Manufacturer"
          size="small"
        >
          <MenuItem value="">All</MenuItem>
          {manufacturers.map(mfr => (
            <MenuItem key={mfr} value={mfr}>{mfr}</MenuItem>
          ))}
        </Select>
      </FormControl>
      
      <FormControl sx={{ minWidth: 150 }}>
        <InputLabel>Warehouse</InputLabel>
        <Select
          value={filterWarehouse}
          onChange={(e) => setFilterWarehouse(e.target.value)}
          label="Warehouse"
          size="small"
        >
          <MenuItem value="">All</MenuItem>
          {warehouseLocations.map(loc => (
            <MenuItem key={loc} value={loc}>{loc}</MenuItem>
          ))}
        </Select>
      </FormControl>
      
      <FormControl sx={{ minWidth: 180 }}>
        <InputLabel>Special Requirements</InputLabel>
        <Select
          value={filterSpecialReq}
          onChange={(e) => setFilterSpecialReq(e.target.value)}
          label="Special Requirements"
          size="small"
        >
          <MenuItem value="">All</MenuItem>
          {specialRequirementOptions.map(opt => (
            <MenuItem key={opt.key} value={opt.key}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                {opt.icon}
                <Box sx={{ ml: 1 }}>{opt.label}</Box>
              </Box>
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      
      {(filterManufacturer || filterWarehouse || filterSpecialReq) && (
        <Button 
          variant="outlined" 
          size="small" 
          onClick={handleResetFilters}
        >
          Clear Filters
        </Button>
      )}
    </Box>
  );
};

export default OrderFilterBar;
