import { useEffect, useRef, useState, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { API_BASE_URL } from '../config/api';

export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'reconnecting' | 'error';

export interface WebSocketMessage {
  type: 'reservation_created' | 'reservation_updated' | 'reservation_cancelled' | 'table_assigned' | 'customer_seated' | 'waitlist_updated' | 'config_updated' | 'system_alert';
  data: any;
  timestamp: string;
}

export interface ReservationEvent {
  reservation_id: string;
  action: 'created' | 'updated' | 'cancelled' | 'confirmed' | 'seated' | 'completed';
  reservation: any;
  timestamp: string;
}

export interface TableEvent {
  table_id: string;
  action: 'assigned' | 'freed' | 'occupied' | 'blocked';
  table: any;
  timestamp: string;
}

export interface WaitlistEvent {
  waitlist_id: string;
  action: 'added' | 'notified' | 'removed' | 'seated';
  entry: any;
  timestamp: string;
}

export interface SystemEvent {
  level: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  service?: string;
  timestamp: string;
}

interface UseWebSocketOptions {
  token?: string;
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onMessage?: (message: WebSocketMessage) => void;
  onReservationEvent?: (event: ReservationEvent) => void;
  onTableEvent?: (event: TableEvent) => void;
  onWaitlistEvent?: (event: WaitlistEvent) => void;
  onSystemEvent?: (event: SystemEvent) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    token,
    autoConnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 10,
    onMessage,
    onReservationEvent,
    onTableEvent,
    onWaitlistEvent,
    onSystemEvent,
    onConnect,
    onDisconnect,
    onError,
  } = options;

  const [status, setStatus] = useState<WebSocketStatus>('disconnected');
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const queryClient = useQueryClient();

  const wsUrl = API_BASE_URL.replace(/^http/, 'ws') + '/ws/reservations';

  const invalidateRelatedQueries = useCallback((messageType: string) => {
    switch (messageType) {
      case 'reservation_created':
      case 'reservation_updated':
      case 'reservation_cancelled':
        queryClient.invalidateQueries({ queryKey: ['reservas'] });
        queryClient.invalidateQueries({ queryKey: ['stats'] });
        queryClient.invalidateQueries({ queryKey: ['activity'] });
        break;

      case 'table_assigned':
      case 'customer_seated':
        queryClient.invalidateQueries({ queryKey: ['mesas'] });
        queryClient.invalidateQueries({ queryKey: ['reservas'] });
        queryClient.invalidateQueries({ queryKey: ['activity'] });
        break;

      case 'waitlist_updated':
        queryClient.invalidateQueries({ queryKey: ['waitlist'] });
        queryClient.invalidateQueries({ queryKey: ['activity'] });
        break;

      case 'config_updated':
        queryClient.invalidateQueries({ queryKey: ['config'] });
        break;

      case 'system_alert':
        queryClient.invalidateQueries({ queryKey: ['system-health'] });
        queryClient.invalidateQueries({ queryKey: ['error-logs'] });
        break;
    }
  }, [queryClient]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setStatus('connecting');

    try {
      const url = token ? `${wsUrl}?token=${token}` : wsUrl;
      const ws = new WebSocket(url);

      ws.onopen = () => {
        setStatus('connected');
        setReconnectAttempts(0);
        onConnect?.();
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);

          // Invalidate related queries for automatic UI updates
          invalidateRelatedQueries(message.type);

          // Call global message handler
          onMessage?.(message);

          // Call specific event handlers
          switch (message.type) {
            case 'reservation_created':
            case 'reservation_updated':
            case 'reservation_cancelled':
              onReservationEvent?.(message.data as ReservationEvent);
              break;

            case 'table_assigned':
            case 'customer_seated':
              onTableEvent?.(message.data as TableEvent);
              break;

            case 'waitlist_updated':
              onWaitlistEvent?.(message.data as WaitlistEvent);
              break;

            case 'system_alert':
              onSystemEvent?.(message.data as SystemEvent);
              break;
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        setStatus('error');
        onError?.(error);
      };

      ws.onclose = () => {
        setStatus('disconnected');
        onDisconnect?.();
        wsRef.current = null;

        // Attempt reconnection with exponential backoff
        if (reconnectAttempts < maxReconnectAttempts) {
          const delay = reconnectInterval * Math.pow(1.5, reconnectAttempts);
          setStatus('reconnecting');
          setReconnectAttempts((prev) => prev + 1);

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      setStatus('error');
    }
  }, [
    token,
    wsUrl,
    reconnectAttempts,
    maxReconnectAttempts,
    reconnectInterval,
    onConnect,
    onDisconnect,
    onError,
    onMessage,
    onReservationEvent,
    onTableEvent,
    onWaitlistEvent,
    onSystemEvent,
    invalidateRelatedQueries,
  ]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setStatus('disconnected');
    setReconnectAttempts(0);
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Message not sent.');
    }
  }, []);

  const reconnect = useCallback(() => {
    disconnect();
    setReconnectAttempts(0);
    connect();
  }, [disconnect, connect]);

  // Auto-connect on mount if enabled
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect]); // Only run on mount/unmount

  return {
    status,
    lastMessage,
    reconnectAttempts,
    connect,
    disconnect,
    reconnect,
    sendMessage,
    isConnected: status === 'connected',
    isConnecting: status === 'connecting',
    isReconnecting: status === 'reconnecting',
    isDisconnected: status === 'disconnected',
    hasError: status === 'error',
  };
}
