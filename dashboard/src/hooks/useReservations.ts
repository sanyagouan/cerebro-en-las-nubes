import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../config/api';

// ============ TYPES ============

export type ReservationStatus = 'Pendiente' | 'Confirmada' | 'Cancelada' | 'Completada' | 'Sentada' | 'NoShow';
export type ReservationChannel = 'VAPI' | 'WhatsApp' | 'Telefono' | 'Presencial';

export interface Reservation {
  id: string;
  nombre: string;
  telefono: string;
  fecha: string;
  hora: string;
  pax: number;
  mesa?: string;
  estado: ReservationStatus;
  notas?: string;
  canal: ReservationChannel;
  creado: string;
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

// ============ TRANSFORM ============

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
    canal: 'Telefono',
    creado: backendRes.created_at,
  };
}

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

// ============ API FUNCTIONS (usando axios con JWT automático) ============

async function fetchReservations(
  filters?: ReservationFilters,
  offset = 0,
  limit = 100
): Promise<PaginatedReservations> {
  const params: Record<string, any> = { offset, limit };
  if (filters?.fecha) params.fecha = filters.fecha;
  if (filters?.estado) params.estado = filters.estado;
  if (filters?.mesa) params.mesa = filters.mesa;

  const response = await api.get('/api/mobile/reservations', { params });
  const data = response.data;

  return {
    reservations: (data.reservations || []).map(transformReservation),
    total: data.total || 0,
    offset: data.offset || 0,
    limit: data.limit || limit,
    has_more: data.has_more || false,
  };
}

async function fetchReservation(id: string): Promise<Reservation> {
  const response = await api.get(`/api/mobile/reservations/${id}`);
  return transformReservation(response.data);
}

async function createReservation(reservationData: Partial<Reservation>): Promise<Reservation> {
  const backendData = transformToBackend(reservationData);
  const response = await api.post('/api/mobile/reservations', backendData);
  return transformReservation(response.data);
}

async function updateReservation({ id, data }: { id: string; data: Partial<Reservation> }): Promise<Reservation> {
  const backendData = transformToBackend(data);
  const response = await api.put(`/api/mobile/reservations/${id}`, backendData);
  return transformReservation(response.data);
}

async function cancelReservation({ id, motivo, notificar }: { id: string; motivo?: string; notificar?: boolean }): Promise<void> {
  await api.post(`/api/mobile/reservations/${id}/cancel`, {
    motivo: motivo || '',
    notificar_cliente: notificar ?? true,
  });
}

async function updateReservationStatus({ id, estado }: { id: string; estado: ReservationStatus }): Promise<void> {
  await api.put(`/api/mobile/reservations/${id}/status`, {
    reservation_id: id,
    status: estado,
  });
}

// ============ HOOKS ============

export function useReservations(filters?: ReservationFilters, offset = 0, limit = 100) {
  return useQuery<PaginatedReservations, Error>({
    queryKey: ['reservations', filters, offset, limit],
    queryFn: () => fetchReservations(filters, offset, limit),
    staleTime: 30000,
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
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['reservations'] });
    },
  });
}
