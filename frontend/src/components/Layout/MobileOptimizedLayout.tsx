import React, { useState, useEffect } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  useTheme,
  useMediaQuery,
  Fab,
  BottomNavigation,
  BottomNavigationAction,
  Paper,
  SwipeableDrawer,
  Divider,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Chip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Assessment as AssessmentIcon,
  Security as SecurityIcon,
  People as PeopleIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  AccountCircle as AccountCircleIcon,
  Logout as LogoutIcon,
  Home as HomeIcon,
  Timeline as TimelineIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

interface MobileOptimizedLayoutProps {
  children: React.ReactNode;
}

const MobileOptimizedLayout: React.FC<MobileOptimizedLayoutProps> = ({ children }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();
  
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [bottomNavValue, setBottomNavValue] = useState(0);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notifications, setNotifications] = useState(3);

  const navigationItems = [
    { label: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { label: 'HACCP', icon: <SecurityIcon />, path: '/haccp' },
    { label: 'Audits', icon: <AssessmentIcon />, path: '/audits' },
    { label: 'Suppliers', icon: <PeopleIcon />, path: '/suppliers' },
    { label: 'Training', icon: <TimelineIcon />, path: '/training' },
    { label: 'Reports', icon: <AssessmentIcon />, path: '/reports' },
  ];

  const bottomNavItems = [
    { label: 'Home', icon: <HomeIcon />, path: '/dashboard' },
    { label: 'HACCP', icon: <SecurityIcon />, path: '/haccp' },
    { label: 'Audits', icon: <AssessmentIcon />, path: '/audits' },
    { label: 'More', icon: <MenuIcon />, path: '/menu' },
  ];

  useEffect(() => {
    // Update bottom navigation based on current route
    const currentIndex = bottomNavItems.findIndex(item => item.path === location.pathname);
    if (currentIndex !== -1) {
      setBottomNavValue(currentIndex);
    }
  }, [location.pathname]);

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      setDrawerOpen(false);
    }
  };

  const handleBottomNavChange = (event: React.SyntheticEvent, newValue: number) => {
    setBottomNavValue(newValue);
    if (newValue === 3) {
      // "More" option - open drawer
      setDrawerOpen(true);
      setBottomNavValue(0); // Reset to first tab
    } else {
      handleNavigation(bottomNavItems[newValue].path);
    }
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    // Handle logout logic
    handleProfileMenuClose();
    navigate('/login');
  };

  const drawerContent = (
    <Box sx={{ width: 280, pt: 2 }}>
      {/* User Profile Section */}
      <Box sx={{ p: 2, textAlign: 'center', borderBottom: `1px solid ${theme.palette.divider}` }}>
        <Avatar
          sx={{ width: 64, height: 64, mx: 'auto', mb: 2 }}
          src="/path-to-avatar.jpg"
        >
          <AccountCircleIcon />
        </Avatar>
        <Typography variant="h6" gutterBottom>
          John Doe
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Food Safety Manager
        </Typography>
        <Chip 
          label="Active" 
          color="success" 
          size="small" 
          sx={{ mt: 1 }}
        />
      </Box>

      {/* Navigation Menu */}
      <List sx={{ pt: 1 }}>
        {navigationItems.map((item, index) => (
          <ListItem
            key={index}
            button
            onClick={() => handleNavigation(item.path)}
            selected={location.pathname === item.path}
            sx={{
              mx: 1,
              borderRadius: 1,
              mb: 0.5,
              '&.Mui-selected': {
                backgroundColor: theme.palette.primary.light,
                color: theme.palette.primary.contrastText,
                '&:hover': {
                  backgroundColor: theme.palette.primary.main,
                },
              },
            }}
          >
            <ListItemIcon sx={{ color: 'inherit' }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItem>
        ))}
      </List>

      <Divider sx={{ my: 2 }} />

      {/* Quick Actions */}
      <List>
        <ListItem button onClick={() => handleNavigation('/notifications')}>
          <ListItemIcon>
            <Badge badgeContent={notifications} color="error">
              <NotificationsIcon />
            </Badge>
          </ListItemIcon>
          <ListItemText primary="Notifications" />
        </ListItem>
        <ListItem button onClick={() => handleNavigation('/settings')}>
          <ListItemIcon>
            <SettingsIcon />
          </ListItemIcon>
          <ListItemText primary="Settings" />
        </ListItem>
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Top App Bar */}
      <AppBar 
        position="fixed" 
        sx={{ 
          zIndex: theme.zIndex.drawer + 1,
          backgroundColor: theme.palette.background.paper,
          color: theme.palette.text.primary,
          boxShadow: theme.shadows[1],
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            ISO 22000 FSMS
          </Typography>

          <Box display="flex" alignItems="center" gap={1}>
            <IconButton color="inherit" onClick={() => handleNavigation('/notifications')}>
              <Badge badgeContent={notifications} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
            
            <IconButton
              color="inherit"
              onClick={handleProfileMenuOpen}
            >
              <Avatar sx={{ width: 32, height: 32 }}>
                <AccountCircleIcon />
              </Avatar>
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Profile Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <MenuItem onClick={() => { handleNavigation('/profile'); handleProfileMenuClose(); }}>
          <ListItemIcon>
            <AccountCircleIcon fontSize="small" />
          </ListItemIcon>
          Profile
        </MenuItem>
        <MenuItem onClick={() => { handleNavigation('/settings'); handleProfileMenuClose(); }}>
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          Settings
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleLogout}>
          <ListItemIcon>
            <LogoutIcon fontSize="small" />
          </ListItemIcon>
          Logout
        </MenuItem>
      </Menu>

      {/* Drawer */}
      {isMobile ? (
        <SwipeableDrawer
          variant="temporary"
          anchor="left"
          open={drawerOpen}
          onClose={handleDrawerToggle}
          onOpen={() => setDrawerOpen(true)}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile
          }}
          sx={{
            '& .MuiDrawer-paper': {
              width: 280,
              boxSizing: 'border-box',
            },
          }}
        >
          {drawerContent}
        </SwipeableDrawer>
      ) : (
        <Drawer
          variant="permanent"
          sx={{
            width: 280,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: 280,
              boxSizing: 'border-box',
              top: 64, // Account for AppBar height
              height: 'calc(100% - 64px)',
            },
          }}
        >
          {drawerContent}
        </Drawer>
      )}

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          pt: isMobile ? 8 : 8, // Account for AppBar
          pl: isMobile ? 0 : '280px', // Account for drawer
          pb: isMobile ? 8 : 0, // Account for bottom navigation
          minHeight: '100vh',
          backgroundColor: theme.palette.background.default,
        }}
      >
        {children}
      </Box>

      {/* Bottom Navigation (Mobile Only) */}
      {isMobile && (
        <Paper
          sx={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            zIndex: theme.zIndex.appBar,
          }}
          elevation={3}
        >
          <BottomNavigation
            value={bottomNavValue}
            onChange={handleBottomNavChange}
            showLabels
            sx={{
              '& .MuiBottomNavigationAction-root': {
                minWidth: 'auto',
                padding: '6px 12px 8px',
              },
            }}
          >
            {bottomNavItems.map((item, index) => (
              <BottomNavigationAction
                key={index}
                label={item.label}
                icon={item.icon}
                sx={{
                  '&.Mui-selected': {
                    color: theme.palette.primary.main,
                  },
                }}
              />
            ))}
          </BottomNavigation>
        </Paper>
      )}
    </Box>
  );
};

export default MobileOptimizedLayout;
