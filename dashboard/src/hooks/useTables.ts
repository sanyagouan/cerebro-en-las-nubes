import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import config from '../config/api';

// ============ TYPES ============

export type TableLocation = 'Interior' | 'Terraza';
export type TableStatus = 'Libre' | 'Ocupada' | 'Reservada' | 'Bloqueada';

export interface Table {
  id: string;
  numero: string;  // nombre en backend
  capacidad: number;  // capacidad_min en backend
  capacidad_max?: number;
  ubicacion: TableLocation;  // zona en backend
  estado: TableStatus;  // status en backend
  notas?: string;
  ampliable?: boolean;
  capacidad_ampliada?: number;
}

export interface TableStats {
  total: number;
  libres: number;
  ocupadas: number;
  reservadas: number;
}

// Backend response (different field names)
interface BackendTableResponse {
  id: string;
  nombre: string;
  zona: string;
  capacidad_min: number;
  capacidad_max: number;
  status: string;
  notas?: string;
  ampliable?: boolean;
  capacidad_ampliada?: number;
  auxiliar_requerida?: boolean;
  requiere_aviso?: boolean;
  prioridad?: number;
}

// ============ API FUNCTIONS ============

const API_URL = config.API_BASE_URL;

// Transform backend response to frontend Table
function transformTable(backendTable: BackendTableResponse): Table {
  return {
    id: backendTable.id,
    numero: backendTable.nombre,
    capacidad: backendTable.capacidad_min,
    capacidad_max: backendTable.capacidad_max,
    ubicacion: backendTable.zona as TableLocation,
    estado: backendTable.status as TableStatus,
    notas: backendTable.notas,
    ampliable: backendTable.ampliable,
    capacidad_ampliada: backendTable.capacidad_ampliada,
  };
}

// Transform frontend Table to backend fields
function transformToBackend(table: Partial<Table>): Record<string, any> {
  const backendFields: Record<string, any> = {};
  
  if (table.numero !== undefined) backendFields.nombre = table.numero;
  if (table.capacidad !== undefined) backendFields.capacidad_min = table.capacidad;
  if (table.capacidad_max !== undefined) backendFields.capacidad_max = table.capacidad_max;
  if (table.ubicacion !== undefined) backendFields.zona = table.ubicacion;
  if (table.estado !== undefined) backendFields.status = table.estado;
  if (table.notas !== undefined) backendFields.notas = table.notas;
  if (table.ampliable !== undefined) backendFields.ampliable = table.ampliable;
  if (table.capacidad_ampliada !== undefined) backendFields.capacidad_ampliada = table.capacidad_ampliada;
  
  return backendFields;
}

async function fetchTables(zona?: TableLocation): Promise<Table[]> {
  const params = new URLSearchParams();
  if (zona) params.append('zona', zona);
  
  const url = `${API_URL}/api/mobile/tables${params.toString() ? `?${params.toString()}` : ''}`;
  
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
  
  if (!response.ok) {
    throw new Error(`Error fetching tables: ${response.statusText}`);
  }
  
  const data: BackendTableResponse[] = await response.json();
  return data.map(transformTable);
}

async function createTable(tableData: Partial<Table>): Promise<Table> {
  const backendData = transformToBackend(tableData);
  
  const response = await fetch(`${API_URL}/api/mobile/tables`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(backendData),
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Error creating table');
  }
  
  const data: BackendTableResponse = await response.json();
  return transformTable(data);
}

async function updateTable({ id, data }: { id: string; data: Partial<Table> }): Promise<Table> {
  const backendData = transformToBackend(data);
  
  const response = await fetch(`${API_URL}/api/mobile/tables/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(backendData),
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Error updating table');
  }
  
  const responseData: BackendTableResponse = await response.json();
  return transformTable(responseData);
}

async function deleteTable(id: string): Promise<void> {
  const response = await fetch(`${API_URL}/api/mobile/tables/${id}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Error deleting table');
  }
}

async function updateTableStatus({ id, estado }: { id: string; estado: TableStatus }): Promise<Table> {
  const response = await fetch(`${API_URL}/api/mobile/tables/${id}/status?status_update=${estado}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Error updating table status');
  }
  
  const data: BackendTableResponse = await response.json();
  return transformTable(data);
}

// ============ HOOKS ============

export function useTables(zona?: TableLocation) {
  return useQuery<Table[], Error>({
    queryKey: ['tables', zona],
    queryFn: () => fetchTables(zona),
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refetch every minute
  });
}

export function useCreateTable() {
  const queryClient = useQueryClient();
  
  return useMutation<Table, Error, Partial<Table>>({
    mutationFn: createTable,
    onSuccess: () => {
      // Invalidate all table queries to refetch
      queryClient.invalidateQueries({ queryKey: ['tables'] });
    },
  });
}

export function useUpdateTable() {
  const queryClient = useQueryClient();
  
  return useMutation<Table, Error, { id: string; data: Partial<Table> }>({
    mutationFn: updateTable,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tables'] });
    },
  });
}

export function useDeleteTable() {
  const queryClient = useQueryClient();
  
  return useMutation<void, Error, string>({
    mutationFn: deleteTable,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tables'] });
    },
  });
}

export function useUpdateTableStatus() {
  const queryClient = useQueryClient();
  
  return useMutation<Table, Error, { id: string; estado: TableStatus }>({
    mutationFn: updateTableStatus,
    onMutate: async ({ id, estado }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['tables'] });
      
      // Snapshot previous value
      const previousTables = queryClient.getQueryData<Table[]>(['tables']);
      
      // Optimistically update
      if (previousTables) {
        queryClient.setQueryData<Table[]>(['tables'], (old) =>
          old?.map((table) =>
            table.id === id ? { ...table, estado } : table
          ) || []
        );
      }
      
      return { previousTables } as { previousTables: Table[] | undefined };
    },
    onError: (_err, _variables, context) => {
      // Rollback on error
      const typedContext = context as { previousTables: Table[] | undefined } | undefined;
      if (typedContext?.previousTables) {
        queryClient.setQueryData(['tables'], typedContext.previousTables);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['tables'] });
    },
  });
}

// Derived hook for table stats
export function useTableStats() {
  const { data: tables } = useTables();
  
  const stats: TableStats = {
    total: tables?.length || 0,
    libres: tables?.filter((t) => t.estado === 'Libre').length || 0,
    ocupadas: tables?.filter((t) => t.estado === 'Ocupada').length || 0,
    reservadas: tables?.filter((t) => t.estado === 'Reservada').length || 0,
  };
  
  return stats;
}
