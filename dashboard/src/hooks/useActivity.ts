import { useQuery } from '@tanstack/react-query';
import { api } from '../config/api';

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
  desde?: string
): Promise<ActivityResponse> {
  const params: Record<string, any> = { limit };
  if (tipo) params.tipo = tipo;
  if (desde) params.desde = desde;

  try {
    const response = await api.get('/api/mobile/activity', { params });
    return response.data;
  } catch {
    // Endpoint puede no existir aún — devolver datos vacíos sin romper la UI
    return { events: [], total: 0 };
  }
}

export function useActivity(
  limit: number = 50,
  tipo?: string,
  desde?: string,
  _token?: string  // mantenido por compatibilidad pero ya no se usa
) {
  return useQuery({
    queryKey: ['activity', limit, tipo, desde],
    queryFn: () => fetchActivity(limit, tipo, desde),
    refetchInterval: 10000,
  });
}
