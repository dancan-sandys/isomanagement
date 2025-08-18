import { useState, useEffect, useRef, useCallback } from 'react';

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp?: string;
}

export interface WebSocketOptions {
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  onMessage?: (message: WebSocketMessage) => void;
  reconnectAttempts?: number;
  reconnectInterval?: number;
  pingInterval?: number;
}

export interface WebSocketState {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  lastMessage: WebSocketMessage | null;
  connectionAttempts: number;
}

const useWebSocket = (url: string, options: WebSocketOptions = {}) => {
  const {
    onOpen,
    onClose,
    onError,
    onMessage,
    reconnectAttempts = 5,
    reconnectInterval = 3000,
    pingInterval = 30000
  } = options;

  const [state, setState] = useState<WebSocketState>({
    isConnected: false,
    isConnecting: false,
    error: null,
    lastMessage: null,
    connectionAttempts: 0
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);

  const cleanup = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    if (!mountedRef.current) return;

    setState(prev => ({
      ...prev,
      isConnecting: true,
      error: null
    }));

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        if (!mountedRef.current) return;

        setState(prev => ({
          ...prev,
          isConnected: true,
          isConnecting: false,
          error: null,
          connectionAttempts: 0
        }));

        // Start ping interval
        if (pingInterval > 0) {
          pingIntervalRef.current = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
              ws.send(JSON.stringify({
                type: 'ping',
                data: { timestamp: new Date().toISOString() }
              }));
            }
          }, pingInterval);
        }

        onOpen?.();
      };

      ws.onclose = () => {
        if (!mountedRef.current) return;

        setState(prev => ({
          ...prev,
          isConnected: false,
          isConnecting: false
        }));

        cleanup();
        onClose?.();

        // Attempt to reconnect
        if (state.connectionAttempts < reconnectAttempts) {
          setState(prev => ({
            ...prev,
            connectionAttempts: prev.connectionAttempts + 1
          }));

          reconnectTimeoutRef.current = setTimeout(() => {
            if (mountedRef.current) {
              connect();
            }
          }, reconnectInterval);
        }
      };

      ws.onerror = (error) => {
        if (!mountedRef.current) return;

        setState(prev => ({
          ...prev,
          isConnecting: false,
          error: 'WebSocket connection error'
        }));

        onError?.(error);
      };

      ws.onmessage = (event) => {
        if (!mountedRef.current) return;

        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          
          setState(prev => ({
            ...prev,
            lastMessage: message
          }));

          onMessage?.(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

    } catch (error) {
      setState(prev => ({
        ...prev,
        isConnecting: false,
        error: 'Failed to create WebSocket connection'
      }));
    }
  }, [url, onOpen, onClose, onError, onMessage, reconnectAttempts, reconnectInterval, pingInterval, cleanup, state.connectionAttempts]);

  const disconnect = useCallback(() => {
    cleanup();
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setState(prev => ({
      ...prev,
      isConnected: false,
      isConnecting: false
    }));
  }, [cleanup]);

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
      return true;
    }
    return false;
  }, []);

  const subscribe = useCallback((subscriptionType: string, id: number) => {
    return sendMessage({
      type: `subscribe_${subscriptionType}`,
      data: { [`${subscriptionType}_id`]: id }
    });
  }, [sendMessage]);

  const subscribeToDepartment = useCallback((departmentId: number) => {
    return subscribe('department', departmentId);
  }, [subscribe]);

  const subscribeToKPI = useCallback((kpiId: number) => {
    return subscribe('kpi', kpiId);
  }, [subscribe]);

  // Connect on mount
  useEffect(() => {
    if (url) {
      connect();
    }

    return () => {
      mountedRef.current = false;
      disconnect();
    };
  }, [url]); // Only reconnect if URL changes

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      mountedRef.current = false;
      cleanup();
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [cleanup]);

  return {
    ...state,
    connect,
    disconnect,
    sendMessage,
    subscribeToDepartment,
    subscribeToKPI
  };
};

export default useWebSocket;