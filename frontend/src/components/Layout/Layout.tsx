import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useLocation } from 'react-router-dom';
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
  ListItemButton,
  Divider,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Tooltip,
  Collapse,
  Stack,
  Chip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  Description,
  Security,
  Assignment,
  LocalShipping,
  Timeline,
  People,
  Settings,
  Person,
  Notifications,
  AccountCircle,
  Logout,
  ExpandLess,
  ExpandMore,
  Brightness4,
  Brightness7,
  Search,
  Task,
} from '@mui/icons-material';
import { RootState } from '../../store';
import { logout } from '../../store/slices/authSlice';
import { fetchNotificationSummary } from '../../store/slices/notificationSlice';
import { hasRole, isSystemAdministrator, canManageUsers } from '../../store/slices/authSlice';
import NotificationPopup from '../Notifications/NotificationPopup';
import QuickSearch from '../UI/QuickSearch';
import { useTheme } from '../../theme/ThemeProvider';
import { ISO_NAVIGATION } from '../../theme/designSystem';

interface NavigationItem {
  readonly text: string;
  readonly path: string;
}

interface NavigationSection {
  readonly title: string;
  readonly items: readonly NavigationItem[];
}

interface NavigationStructure {
  [key: string]: NavigationSection;
}

interface LayoutProps {
  children: React.ReactNode;
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
  const [expandedSections, setExpandedSections] = useState<string[]>(['dashboard']);

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

  const handleSectionToggle = (sectionKey: string) => {
    setExpandedSections(prev => 
      prev.includes(sectionKey) 
        ? prev.filter(key => key !== sectionKey)
        : [...prev, sectionKey]
    );
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

  const getSectionIcon = (sectionKey: string) => {
    switch (sectionKey) {
      case 'dashboard':
        return <Dashboard />;
      case 'documents':
        return <Description />;
      case 'users':
        return <People />;
      case 'haccp':
        return <Security />;
      case 'prp':
        return <Assignment />;
      case 'suppliers':
        return <LocalShipping />;
      case 'traceability':
        return <Timeline />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  // Filter navigation based on user role and permissions
  const getFilteredNavigation = (): NavigationStructure => {
    if (!user) return {};

    const filteredNavigation: NavigationStructure = {};

    Object.entries(ISO_NAVIGATION).forEach(([sectionKey, section]) => {
      // Check if user has access to this section
      let hasAccess = false;

      switch (sectionKey) {
        case 'dashboard':
          hasAccess = true; // All users can access dashboard
          break;
        case 'documents':
          // All authenticated users can access documents
          hasAccess = true;
          break;
        case 'users':
          // Only System Administrators and QA Managers can access user management
          hasAccess = canManageUsers(user);
          break;
        case 'haccp':
          // QA roles and production roles can access HACCP
          hasAccess = hasRole(user, 'QA Manager') || 
                     hasRole(user, 'QA Specialist') || 
                     hasRole(user, 'Production Manager') || 
                     hasRole(user, 'Production Operator') ||
                     isSystemAdministrator(user);
          break;
        case 'prp':
          // Production roles and maintenance can access PRP
          hasAccess = hasRole(user, 'Production Manager') || 
                     hasRole(user, 'Production Operator') || 
                     hasRole(user, 'Maintenance') ||
                     isSystemAdministrator(user);
          break;
        case 'suppliers':
          // QA roles and management can access suppliers
          hasAccess = hasRole(user, 'QA Manager') || 
                     hasRole(user, 'QA Specialist') || 
                     hasRole(user, 'Production Manager') ||
                     isSystemAdministrator(user);
          break;
        case 'traceability':
          // Production roles and QA can access traceability
          hasAccess = hasRole(user, 'Production Manager') || 
                     hasRole(user, 'Production Operator') || 
                     hasRole(user, 'QA Manager') || 
                     hasRole(user, 'QA Specialist') ||
                     isSystemAdministrator(user);
          break;
        case 'settings':
          // Only System Administrators can access settings
          hasAccess = isSystemAdministrator(user);
          break;
        default:
          hasAccess = true;
      }

      if (hasAccess) {
        filteredNavigation[sectionKey] = section;
      }
    });

    return filteredNavigation;
  };

  const filteredNavigation = getFilteredNavigation();

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Security color="primary" sx={{ fontSize: 32 }} />
          <Box>
            <Typography variant="h6" fontWeight={700} noWrap>
              ISO 22000 FSMS
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Food Safety Management System
            </Typography>
          </Box>
        </Box>
        
        {/* User Info */}
        {user && (
          <Box sx={{ mb: 2, p: 2, backgroundColor: 'action.hover', borderRadius: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Avatar sx={{ width: 32, height: 32 }}>
                {user.profile_picture ? (
                  <img src={user.profile_picture} alt={user.full_name} />
                ) : (
                  <Person fontSize="small" />
                )}
              </Avatar>
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography variant="body2" fontWeight={600} noWrap>
                  {user.full_name}
                </Typography>
                <Typography variant="caption" color="text.secondary" noWrap>
                  {user.role_name || 'Unknown Role'}
                </Typography>
              </Box>
            </Box>
            <Chip 
              label={user.department || 'No Department'} 
              size="small" 
              color="primary" 
              variant="outlined"
            />
          </Box>
        )}
        
        {/* Quick Search */}
        <QuickSearch placeholder="Search..." fullWidth />
      </Box>

      {/* Navigation */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <List sx={{ py: 1 }}>
          {/* ISO Navigation Sections */}
          {filteredNavigation && Object.entries(filteredNavigation).map(([sectionKey, section]) => {
            if (!section || !section.items) {
              return null; // Skip rendering if section or items is undefined
            }
            
            const isExpanded = expandedSections.includes(sectionKey);
            const hasSelectedItem = section.items.some(item => isSelected(item.path));
            
            return (
              <Box key={sectionKey}>
                <ListItem disablePadding>
                  <ListItemButton
                    onClick={() => handleSectionToggle(sectionKey)}
                    sx={{
                      mx: 1,
                      mb: 0.5,
                      borderRadius: 2,
                      backgroundColor: hasSelectedItem ? 'action.selected' : 'transparent',
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      {getSectionIcon(sectionKey)}
                    </ListItemIcon>
                    <ListItemText 
                      primary={section.title}
                      primaryTypographyProps={{
                        fontWeight: hasSelectedItem ? 600 : 400,
                      }}
                    />
                    {isExpanded ? <ExpandLess /> : <ExpandMore />}
                  </ListItemButton>
                </ListItem>
                
                <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                  <List component="div" disablePadding>
                    {section.items.map((item) => {
                      const selected = isSelected(item.path);
                      return (
                        <ListItem key={item.path} disablePadding>
                          <ListItemButton
                            onClick={() => handleNavigation(item.path)}
                            selected={selected}
                            sx={{
                              pl: 4,
                              mx: 1,
                              mb: 0.5,
                              borderRadius: 2,
                              '&.Mui-selected': {
                                backgroundColor: 'primary.main',
                                color: 'primary.contrastText',
                                '&:hover': {
                                  backgroundColor: 'primary.dark',
                                },
                              },
                            }}
                          >
                            <ListItemText 
                              primary={item.text}
                              primaryTypographyProps={{
                                fontSize: '0.875rem',
                                fontWeight: selected ? 600 : 400,
                              }}
                            />
                          </ListItemButton>
                        </ListItem>
                      );
                    })}
                  </List>
                </Collapse>
              </Box>
            );
          })}
        </List>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          backgroundColor: 'background.paper',
          color: 'text.primary',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
          borderBottom: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" fontWeight={600} noWrap>
              ISO 22000 Food Safety Management System
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {new Date().toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </Typography>
          </Box>

          <Stack direction="row" spacing={1} alignItems="center">
            {/* Theme Toggle */}
            <Tooltip title={`Switch to ${mode === 'light' ? 'dark' : 'light'} mode`}>
              <IconButton color="inherit" onClick={toggleMode}>
                {mode === 'light' ? <Brightness4 /> : <Brightness7 />}
              </IconButton>
            </Tooltip>

            {/* Task Center */}
            <Tooltip title="Task Center">
              <IconButton color="inherit">
                <Badge badgeContent={3} color="error">
                  <Task />
                </Badge>
              </IconButton>
            </Tooltip>

            {/* Notifications */}
            <Tooltip title="Notifications">
              <IconButton 
                color="inherit"
                onClick={handleNotificationClick}
              >
                <Badge badgeContent={unreadCount} color="error">
                  <Notifications />
                </Badge>
              </IconButton>
            </Tooltip>

            {/* User Menu */}
            <Tooltip title="Account">
              <IconButton
                color="inherit"
                onClick={handleProfileMenuOpen}
              >
                {user?.profile_picture ? (
                  <Avatar src={user.profile_picture} sx={{ width: 32, height: 32 }} />
                ) : (
                  <AccountCircle />
                )}
              </IconButton>
            </Tooltip>
          </Stack>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleProfileMenuClose}
            onClick={handleProfileMenuClose}
          >
            <MenuItem onClick={() => handleNavigation('/profile')}>
              <ListItemIcon>
                <AccountCircle fontSize="small" />
              </ListItemIcon>
              Profile
            </MenuItem>
            {isSystemAdministrator(user) && (
              <MenuItem onClick={() => handleNavigation('/settings')}>
                <ListItemIcon>
                  <Settings fontSize="small" />
                </ListItemIcon>
                Settings
              </MenuItem>
            )}
            <Divider />
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <Logout fontSize="small" />
              </ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Navigation Drawer */}
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        
        {/* Desktop drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          mt: 8, // Account for AppBar height
          backgroundColor: 'background.default',
          minHeight: '100vh',
        }}
      >
        {children}
      </Box>

      {/* Notification Popup */}
      <NotificationPopup
        anchorEl={notificationAnchorEl}
        onClose={handleNotificationClose}
      />
    </Box>
  );
};

export default Layout; 