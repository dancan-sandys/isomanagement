import React, { useState, useEffect } from 'react';
import {
  Box,
  BottomNavigation,
  BottomNavigationAction,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Fab,
  useMediaQuery,
  useTheme,
  Drawer,
  SwipeableDrawer,
  Paper,
  Typography,
  IconButton,
  Badge,
  Avatar,
  Stack,
  Divider,
} from '@mui/material';
import {
  Dashboard,
  Assignment,
  Business,
  Description,
  People,
  Notifications,
  Add,
  Edit,
  Camera,
  QrCodeScanner,
  Schedule,
  CheckCircle,
  Warning,
  Star,
  Search,
  Menu,
  Close,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';

interface MobileOptimizedLayoutProps {
  children: React.ReactNode;
}

const MobileOptimizedLayout: React.FC<MobileOptimizedLayoutProps> = ({ children }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useSelector((state: RootState) => state.auth);
  
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.down('lg'));
  
  const [bottomNavValue, setBottomNavValue] = useState(0);
  const [speedDialOpen, setSpeedDialOpen] = useState(false);
  const [quickActionsOpen, setQuickActionsOpen] = useState(false);

  // Quick action buttons for mobile
  const quickActions = [
    {
      icon: <Assignment />,
      name: 'New Checklist',
      action: () => navigate('/prp'),
      color: 'primary' as const,
    },
    {
      icon: <Camera />,
      name: 'Take Photo',
      action: () => {
        // Trigger camera
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.capture = 'environment';
        input.click();
      },
      color: 'success' as const,
    },
    {
      icon: <QrCodeScanner />,
      name: 'Scan QR',
      action: () => {
        // Implement QR scanner
        console.log('QR Scanner not implemented yet');
      },
      color: 'warning' as const,
    },
    {
      icon: <Schedule />,
      name: 'Quick Log',
      action: () => navigate('/haccp'),
      color: 'info' as const,
    },
  ];

  // Bottom navigation items
  const bottomNavItems = [
    { label: 'Dashboard', icon: <Dashboard />, path: '/dashboard' },
    { label: 'Tasks', icon: <Assignment />, path: '/prp' },
    { label: 'HACCP', icon: <CheckCircle />, path: '/haccp' },
    { label: 'Docs', icon: <Description />, path: '/documents' },
    { label: 'More', icon: <Menu />, path: '/menu' },
  ];

  useEffect(() => {
    // Update bottom navigation based on current path
    const currentPath = location.pathname;
    const navIndex = bottomNavItems.findIndex(item => 
      currentPath.startsWith(item.path) || (item.path === '/dashboard' && currentPath === '/')
    );
    if (navIndex !== -1) {
      setBottomNavValue(navIndex);
    }
  }, [location.pathname]);

  const handleBottomNavChange = (event: React.SyntheticEvent, newValue: number) => {
    setBottomNavValue(newValue);
    const selectedItem = bottomNavItems[newValue];
    
    if (selectedItem.path === '/menu') {
      setQuickActionsOpen(true);
    } else {
      navigate(selectedItem.path);
    }
  };

  if (!isMobile) {
    // Return regular layout for desktop
    return <>{children}</>;
  }

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100vh',
      overflow: 'hidden',
    }}>
      {/* Mobile Header */}
      <Paper 
        elevation={2}
        sx={{ 
          p: 2,
          background: 'linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%)',
          color: 'white',
          position: 'sticky',
          top: 0,
          zIndex: 1100,
        }}
      >
        <Stack direction="row" alignItems="center" justifyContent="space-between">
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Avatar sx={{ 
              width: 32, 
              height: 32, 
              bgcolor: 'rgba(255,255,255,0.2)',
              fontSize: '0.875rem',
              fontWeight: 700,
            }}>
              ISO
            </Avatar>
            <Typography variant="h6" fontWeight={700} noWrap>
              FSMS Mobile
            </Typography>
          </Box>
          
          <Stack direction="row" alignItems="center" spacing={1}>
            <IconButton 
              color="inherit" 
              size="small"
              onClick={() => navigate('/search')}
            >
              <Search />
            </IconButton>
            
            <IconButton 
              color="inherit" 
              size="small"
              onClick={() => navigate('/notifications')}
            >
              <Badge badgeContent={3} color="error">
                <Notifications />
              </Badge>
            </IconButton>

            <Avatar 
              sx={{ width: 28, height: 28 }}
              onClick={() => navigate('/profile')}
            >
              {user?.full_name?.[0] || 'U'}
            </Avatar>
          </Stack>
        </Stack>
      </Paper>

      {/* Main Content */}
      <Box sx={{ 
        flex: 1, 
        overflow: 'auto',
        pb: 8, // Space for bottom navigation
        background: 'linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%)',
      }}>
        {children}
      </Box>

      {/* Speed Dial for Quick Actions */}
      <SpeedDial
        ariaLabel="Quick Actions"
        sx={{ 
          position: 'fixed', 
          bottom: 80, 
          right: 16,
          '& .MuiFab-primary': {
            background: 'linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%)',
          },
        }}
        icon={<SpeedDialIcon />}
        open={speedDialOpen}
        onOpen={() => setSpeedDialOpen(true)}
        onClose={() => setSpeedDialOpen(false)}
      >
        {quickActions.map((action) => (
          <SpeedDialAction
            key={action.name}
            icon={action.icon}
            tooltipTitle={action.name}
            onClick={() => {
              action.action();
              setSpeedDialOpen(false);
            }}
            sx={{
              '& .MuiFab-root': {
                bgcolor: `${action.color}.main`,
                '&:hover': {
                  bgcolor: `${action.color}.dark`,
                  transform: 'scale(1.1)',
                },
              },
            }}
          />
        ))}
      </SpeedDial>

      {/* Bottom Navigation */}
      <Paper 
        sx={{ 
          position: 'fixed', 
          bottom: 0, 
          left: 0, 
          right: 0,
          zIndex: 1100,
          borderTop: '1px solid',
          borderColor: 'divider',
        }} 
        elevation={8}
      >
        <BottomNavigation
          value={bottomNavValue}
          onChange={handleBottomNavChange}
          showLabels
          sx={{
            height: 64,
            '& .MuiBottomNavigationAction-root': {
              minWidth: 0,
              px: 0,
              transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
              '&.Mui-selected': {
                color: 'primary.main',
                transform: 'scale(1.1)',
                '& .MuiBottomNavigationAction-label': {
                  fontSize: '0.75rem',
                  fontWeight: 600,
                },
              },
            },
          }}
        >
          {bottomNavItems.map((item, index) => (
            <BottomNavigationAction
              key={item.label}
              label={item.label}
              icon={
                item.label === 'Tasks' ? (
                  <Badge badgeContent={2} color="error" variant="dot">
                    {item.icon}
                  </Badge>
                ) : item.label === 'More' ? (
                  <Badge badgeContent="•" color="primary">
                    {item.icon}
                  </Badge>
                ) : (
                  item.icon
                )
              }
            />
          ))}
        </BottomNavigation>
      </Paper>

      {/* Quick Actions Menu Drawer */}
      <SwipeableDrawer
        anchor="bottom"
        open={quickActionsOpen}
        onClose={() => setQuickActionsOpen(false)}
        onOpen={() => setQuickActionsOpen(true)}
        PaperProps={{
          sx: {
            borderTopLeftRadius: 24,
            borderTopRightRadius: 24,
            p: 3,
            maxHeight: '50vh',
          },
        }}
      >
        <Box sx={{ 
          width: 40, 
          height: 4, 
          bgcolor: 'grey.300', 
          borderRadius: 2, 
          mx: 'auto', 
          mb: 2 
        }} />
        
        <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
          Quick Actions
        </Typography>
        
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(2, 1fr)', 
          gap: 2,
          mb: 2,
        }}>
          {quickActions.map((action, index) => (
            <Paper
              key={action.name}
              elevation={1}
              sx={{
                p: 2,
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'scale(1.02)',
                  boxShadow: 4,
                },
                '&:active': {
                  transform: 'scale(0.98)',
                },
              }}
              onClick={() => {
                action.action();
                setQuickActionsOpen(false);
              }}
            >
              <Avatar sx={{ 
                bgcolor: `${action.color}.main`, 
                mx: 'auto', 
                mb: 1,
                width: 48,
                height: 48,
              }}>
                {action.icon}
              </Avatar>
              <Typography variant="body2" fontWeight={500}>
                {action.name}
              </Typography>
            </Paper>
          ))}
        </Box>

        <Divider sx={{ my: 2 }} />
        
        <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
          Navigate
        </Typography>
        
        <Stack spacing={1}>
          {[
            { label: 'Suppliers', path: '/suppliers', icon: <Business /> },
            { label: 'Traceability', path: '/traceability', icon: <Star /> },
            { label: 'Non-Conformance', path: '/nonconformance', icon: <Warning /> },
            { label: 'Settings', path: '/settings', icon: <Menu /> },
          ].map((item) => (
            <Paper
              key={item.label}
              elevation={0}
              sx={{
                p: 2,
                cursor: 'pointer',
                bgcolor: 'grey.50',
                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  bgcolor: 'primary.50',
                  transform: 'translateX(4px)',
                },
              }}
              onClick={() => {
                navigate(item.path);
                setQuickActionsOpen(false);
              }}
            >
              <Stack direction="row" alignItems="center" spacing={2}>
                {item.icon}
                <Typography variant="body1" fontWeight={500}>
                  {item.label}
                </Typography>
              </Stack>
            </Paper>
          ))}
        </Stack>
      </SwipeableDrawer>
    </Box>
  );
};

export default MobileOptimizedLayout;
