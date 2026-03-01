import { useQuery } from '@tanstack/react-query';
import { API_BASE_URL } from '../config/api';

export interface ActivityEvent {
  id: string;
  tipo: 'reserva_creada' | 'reserva_editada' | 'reserva_cancelada' | 'mesa_asignada' | 'cliente_sentado' | 'reserva_completada' | 'waitlist_agregado' | 'sistema';
  descripcion: string;
  usuario?: string;
  timestamp: string;
  metadata?: {
    reserva_id?: string;
    mesa_id?: string;
    cliente_nombre?: string;
    cambios?: Record<string, any>;
  };
}

interface ActivityResponse {
  events: ActivityEvent[];
  total: number;
}

async function fetchActivity(
  limit: number = 50,
  tipo?: string,
  desde?: string,
  token?: string
): Promise<ActivityResponse> {
  const params = new URLSearchParams();
  params.append('limit', limit.toString());
  if (tipo) params.append('tipo', tipo);
  if (desde) params.append('desde', desde);

  const response = await fetch(`${API_BASE_URL}/api/mobile/activity?${params}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Error al cargar actividad');
  }

  return response.json();
}

export function useActivity(
  limit: number = 50,
  tipo?: string,
  desde?: string,
  token?: string
) {
  return useQuery({
    queryKey: ['activity', limit, tipo, desde],
    queryFn: () => fetchActivity(limit, tipo, desde, token),
    refetchInterval: 5000, // Refetch every 5 seconds for real-time feel
  });
}
