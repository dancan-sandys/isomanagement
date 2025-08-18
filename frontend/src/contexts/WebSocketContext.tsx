import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import useWebSocket, { WebSocketMessage } from '../hooks/useWebSocket';

interface WebSocketContextType {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  lastMessage: WebSocketMessage | null;
  sendMessage: (message: WebSocketMessage) => boolean;
  subscribeToDepartment: (departmentId: number) => boolean;
  subscribeToKPI: (kpiId: number) => boolean;
  connect: () => void;
  disconnect: () => void;
}

const WebSocketContext = createContext<WebSocketContextType | null>(null);

interface WebSocketProviderProps {
  children: ReactNode;
  userId?: number;
  enabled?: boolean;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({
  children,
  userId,
  enabled = true
}) => {
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  
  // Construct WebSocket URL
  const wsUrl = userId && enabled ? 
    `ws://localhost:8000/ws/dashboard/${userId}` : '';

  const {
    isConnected,
    isConnecting,
    error,
    lastMessage,
    sendMessage,
    subscribeToDepartment,
    subscribeToKPI,
    connect,
    disconnect
  } = useWebSocket(wsUrl, {
    onOpen: () => {
      console.log('Dashboard WebSocket connected');
    },
    onClose: () => {
      console.log('Dashboard WebSocket disconnected');
    },
    onError: (error) => {
      console.error('Dashboard WebSocket error:', error);
    },
    onMessage: (message) => {
      console.log('Dashboard WebSocket message:', message);
      setMessages(prev => [...prev.slice(-99), message]); // Keep last 100 messages
      
      // Handle specific message types
      handleWebSocketMessage(message);
    },
    reconnectAttempts: 5,
    reconnectInterval: 3000,
    pingInterval: 30000
  });

  const handleWebSocketMessage = (message: WebSocketMessage) => {
    switch (message.type) {
      case 'connection_established':
        console.log('WebSocket connection established:', message.data);
        break;
        
      case 'dashboard_update':
        // Trigger dashboard refresh
        window.dispatchEvent(new CustomEvent('dashboardUpdate', {
          detail: message.data
        }));
        break;
        
      case 'kpi_update':
        // Trigger KPI update
        window.dispatchEvent(new CustomEvent('kpiUpdate', {
          detail: message.data
        }));
        break;
        
      case 'alert':
        // Trigger alert notification
        window.dispatchEvent(new CustomEvent('newAlert', {
          detail: message.data
        }));
        
        // Show browser notification if permitted
        if (Notification.permission === 'granted') {
          new Notification('Compli FSMS Alert', {
            body: message.data.message,
            icon: '/favicon.ico',
            tag: `alert-${message.data.alert_id}`
          });
        }
        break;
        
      case 'system_status':
        // Trigger system status update
        window.dispatchEvent(new CustomEvent('systemStatusUpdate', {
          detail: message.data
        }));
        break;
        
      case 'subscription_confirmed':
        console.log('Subscription confirmed:', message.data);
        break;
        
      case 'error':
        console.error('WebSocket error message:', message.data);
        break;
        
      case 'pong':
        // Handle ping response (connection health check)
        break;
        
      default:
        console.log('Unhandled WebSocket message type:', message.type);
    }
  };

  // Request notification permission on mount
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  const contextValue: WebSocketContextType = {
    isConnected,
    isConnecting,
    error,
    lastMessage,
    sendMessage,
    subscribeToDepartment,
    subscribeToKPI,
    connect,
    disconnect
  };

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocketContext = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocketContext must be used within a WebSocketProvider');
  }
  return context;
};

// Custom hook for dashboard-specific WebSocket operations
export const useDashboardWebSocket = () => {
  const context = useWebSocketContext();
  
  const subscribeToCurrentDashboard = (departmentId?: number, kpiIds?: number[]) => {
    if (departmentId) {
      context.subscribeToDepartment(departmentId);
    }
    
    if (kpiIds) {
      kpiIds.forEach(kpiId => {
        context.subscribeToKPI(kpiId);
      });
    }
  };
  
  const requestDashboardStats = () => {
    return context.sendMessage({
      type: 'get_stats',
      data: {}
    });
  };
  
  return {
    ...context,
    subscribeToCurrentDashboard,
    requestDashboardStats
  };
};

export default WebSocketContext;