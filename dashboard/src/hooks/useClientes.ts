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
  tier: CustomerTier; // Nivel del cliente basado en historial
  total_reservas: number; // Total de reservas históricas
  reservas_completadas: number; // Reservas que llegaron y completaron
  reservas_canceladas: number; // Reservas canceladas por el cliente
  no_shows: number; // Reservas donde no apareció
  primera_reserva: string; // Fecha ISO de primera reserva
  ultima_reserva?: string; // Fecha ISO de última reserva
  gasto_promedio?: number; // Promedio de gasto (si se integra con TPV)
  notas_staff?: string; // Notas generales del staff sobre este cliente
  preferencias: CustomerPreference[]; // Lista de preferencias guardadas
  created_at: string;
  updated_at: string;
}

export interface CustomerPreference {
  id: string;
  customer_id: string;
  tipo: CustomerPreferenceType;
  descripcion: string; // Texto libre de la preferencia
  created_at: string;
}

export interface CustomerNote {
  id: string;
  customer_id: string;
  staff_user_id: string; // Usuario que creó la nota
  staff_user_name: string; // Nombre del usuario para display
  contenido: string; // Texto de la nota
  is_important: boolean; // Marcar nota como importante (VIP)
  created_at: string;
}

export interface ReservationHistory {
  id: string;
  customer_id: string;
  fecha: string; // YYYY-MM-DD
  hora: string; // HH:mm
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
  tasa_no_show_promedio: number; // Porcentaje de no-shows global
  reservas_mes_actual: number;
}

export interface CustomerSearchFilters {
  query?: string; // Búsqueda por nombre o teléfono
  tier?: CustomerTier;
  min_reservas?: number;
  has_notes?: boolean; // Solo clientes con notas del staff
}

// ========================================
// HOOKS - LISTADO Y BÚSQUEDA DE CLIENTES
// ========================================

/**
 * Hook para obtener lista paginada de clientes
 */
export function useCustomers(filters?: CustomerSearchFilters, limit: number = 50, offset: number = 0) {
  return useQuery<{ customers: Customer[]; total: number }>({
    queryKey: ['customers', filters, limit, offset],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.query) params.append('query', filters.query);
      if (filters?.tier) params.append('tier', filters.tier);
      if (filters?.min_reservas) params.append('min_reservas', filters.min_reservas.toString());
      if (filters?.has_notes !== undefined) params.append('has_notes', filters.has_notes.toString());
      params.append('limit', limit.toString());
      params.append('offset', offset.toString());

      const response = await fetch(`${api.baseURL}/api/clients?${params.toString()}`);
      if (!response.ok) throw new Error('Error al cargar clientes');
      return response.json();
    },
  });
}

/**
 * Hook para obtener detalles de un cliente específico
 */
export function useCustomer(customerId: string | null) {
  return useQuery<Customer>({
    queryKey: ['customer', customerId],
    queryFn: async () => {
      if (!customerId) throw new Error('ID de cliente requerido');
      
      const response = await fetch(`${api.baseURL}/api/clients/${customerId}`);
      if (!response.ok) throw new Error('Error al cargar cliente');
      return response.json();
    },
    enabled: !!customerId, // Solo ejecutar si hay customerId
  });
}

/**
 * Hook para obtener estadísticas generales de clientes
 */
export function useCustomerStats() {
  return useQuery<CustomerStats>({
    queryKey: ['customer-stats'],
    queryFn: async () => {
      const response = await fetch(`${api.baseURL}/api/clients/stats`);
      if (!response.ok) throw new Error('Error al cargar estadísticas de clientes');
      return response.json();
    },
  });
}

/**
 * Hook para buscar clientes por nombre o teléfono (búsqueda rápida)
 */
export function useSearchCustomers(query: string) {
  return useQuery<Customer[]>({
    queryKey: ['customers-search', query],
    queryFn: async () => {
      if (!query || query.length < 2) return [];
      
      const response = await fetch(`${api.baseURL}/api/clients/search?q=${encodeURIComponent(query)}`);
      if (!response.ok) throw new Error('Error en búsqueda de clientes');
      return response.json();
    },
    enabled: query.length >= 2, // Solo buscar si hay al menos 2 caracteres
  });
}

// ========================================
// HOOKS - HISTORIAL DE RESERVAS DEL CLIENTE
// ========================================

/**
 * Hook para obtener historial de reservas de un cliente
 */
export function useCustomerReservations(customerId: string | null, limit: number = 20) {
  return useQuery<{ reservations: ReservationHistory[]; total: number }>({
    queryKey: ['customer-reservations', customerId, limit],
    queryFn: async () => {
      if (!customerId) throw new Error('ID de cliente requerido');
      
      const response = await fetch(`${api.baseURL}/api/clients/${customerId}/reservations?limit=${limit}`);
      if (!response.ok) throw new Error('Error al cargar historial de reservas');
      return response.json();
    },
    enabled: !!customerId,
  });
}

// ========================================
// HOOKS - PREFERENCIAS DEL CLIENTE
// ========================================

/**
 * Hook para obtener preferencias de un cliente
 */
export function useCustomerPreferences(customerId: string | null) {
  return useQuery<CustomerPreference[]>({
    queryKey: ['customer-preferences', customerId],
    queryFn: async () => {
      if (!customerId) throw new Error('ID de cliente requerido');
      
      const response = await fetch(`${api.baseURL}/api/clients/${customerId}/preferences`);
      if (!response.ok) throw new Error('Error al cargar preferencias');
      return response.json();
    },
    enabled: !!customerId,
  });
}

/**
 * Hook para agregar una preferencia a un cliente
 */
export function useAddCustomerPreference() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ customerId, tipo, descripcion }: { 
      customerId: string; 
      tipo: CustomerPreferenceType; 
      descripcion: string;
    }) => {
      const response = await fetch(`${api.baseURL}/api/clients/${customerId}/preferences`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tipo, descripcion }),
      });
      if (!response.ok) throw new Error('Error al agregar preferencia');
      return response.json();
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['customer-preferences', variables.customerId] });
      queryClient.invalidateQueries({ queryKey: ['customer', variables.customerId] });
    },
  });
}

/**
 * Hook para eliminar una preferencia
 */
export function useDeleteCustomerPreference() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ customerId, preferenceId }: { customerId: string; preferenceId: string }) => {
      const response = await fetch(`${api.baseURL}/api/clients/${customerId}/preferences/${preferenceId}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Error al eliminar preferencia');
      return response.json();
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['customer-preferences', variables.customerId] });
      queryClient.invalidateQueries({ queryKey: ['customer', variables.customerId] });
    },
  });
}

// ========================================
// HOOKS - NOTAS DEL STAFF SOBRE CLIENTES
// ========================================

/**
 * Hook para obtener notas del staff sobre un cliente
 */
export function useCustomerNotes(customerId: string | null) {
  return useQuery<CustomerNote[]>({
    queryKey: ['customer-notes', customerId],
    queryFn: async () => {
      if (!customerId) throw new Error('ID de cliente requerido');
      
      const response = await fetch(`${api.baseURL}/api/clients/${customerId}/notes`);
      if (!response.ok) throw new Error('Error al cargar notas');
      return response.json();
    },
    enabled: !!customerId,
  });
}

/**
 * Hook para agregar una nota sobre un cliente
 */
export function useAddCustomerNote() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ customerId, contenido, is_important }: { 
      customerId: string; 
      contenido: string; 
      is_important: boolean;
    }) => {
      const response = await fetch(`${api.baseURL}/api/clients/${customerId}/notes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contenido, is_important }),
      });
      if (!response.ok) throw new Error('Error al agregar nota');
      return response.json();
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['customer-notes', variables.customerId] });
      queryClient.invalidateQueries({ queryKey: ['customer', variables.customerId] });
    },
  });
}

/**
 * Hook para eliminar una nota
 */
export function useDeleteCustomerNote() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ customerId, noteId }: { customerId: string; noteId: string }) => {
      const response = await fetch(`${api.baseURL}/api/clients/${customerId}/notes/${noteId}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Error al eliminar nota');
      return response.json();
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['customer-notes', variables.customerId] });
      queryClient.invalidateQueries({ queryKey: ['customer', variables.customerId] });
    },
  });
}

/**
 * Hook para marcar/desmarcar una nota como importante
 */
export function useToggleNoteImportance() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ customerId, noteId, is_important }: { 
      customerId: string; 
      noteId: string;
      is_important: boolean;
    }) => {
      const response = await fetch(`${api.baseURL}/api/clients/${customerId}/notes/${noteId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_important }),
      });
      if (!response.ok) throw new Error('Error al actualizar nota');
      return response.json();
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['customer-notes', variables.customerId] });
    },
  });
}

// ========================================
// HOOKS - ACTUALIZACIÓN DE INFORMACIÓN DEL CLIENTE
// ========================================

/**
 * Hook para actualizar información básica de un cliente
 */
export function useUpdateCustomer() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ customerId, data }: { 
      customerId: string; 
      data: Partial<Pick<Customer, 'nombre' | 'email' | 'notas_staff'>>;
    }) => {
      const response = await fetch(`${api.baseURL}/api/clients/${customerId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Error al actualizar cliente');
      return response.json();
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['customer', variables.customerId] });
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      queryClient.invalidateQueries({ queryKey: ['customer-stats'] });
    },
  });
}

/**
 * Hook para actualizar el tier de un cliente manualmente
 * (normalmente se calcula automáticamente, pero puede ajustarse manualmente)
 */
export function useUpdateCustomerTier() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ customerId, tier }: { customerId: string; tier: CustomerTier }) => {
      const response = await fetch(`${api.baseURL}/api/clients/${customerId}/tier`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tier }),
      });
      if (!response.ok) throw new Error('Error al actualizar tier del cliente');
      return response.json();
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['customer', variables.customerId] });
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      queryClient.invalidateQueries({ queryKey: ['customer-stats'] });
    },
  });
}

// ========================================
// HOOKS - EXPORTACIÓN DE DATOS
// ========================================

/**
 * Hook para exportar lista de clientes a CSV
 */
export function useExportCustomers() {
  return useMutation({
    mutationFn: async (filters?: CustomerSearchFilters) => {
      const params = new URLSearchParams();
      if (filters?.query) params.append('query', filters.query);
      if (filters?.tier) params.append('tier', filters.tier);
      if (filters?.min_reservas) params.append('min_reservas', filters.min_reservas.toString());
      if (filters?.has_notes !== undefined) params.append('has_notes', filters.has_notes.toString());

      const response = await fetch(`${api.baseURL}/api/clients/export?${params.toString()}`);
      if (!response.ok) throw new Error('Error al exportar clientes');
      
      // Descargar CSV
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
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
