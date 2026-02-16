import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { API_BASE_URL } from '../config/api';

export interface ClientePreferencias {
  zona_favorita?: 'Interior' | 'Terraza';
  solicitudes_especiales?: string[];
  alergias?: string[];
  ocasiones_especiales?: string[];
}

export interface ClienteHistorialReserva {
  id: string;
  fecha: string;
  hora: string;
  pax: number;
  estado: 'completada' | 'cancelada' | 'no_show';
  mesa_asignada?: string;
  zona?: 'Interior' | 'Terraza';
  valoracion?: number; // 1-5
  notas?: string;
}

export interface ClienteNota {
  id: string;
  contenido: string;
  autor: string;
  timestamp: string;
  tipo: 'general' | 'preferencia' | 'queja' | 'elogio' | 'vip';
  privada: boolean;
}

export interface Cliente {
  id: string;
  nombre: string;
  telefono: string;
  email?: string;
  tipo: 'regular' | 'vip' | 'nuevo' | 'problema';
  total_reservas: number;
  reservas_completadas: number;
  reservas_canceladas: number;
  no_shows: number;
  primera_visita: string;
  ultima_visita?: string;
  valoracion_promedio?: number;
  gasto_promedio?: number;
  preferencias: ClientePreferencias;
  notas: ClienteNota[];
  historial: ClienteHistorialReserva[];
  tags?: string[];
  activo: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ClienteStats {
  total_clientes: number;
  clientes_nuevos_mes: number;
  clientes_vip: number;
  clientes_regulares: number;
  tasa_retencion: number;
  clientes_con_problemas: number;
  distribucion_por_tipo: {
    regular: number;
    vip: number;
    nuevo: number;
    problema: number;
  };
}

interface ClientesResponse {
  clientes: Cliente[];
  total: number;
  stats?: ClienteStats;
}

async function fetchClientes(
  limit: number = 100,
  tipo?: string,
  busqueda?: string,
  token?: string
): Promise<ClientesResponse> {
  const params = new URLSearchParams();
  params.append('limit', limit.toString());
  if (tipo) params.append('tipo', tipo);
  if (busqueda) params.append('busqueda', busqueda);

  const response = await fetch(`${API_BASE_URL}/api/clients?${params}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Error al cargar clientes');
  }

  return response.json();
}

async function fetchCliente(
  clienteId: string,
  token?: string
): Promise<Cliente> {
  const response = await fetch(`${API_BASE_URL}/api/clients/${clienteId}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Error al cargar detalles del cliente');
  }

  return response.json();
}

async function fetchClienteStats(
  desde?: string,
  hasta?: string,
  token?: string
): Promise<ClienteStats> {
  const params = new URLSearchParams();
  if (desde) params.append('desde', desde);
  if (hasta) params.append('hasta', hasta);

  const response = await fetch(`${API_BASE_URL}/api/clients/stats?${params}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Error al cargar estadísticas de clientes');
  }

  return response.json();
}

async function createCliente(
  data: Omit<Cliente, 'id' | 'total_reservas' | 'reservas_completadas' | 'reservas_canceladas' | 'no_shows' | 'created_at' | 'updated_at' | 'historial'>,
  token?: string
): Promise<Cliente> {
  const response = await fetch(`${API_BASE_URL}/api/clients`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Error al crear cliente');
  }

  return response.json();
}

async function updateCliente(
  clienteId: string,
  data: Partial<Cliente>,
  token?: string
): Promise<Cliente> {
  const response = await fetch(`${API_BASE_URL}/api/clients/${clienteId}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Error al actualizar cliente');
  }

  return response.json();
}

async function addClienteNota(
  clienteId: string,
  nota: Omit<ClienteNota, 'id' | 'timestamp'>,
  token?: string
): Promise<ClienteNota> {
  const response = await fetch(`${API_BASE_URL}/api/clients/${clienteId}/notas`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(nota),
  });

  if (!response.ok) {
    throw new Error('Error al agregar nota');
  }

  return response.json();
}

async function updateClientePreferencias(
  clienteId: string,
  preferencias: ClientePreferencias,
  token?: string
): Promise<Cliente> {
  const response = await fetch(`${API_BASE_URL}/api/clients/${clienteId}/preferencias`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(preferencias),
  });

  if (!response.ok) {
    throw new Error('Error al actualizar preferencias');
  }

  return response.json();
}

async function mergeClientes(
  clienteIdPrincipal: string,
  clienteIdSecundario: string,
  token?: string
): Promise<Cliente> {
  const response = await fetch(`${API_BASE_URL}/api/clients/merge`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      cliente_principal: clienteIdPrincipal,
      cliente_secundario: clienteIdSecundario,
    }),
  });

  if (!response.ok) {
    throw new Error('Error al fusionar clientes');
  }

  return response.json();
}

export function useClientes(
  limit: number = 100,
  tipo?: string,
  busqueda?: string,
  token?: string
) {
  return useQuery({
    queryKey: ['clientes', limit, tipo, busqueda],
    queryFn: () => fetchClientes(limit, tipo, busqueda, token),
    refetchInterval: 60000, // Refetch every 60 seconds
  });
}

export function useCliente(clienteId: string, token?: string) {
  return useQuery({
    queryKey: ['cliente', clienteId],
    queryFn: () => fetchCliente(clienteId, token),
    enabled: !!clienteId,
  });
}

export function useClienteStats(
  desde?: string,
  hasta?: string,
  token?: string
) {
  return useQuery({
    queryKey: ['cliente-stats', desde, hasta],
    queryFn: () => fetchClienteStats(desde, hasta, token),
    refetchInterval: 120000, // Refetch every 2 minutes
  });
}

export function useCreateCliente() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ data, token }: { data: Omit<Cliente, 'id' | 'total_reservas' | 'reservas_completadas' | 'reservas_canceladas' | 'no_shows' | 'created_at' | 'updated_at' | 'historial'>; token?: string }) =>
      createCliente(data, token),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clientes'] });
      queryClient.invalidateQueries({ queryKey: ['cliente-stats'] });
    },
  });
}

export function useUpdateCliente() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ clienteId, data, token }: { clienteId: string; data: Partial<Cliente>; token?: string }) =>
      updateCliente(clienteId, data, token),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['clientes'] });
      queryClient.invalidateQueries({ queryKey: ['cliente', variables.clienteId] });
      queryClient.invalidateQueries({ queryKey: ['cliente-stats'] });
    },
  });
}

export function useAddClienteNota() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ clienteId, nota, token }: { clienteId: string; nota: Omit<ClienteNota, 'id' | 'timestamp'>; token?: string }) =>
      addClienteNota(clienteId, nota, token),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['cliente', variables.clienteId] });
    },
  });
}

export function useUpdateClientePreferencias() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ clienteId, preferencias, token }: { clienteId: string; preferencias: ClientePreferencias; token?: string }) =>
      updateClientePreferencias(clienteId, preferencias, token),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['cliente', variables.clienteId] });
      queryClient.invalidateQueries({ queryKey: ['clientes'] });
    },
  });
}

export function useMergeClientes() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ clienteIdPrincipal, clienteIdSecundario, token }: { clienteIdPrincipal: string; clienteIdSecundario: string; token?: string }) =>
      mergeClientes(clienteIdPrincipal, clienteIdSecundario, token),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clientes'] });
      queryClient.invalidateQueries({ queryKey: ['cliente-stats'] });
    },
  });
}
