import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../config/api';

// ==================== INTERFACES ====================

export interface DaySchedule {
  day: 'lunes' | 'martes' | 'miércoles' | 'jueves' | 'viernes' | 'sábado' | 'domingo';
  is_open: boolean;
  lunch_start?: string; // HH:mm
  lunch_end?: string;
  dinner_start?: string;
  dinner_end?: string;
}

export interface Holiday {
  id: string;
  date: string; // YYYY-MM-DD
  name: string;
  is_closed: boolean;
  special_hours?: {
    lunch_start?: string;
    lunch_end?: string;
    dinner_start?: string;
    dinner_end?: string;
  };
}

export interface Shift {
  id: string;
  name: 'almuerzo' | 'cena';
  default_start: string; // HH:mm
  default_end: string;
  max_capacity: number;
  is_active: boolean;
}

export interface CapacityConfig {
  max_simultaneous_reservations: number;
  max_party_size: number;
  min_party_size: number;
  overbooking_percentage: number; // 0-20
}

export interface ReservationTiming {
  party_size_min: number;
  party_size_max: number;
  duration_minutes: number;
}

export interface StaffUser {
  id: string;
  name: string;
  email: string;
  phone: string;
  role: 'Waiter' | 'Cook' | 'Manager' | 'Admin';
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

// ==================== HOOKS ====================

// Hook 1: Gestión horarios por día de la semana
export function useSchedule() {
  return useQuery<{ schedule: DaySchedule[] }>({
    queryKey: ['schedule'],
    queryFn: async () => {
      const response = await fetch(`${api.baseURL}/api/config/schedule`);
      if (!response.ok) throw new Error('Error al cargar horarios');
      return response.json();
    },
  });
}

export function useUpdateSchedule() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (schedule: DaySchedule[]) => {
      const response = await fetch(`${api.baseURL}/api/config/schedule`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ schedule }),
      });
      if (!response.ok) throw new Error('Error al actualizar horarios');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedule'] });
    },
  });
}

// Hook 2: Gestión festivos
export function useHolidays() {
  return useQuery<{ holidays: Holiday[] }>({
    queryKey: ['holidays'],
    queryFn: async () => {
      const response = await fetch(`${api.baseURL}/api/config/holidays`);
      if (!response.ok) throw new Error('Error al cargar festivos');
      return response.json();
    },
  });
}

export function useCreateHoliday() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (holiday: Omit<Holiday, 'id'>) => {
      const response = await fetch(`${api.baseURL}/api/config/holidays`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(holiday),
      });
      if (!response.ok) throw new Error('Error al crear festivo');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['holidays'] });
    },
  });
}

export function useUpdateHoliday() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Holiday> }) => {
      const response = await fetch(`${api.baseURL}/api/config/holidays/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Error al actualizar festivo');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['holidays'] });
    },
  });
}

export function useDeleteHoliday() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await fetch(`${api.baseURL}/api/config/holidays/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Error al eliminar festivo');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['holidays'] });
    },
  });
}

// Hook 3: Gestión turnos
export function useShifts() {
  return useQuery<{ shifts: Shift[] }>({
    queryKey: ['shifts'],
    queryFn: async () => {
      const response = await fetch(`${api.baseURL}/api/config/shifts`);
      if (!response.ok) throw new Error('Error al cargar turnos');
      return response.json();
    },
  });
}

export function useUpdateShift() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Shift> }) => {
      const response = await fetch(`${api.baseURL}/api/config/shifts/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Error al actualizar turno');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shifts'] });
    },
  });
}

// Hook 4: Gestión capacidad
export function useCapacity() {
  return useQuery<CapacityConfig>({
    queryKey: ['capacity'],
    queryFn: async () => {
      const response = await fetch(`${api.baseURL}/api/config/capacity`);
      if (!response.ok) throw new Error('Error al cargar capacidad');
      return response.json();
    },
  });
}

export function useUpdateCapacity() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (capacity: CapacityConfig) => {
      const response = await fetch(`${api.baseURL}/api/config/capacity`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(capacity),
      });
      if (!response.ok) throw new Error('Error al actualizar capacidad');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['capacity'] });
    },
  });
}

// Hook 5: Gestión tiempos de reserva
export function useReservationTimings() {
  return useQuery<{ timings: ReservationTiming[] }>({
    queryKey: ['reservation-timings'],
    queryFn: async () => {
      const response = await fetch(`${api.baseURL}/api/config/timings`);
      if (!response.ok) throw new Error('Error al cargar tiempos de reserva');
      return response.json();
    },
  });
}

export function useUpdateReservationTimings() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (timings: ReservationTiming[]) => {
      const response = await fetch(`${api.baseURL}/api/config/timings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ timings }),
      });
      if (!response.ok) throw new Error('Error al actualizar tiempos');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reservation-timings'] });
    },
  });
}

// Hook 6: Gestión usuarios staff
export function useUsers() {
  return useQuery<{ users: StaffUser[] }>({
    queryKey: ['staff-users'],
    queryFn: async () => {
      const response = await fetch(`${api.baseURL}/api/config/users`);
      if (!response.ok) throw new Error('Error al cargar usuarios');
      return response.json();
    },
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (user: Omit<StaffUser, 'id' | 'created_at' | 'last_login'>) => {
      const response = await fetch(`${api.baseURL}/api/config/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(user),
      });
      if (!response.ok) throw new Error('Error al crear usuario');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff-users'] });
    },
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<StaffUser> }) => {
      const response = await fetch(`${api.baseURL}/api/config/users/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Error al actualizar usuario');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff-users'] });
    },
  });
}

export function useDeleteUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await fetch(`${api.baseURL}/api/config/users/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Error al eliminar usuario');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff-users'] });
    },
  });
}
