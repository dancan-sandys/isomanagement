import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Menu,
  MenuItem,
  Skeleton,
  Chip,
  Badge,
  Divider,
  Button,
  Tooltip,
  Avatar
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  Notifications as NotificationsIcon,
  NotificationsActive as NotificationsActiveIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  Clear as ClearIcon,
  FilterList as FilterListIcon,
  Circle as CircleIcon
} from '@mui/icons-material';

import { dashboardService } from '../../../services/dashboardService';
import { DashboardAlert, DashboardStats } from '../../../types/dashboard';

interface AlertFeedWidgetProps {
  config: {
    max_items?: number;
    alert_levels?: ('info' | 'warning' | 'critical')[];
    auto_refresh?: boolean;
    title?: string;
    show_timestamps?: boolean;
    refresh_interval?: number;
  };
  dashboardStats?: DashboardStats | null;
  selectedDepartment?: number | null;
  isEditMode?: boolean;
}

interface AlertItem {
  id: number;
  title: string;
  message: string;
  level: 'info' | 'warning' | 'critical';
  timestamp: string;
  source?: string;
  isRead?: boolean;
  kpi_id?: number;
}

const AlertFeedWidget: React.FC<AlertFeedWidgetProps> = ({
  config,
  dashboardStats,
  selectedDepartment,
  isEditMode = false
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const [filterLevel, setFilterLevel] = useState<string>('all');

  useEffect(() => {
    loadAlerts();
  }, [selectedDepartment, config.max_items]);

  useEffect(() => {
    // Auto-refresh if configured
    if (config.auto_refresh) {
      const refreshInterval = config.refresh_interval || 30000; // 30 seconds default for alerts
      const interval = setInterval(loadAlerts, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [config.auto_refresh, config.refresh_interval]);

  useEffect(() => {
    // Load alerts from dashboard stats if available
    if (dashboardStats?.recent_alerts) {
      const mappedAlerts: AlertItem[] = dashboardStats.recent_alerts.map((alert, index) => ({
        id: alert.id || index,
        title: alert.name || 'System Alert',
        message: alert.message || 'No message available',
        level: (alert.level as 'info' | 'warning' | 'critical') || 'info',
        timestamp: alert.created_at || new Date().toISOString(),
        source: 'Dashboard',
        isRead: false
      }));
      
      setAlerts(mappedAlerts);
      setUnreadCount(mappedAlerts.filter(alert => !alert.isRead).length);
    }
  }, [dashboardStats]);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load dashboard alerts
      const dashboardAlerts = await dashboardService.getDashboardAlerts(config.max_items || 10);
      
      // Convert to AlertItem format
      const alertItems: AlertItem[] = dashboardAlerts.map(alert => ({
        id: alert.id,
        title: alert.name,
        message: alert.description || 'Alert triggered',
        level: alert.alert_level as 'info' | 'warning' | 'critical',
        timestamp: alert.last_triggered_at || alert.created_at,
        source: 'KPI Alert',
        isRead: false,
        kpi_id: alert.kpi_definition_id
      }));

      // Add some mock real-time alerts for demonstration
      const mockAlerts: AlertItem[] = [
        {
          id: -1,
          title: 'CCP Temperature Deviation',
          message: 'Refrigeration unit temperature exceeded critical limit of 4°C',
          level: 'critical',
          timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(), // 5 minutes ago
          source: 'HACCP Monitoring',
          isRead: false
        },
        {
          id: -2,
          title: 'Training Due Reminder',
          message: '15 employees have mandatory food safety training due this week',
          level: 'warning',
          timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(), // 30 minutes ago
          source: 'Training System',
          isRead: false
        },
        {
          id: -3,
          title: 'Supplier Audit Completed',
          message: 'ABC Ingredients supplier audit completed with 92% score',
          level: 'info',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
          source: 'Supplier Management',
          isRead: true
        }
      ];

      const allAlerts = [...mockAlerts, ...alertItems];
      
      // Filter by configured alert levels
      const filteredAlerts = config.alert_levels 
        ? allAlerts.filter(alert => config.alert_levels!.includes(alert.level))
        : allAlerts;

      // Sort by timestamp (newest first)
      const sortedAlerts = filteredAlerts.sort((a, b) => 
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      );

      // Limit to max items
      const limitedAlerts = sortedAlerts.slice(0, config.max_items || 10);

      setAlerts(limitedAlerts);
      setUnreadCount(limitedAlerts.filter(alert => !alert.isRead).length);

    } catch (err) {
      console.error('Error loading alerts:', err);
      setError(err instanceof Error ? err.message : 'Failed to load alerts');
    } finally {
      setLoading(false);
    }
  };

  const getAlertIcon = (level: string) => {
    switch (level) {
      case 'critical':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'info':
      default:
        return <InfoIcon color="info" />;
    }
  };

  const getAlertColor = (level: string) => {
    switch (level) {
      case 'critical':
        return '#f44336';
      case 'warning':
        return '#ff9800';
      case 'info':
      default:
        return '#2196f3';
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setMenuAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
  };

  const handleRefresh = () => {
    loadAlerts();
    handleMenuClose();
  };

  const handleMarkAllRead = () => {
    setAlerts(prev => prev.map(alert => ({ ...alert, isRead: true })));
    setUnreadCount(0);
    handleMenuClose();
  };

  const handleClearAll = () => {
    setAlerts([]);
    setUnreadCount(0);
    handleMenuClose();
  };

  const handleAlertClick = (alertId: number) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === alertId ? { ...alert, isRead: true } : alert
    ));
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  const getTimeAgo = (timestamp: string): string => {
    const now = new Date();
    const alertTime = new Date(timestamp);
    const diffMs = now.getTime() - alertTime.getTime();
    
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  const filteredAlerts = filterLevel === 'all' 
    ? alerts 
    : alerts.filter(alert => alert.level === filterLevel);

  if (loading && alerts.length === 0) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardHeader
          title={<Skeleton variant="text" width="60%" />}
          action={<Skeleton variant="circular" width={40} height={40} />}
        />
        <CardContent>
          {Array.from({ length: 5 }).map((_, index) => (
            <Box key={index} display="flex" alignItems="center" gap={2} mb={2}>
              <Skeleton variant="circular" width={40} height={40} />
              <Box flex={1}>
                <Skeleton variant="text" width="80%" />
                <Skeleton variant="text" width="60%" />
              </Box>
            </Box>
          ))}
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardHeader
          title={
            <Typography variant="h6" color="error">
              Alert Feed Error
            </Typography>
          }
        />
        <CardContent>
          <Typography color="error" variant="body2">
            {error}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card 
      sx={{ 
        height: '100%',
        border: isEditMode ? '2px dashed #ccc' : 'none',
        position: 'relative',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      <CardHeader
        title={
          <Box display="flex" alignItems="center" gap={1}>
            <Badge badgeContent={unreadCount} color="error">
              {unreadCount > 0 ? (
                <NotificationsActiveIcon color="primary" />
              ) : (
                <NotificationsIcon color="primary" />
              )}
            </Badge>
            <Typography variant="h6">
              {config.title || 'Alert Feed'}
            </Typography>
          </Box>
        }
        action={
          <Box display="flex" alignItems="center" gap={1}>
            <Tooltip title="Filter alerts">
              <IconButton 
                size="small"
                onClick={() => setFilterLevel(prev => 
                  prev === 'all' ? 'critical' : 
                  prev === 'critical' ? 'warning' : 
                  prev === 'warning' ? 'info' : 'all'
                )}
              >
                <FilterListIcon />
              </IconButton>
            </Tooltip>
            <IconButton onClick={handleMenuOpen}>
              <MoreVertIcon />
            </IconButton>
          </Box>
        }
        sx={{ pb: 1 }}
      />
      
      <CardContent sx={{ pt: 0, flex: 1, overflow: 'hidden' }}>
        {/* Filter Indicator */}
        {filterLevel !== 'all' && (
          <Box mb={1}>
            <Chip
              label={`Showing ${filterLevel} alerts`}
              size="small"
              onDelete={() => setFilterLevel('all')}
              color="primary"
              variant="outlined"
            />
          </Box>
        )}

        {/* Alert List */}
        {filteredAlerts.length === 0 ? (
          <Box 
            display="flex" 
            flexDirection="column" 
            alignItems="center" 
            justifyContent="center" 
            height="200px"
            textAlign="center"
          >
            <NotificationsIcon sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
            <Typography variant="body2" color="textSecondary">
              No alerts to display
            </Typography>
            <Button 
              size="small" 
              onClick={loadAlerts}
              sx={{ mt: 1 }}
            >
              Refresh
            </Button>
          </Box>
        ) : (
          <List sx={{ py: 0, overflow: 'auto', maxHeight: '400px' }}>
            {filteredAlerts.map((alert, index) => (
              <React.Fragment key={alert.id}>
                <ListItem
                  button
                  onClick={() => handleAlertClick(alert.id)}
                  sx={{
                    borderRadius: 1,
                    mb: 0.5,
                    backgroundColor: alert.isRead ? 'transparent' : 'action.hover',
                    '&:hover': {
                      backgroundColor: 'action.selected'
                    }
                  }}
                >
                  <ListItemIcon>
                    <Box position="relative">
                      <Avatar 
                        sx={{ 
                          width: 32, 
                          height: 32,
                          bgcolor: getAlertColor(alert.level) + '20',
                          color: getAlertColor(alert.level)
                        }}
                      >
                        {getAlertIcon(alert.level)}
                      </Avatar>
                      {!alert.isRead && (
                        <CircleIcon 
                          sx={{ 
                            position: 'absolute',
                            top: -2,
                            right: -2,
                            fontSize: 12,
                            color: 'primary.main'
                          }}
                        />
                      )}
                    </Box>
                  </ListItemIcon>
                  
                  <ListItemText
                    primary={
                      <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            fontWeight: alert.isRead ? 400 : 600,
                            lineHeight: 1.3
                          }}
                        >
                          {alert.title}
                        </Typography>
                        {config.show_timestamps !== false && (
                          <Typography 
                            variant="caption" 
                            color="textSecondary"
                            sx={{ ml: 1, flexShrink: 0 }}
                          >
                            {getTimeAgo(alert.timestamp)}
                          </Typography>
                        )}
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography 
                          variant="caption" 
                          color="textSecondary"
                          sx={{ 
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden',
                            lineHeight: 1.2,
                            mt: 0.5
                          }}
                        >
                          {alert.message}
                        </Typography>
                        {alert.source && (
                          <Chip
                            label={alert.source}
                            size="small"
                            variant="outlined"
                            sx={{ 
                              mt: 0.5, 
                              height: 20, 
                              fontSize: '0.6875rem',
                              borderColor: getAlertColor(alert.level),
                              color: getAlertColor(alert.level)
                            }}
                          />
                        )}
                      </Box>
                    }
                  />
                </ListItem>
                {index < filteredAlerts.length - 1 && <Divider variant="inset" />}
              </React.Fragment>
            ))}
          </List>
        )}
      </CardContent>

      {/* Context Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleRefresh}>
          <RefreshIcon sx={{ mr: 1 }} />
          Refresh Alerts
        </MenuItem>
        <MenuItem onClick={handleMarkAllRead} disabled={unreadCount === 0}>
          <NotificationsIcon sx={{ mr: 1 }} />
          Mark All Read
        </MenuItem>
        <MenuItem onClick={handleClearAll} disabled={alerts.length === 0}>
          <ClearIcon sx={{ mr: 1 }} />
          Clear All
        </MenuItem>
      </Menu>

      {/* Edit Mode Overlay */}
      {isEditMode && (
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'move'
          }}
        >
          <Typography variant="caption" sx={{ 
            backgroundColor: 'white',
            padding: '4px 8px',
            borderRadius: 1,
            fontWeight: 600
          }}>
            Alert Feed Widget
          </Typography>
        </Box>
      )}
    </Card>
  );
};

export default AlertFeedWidget;