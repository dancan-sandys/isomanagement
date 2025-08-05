import React, { useState, useEffect } from 'react';
import {
  Popover,
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Button,
  Chip,
  Badge,
  CircularProgress,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Report as ReportIcon,
  Close as CloseIcon,
  DoneAll as DoneAllIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { RootState } from '../../store';
import {
  fetchUnreadNotifications,
  fetchNotifications,
  markNotificationAsRead,
  markAllNotificationsAsRead,
  deleteNotification,
  clearReadNotifications,
  Notification,
} from '../../store/slices/notificationSlice';

interface NotificationPopupProps {
  anchorEl: HTMLElement | null;
  onClose: () => void;
}

const NotificationPopup: React.FC<NotificationPopupProps> = ({ anchorEl, onClose }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);

  const { unreadNotifications, notifications, unreadCount, loading: notificationsLoading } = useSelector(
    (state: RootState) => state.notifications
  );

  const open = Boolean(anchorEl);

  useEffect(() => {
    if (open) {
      dispatch(fetchUnreadNotifications(10) as any);
      dispatch(fetchNotifications({ page: 1, size: 20 }) as any);
    }
  }, [open, dispatch]);

  const handleNotificationClick = async (notification: Notification) => {
    if (!notification.is_read) {
      await dispatch(markNotificationAsRead(notification.id) as any);
    }
    
    if (notification.action_url) {
      navigate(notification.action_url);
    }
    
    onClose();
  };

  const handleMarkAllAsRead = async () => {
    setLoading(true);
    await dispatch(markAllNotificationsAsRead() as any);
    setLoading(false);
  };

  const handleClearRead = async () => {
    setLoading(true);
    await dispatch(clearReadNotifications() as any);
    setLoading(false);
  };

  const handleDeleteNotification = async (event: React.MouseEvent, notificationId: number) => {
    event.stopPropagation();
    await dispatch(deleteNotification(notificationId) as any);
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'SUCCESS':
        return <CheckCircleIcon color="success" />;
      case 'WARNING':
        return <WarningIcon color="warning" />;
      case 'ERROR':
        return <ErrorIcon color="error" />;
      case 'ALERT':
        return <ReportIcon color="error" />;
      default:
        return <InfoIcon color="info" />;
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    
    return date.toLocaleDateString();
  };

  const renderNotificationItem = (notification: Notification, showActions: boolean = true) => (
    <ListItem
      key={notification.id}
      sx={{
        cursor: 'pointer',
        backgroundColor: notification.is_read ? 'transparent' : 'action.hover',
        '&:hover': {
          backgroundColor: 'action.selected',
        },
        borderLeft: `4px solid ${
          notification.is_read ? 'transparent' : 'primary.main'
        }`,
      }}
      onClick={() => handleNotificationClick(notification)}
    >
      <ListItemIcon sx={{ minWidth: 40 }}>
        {getNotificationIcon(notification.notification_type)}
      </ListItemIcon>
      <ListItemText
        primary={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography
              variant="subtitle2"
              sx={{
                fontWeight: notification.is_read ? 'normal' : 'bold',
                flex: 1,
              }}
            >
              {notification.title}
            </Typography>
            <Chip
              label={notification.priority}
              size="small"
              color={notification.priority === 'CRITICAL' ? 'error' : 'default'}
              variant="outlined"
            />
          </Box>
        }
        secondary={
          <Box>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
              {notification.message}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="caption" color="textSecondary">
                {formatTimeAgo(notification.created_at)}
              </Typography>
              <Chip
                label={notification.category}
                size="small"
                variant="outlined"

              />
            </Box>
          </Box>
        }
      />
      {showActions && (
        <IconButton
          size="small"
          onClick={(e) => handleDeleteNotification(e, notification.id)}
          sx={{ opacity: 0.7, '&:hover': { opacity: 1 } }}
        >
          <DeleteIcon fontSize="small" />
        </IconButton>
      )}
    </ListItem>
  );

  const renderEmptyState = (message: string) => (
    <Box sx={{ p: 3, textAlign: 'center' }}>
      <NotificationsIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
      <Typography variant="body2" color="textSecondary">
        {message}
      </Typography>
    </Box>
  );

  return (
    <Popover
      open={open}
      anchorEl={anchorEl}
      onClose={onClose}
      anchorOrigin={{
        vertical: 'bottom',
        horizontal: 'right',
      }}
      transformOrigin={{
        vertical: 'top',
        horizontal: 'right',
      }}
      PaperProps={{
        sx: {
          width: 400,
          maxHeight: 600,
          mt: 1,
        },
      }}
    >
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <NotificationsIcon />
            Notifications
            {unreadCount > 0 && (
              <Badge badgeContent={unreadCount} color="error" />
            )}
          </Typography>
          <Box>
            <IconButton size="small" onClick={onClose}>
              <CloseIcon />
            </IconButton>
          </Box>
        </Box>
      </Box>

      <Tabs
        value={activeTab}
        onChange={(e, newValue) => setActiveTab(newValue)}
        sx={{ borderBottom: 1, borderColor: 'divider' }}
      >
        <Tab label={`Unread (${unreadCount})`} />
        <Tab label="All" />
      </Tabs>

      <Box sx={{ p: 1 }}>
        {activeTab === 0 && (
          <Box>
            {unreadCount > 0 && (
              <Box sx={{ p: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Button
                  size="small"
                  startIcon={<DoneAllIcon />}
                  onClick={handleMarkAllAsRead}
                  disabled={loading}
                >
                  Mark all as read
                </Button>
                <Button
                  size="small"
                  startIcon={<RefreshIcon />}
                  onClick={() => dispatch(fetchUnreadNotifications(10) as any)}
                  disabled={notificationsLoading}
                >
                  Refresh
                </Button>
              </Box>
            )}
            
            {notificationsLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress size={24} />
              </Box>
            ) : unreadNotifications.length > 0 ? (
              <List sx={{ p: 0 }}>
                {unreadNotifications.map((notification) => renderNotificationItem(notification, true))}
              </List>
            ) : (
              renderEmptyState('No unread notifications')
            )}
          </Box>
        )}

        {activeTab === 1 && (
          <Box>
            <Box sx={{ p: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Button
                size="small"
                startIcon={<DoneAllIcon />}
                onClick={handleMarkAllAsRead}
                disabled={loading}
              >
                Mark all as read
              </Button>
              <Button
                size="small"
                startIcon={<DeleteIcon />}
                onClick={handleClearRead}
                disabled={loading}
              >
                Clear read
              </Button>
            </Box>
            
            {notificationsLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress size={24} />
              </Box>
            ) : notifications.length > 0 ? (
              <List sx={{ p: 0 }}>
                {notifications.map((notification) => renderNotificationItem(notification, true))}
              </List>
            ) : (
              renderEmptyState('No notifications')
            )}
          </Box>
        )}
      </Box>
    </Popover>
  );
};

export default NotificationPopup; 