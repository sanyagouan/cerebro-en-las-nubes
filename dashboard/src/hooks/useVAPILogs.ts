import { useQuery } from '@tanstack/react-query';
import { api } from '../config/api';

export interface VAPICall {
  id: string;
  call_id: string;
  phone_number: string;
  direction: 'inbound' | 'outbound';
  status: 'completed' | 'failed' | 'in-progress' | 'no-answer' | 'busy';
  duration_seconds?: number;
  started_at: string;
  ended_at?: string;
  transcript?: string;
  summary?: string;
  reservation_created?: boolean;
  reservation_id?: string;
  cost?: number;
  metadata?: {
    customer_name?: string;
    party_size?: number;
    date?: string;
    time?: string;
    error_message?: string;
  };
}

export interface VAPIAnalytics {
  total_calls: number;
  completed_calls: number;
  failed_calls: number;
  avg_duration_seconds: number;
  total_cost: number;
  conversion_rate: number;
  reservations_created: number;
  calls_by_status: {
    completed: number;
    failed: number;
    no_answer: number;
    busy: number;
  };
  calls_by_hour: Array<{
    hour: number;
    count: number;
  }>;
}

interface VAPILogsResponse {
  calls: VAPICall[];
  total: number;
  analytics?: VAPIAnalytics;
}

async function fetchVAPILogs(
  limit: number = 100,
  status?: string,
  desde?: string,
  hasta?: string
): Promise<VAPILogsResponse> {
  const params = new URLSearchParams();
  params.append('limit', limit.toString());
  if (status) params.append('status', status);
  if (desde) params.append('desde', desde);
  if (hasta) params.append('hasta', hasta);

  const response = await api.get(`/api/vapi/logs?${params.toString()}`);
  return response.data;
}

async function fetchVAPIAnalytics(
  desde?: string,
  hasta?: string
): Promise<VAPIAnalytics> {
  const params = new URLSearchParams();
  if (desde) params.append('desde', desde);
  if (hasta) params.append('hasta', hasta);

  const response = await api.get(`/api/vapi/analytics?${params.toString()}`);
  return response.data;
}

async function fetchVAPICall(
  callId: string
): Promise<VAPICall> {
  const response = await api.get(`/api/vapi/logs/${callId}`);
  return response.data;
}

export function useVAPILogs(
  limit: number = 100,
  status?: string,
  desde?: string,
  hasta?: string
) {
  return useQuery({
    queryKey: ['vapi-logs', limit, status, desde, hasta],
    queryFn: () => fetchVAPILogs(limit, status, desde, hasta),
    refetchInterval: 10000,
  });
}

export function useVAPIAnalytics(
  desde?: string,
  hasta?: string
) {
  return useQuery({
    queryKey: ['vapi-analytics', desde, hasta],
    queryFn: () => fetchVAPIAnalytics(desde, hasta),
    refetchInterval: 30000,
  });
}

export function useVAPICall(callId: string) {
  return useQuery({
    queryKey: ['vapi-call', callId],
    queryFn: () => fetchVAPICall(callId),
    enabled: !!callId,
  });
}
