import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { notificationAPI } from '../../services/api';

// Types
export interface Notification {
  id: number;
  user_id: number;
  title: string;
  message: string;
  notification_type: 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR' | 'ALERT';
  category: 'SYSTEM' | 'HACCP' | 'PRP' | 'SUPPLIER' | 'TRACEABILITY' | 'DOCUMENT' | 'USER' | 'TRAINING' | 'AUDIT' | 'MAINTENANCE';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  is_read: boolean;
  read_at?: string;
  action_url?: string;
  action_text?: string;
  notification_data?: any;
  created_at: string;
  expires_at?: string;
}

export interface NotificationSummary {
  total: number;
  unread: number;
  by_category: { [key: string]: number };
  by_priority: { [key: string]: number };
}

export interface NotificationState {
  notifications: Notification[];
  unreadNotifications: Notification[];
  summary: NotificationSummary | null;
  loading: boolean;
  error: string | null;
  unreadCount: number;
}

const initialState: NotificationState = {
  notifications: [],
  unreadNotifications: [],
  summary: null,
  loading: false,
  error: null,
  unreadCount: 0,
};

// Async thunks
export const fetchNotifications = createAsyncThunk(
  'notifications/fetchNotifications',
  async (params?: { page?: number; size?: number; is_read?: boolean }) => {
    const response = await notificationAPI.getNotifications(params);
    return response;
  }
);

export const fetchUnreadNotifications = createAsyncThunk(
  'notifications/fetchUnreadNotifications',
  async (limit: number = 10) => {
    const response = await notificationAPI.getUnreadNotifications(limit);
    return response;
  }
);

export const fetchNotificationSummary = createAsyncThunk(
  'notifications/fetchNotificationSummary',
  async () => {
    const response = await notificationAPI.getNotificationSummary();
    return response;
  }
);

export const markNotificationAsRead = createAsyncThunk(
  'notifications/markAsRead',
  async (id: number) => {
    const response = await notificationAPI.markAsRead(id);
    return { id, notification: response };
  }
);

export const markAllNotificationsAsRead = createAsyncThunk(
  'notifications/markAllAsRead',
  async () => {
    const response = await notificationAPI.markAllAsRead();
    return response;
  }
);

export const deleteNotification = createAsyncThunk(
  'notifications/deleteNotification',
  async (id: number) => {
    await notificationAPI.deleteNotification(id);
    return id;
  }
);

export const clearReadNotifications = createAsyncThunk(
  'notifications/clearReadNotifications',
  async () => {
    const response = await notificationAPI.clearReadNotifications();
    return response;
  }
);

const notificationSlice = createSlice({
  name: 'notifications',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    addNotification: (state, action: PayloadAction<Notification>) => {
      state.notifications.unshift(action.payload);
      if (!action.payload.is_read) {
        state.unreadNotifications.unshift(action.payload);
        state.unreadCount += 1;
      }
    },
    updateUnreadCount: (state, action: PayloadAction<number>) => {
      state.unreadCount = action.payload;
    },
  },
  extraReducers: (builder) => {
    // Fetch notifications
    builder
      .addCase(fetchNotifications.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchNotifications.fulfilled, (state, action) => {
        state.loading = false;
        state.notifications = action.payload.items;
      })
      .addCase(fetchNotifications.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch notifications';
      });

    // Fetch unread notifications
    builder
      .addCase(fetchUnreadNotifications.pending, (state) => {
        state.error = null;
      })
      .addCase(fetchUnreadNotifications.fulfilled, (state, action) => {
        state.unreadNotifications = action.payload;
        state.unreadCount = action.payload.length;
      })
      .addCase(fetchUnreadNotifications.rejected, (state, action) => {
        state.error = action.error.message || 'Failed to fetch unread notifications';
      });

    // Fetch notification summary
    builder
      .addCase(fetchNotificationSummary.pending, (state) => {
        state.error = null;
      })
      .addCase(fetchNotificationSummary.fulfilled, (state, action) => {
        state.summary = action.payload;
        state.unreadCount = action.payload.unread;
      })
      .addCase(fetchNotificationSummary.rejected, (state, action) => {
        state.error = action.error.message || 'Failed to fetch notification summary';
      });

    // Mark notification as read
    builder
      .addCase(markNotificationAsRead.fulfilled, (state, action) => {
        const { id, notification } = action.payload;
        // Update in notifications array
        const notificationIndex = state.notifications.findIndex(n => n.id === id);
        if (notificationIndex !== -1) {
          state.notifications[notificationIndex] = notification;
        }
        // Remove from unread notifications
        state.unreadNotifications = state.unreadNotifications.filter(n => n.id !== id);
        state.unreadCount = Math.max(0, state.unreadCount - 1);
      });

    // Mark all notifications as read
    builder
      .addCase(markAllNotificationsAsRead.fulfilled, (state) => {
        state.notifications = state.notifications.map(n => ({ ...n, is_read: true }));
        state.unreadNotifications = [];
        state.unreadCount = 0;
      });

    // Delete notification
    builder
      .addCase(deleteNotification.fulfilled, (state, action) => {
        const deletedId = action.payload;
        state.notifications = state.notifications.filter(n => n.id !== deletedId);
        state.unreadNotifications = state.unreadNotifications.filter(n => n.id !== deletedId);
        // Recalculate unread count
        state.unreadCount = state.unreadNotifications.length;
      });

    // Clear read notifications
    builder
      .addCase(clearReadNotifications.fulfilled, (state) => {
        state.notifications = state.notifications.filter(n => !n.is_read);
      });
  },
});

export const { clearError, addNotification, updateUnreadCount } = notificationSlice.actions;
export default notificationSlice.reducer; 