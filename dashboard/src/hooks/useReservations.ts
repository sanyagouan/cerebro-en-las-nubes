import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import config from '../config/api';

// ============ TYPES ============

export type ReservationStatus = 'Pendiente' | 'Confirmada' | 'Cancelada' | 'Completada' | 'Sentada' | 'NoShow';
export type ReservationChannel = 'VAPI' | 'WhatsApp' | 'Telefono' | 'Presencial';

export interface Reservation {
  id: string;
  nombre: string;  // customer_name in backend
  telefono: string;  // phone in backend
  fecha: string;  // date in backend
  hora: string;  // time in backend
  pax: number;
  mesa?: string;  // table_name in backend
  estado: ReservationStatus;  // status in backend
  notas?: string;  // notes in backend
  canal: ReservationChannel;
  creado: string;  // created_at in backend
}

export interface ReservationFilters {
  fecha?: string;
  estado?: ReservationStatus;
  mesa?: string;
}

export interface PaginatedReservations {
  reservations: Reservation[];
  total: number;
  offset: number;
  limit: number;
  has_more: boolean;
}

// Backend response (different field names)
interface BackendReservationResponse {
  id: string;
  customer_name: string;
  phone: string;
  date: string;
  time: string;
  pax: number;
  status: string;
  table_id?: string;
  table_name?: string;
  location?: string;
  notes?: string;
  special_requests?: string[];
  created_at: string;
}

// ============ API FUNCTIONS ============

const API_URL = config.API_BASE_URL;

// Transform backend response to frontend Reservation
function transformReservation(backendRes: BackendReservationResponse): Reservation {
  return {
    id: backendRes.id,
    nombre: backendRes.customer_name,
    telefono: backendRes.phone,
    fecha: backendRes.date,
    hora: backendRes.time,
    pax: backendRes.pax,
    mesa: backendRes.table_name,
    estado: backendRes.status as ReservationStatus,
    notas: backendRes.notes,
    canal: 'Telefono', // Default, backend doesn't return this
    creado: backendRes.created_at,
  };
}

// Transform frontend Reservation to backend fields
function transformToBackend(reservation: Partial<Reservation>): Record<string, any> {
  const backendFields: Record<string, any> = {};
  
  if (reservation.nombre !== undefined) backendFields.customer_name = reservation.nombre;
  if (reservation.telefono !== undefined) backendFields.phone = reservation.telefono;
  if (reservation.fecha !== undefined) backendFields.date = reservation.fecha;
  if (reservation.hora !== undefined) backendFields.time = reservation.hora;
  if (reservation.pax !== undefined) backendFields.pax = reservation.pax;
  if (reservation.estado !== undefined) backendFields.status = reservation.estado;
  if (reservation.notas !== undefined) backendFields.notes = reservation.notas;
  
  return backendFields;
}

async function fetchReservations(
  filters?: ReservationFilters,
  offset = 0,
  limit = 100,
  token?: string | null
): Promise<PaginatedReservations> {
  const params = new URLSearchParams();
  params.append('offset', offset.toString());
  params.append('limit', limit.toString());
  
  if (filters?.fecha) params.append('fecha', filters.fecha);
  if (filters?.estado) params.append('estado', filters.estado);
  if (filters?.mesa) params.append('mesa', filters.mesa);
  
  const url = `${API_URL}/api/mobile/reservations?${params.toString()}`;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(url, { headers });
  
  if (!response.ok) {
    throw new Error(`Error fetching reservations: ${response.statusText}`);
  }
  
  const data: {
    reservations: BackendReservationResponse[];
    total: number;
    offset: number;
    limit: number;
    has_more: boolean;
  } = await response.json();
  
  return {
    reservations: data.reservations.map(transformReservation),
    total: data.total,
    offset: data.offset,
    limit: data.limit,
    has_more: data.has_more,
  };
}

async function fetchReservation(id: string): Promise<Reservation> {
  const response = await fetch(`${API_URL}/api/mobile/reservations/${id}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
  
  if (!response.ok) {
    throw new Error(`Error fetching reservation: ${response.statusText}`);
  }
  
  const data: BackendReservationResponse = await response.json();
  return transformReservation(data);
}

async function createReservation(reservationData: Partial<Reservation>): Promise<Reservation> {
  const backendData = transformToBackend(reservationData);
  
  const response = await fetch(`${API_URL}/api/mobile/reservations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(backendData),
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Error creating reservation');
  }
  
  const data: BackendReservationResponse = await response.json();
  return transformReservation(data);
}

async function updateReservation({ id, data }: { id: string; data: Partial<Reservation> }): Promise<Reservation> {
  const backendData = transformToBackend(data);
  
  const response = await fetch(`${API_URL}/api/mobile/reservations/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(backendData),
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Error updating reservation');
  }
  
  const responseData: BackendReservationResponse = await response.json();
  return transformReservation(responseData);
}

async function cancelReservation({ id, motivo, notificar }: { id: string; motivo?: string; notificar?: boolean }): Promise<void> {
  const response = await fetch(`${API_URL}/api/mobile/reservations/${id}/cancel`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      motivo: motivo || '',
      notificar_cliente: notificar ?? true,
    }),
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Error cancelling reservation');
  }
}

async function updateReservationStatus({ id, estado }: { id: string; estado: ReservationStatus }): Promise<void> {
  const response = await fetch(`${API_URL}/api/mobile/reservations/${id}/status`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      reservation_id: id,
      status: estado,
    }),
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Error updating reservation status');
  }
}

// ============ HOOKS ============

export function useReservations(filters?: ReservationFilters, offset = 0, limit = 100, token?: string | null) {
  return useQuery<PaginatedReservations, Error>({
    queryKey: ['reservations', filters, offset, limit],
    queryFn: () => fetchReservations(filters, offset, limit, token),
    staleTime: 30000, // 30 seconds
    enabled: !!token, // Only fetch if authenticated
  });
}

export function useReservation(id: string) {
  return useQuery<Reservation, Error>({
    queryKey: ['reservation', id],
    queryFn: () => fetchReservation(id),
    enabled: !!id,
  });
}

export function useCreateReservation() {
  const queryClient = useQueryClient();
  
  return useMutation<Reservation, Error, Partial<Reservation>>({
    mutationFn: createReservation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reservations'] });
    },
  });
}

export function useUpdateReservation() {
  const queryClient = useQueryClient();
  
  return useMutation<Reservation, Error, { id: string; data: Partial<Reservation> }>({
    mutationFn: updateReservation,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['reservations'] });
      queryClient.invalidateQueries({ queryKey: ['reservation', data.id] });
    },
  });
}

export function useCancelReservation() {
  const queryClient = useQueryClient();
  
  return useMutation<void, Error, { id: string; motivo?: string; notificar?: boolean }>({
    mutationFn: cancelReservation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reservations'] });
    },
  });
}

export function useUpdateReservationStatus() {
  const queryClient = useQueryClient();
  
  return useMutation<void, Error, { id: string; estado: ReservationStatus }>({
    mutationFn: updateReservationStatus,
    onMutate: async ({ id, estado }) => {
      await queryClient.cancelQueries({ queryKey: ['reservations'] });
      
      const previousReservations = queryClient.getQueryData(['reservations']);
      
      // Optimistically update
      queryClient.setQueriesData<PaginatedReservations>(
        { queryKey: ['reservations'] },
        (old) => {
          if (!old) return old;
          return {
            ...old,
            reservations: old.reservations.map((res) =>
              res.id === id ? { ...res, estado } : res
            ),
          };
        }
      );
      
      return { previousReservations } as { previousReservations: PaginatedReservations | undefined };
    },
    onError: (_err, _variables, context) => {
      const typedContext = context as { previousReservations: PaginatedReservations | undefined } | undefined;
      if (typedContext?.previousReservations) {
        queryClient.setQueryData(['reservations'], typedContext.previousReservations);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['reservations'] });
    },
  });
}
