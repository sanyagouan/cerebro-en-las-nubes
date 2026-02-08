export interface Reserva {
  id: string;
  nombre: string;
  telefono: string;
  fecha: string;
  hora: string;
  personas: number;
  mesa?: string;
  estado: 'Pendiente' | 'Confirmada' | 'Cancelada' | 'Completada';
  notas?: string;
  origen: 'VAPI' | 'WhatsApp' | 'Telefono' | 'Presencial';
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
    personas: 4,
    mesa: 'Mesa 2T',
    estado: 'Confirmada',
    notas: 'Prefieren terraza',
    origen: 'VAPI',
    creado: '2026-02-07T10:30:00Z'
  },
  {
    id: '2',
    nombre: 'María García',
    telefono: '+34600987654',
    fecha: '2026-02-08',
    hora: '21:30',
    personas: 2,
    estado: 'Pendiente',
    origen: 'WhatsApp',
    creado: '2026-02-08T14:20:00Z'
  },
  {
    id: '3',
    nombre: 'Carlos López',
    telefono: '+34600555111',
    fecha: '2026-02-08',
    hora: '20:00',
    personas: 6,
    mesa: 'Mesa 3I',
    estado: 'Confirmada',
    notas: 'Celebración cumpleaños',
    origen: 'Telefono',
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
