import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { API_BASE_URL } from '../config/api';

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
}

interface WaitlistResponse {
  entries: WaitlistEntry[];
  total: number;
}

async function fetchWaitlist(token?: string): Promise<WaitlistResponse> {
  const response = await fetch(`${API_BASE_URL}/api/mobile/waitlist`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Error al cargar lista de espera');
  }

  return response.json();
}

async function addToWaitlist(data: Partial<WaitlistEntry>, token?: string): Promise<WaitlistEntry> {
  const response = await fetch(`${API_BASE_URL}/api/mobile/waitlist`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Error al agregar a lista de espera');
  }

  return response.json();
}

async function removeFromWaitlist(id: string, token?: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/mobile/waitlist/${id}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Error al eliminar de lista de espera');
  }
}

async function notifyWaitlist(id: string, token?: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/mobile/waitlist/${id}/notify`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Error al notificar cliente');
  }
}

export function useWaitlist(token?: string) {
  return useQuery({
    queryKey: ['waitlist'],
    queryFn: () => fetchWaitlist(token),
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

export function useAddToWaitlist() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ data, token }: { data: Partial<WaitlistEntry>; token?: string }) =>
      addToWaitlist(data, token),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['waitlist'] });
    },
  });
}

export function useRemoveFromWaitlist() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, token }: { id: string; token?: string }) =>
      removeFromWaitlist(id, token),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['waitlist'] });
    },
  });
}

export function useNotifyWaitlist() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, token }: { id: string; token?: string }) =>
      notifyWaitlist(id, token),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['waitlist'] });
    },
  });
}
