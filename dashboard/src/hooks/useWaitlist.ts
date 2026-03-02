import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../config/api';

export interface WaitlistEntry {
  id: string;
  nombre: string;
  telefono: string;
  pax: number;
  zona_preferida?: 'Interior' | 'Terraza';
  created_at: string;
  notified: boolean;
  tiempo_espera_estimado?: number;
  notas?: string;
  estado: 'waiting' | 'notified' | 'seated' | 'cancelled';
}

interface WaitlistResponse {
  entries: WaitlistEntry[];
  total: number;
  stats?: {
    total_waiting: number;
    total_party_size: number;
    total_notified: number;
    avg_wait_time_minutes: number;
  };
}

async function fetchWaitlist(): Promise<WaitlistResponse> {
  const response = await api.get('/api/mobile/waitlist');
  return response.data;
}

async function addToWaitlist(data: Partial<WaitlistEntry>): Promise<WaitlistEntry> {
  const response = await api.post('/api/mobile/waitlist', data);
  return response.data;
}

async function removeFromWaitlist(id: string): Promise<void> {
  await api.delete(`/api/mobile/waitlist/${id}`);
}

async function notifyWaitlist(id: string): Promise<void> {
  await api.post(`/api/mobile/waitlist/${id}/notify`, { estado: 'notified' });
}

export function useWaitlist(_token?: string) { // _token mantenido por compatibilidad
  return useQuery({
    queryKey: ['waitlist'],
    queryFn: fetchWaitlist,
    refetchInterval: 30000,
  });
}

export function useAddToWaitlist() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ data }: { data: Partial<WaitlistEntry>; token?: string }) =>
      addToWaitlist(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['waitlist'] });
    },
  });
}

export function useRemoveFromWaitlist() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id }: { id: string; token?: string }) => removeFromWaitlist(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['waitlist'] });
    },
  });
}

export function useNotifyWaitlist() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id }: { id: string; token?: string }) => notifyWaitlist(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['waitlist'] });
    },
  });
}
