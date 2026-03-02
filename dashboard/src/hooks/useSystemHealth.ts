import { useQuery } from '@tanstack/react-query';
import { api } from '../config/api';

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

async function fetchSystemHealth(): Promise<SystemHealth> {
  const response = await api.get('/api/system/health');
  return response.data;
}

async function fetchSystemMetrics(): Promise<SystemMetrics> {
  const response = await api.get('/api/system/metrics');
  return response.data;
}

async function fetchErrorLogs(
  limit: number = 50,
  level?: string,
  service?: string,
  desde?: string
): Promise<ErrorLogsResponse> {
  const params = new URLSearchParams();
  params.append('limit', limit.toString());
  if (level) params.append('level', level);
  if (service) params.append('service', service);
  if (desde) params.append('desde', desde);

  const response = await api.get(`/api/system/logs?${params.toString()}`);
  return response.data;
}

async function fetchUptimeStatus(): Promise<UptimeStatus> {
  const response = await api.get('/api/system/uptime');
  return response.data;
}

export function useSystemHealth() {
  return useQuery({
    queryKey: ['system-health'],
    queryFn: () => fetchSystemHealth(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

export function useSystemMetrics() {
  return useQuery({
    queryKey: ['system-metrics'],
    queryFn: () => fetchSystemMetrics(),
    refetchInterval: 10000,
  });
}

export function useErrorLogs(
  limit: number = 50,
  level?: string,
  service?: string,
  desde?: string
) {
  return useQuery({
    queryKey: ['error-logs', limit, level, service, desde],
    queryFn: () => fetchErrorLogs(limit, level, service, desde),
    refetchInterval: 15000,
  });
}

export function useUptimeStatus() {
  return useQuery({
    queryKey: ['uptime-status'],
    queryFn: () => fetchUptimeStatus(),
    refetchInterval: 60000,
  });
}
