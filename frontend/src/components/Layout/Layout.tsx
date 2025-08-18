import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Tooltip,
  Stack,
  Fade,
  Grow,
} from '@mui/material';
import {
  Menu as MenuIcon,
  AccountCircle,
  Notifications,
  Logout,
  Brightness4,
  Brightness7,
  Task,
  Settings,
} from '@mui/icons-material';
import { RootState } from '../../store';
import { logout } from '../../store/slices/authSlice';
import { fetchNotificationSummary } from '../../store/slices/notificationSlice';
import NotificationPopup from '../Notifications/NotificationPopup';
import NavigationDrawer from './NavigationDrawer';
import SideRail from './SideRail';
import AccessibilityPanel from '../Accessibility/AccessibilityPanel';
import { useTheme } from '../../theme/ThemeProvider';

interface LayoutProps {
  children?: React.ReactNode;
}

const drawerWidth = 280;

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useSelector((state: RootState) => state.auth);
  const { unreadCount } = useSelector((state: RootState) => state.notifications);
  const { mode, toggleMode } = useTheme();
  
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notificationAnchorEl, setNotificationAnchorEl] = useState<null | HTMLElement>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    // Add a subtle entrance animation
    const timer = setTimeout(() => {
      setIsLoaded(true);
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationClick = (event: React.MouseEvent<HTMLElement>) => {
    setNotificationAnchorEl(event.currentTarget);
  };

  const handleNotificationClose = () => {
    setNotificationAnchorEl(null);
  };

  // Load notification summary on component mount
  useEffect(() => {
    if (user) {
      dispatch(fetchNotificationSummary() as any);
    }
  }, [dispatch, user]);

  const handleLogout = async () => {
    try {
      await dispatch(logout() as any);
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
      // Force logout even if API fails
      navigate('/login');
    }
    handleProfileMenuClose();
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    setMobileOpen(false);
  };

  // Check if a menu item is currently selected
  const isSelected = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <Fade in={isLoaded} timeout={500}>
      <Box sx={{ display: 'flex' }}>
        {/* Skip Navigation Links for Screen Readers */}
        <a href="#main-content" className="skip-link">
          Skip to main content
        </a>
        <a href="#navigation" className="skip-link">
          Skip to navigation
        </a>
        {/* Enhanced App Bar */}
        <AppBar
          position="fixed"
          sx={{
            // Full width on mobile; account for compact rail on md+
            width: { md: 'calc(100% - 72px)' },
            ml: { md: '72px' },
            backgroundColor: 'background.paper',
            color: 'text.primary',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.06)',
            borderBottom: '1px solid',
            borderColor: 'divider',
            backdropFilter: 'blur(10px)',
            background: (theme) => theme.palette.mode === 'light' ? 'rgba(255, 255, 255, 0.9)' : 'rgba(30, 41, 59, 0.9)',
            zIndex: 1200,
          }}
        >
          <Toolbar>
            <Grow in={isLoaded} timeout={600}>
              <IconButton
                color="inherit"
                aria-label="open drawer"
                edge="start"
                onClick={handleDrawerToggle}
                sx={{ 
                  mr: 2, 
                  display: { md: 'none' },
                  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': {
                    transform: 'scale(1.1)',
                    backgroundColor: 'rgba(30, 64, 175, 0.08)',
                  },
                }}
              >
                <MenuIcon />
              </IconButton>
            </Grow>
            
            <Grow in={isLoaded} timeout={700}>
              <Box sx={{ flexGrow: 1 }}>
                <Typography 
                  variant="h6" 
                  fontWeight={700} 
                  noWrap
                  sx={{
                    background: 'linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%)',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    textShadow: '0 1px 2px rgba(0,0,0,0.1)',
                  }}
                >
                  Compli FSMS Food Safety Management System
                </Typography>
                <Typography 
                  variant="caption" 
                  color="text.secondary"
                  sx={{ 
                    fontWeight: 500,
                    opacity: 0.8,
                  }}
                >
                  {new Date().toLocaleDateString('en-US', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </Typography>
              </Box>
            </Grow>

            <Grow in={isLoaded} timeout={800}>
              <Stack direction="row" spacing={1} alignItems="center">
                {/* Enhanced Theme Toggle */}
                <Tooltip title={`Switch to ${mode === 'light' ? 'dark' : 'light'} mode`}>
                  <IconButton 
                    color="inherit" 
                    onClick={toggleMode}
                    sx={{
                      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                      '&:hover': {
                        transform: 'rotate(180deg)',
                        backgroundColor: 'rgba(30, 64, 175, 0.08)',
                      },
                    }}
                  >
                    {mode === 'light' ? <Brightness4 /> : <Brightness7 />}
                  </IconButton>
                </Tooltip>

                {/* Enhanced Task Center */}
                <Tooltip title="Task Center">
                  <IconButton 
                    color="inherit"
                    sx={{
                      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                      '&:hover': {
                        transform: 'scale(1.1)',
                        backgroundColor: 'rgba(30, 64, 175, 0.08)',
                      },
                    }}
                  >
                    <Badge 
                      badgeContent={3} 
                      color="error"
                      sx={{
                        '& .MuiBadge-badge': {
                          animation: 'pulse 2s infinite',
                          '@keyframes pulse': {
                            '0%': {
                              boxShadow: '0 0 0 0 rgba(220, 38, 38, 0.7)',
                            },
                            '70%': {
                              boxShadow: '0 0 0 6px rgba(220, 38, 38, 0)',
                            },
                            '100%': {
                              boxShadow: '0 0 0 0 rgba(220, 38, 38, 0)',
                            },
                          },
                        },
                      }}
                    >
                      <Task />
                    </Badge>
                  </IconButton>
                </Tooltip>

                {/* Enhanced Notifications */}
                <Tooltip title="Notifications">
                  <IconButton 
                    color="inherit"
                    onClick={handleNotificationClick}
                    sx={{
                      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                      '&:hover': {
                        transform: 'scale(1.1)',
                        backgroundColor: 'rgba(30, 64, 175, 0.08)',
                      },
                    }}
                  >
                    <Badge 
                      badgeContent={unreadCount} 
                      color="error"
                      sx={{
                        '& .MuiBadge-badge': {
                          animation: unreadCount > 0 ? 'bounce 1s infinite' : 'none',
                          '@keyframes bounce': {
                            '0%, 20%, 53%, 80%, 100%': {
                              transform: 'translate3d(0,0,0)',
                            },
                            '40%, 43%': {
                              transform: 'translate3d(0, -8px, 0)',
                            },
                            '70%': {
                              transform: 'translate3d(0, -4px, 0)',
                            },
                            '90%': {
                              transform: 'translate3d(0, -2px, 0)',
                            },
                          },
                        },
                      }}
                    >
                      <Notifications />
                    </Badge>
                  </IconButton>
                </Tooltip>

                {/* Enhanced User Menu */}
                <Tooltip title="Account">
                  <IconButton
                    color="inherit"
                    onClick={handleProfileMenuOpen}
                    sx={{
                      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                      '&:hover': {
                        transform: 'scale(1.05)',
                        backgroundColor: 'rgba(30, 64, 175, 0.08)',
                      },
                    }}
                  >
                    {user?.profile_picture ? (
                      <Avatar 
                        src={user.profile_picture} 
                        sx={{ 
                          width: 32, 
                          height: 32,
                          border: '2px solid',
                          borderColor: 'primary.main',
                          boxShadow: '0 2px 8px rgba(30, 64, 175, 0.2)',
                        }} 
                      />
                    ) : (
                      <AccountCircle />
                    )}
                  </IconButton>
                </Tooltip>
              </Stack>
            </Grow>

            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleProfileMenuClose}
              onClick={handleProfileMenuClose}
              TransitionComponent={Grow}
              transitionDuration={200}
              sx={{
                '& .MuiPaper-root': {
                  borderRadius: 12,
                  boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                  border: '1px solid',
                  borderColor: 'divider',
                },
              }}
            >
              <MenuItem 
                onClick={() => handleNavigation('/profile')}
                sx={{
                  borderRadius: 1,
                  mx: 1,
                  mb: 0.5,
                  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': {
                    backgroundColor: 'rgba(30, 64, 175, 0.08)',
                    transform: 'translateX(4px)',
                  },
                }}
              >
                <AccountCircle fontSize="small" sx={{ mr: 1 }} />
                Profile
              </MenuItem>
              {user?.role_name === 'System Administrator' && (
                <MenuItem 
                  onClick={() => handleNavigation('/settings')}
                  sx={{
                    borderRadius: 1,
                    mx: 1,
                    mb: 0.5,
                    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      backgroundColor: 'rgba(30, 64, 175, 0.08)',
                      transform: 'translateX(4px)',
                    },
                  }}
                >
                  <Settings fontSize="small" sx={{ mr: 1 }} />
                  Settings
                </MenuItem>
              )}
              <MenuItem 
                onClick={handleLogout}
                sx={{
                  borderRadius: 1,
                  mx: 1,
                  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': {
                    backgroundColor: 'rgba(220, 38, 38, 0.08)',
                    transform: 'translateX(4px)',
                  },
                }}
              >
                <Logout fontSize="small" sx={{ mr: 1 }} />
                Logout
              </MenuItem>
            </Menu>
          </Toolbar>
        </AppBar>

        {/* Navigation: Mobile gets Drawer; Desktop gets compact SideRail */}
        <Box component="nav" id="navigation">
          {/* Mobile drawer */}
          <Drawer
            variant="temporary"
            open={mobileOpen}
            onClose={handleDrawerToggle}
            ModalProps={{ keepMounted: true }}
            sx={{
              display: { xs: 'block', md: 'none' },
              '& .MuiDrawer-paper': { 
                boxSizing: 'border-box', 
                width: drawerWidth,
                backdropFilter: 'blur(10px)',
              },
            }}
          >
            <NavigationDrawer onNavigate={handleNavigation} isSelected={isSelected} />
          </Drawer>

          {/* Desktop compact rail */}
          {/* Extend a subtle background behind the AppBar to eliminate corner gap */}
          <Box
            sx={{
              position: 'fixed',
              top: 0,
              left: 0,
              width: 72,
              height: { xs: 56, sm: 64 },
              display: { xs: 'none', md: 'block' },
              background: (theme) => theme.palette.mode === 'light' ? 'rgba(255, 255, 255, 0.9)' : 'rgba(30, 41, 59, 0.9)',
              borderRight: '1px solid',
              borderColor: 'divider',
              zIndex: 1200,
            }}
          />
          <SideRail onNavigate={handleNavigation} isSelected={isSelected} />
        </Box>

        {/* Enhanced Main Content */}
        <Box
          component="main"
          id="main-content"
          tabIndex={-1}
          sx={{
            flexGrow: 1,
            p: 3,
            // Leave space for the compact rail on desktop
            ml: { md: `72px` },
            width: { sm: '100%' },
            mt: 8, // Account for AppBar height
            backgroundColor: 'background.default',
            minHeight: '100vh',
            background: (theme) => theme.palette.mode === 'light' 
              ? 'radial-gradient(1200px 600px at -10% -10%, #FFFFFF 0%, #F8FAFC 40%, #F1F5F9 100%)' 
              : 'radial-gradient(1200px 600px at -10% -10%, #0B1220 0%, #0F172A 40%, #111827 100%)',
          }}
        >
          <Box sx={{ minHeight: '100%' }}>
            {children ? children : <Outlet />}
          </Box>
        </Box>

        {/* Enhanced Notification Popup */}
        <NotificationPopup
          anchorEl={notificationAnchorEl}
          onClose={handleNotificationClose}
        />

        {/* Accessibility Panel */}
        <AccessibilityPanel />
      </Box>
    </Fade>
  );
};

export default Layout; 