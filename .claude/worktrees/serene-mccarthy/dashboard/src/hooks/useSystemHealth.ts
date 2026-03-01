import { useQuery } from '@tanstack/react-query';
import { API_BASE_URL } from '../config/api';

export interface HealthCheck {
  status: 'healthy' | 'unhealthy' | 'degraded';
  service: string;
  message?: string;
  error?: string;
  timestamp: string;
}

export interface SystemHealth {
  overall_status: 'healthy' | 'unhealthy' | 'degraded';
  services: {
    backend: HealthCheck;
    redis: HealthCheck;
    airtable: HealthCheck;
    vapi: HealthCheck;
    twilio: HealthCheck;
  };
  timestamp: string;
}

export interface SystemMetrics {
  cpu_usage_percent: number;
  memory_usage_mb: number;
  memory_total_mb: number;
  memory_percent: number;
  requests_per_minute: number;
  avg_response_time_ms: number;
  active_websocket_connections: number;
  cache_hit_rate_percent: number;
  uptime_seconds: number;
  timestamp: string;
}

export interface ErrorLog {
  id: string;
  level: 'error' | 'critical' | 'warning';
  message: string;
  timestamp: string;
  service: string;
  stack_trace?: string;
  metadata?: Record<string, any>;
}

interface ErrorLogsResponse {
  logs: ErrorLog[];
  total: number;
}

export interface UptimeStatus {
  uptime_seconds: number;
  uptime_formatted: string;
  started_at: string;
  current_time: string;
  healthy_since: string;
}

async function fetchSystemHealth(token?: string): Promise<SystemHealth> {
  const response = await fetch(`${API_BASE_URL}/api/system/health`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Error al cargar estado del sistema');
  }

  return response.json();
}

async function fetchSystemMetrics(token?: string): Promise<SystemMetrics> {
  const response = await fetch(`${API_BASE_URL}/api/system/metrics`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Error al cargar métricas del sistema');
  }

  return response.json();
}

async function fetchErrorLogs(
  limit: number = 50,
  level?: string,
  service?: string,
  desde?: string,
  token?: string
): Promise<ErrorLogsResponse> {
  const params = new URLSearchParams();
  params.append('limit', limit.toString());
  if (level) params.append('level', level);
  if (service) params.append('service', service);
  if (desde) params.append('desde', desde);

  const response = await fetch(`${API_BASE_URL}/api/system/logs?${params}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Error al cargar logs de errores');
  }

  return response.json();
}

async function fetchUptimeStatus(token?: string): Promise<UptimeStatus> {
  const response = await fetch(`${API_BASE_URL}/api/system/uptime`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Error al cargar uptime del sistema');
  }

  return response.json();
}

export function useSystemHealth(token?: string) {
  return useQuery({
    queryKey: ['system-health'],
    queryFn: () => fetchSystemHealth(token),
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

export function useSystemMetrics(token?: string) {
  return useQuery({
    queryKey: ['system-metrics'],
    queryFn: () => fetchSystemMetrics(token),
    refetchInterval: 10000, // Refetch every 10 seconds for real-time monitoring
  });
}

export function useErrorLogs(
  limit: number = 50,
  level?: string,
  service?: string,
  desde?: string,
  token?: string
) {
  return useQuery({
    queryKey: ['error-logs', limit, level, service, desde],
    queryFn: () => fetchErrorLogs(limit, level, service, desde, token),
    refetchInterval: 15000, // Refetch every 15 seconds
  });
}

export function useUptimeStatus(token?: string) {
  return useQuery({
    queryKey: ['uptime-status'],
    queryFn: () => fetchUptimeStatus(token),
    refetchInterval: 60000, // Refetch every 60 seconds
  });
}
