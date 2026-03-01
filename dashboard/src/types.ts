export interface Reserva {
  id: string;
  nombre: string;
  telefono: string;
  fecha: string;
  hora: string;
  pax: number;  // Cambiado de 'personas' para coincidir con backend
  mesa?: string;
  estado: 'Pendiente' | 'Confirmada' | 'Cancelada' | 'Completada' | 'Sentada' | 'NoShow';
  notas?: string;
  canal: 'VAPI' | 'WhatsApp' | 'Telefono' | 'Presencial';  // Cambiado de 'origen'
  creado: string;
}

export interface Mesa {
  id: string;
  nombre: string;
  capacidad: number;
  capacidadAmpliada?: number;
  ubicacion: 'Interior' | 'Terraza';
  disponible: boolean;
  notas?: string;
}

export interface Metricas {
  totalReservasHoy: number;
  reservasConfirmadas: number;
  reservasPendientes: number;
  ocupacion: number;
  clientesNuevos: number;
  cancelaciones: number;
}

// Interfaces adicionales deducidas de los errores del dashboard
export interface ActivityEvent {
  id: string;
  event_type: string;
  descripcion: string;
  user?: string;
  created_at: string;
  metadata?: any;
}

export interface WaitlistEntry {
  id: string;
  nombre: string;
  telefono: string;
  party_size: number;
  status: 'waiting' | 'notified' | 'seated' | 'cancelled';
  wait_time_minutes?: number;
  created_at: string;
}

export interface WaitlistResponse {
  entries: WaitlistEntry[];
  stats: {
    waiting: number;
    notified: number;
    seated: number;
    cancelled: number;
  };
}

export type CustomerTier = 'standard' | 'vip' | 'blocked';
export type CustomerPreferenceType = 'alergia' | 'mesa' | 'bebida' | 'comida' | 'otro';

export interface CustomerPreference {
  id: string;
  tipo: CustomerPreferenceType;
  valor: string;
}

export interface CustomerNote {
  id: string;
  contenido: string;
  is_important: boolean;
  staff_name?: string;
  created_at: string;
}

export interface ReservationHistory {
  id: string;
  fecha: string;
  estado: string;
}

export interface Customer {
  id: string;
  nombre: string;
  telefono: string;
  tier: CustomerTier;
  email?: string;
  preferencias: CustomerPreference[];
  notas: CustomerNote[];
  totalReservas: number;
  noShows: number;
  reservations?: ReservationHistory[];
  created_at: string;
  updated_at: string;
}

export const MESAS_EJEMPLO: Mesa[] = [
  { id: '1', nombre: 'Mesa 1I', capacidad: 4, capacidadAmpliada: 6, ubicacion: 'Interior', disponible: true },
  { id: '2', nombre: 'Mesa 2I', capacidad: 4, capacidadAmpliada: 6, ubicacion: 'Interior', disponible: true },
  { id: '3', nombre: 'Mesa 3I', capacidad: 8, capacidadAmpliada: 10, ubicacion: 'Interior', disponible: false },
  { id: '4', nombre: 'Mesa 1T', capacidad: 10, capacidadAmpliada: 12, ubicacion: 'Terraza', disponible: true },
  { id: '5', nombre: 'Mesa 2T', capacidad: 6, capacidadAmpliada: 8, ubicacion: 'Terraza', disponible: true },
];

export const RESERVAS_EJEMPLO: Reserva[] = [
  {
    id: '1',
    nombre: 'Juan Pérez',
    telefono: '+34600123456',
    fecha: '2026-02-08',
    hora: '21:00',
    pax: 4,  // Cambiado de 'personas'
    mesa: 'Mesa 2T',
    estado: 'Confirmada',
    notas: 'Prefieren terraza',
    canal: 'VAPI',  // Cambiado de 'origen'
    creado: '2026-02-07T10:30:00Z'
  },
  {
    id: '2',
    nombre: 'María García',
    telefono: '+34600987654',
    fecha: '2026-02-08',
    hora: '21:30',
    pax: 2,  // Cambiado de 'personas'
    estado: 'Pendiente',
    canal: 'WhatsApp',  // Cambiado de 'origen'
    creado: '2026-02-08T14:20:00Z'
  },
  {
    id: '3',
    nombre: 'Carlos López',
    telefono: '+34600555111',
    fecha: '2026-02-08',
    hora: '20:00',
    pax: 6,  // Cambiado de 'personas'
    mesa: 'Mesa 3I',
    estado: 'Confirmada',
    notas: 'Celebración cumpleaños',
    canal: 'Telefono',  // Cambiado de 'origen'
    creado: '2026-02-06T09:15:00Z'
  },
];

export const METRICAS_EJEMPLO: Metricas = {
  totalReservasHoy: 12,
  reservasConfirmadas: 8,
  reservasPendientes: 3,
  ocupacion: 67,
  clientesNuevos: 5,
  cancelaciones: 1
};
