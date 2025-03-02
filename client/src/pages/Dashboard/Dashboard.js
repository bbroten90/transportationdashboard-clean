import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
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
  Button,
  Avatar,
  IconButton,
  Tooltip,
  useTheme,
  alpha,
  LinearProgress,
} from '@mui/material';
import {
  LocalShipping as LocalShippingIcon,
  Assignment as AssignmentIcon,
  TrendingUp as TrendingUpIcon,
  CalendarToday as CalendarIcon,
  MoreVert as MoreVertIcon,
  Refresh as RefreshIcon,
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
  LocationOn as LocationOnIcon,
  LocalShipping as DirectionsTruckIcon,
  Inventory as InventoryIcon,
  PriorityHigh as PriorityHighIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { fleetService, orderService, scheduleService } from '../../services';

// Enhanced stat card with animations and better styling
const StatCard = ({ title, value, icon, color, loading, subtitle, trend }) => {
  const theme = useTheme();
  
  return (
    <Card 
      sx={{ 
        height: '100%',
        position: 'relative',
        overflow: 'hidden',
        transition: 'transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 8px 16px rgba(0,0,0,0.1)',
        },
      }}
    >
      {/* Decorative accent color at top of card */}
      <Box 
        sx={{ 
          position: 'absolute', 
          top: 0, 
          left: 0, 
          right: 0, 
          height: '4px', 
          bgcolor: color,
          zIndex: 1,
        }} 
      />
      
      <CardContent sx={{ p: 3, pt: 2.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Avatar 
              sx={{ 
                bgcolor: alpha(color, 0.1), 
                color: color,
                mr: 2,
                width: 48,
                height: 48,
              }}
            >
              {icon}
            </Avatar>
            <Box>
              <Typography variant="subtitle1" color="text.secondary" fontWeight={500}>
                {title}
              </Typography>
              {subtitle && (
                <Typography variant="caption" color="text.secondary">
                  {subtitle}
                </Typography>
              )}
            </Box>
          </Box>
          
          {trend && (
            <Chip 
              icon={trend > 0 ? <ArrowUpwardIcon fontSize="small" /> : <ArrowDownwardIcon fontSize="small" />} 
              label={`${Math.abs(trend)}%`}
              size="small"
              color={trend > 0 ? 'success' : 'error'}
              sx={{ height: 24 }}
            />
          )}
        </Box>
        
        {loading ? (
          <LinearProgress sx={{ mt: 2, mb: 1 }} />
        ) : (
          <Typography variant="h3" component="div" sx={{ mt: 1, fontWeight: 600 }}>
            {value}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

// Enhanced warehouse status card
const WarehouseStatusCard = ({ warehouse, stats, onClick }) => {
  const theme = useTheme();
  const utilization = stats?.utilization || 0;
  
  return (
    <Card 
      sx={{ 
        mb: 2, 
        cursor: 'pointer',
        transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        },
      }}
      onClick={onClick}
    >
      <CardContent sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Avatar 
              sx={{ 
                bgcolor: alpha(theme.palette.primary.main, 0.1), 
                color: theme.palette.primary.main,
                mr: 1.5,
                width: 36,
                height: 36,
              }}
            >
              <LocationOnIcon />
            </Avatar>
            <Typography variant="subtitle1" fontWeight={500}>
              {warehouse}
            </Typography>
          </Box>
          <Chip
            label={`${utilization.toFixed(1)}% utilized`}
            color={utilization > 80 ? 'error' : utilization > 50 ? 'warning' : 'success'}
            size="small"
          />
        </Box>
        
        <Box sx={{ mt: 1.5 }}>
          <LinearProgress 
            variant="determinate" 
            value={utilization} 
            sx={{ 
              height: 8, 
              borderRadius: 4,
              bgcolor: alpha(theme.palette.primary.main, 0.1),
              '& .MuiLinearProgress-bar': {
                borderRadius: 4,
                bgcolor: utilization > 80 
                  ? theme.palette.error.main 
                  : utilization > 50 
                    ? theme.palette.warning.main 
                    : theme.palette.success.main,
              }
            }} 
          />
        </Box>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1.5 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <DirectionsTruckIcon fontSize="small" sx={{ mr: 0.5, color: 'text.secondary' }} />
            <Typography variant="body2" color="text.secondary">
              {stats?.assignedTrucks || 0}/{stats?.totalTrucks || 0} trucks
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <InventoryIcon fontSize="small" sx={{ mr: 0.5, color: 'text.secondary' }} />
            <Typography variant="body2" color="text.secondary">
              {stats?.assignedTrailers || 0}/{stats?.totalTrailers || 0} trailers
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

// Enhanced order item component
const OrderItem = ({ order, onClick }) => {
  const theme = useTheme();
  
  // Determine priority color
  const getPriorityColor = (priority) => {
    switch(priority) {
      case 'high': return theme.palette.error.main;
      case 'medium': return theme.palette.warning.main;
      default: return theme.palette.success.main;
    }
  };
  
  return (
    <Card 
      sx={{ 
        mb: 2, 
        cursor: 'pointer',
        transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        },
      }}
      onClick={onClick}
    >
      <CardContent sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="subtitle1" fontWeight={500}>
              {order.customer_name}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              {order.ship_from} → {order.ship_to}
            </Typography>
          </Box>
          <Chip
            icon={<PriorityHighIcon fontSize="small" />}
            label={order.priority}
            size="small"
            sx={{ 
              bgcolor: alpha(getPriorityColor(order.priority), 0.1),
              color: getPriorityColor(order.priority),
              fontWeight: 500,
            }}
          />
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', mt: 1.5, flexWrap: 'wrap', gap: 1 }}>
          <Chip 
            label={`ID: ${order.id}`} 
            size="small" 
            variant="outlined" 
            sx={{ height: 24 }}
          />
          <Chip 
            label={`${order.weight_kg} kg`} 
            size="small" 
            variant="outlined" 
            sx={{ height: 24 }}
          />
          <Chip 
            icon={<CalendarIcon fontSize="small" />}
            label={format(new Date(order.pickup_date), 'MMM d, yyyy')} 
            size="small" 
            variant="outlined" 
            sx={{ height: 24 }}
          />
        </Box>
      </CardContent>
    </Card>
  );
};

const Dashboard = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [fleetStats, setFleetStats] = useState(null);
  const [orderStats, setOrderStats] = useState(null);
  const [revenueStats, setRevenueStats] = useState(null);
  const [warehouses, setWarehouses] = useState([]);
  const [pendingOrders, setPendingOrders] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch fleet stats
      const utilization = await fleetService.getFleetUtilization();
      const warehouseList = await fleetService.getWarehouseLocations();
      const trucks = await fleetService.getAvailableTrucks();
      const trailers = await fleetService.getAvailableTrailers();
      
      setFleetStats({
        utilization,
        totalTrucks: trucks.length,
        totalTrailers: trailers.length,
        availableTrucks: trucks.filter(t => !t.assigned).length,
        availableTrailers: trailers.filter(t => !t.assigned).length,
      });
      
      setWarehouses(warehouseList);
      
      // Fetch order stats
      const today = new Date();
      const orderStatsData = await orderService.getDailyOrderStats(today.toISOString());
      setOrderStats(orderStatsData);
      
      // Fetch pending orders
      const pending = await orderService.getOrders({ status: 'pending', limit: 5 });
      setPendingOrders(pending);
      
      // Calculate revenue for today
      const todayRevenue = await scheduleService.calculateDateRevenue(today);
      
      // Calculate revenue for tomorrow
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      const tomorrowRevenue = await scheduleService.calculateDateRevenue(tomorrow);
      
      setRevenueStats({
        today: todayRevenue,
        tomorrow: tomorrowRevenue,
        // Simulated trend data (would be real in production)
        trend: Math.round((todayRevenue - 5000) / 5000 * 100)
      });
      
      setLoading(false);
    } catch (err) {
      setError('Failed to load dashboard data: ' + err.message);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchDashboardData();
    setRefreshing(false);
  };

  const navigateTo = (path) => {
    navigate(path);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight={600} gutterBottom>
            CWS Transportation Dashboard
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Welcome back! Here's what's happening today.
          </Typography>
        </Box>
        <Tooltip title="Refresh dashboard">
          <IconButton 
            onClick={handleRefresh} 
            disabled={refreshing || loading}
            sx={{ 
              bgcolor: alpha(theme.palette.primary.main, 0.1),
              '&:hover': {
                bgcolor: alpha(theme.palette.primary.main, 0.2),
              }
            }}
          >
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {error && (
        <Alert 
          severity="error" 
          sx={{ 
            mb: 3,
            boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
          }}
        >
          {error}
        </Alert>
      )}

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Available Trucks"
            subtitle="Ready for dispatch"
            value={fleetStats ? `${fleetStats.availableTrucks}/${fleetStats.totalTrucks}` : '0'}
            icon={<LocalShippingIcon />}
            color={theme.palette.primary.main}
            loading={loading}
            trend={12} // Simulated trend data
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Available Trailers"
            subtitle="Ready for loading"
            value={fleetStats ? `${fleetStats.availableTrailers}/${fleetStats.totalTrailers}` : '0'}
            icon={<LocalShippingIcon />}
            color={theme.palette.secondary.main}
            loading={loading}
            trend={-5} // Simulated trend data
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Today's Orders"
            subtitle="Pending deliveries"
            value={orderStats ? orderStats.total_orders : '0'}
            icon={<AssignmentIcon />}
            color={theme.palette.info.main}
            loading={loading}
            trend={8} // Simulated trend data
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Today's Revenue"
            subtitle="Projected earnings"
            value={revenueStats ? `$${revenueStats.today.toFixed(2)}` : '$0.00'}
            icon={<TrendingUpIcon />}
            color={theme.palette.success.main}
            loading={loading}
            trend={revenueStats?.trend || 0}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardHeader 
              title="Warehouse Status" 
              titleTypographyProps={{ variant: 'h6', fontWeight: 600 }}
              action={
                <Button
                  variant="outlined"
                  color="primary"
                  size="small"
                  onClick={() => navigateTo('/fleet')}
                >
                  View All
                </Button>
              }
            />
            <Divider />
            <CardContent sx={{ p: 2 }}>
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4, mb: 4 }}>
                  <CircularProgress />
                </Box>
              ) : warehouses.length === 0 ? (
                <Alert severity="info">No warehouses available.</Alert>
              ) : (
                <Box sx={{ maxHeight: 400, overflow: 'auto', pr: 1 }}>
                  {warehouses.map((warehouse) => (
                    <WarehouseStatusCard 
                      key={warehouse}
                      warehouse={warehouse}
                      stats={fleetStats?.utilization?.[warehouse] || {}}
                      onClick={() => navigateTo('/fleet')}
                    />
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardHeader 
              title="Pending Orders" 
              titleTypographyProps={{ variant: 'h6', fontWeight: 600 }}
              action={
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="outlined"
                    color="primary"
                    size="small"
                    onClick={() => navigateTo('/orders')}
                  >
                    View All
                  </Button>
                  <Button
                    variant="contained"
                    color="secondary"
                    size="small"
                    startIcon={<CalendarIcon />}
                    onClick={() => navigateTo('/schedule')}
                  >
                    Schedule
                  </Button>
                </Box>
              }
            />
            <Divider />
            <CardContent sx={{ p: 2 }}>
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4, mb: 4 }}>
                  <CircularProgress />
                </Box>
              ) : pendingOrders.length === 0 ? (
                <Alert severity="info">No pending orders.</Alert>
              ) : (
                <Box sx={{ maxHeight: 400, overflow: 'auto', pr: 1 }}>
                  {pendingOrders.map((order) => (
                    <OrderItem 
                      key={order.id} 
                      order={order}
                      onClick={() => navigateTo('/orders')}
                    />
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
