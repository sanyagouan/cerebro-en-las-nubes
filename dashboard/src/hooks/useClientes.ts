import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../config/api';

// ========================================
// INTERFACES Y TIPOS
// ========================================

export type CustomerPreferenceType = 'zona_favorita' | 'solicitud_especial' | 'restriccion_dietetica' | 'ocasion_celebracion';
export type CustomerTier = 'Regular' | 'Frecuente' | 'VIP' | 'Premium';

export interface Customer {
  id: string;
  nombre: string;
  telefono: string;
  email?: string;
  tier: CustomerTier;
  total_reservas: number;
  reservas_completadas: number;
  reservas_canceladas: number;
  no_shows: number;
  primera_reserva: string;
  ultima_reserva?: string;
  gasto_promedio?: number;
  notas_staff?: string;
  preferencias: CustomerPreference[];
  created_at: string;
  updated_at: string;
}

export interface CustomerPreference {
  id: string;
  customer_id: string;
  tipo: CustomerPreferenceType;
  descripcion: string;
  created_at: string;
}

export interface CustomerNote {
  id: string;
  customer_id: string;
  staff_user_id: string;
  staff_user_name: string;
  contenido: string;
  is_important: boolean;
  created_at: string;
}

export interface ReservationHistory {
  id: string;
  customer_id: string;
  fecha: string;
  hora: string;
  pax: number;
  mesa?: string;
  estado: 'Pendiente' | 'Confirmada' | 'Sentada' | 'Completada' | 'Cancelada' | 'NoShow';
  canal: 'VAPI' | 'WhatsApp' | 'Dashboard' | 'Android';
  notas?: string;
  created_at: string;
}

export interface CustomerStats {
  total_clientes: number;
  clientes_vip: number;
  clientes_premium: number;
  clientes_frecuentes: number;
  clientes_regulares: number;
  tasa_no_show_promedio: number;
  reservas_mes_actual: number;
}

export interface CustomerSearchFilters {
  query?: string;
  tier?: CustomerTier;
  min_reservas?: number;
  has_notes?: boolean;
}

// ========================================
// HOOKS — usando Axios con JWT automático
// ========================================

export function useCustomers(filters?: CustomerSearchFilters, limit: number = 50, offset: number = 0) {
  return useQuery<{ customers: Customer[]; total: number }>({
    queryKey: ['customers', filters, limit, offset],
    queryFn: async () => {
      const params: Record<string, any> = { limit, offset };
      if (filters?.query) params.query = filters.query;
      if (filters?.tier) params.tier = filters.tier;
      if (filters?.min_reservas) params.min_reservas = filters.min_reservas;
      if (filters?.has_notes !== undefined) params.has_notes = filters.has_notes;
      const response = await api.get('/api/clients', { params });
      return response.data;
    },
  });
}

export function useCustomer(customerId: string | null) {
  return useQuery<Customer>({
    queryKey: ['customer', customerId],
    queryFn: async () => {
      const response = await api.get(`/api/clients/${customerId}`);
      return response.data;
    },
    enabled: !!customerId,
  });
}

export function useCustomerStats() {
  return useQuery<CustomerStats>({
    queryKey: ['customer-stats'],
    queryFn: async () => {
      const response = await api.get('/api/clients/stats');
      return response.data;
    },
  });
}

export function useSearchCustomers(query: string) {
  return useQuery<Customer[]>({
    queryKey: ['customers-search', query],
    queryFn: async () => {
      if (!query || query.length < 2) return [];
      const response = await api.get('/api/clients/search', { params: { q: query } });
      return response.data;
    },
    enabled: query.length >= 2,
  });
}

export function useCustomerReservations(customerId: string | null, limit: number = 20) {
  return useQuery<{ reservations: ReservationHistory[]; total: number }>({
    queryKey: ['customer-reservations', customerId, limit],
    queryFn: async () => {
      const response = await api.get(`/api/clients/${customerId}/reservations`, { params: { limit } });
      return response.data;
    },
    enabled: !!customerId,
  });
}

export function useCustomerPreferences(customerId: string | null) {
  return useQuery<CustomerPreference[]>({
    queryKey: ['customer-preferences', customerId],
    queryFn: async () => {
      const response = await api.get(`/api/clients/${customerId}/preferences`);
      return response.data;
    },
    enabled: !!customerId,
  });
}

export function useAddCustomerPreference() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ customerId, tipo, descripcion }: {
      customerId: string;
      tipo: CustomerPreferenceType;
      descripcion: string;
    }) => {
      const response = await api.post(`/api/clients/${customerId}/preferences`, { tipo, descripcion });
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['customer-preferences', variables.customerId] });
      queryClient.invalidateQueries({ queryKey: ['customer', variables.customerId] });
    },
  });
}

export function useDeleteCustomerPreference() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ customerId, preferenceId }: { customerId: string; preferenceId: string }) => {
      const response = await api.delete(`/api/clients/${customerId}/preferences/${preferenceId}`);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['customer-preferences', variables.customerId] });
      queryClient.invalidateQueries({ queryKey: ['customer', variables.customerId] });
    },
  });
}

export function useCustomerNotes(customerId: string | null) {
  return useQuery<CustomerNote[]>({
    queryKey: ['customer-notes', customerId],
    queryFn: async () => {
      const response = await api.get(`/api/clients/${customerId}/notes`);
      return response.data;
    },
    enabled: !!customerId,
  });
}

export function useAddCustomerNote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ customerId, contenido, is_important }: {
      customerId: string; contenido: string; is_important: boolean;
    }) => {
      const response = await api.post(`/api/clients/${customerId}/notes`, { contenido, is_important });
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['customer-notes', variables.customerId] });
      queryClient.invalidateQueries({ queryKey: ['customer', variables.customerId] });
    },
  });
}

export function useDeleteCustomerNote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ customerId, noteId }: { customerId: string; noteId: string }) => {
      const response = await api.delete(`/api/clients/${customerId}/notes/${noteId}`);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['customer-notes', variables.customerId] });
      queryClient.invalidateQueries({ queryKey: ['customer', variables.customerId] });
    },
  });
}

export function useToggleNoteImportance() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ customerId, noteId, is_important }: {
      customerId: string; noteId: string; is_important: boolean;
    }) => {
      const response = await api.put(`/api/clients/${customerId}/notes/${noteId}`, { is_important });
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['customer-notes', variables.customerId] });
    },
  });
}

export function useUpdateCustomer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ customerId, data }: {
      customerId: string;
      data: Partial<Pick<Customer, 'nombre' | 'email' | 'notas_staff'>>;
    }) => {
      const response = await api.put(`/api/clients/${customerId}`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['customer', variables.customerId] });
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      queryClient.invalidateQueries({ queryKey: ['customer-stats'] });
    },
  });
}

export function useUpdateCustomerTier() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ customerId, tier }: { customerId: string; tier: CustomerTier }) => {
      const response = await api.put(`/api/clients/${customerId}/tier`, { tier });
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['customer', variables.customerId] });
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      queryClient.invalidateQueries({ queryKey: ['customer-stats'] });
    },
  });
}

export function useExportCustomers() {
  return useMutation({
    mutationFn: async (filters?: CustomerSearchFilters) => {
      const params: Record<string, any> = {};
      if (filters?.query) params.query = filters.query;
      if (filters?.tier) params.tier = filters.tier;
      if (filters?.min_reservas) params.min_reservas = filters.min_reservas;
      if (filters?.has_notes !== undefined) params.has_notes = filters.has_notes;

      const response = await api.get('/api/clients/export', { params, responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const a = document.createElement('a');
      a.href = url;
      a.download = `clientes_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      return { success: true };
    },
  });
}
