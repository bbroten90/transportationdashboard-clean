import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { styled, alpha } from '@mui/material/styles';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Tooltip,
  Paper,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  Dashboard as DashboardIcon,
  LocalShipping as LocalShippingIcon,
  Assignment as AssignmentIcon,
  Calculate as CalculateIcon,
  Schedule as ScheduleIcon,
  PictureAsPdf as PictureAsPdfIcon,
  Help as HelpIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

const drawerWidth = 260;

const Main = styled('main', { shouldForwardProp: (prop) => prop !== 'open' })(
  ({ theme, open }) => ({
    flexGrow: 1,
    padding: theme.spacing(3),
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    marginLeft: `-${drawerWidth}px`,
    ...(open && {
      transition: theme.transitions.create('margin', {
        easing: theme.transitions.easing.easeOut,
        duration: theme.transitions.duration.enteringScreen,
      }),
      marginLeft: 0,
    }),
  }),
);

const AppBarStyled = styled(AppBar, {
  shouldForwardProp: (prop) => prop !== 'open',
})(({ theme, open }) => ({
  transition: theme.transitions.create(['margin', 'width'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  boxShadow: '0 4px 20px 0 rgba(0,0,0,0.1)',
  ...(open && {
    width: `calc(100% - ${drawerWidth}px)`,
    marginLeft: `${drawerWidth}px`,
    transition: theme.transitions.create(['margin', 'width'], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(0, 1),
  // necessary for content to be below app bar
  ...theme.mixins.toolbar,
  justifyContent: 'flex-end',
}));

const LogoContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(2, 2),
  backgroundColor: alpha(theme.palette.primary.main, 0.04),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}));

const StyledListItemButton = styled(ListItemButton)(({ theme }) => ({
  borderRadius: theme.spacing(1),
  margin: theme.spacing(0.5, 1),
  '&.Mui-selected': {
    backgroundColor: alpha(theme.palette.primary.main, 0.15),
    '&:hover': {
      backgroundColor: alpha(theme.palette.primary.main, 0.25),
    },
  },
  '&:hover': {
    backgroundColor: alpha(theme.palette.primary.main, 0.08),
  },
}));

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Fleet Management', icon: <LocalShippingIcon />, path: '/fleet' },
  { text: 'Order Management', icon: <AssignmentIcon />, path: '/orders' },
  { text: 'Rate Calculator', icon: <CalculateIcon />, path: '/rates' },
  { text: 'Schedule Planner', icon: <ScheduleIcon />, path: '/schedule' },
  { text: 'PDF Processor', icon: <PictureAsPdfIcon />, path: '/pdf' },
];

const Layout = ({ children }) => {
  const [open, setOpen] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Auto-close drawer on mobile
  React.useEffect(() => {
    if (isMobile) {
      setOpen(false);
    } else {
      setOpen(true);
    }
  }, [isMobile]);

  const handleDrawerOpen = () => {
    setOpen(true);
  };

  const handleDrawerClose = () => {
    setOpen(false);
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBarStyled position="fixed" open={open}>
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            onClick={handleDrawerOpen}
            edge="start"
            sx={{ mr: 2, ...(open && { display: 'none' }) }}
          >
            <MenuIcon />
          </IconButton>
          
          {/* Small logo in app bar */}
          {!open && (
            <Box sx={{ display: 'flex', alignItems: 'center', mr: 1 }}>
              <Box 
                sx={{ 
                  bgcolor: 'primary.main', 
                  color: 'white', 
                  height: 30, 
                  width: 30, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  borderRadius: 1,
                  fontWeight: 'bold',
                  mr: 1
                }}
              >
                CWS
              </Box>
            </Box>
          )}
          
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            CWS Transportation Dashboard
          </Typography>
          
          <Box sx={{ display: 'flex' }}>
            <Tooltip title="Help">
              <IconButton color="inherit" sx={{ ml: 1 }}>
                <HelpIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Settings">
              <IconButton color="inherit" sx={{ ml: 1 }}>
                <SettingsIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="User Profile">
              <IconButton color="inherit" sx={{ ml: 1 }}>
                <Avatar sx={{ width: 32, height: 32, bgcolor: theme.palette.secondary.main }}>
                  CW
                </Avatar>
              </IconButton>
            </Tooltip>
          </Box>
        </Toolbar>
      </AppBarStyled>
      
      <Drawer
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            boxShadow: '4px 0 10px rgba(0,0,0,0.05)',
          },
        }}
        variant="persistent"
        anchor="left"
        open={open}
      >
        <LogoContainer>
          <Box 
            sx={{ 
              bgcolor: 'primary.main', 
              color: 'white', 
              height: 50, 
              width: 50, 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              borderRadius: 2,
              fontWeight: 'bold',
              mr: 2
            }}
          >
            CWS
          </Box>
          <Typography variant="h6" color="primary" sx={{ fontWeight: 600 }}>
            CWS Logistics
          </Typography>
        </LogoContainer>
        
        <Box sx={{ overflow: 'auto', flexGrow: 1, p: 1 }}>
          <List>
            {menuItems.map((item) => (
              <ListItem key={item.text} disablePadding>
                <StyledListItemButton
                  selected={location.pathname === item.path}
                  onClick={() => {
                    navigate(item.path);
                    if (isMobile) setOpen(false);
                  }}
                >
                  <ListItemIcon sx={{ 
                    color: location.pathname === item.path ? theme.palette.primary.main : 'inherit',
                    minWidth: 40
                  }}>
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText 
                    primary={item.text} 
                    primaryTypographyProps={{ 
                      fontWeight: location.pathname === item.path ? 600 : 400 
                    }}
                  />
                </StyledListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
        
        <Paper elevation={0} sx={{ p: 2, borderTop: `1px solid ${theme.palette.divider}` }}>
          <Typography variant="caption" color="text.secondary">
            CWS Transportation Dashboard v1.0
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                bgcolor: 'success.main',
                mr: 1,
              }}
            />
            <Typography variant="caption" color="text.secondary">
              System Online
            </Typography>
          </Box>
        </Paper>
        
        <DrawerHeader>
          <IconButton onClick={handleDrawerClose}>
            <ChevronLeftIcon />
          </IconButton>
        </DrawerHeader>
      </Drawer>
      
      <Main open={open}>
        <DrawerHeader />
        <Paper 
          elevation={0} 
          sx={{ 
            p: 3, 
            borderRadius: 2, 
            boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
            minHeight: 'calc(100vh - 100px)'
          }}
        >
          {children}
        </Paper>
      </Main>
    </Box>
  );
};

export default Layout;
