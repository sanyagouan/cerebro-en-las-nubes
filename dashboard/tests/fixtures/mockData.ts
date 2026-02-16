/**
 * Mock Data Fixtures for Testing
 *
 * Provides realistic mock data for reservations, tables, users, and API responses
 * Follows Spanish validation rules and business logic from the real application
 */

import { Reservation, ReservationStatus } from '../../src/hooks/useReservations';

// ============================================================================
// MOCK RESERVATIONS
// ============================================================================

/**
 * Base mock reservation template
 * Uses the mock date from tests/setup.ts: 2024-01-15 (Monday, lunch service)
 */
const baseMockReservation: Omit<Reservation, 'id' | 'estado'> = {
  nombre: 'Juan Pérez García',
  telefono: '612345678',
  fecha: '2024-01-15',
  hora: '14:30',
  pax: 4,
  mesa: 'Mesa 5',
  canal: 'Dashboard',
  notas: '',
  creado: '2024-01-15T10:00:00Z',
};

/**
 * Mock reservations covering all possible states
 */
export const mockReservations: Reservation[] = [
  // Pendiente - Awaiting confirmation
  {
    ...baseMockReservation,
    id: 'res-001-pendiente',
    nombre: 'María López Sánchez',
    telefono: '654321098',
    fecha: '2024-01-15',
    hora: '13:00',
    pax: 2,
    estado: 'Pendiente' as ReservationStatus,
    mesa: undefined,
    canal: 'VAPI',
    notas: 'Primera reserva del cliente',
    creado: '2024-01-15T09:30:00Z',
  },

  // Confirmada - Confirmed, table assigned
  {
    ...baseMockReservation,
    id: 'res-002-confirmada',
    nombre: 'Carlos Rodríguez Fernández',
    telefono: '698765432',
    fecha: '2024-01-15',
    hora: '14:00',
    pax: 4,
    estado: 'Confirmada' as ReservationStatus,
    mesa: 'Mesa 3',
    canal: 'WhatsApp',
    notas: 'Mesa cerca de la ventana si es posible',
    creado: '2024-01-15T08:45:00Z',
  },

  // Sentada - Customer is seated
  {
    ...baseMockReservation,
    id: 'res-003-sentada',
    nombre: 'Ana García Martínez',
    telefono: '677889900',
    fecha: '2024-01-15',
    hora: '13:30',
    pax: 6,
    estado: 'Sentada' as ReservationStatus,
    mesa: 'Mesa 8',
    canal: 'Dashboard',
    notas: 'Celebración cumpleaños, necesitan silla para bebé',
    creado: '2024-01-14T18:20:00Z',
  },

  // Completada - Service completed
  {
    ...baseMockReservation,
    id: 'res-004-completada',
    nombre: 'Pedro Martín González',
    telefono: '611223344',
    fecha: '2024-01-14',
    hora: '21:00',
    pax: 2,
    estado: 'Completada' as ReservationStatus,
    mesa: 'Mesa 12',
    canal: 'Dashboard',
    notas: '',
    creado: '2024-01-14T15:00:00Z',
  },

  // Cancelada - Cancelled by customer or restaurant
  {
    ...baseMockReservation,
    id: 'res-005-cancelada',
    nombre: 'Laura Sánchez Ruiz',
    telefono: '644556677',
    fecha: '2024-01-15',
    hora: '20:00',
    pax: 8,
    estado: 'Cancelada' as ReservationStatus,
    mesa: undefined,
    canal: 'VAPI',
    notas: 'Cliente canceló por enfermedad',
    creado: '2024-01-13T10:00:00Z',
  },

  // Large group (>6 people)
  {
    ...baseMockReservation,
    id: 'res-006-grupo-grande',
    nombre: 'Empresa Tech Solutions SL',
    telefono: '687654321',
    fecha: '2024-01-16',
    hora: '14:30',
    pax: 12,
    estado: 'Confirmada' as ReservationStatus,
    mesa: 'Mesa 15, Mesa 16',
    canal: 'Dashboard',
    notas: 'Comida de empresa, necesitan factura',
    creado: '2024-01-15T11:00:00Z',
  },

  // Peak hour reservation (cena)
  {
    ...baseMockReservation,
    id: 'res-007-cena',
    nombre: 'Roberto Díaz Torres',
    telefono: '633445566',
    fecha: '2024-01-15',
    hora: '21:30',
    pax: 4,
    estado: 'Confirmada' as ReservationStatus,
    mesa: 'Mesa 7',
    canal: 'WhatsApp',
    notas: 'Cena romántica, mesa tranquila',
    creado: '2024-01-15T12:00:00Z',
  },

  // Terraza reservation
  {
    ...baseMockReservation,
    id: 'res-008-terraza',
    nombre: 'Isabel Moreno Jiménez',
    telefono: '655778899',
    fecha: '2024-01-15',
    hora: '13:00',
    pax: 3,
    estado: 'Confirmada' as ReservationStatus,
    mesa: 'Terraza 2',
    canal: 'Dashboard',
    notas: 'Prefieren terraza, buen tiempo',
    creado: '2024-01-15T09:00:00Z',
  },
];

// ============================================================================
// MOCK TABLES
// ============================================================================

export interface MockTable {
  id: string;
  numero: string;
  capacidad: number;
  ubicacion: 'Interior' | 'Terraza';
  estado: 'Libre' | 'Ocupada' | 'Reservada' | 'Bloqueada';
  reservaId?: string;
}

export const mockTables: MockTable[] = [
  // Interior tables (1-12)
  { id: 'table-001', numero: 'Mesa 1', capacidad: 2, ubicacion: 'Interior', estado: 'Libre' },
  { id: 'table-002', numero: 'Mesa 2', capacidad: 2, ubicacion: 'Interior', estado: 'Libre' },
  { id: 'table-003', numero: 'Mesa 3', capacidad: 4, ubicacion: 'Interior', estado: 'Reservada', reservaId: 'res-002-confirmada' },
  { id: 'table-004', numero: 'Mesa 4', capacidad: 4, ubicacion: 'Interior', estado: 'Libre' },
  { id: 'table-005', numero: 'Mesa 5', capacidad: 4, ubicacion: 'Interior', estado: 'Libre' },
  { id: 'table-006', numero: 'Mesa 6', capacidad: 6, ubicacion: 'Interior', estado: 'Libre' },
  { id: 'table-007', numero: 'Mesa 7', capacidad: 4, ubicacion: 'Interior', estado: 'Reservada', reservaId: 'res-007-cena' },
  { id: 'table-008', numero: 'Mesa 8', capacidad: 6, ubicacion: 'Interior', estado: 'Ocupada', reservaId: 'res-003-sentada' },
  { id: 'table-009', numero: 'Mesa 9', capacidad: 2, ubicacion: 'Interior', estado: 'Libre' },
  { id: 'table-010', numero: 'Mesa 10', capacidad: 4, ubicacion: 'Interior', estado: 'Libre' },
  { id: 'table-011', numero: 'Mesa 11', capacidad: 2, ubicacion: 'Interior', estado: 'Bloqueada' },
  { id: 'table-012', numero: 'Mesa 12', capacidad: 2, ubicacion: 'Interior', estado: 'Libre' },

  // Terraza tables (T1-T6)
  { id: 'table-t01', numero: 'Terraza 1', capacidad: 4, ubicacion: 'Terraza', estado: 'Libre' },
  { id: 'table-t02', numero: 'Terraza 2', capacidad: 4, ubicacion: 'Terraza', estado: 'Reservada', reservaId: 'res-008-terraza' },
  { id: 'table-t03', numero: 'Terraza 3', capacidad: 2, ubicacion: 'Terraza', estado: 'Libre' },
  { id: 'table-t04', numero: 'Terraza 4', capacidad: 6, ubicacion: 'Terraza', estado: 'Libre' },
  { id: 'table-t05', numero: 'Terraza 5', capacidad: 4, ubicacion: 'Terraza', estado: 'Libre' },
  { id: 'table-t06', numero: 'Terraza 6', capacidad: 2, ubicacion: 'Terraza', estado: 'Libre' },

  // Large group tables (15-16, can be combined)
  { id: 'table-015', numero: 'Mesa 15', capacidad: 8, ubicacion: 'Interior', estado: 'Reservada', reservaId: 'res-006-grupo-grande' },
  { id: 'table-016', numero: 'Mesa 16', capacidad: 8, ubicacion: 'Interior', estado: 'Reservada', reservaId: 'res-006-grupo-grande' },
];

// ============================================================================
// MOCK USERS
// ============================================================================

export interface MockUser {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'manager' | 'waiter' | 'cook';
  nombre: string;
}

export const mockUsers: MockUser[] = [
  {
    id: 'user-001',
    username: 'admin',
    email: 'admin@enlasnubes.com',
    role: 'admin',
    nombre: 'Administrador Sistema',
  },
  {
    id: 'user-002',
    username: 'manager',
    email: 'manager@enlasnubes.com',
    role: 'manager',
    nombre: 'Carlos Encargado',
  },
  {
    id: 'user-003',
    username: 'camarero1',
    email: 'camarero1@enlasnubes.com',
    role: 'waiter',
    nombre: 'Ana Camarera',
  },
  {
    id: 'user-004',
    username: 'cocinero1',
    email: 'cocinero1@enlasnubes.com',
    role: 'cook',
    nombre: 'Pedro Cocinero',
  },
];

// ============================================================================
// MOCK AUTHENTICATION
// ============================================================================

export const mockAuthTokens = {
  admin: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTAwMSIsInVzZXJuYW1lIjoiYWRtaW4iLCJyb2xlIjoiYWRtaW4ifQ.mock',
  manager: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTAwMiIsInVzZXJuYW1lIjoibWFuYWdlciIsInJvbGUiOiJtYW5hZ2VyIn0.mock',
  waiter: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTAwMyIsInVzZXJuYW1lIjoiY2FtYXJlcm8xIiwicm9sZSI6IndhaXRlciJ9.mock',
  cook: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTAwNCIsInVzZXJuYW1lIjoiY29jaW5lcm8xIiwicm9sZSI6ImNvb2sifQ.mock',
};

export const mockLoginResponse = {
  success: true,
  user: mockUsers[0],
  token: mockAuthTokens.admin,
  refreshToken: 'mock-refresh-token-12345',
};

// ============================================================================
// MOCK API RESPONSES
// ============================================================================

export const mockApiResponses = {
  // GET /api/mobile/reservations
  getReservations: {
    success: true,
    data: mockReservations,
    total: mockReservations.length,
    page: 1,
    pageSize: 100,
  },

  // GET /api/mobile/tables
  getTables: {
    success: true,
    data: mockTables,
    total: mockTables.length,
  },

  // POST /api/mobile/reservations (create)
  createReservation: (reservation: Partial<Reservation>) => ({
    success: true,
    data: {
      ...baseMockReservation,
      ...reservation,
      id: `res-${Date.now()}`,
      estado: 'Pendiente' as ReservationStatus,
      creado: new Date().toISOString(),
    },
    message: 'Reserva creada exitosamente',
  }),

  // PUT /api/mobile/reservations/:id (update)
  updateReservation: (id: string, updates: Partial<Reservation>) => ({
    success: true,
    data: {
      ...mockReservations[0],
      ...updates,
      id,
    },
    message: 'Reserva actualizada exitosamente',
  }),

  // POST /api/mobile/reservations/:id/cancel
  cancelReservation: (id: string) => ({
    success: true,
    data: {
      ...mockReservations[0],
      id,
      estado: 'Cancelada' as ReservationStatus,
    },
    message: 'Reserva cancelada exitosamente',
  }),

  // Error responses
  error404: {
    success: false,
    error: 'Recurso no encontrado',
    code: 'NOT_FOUND',
  },

  error400: {
    success: false,
    error: 'Datos de entrada inválidos',
    code: 'VALIDATION_ERROR',
    details: {
      telefono: 'Formato de teléfono inválido',
    },
  },

  error500: {
    success: false,
    error: 'Error interno del servidor',
    code: 'INTERNAL_ERROR',
  },
};

// ============================================================================
// FACTORY FUNCTIONS - Generate dynamic mock data
// ============================================================================

/**
 * Creates a mock reservation with custom properties
 */
export function createMockReservation(
  overrides: Partial<Reservation> = {}
): Reservation {
  const id = overrides.id || `res-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  return {
    ...baseMockReservation,
    id,
    estado: 'Pendiente' as ReservationStatus,
    creado: new Date().toISOString(),
    ...overrides,
  };
}

/**
 * Creates a mock table with custom properties
 */
export function createMockTable(overrides: Partial<MockTable> = {}): MockTable {
  const id = overrides.id || `table-${Date.now()}`;
  return {
    id,
    numero: `Mesa ${id.split('-')[1]}`,
    capacidad: 4,
    ubicacion: 'Interior',
    estado: 'Libre',
    ...overrides,
  };
}

/**
 * Creates a mock user with custom properties
 */
export function createMockUser(overrides: Partial<MockUser> = {}): MockUser {
  const id = overrides.id || `user-${Date.now()}`;
  return {
    id,
    username: `user${id.split('-')[1]}`,
    email: `user${id.split('-')[1]}@enlasnubes.com`,
    role: 'waiter',
    nombre: 'Usuario de Prueba',
    ...overrides,
  };
}

/**
 * Creates multiple mock reservations for testing lists
 */
export function createMockReservations(count: number): Reservation[] {
  const estados: ReservationStatus[] = ['Pendiente', 'Confirmada', 'Sentada', 'Completada', 'Cancelada'];
  const canales = ['VAPI', 'WhatsApp', 'Dashboard'];
  
  return Array.from({ length: count }, (_, i) => {
    const estado = estados[i % estados.length];
    return createMockReservation({
      id: `res-bulk-${i + 1}`,
      nombre: `Cliente ${i + 1}`,
      telefono: `6${Math.floor(10000000 + Math.random() * 90000000)}`,
      hora: `${12 + (i % 12)}:00`,
      pax: 2 + (i % 6),
      estado,
      canal: canales[i % canales.length],
      mesa: estado !== 'Pendiente' && estado !== 'Cancelada' ? `Mesa ${i + 1}` : undefined,
    });
  });
}

// ============================================================================
// VALIDATION HELPERS - Spanish business rules
// ============================================================================

/**
 * Valid Spanish phone numbers for testing
 */
export const validSpanishPhones = [
  '612345678',      // Standard format
  '654321098',      // Standard format
  '+34612345678',   // With country code
  '0034698765432',  // With 00 prefix
  '34677889900',    // With country code no +
  '6 12 34 56 78',  // With spaces (should be cleaned)
  '612-345-678',    // With dashes (should be cleaned)
];

/**
 * Invalid Spanish phone numbers for testing
 */
export const invalidSpanishPhones = [
  '512345678',      // Wrong first digit (must be 6, 7, 8, or 9)
  '12345678',       // Too short
  '61234567890',    // Too long
  'abcdefghi',      // Non-numeric
  '+1234567890',    // Wrong country code
  '412345678',      // Invalid first digit
];

/**
 * Valid service hours (12:00 - 23:59)
 */
export const validServiceHours = [
  '12:00', '13:00', '14:00', '15:00',
  '20:00', '21:00', '22:00', '23:00', '23:59',
];

/**
 * Invalid service hours (outside 12:00 - 23:59)
 */
export const invalidServiceHours = [
  '00:00', '01:00', '06:00', '11:00', '11:59',
];

/**
 * Valid party sizes (1-20)
 */
export const validPartySizes = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20];

/**
 * Invalid party sizes (0 or >20)
 */
export const invalidPartySizes = [0, -1, 21, 25, 50, 100];
