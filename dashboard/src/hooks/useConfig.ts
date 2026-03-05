import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../config/api';

// ==================== INTERFACES ====================

export interface DaySchedule {
  day: 'lunes' | 'martes' | 'miércoles' | 'jueves' | 'viernes' | 'sábado' | 'domingo';
  is_open: boolean;
  lunch_start?: string;
  lunch_end?: string;
  dinner_start?: string;
  dinner_end?: string;
}

export interface Holiday {
  id: string;
  date: string;
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
  default_start: string;
  default_end: string;
  max_capacity: number;
  is_active: boolean;
}

export interface CapacityConfig {
  max_simultaneous_reservations: number;
  max_party_size: number;
  min_party_size: number;
  overbooking_percentage: number;
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
  role: 'Waiter' | 'Cook' | 'Manager' | 'Admin' | 'Technician';
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

// ==================== HOOKS — Axios con JWT automático ====================

export function useSchedule() {
  return useQuery<{ schedule: DaySchedule[] }>({
    queryKey: ['schedule'],
    queryFn: async () => {
      const response = await api.get('/api/config/schedule');
      return response.data;
    },
  });
}

export function useUpdateSchedule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (schedule: DaySchedule[]) => {
      const response = await api.put('/api/config/schedule', { schedule });
      return response.data;
    },
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['schedule'] }); },
  });
}

export function useHolidays() {
  return useQuery<{ holidays: Holiday[] }>({
    queryKey: ['holidays'],
    queryFn: async () => {
      const response = await api.get('/api/config/holidays');
      return response.data;
    },
  });
}

export function useCreateHoliday() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (holiday: Omit<Holiday, 'id'>) => {
      const response = await api.post('/api/config/holidays', holiday);
      return response.data;
    },
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['holidays'] }); },
  });
}

export function useUpdateHoliday() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Holiday> }) => {
      const response = await api.put(`/api/config/holidays/${id}`, data);
      return response.data;
    },
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['holidays'] }); },
  });
}

export function useDeleteHoliday() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await api.delete(`/api/config/holidays/${id}`);
      return response.data;
    },
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['holidays'] }); },
  });
}

export function useShifts() {
  return useQuery<{ shifts: Shift[] }>({
    queryKey: ['shifts'],
    queryFn: async () => {
      const response = await api.get('/api/config/shifts');
      return response.data;
    },
  });
}

export function useUpdateShift() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Shift> }) => {
      const response = await api.put(`/api/config/shifts/${id}`, data);
      return response.data;
    },
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['shifts'] }); },
  });
}

export function useCapacity() {
  return useQuery<CapacityConfig>({
    queryKey: ['capacity'],
    queryFn: async () => {
      const response = await api.get('/api/config/capacity');
      return response.data;
    },
  });
}

export function useUpdateCapacity() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (capacity: CapacityConfig) => {
      const response = await api.put('/api/config/capacity', capacity);
      return response.data;
    },
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['capacity'] }); },
  });
}

export function useReservationTimings() {
  return useQuery<{ timings: ReservationTiming[] }>({
    queryKey: ['reservation-timings'],
    queryFn: async () => {
      const response = await api.get('/api/config/timings');
      return response.data;
    },
  });
}

export function useUpdateReservationTimings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (timings: ReservationTiming[]) => {
      const response = await api.put('/api/config/timings', { timings });
      return response.data;
    },
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['reservation-timings'] }); },
  });
}

export function useUsers() {
  return useQuery<{ users: StaffUser[] }>({
    queryKey: ['staff-users'],
    queryFn: async () => {
      const response = await api.get('/api/config/users');
      return response.data;
    },
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (user: Omit<StaffUser, 'id' | 'created_at' | 'last_login'>) => {
      const response = await api.post('/api/config/users', user);
      return response.data;
    },
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['staff-users'] }); },
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<StaffUser> }) => {
      const response = await api.put(`/api/config/users/${id}`, data);
      return response.data;
    },
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['staff-users'] }); },
  });
}

export function useDeleteUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await api.delete(`/api/config/users/${id}`);
      return response.data;
    },
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['staff-users'] }); },
  });
}
