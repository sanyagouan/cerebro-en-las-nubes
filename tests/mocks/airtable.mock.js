/**
 * Mock de Airtable para testing
 * Simula las respuestas de la API de Airtable
 */

/**
 * Genera un registro de cliente de Airtable
 */
export const mockAirtableCustomer = (overrides = {}) => {
  const defaults = {
    id: `rec${Math.random().toString(36).substring(2, 17)}`,
    createdTime: new Date().toISOString(),
    fields: {
      customer_id: `cust_${Date.now()}`,
      name: 'Juan Pérez',
      phone: '+34600123456',
      whatsapp: '+34600123456',
      email: 'juan.perez@example.com',
      preferences: JSON.stringify({
        dietary: [],
        seating: 'interior',
      }),
      total_reservations: 5,
      loyalty_points: 50,
      last_visit_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      data_consent: true,
      consent_date: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      created_at: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date().toISOString(),
    },
  };

  return {
    ...defaults,
    fields: { ...defaults.fields, ...(overrides.fields || {}) },
    ...overrides,
  };
};

/**
 * Genera un registro de reserva de Airtable
 */
export const mockAirtableReservation = (overrides = {}) => {
  const defaults = {
    id: `rec${Math.random().toString(36).substring(2, 17)}`,
    createdTime: new Date().toISOString(),
    fields: {
      id: `res_${Date.now()}`,
      customer_id: ['recXXXXXXXXXXXXXXX'], // Link a customers
      table_id: ['recYYYYYYYYYYYYYYY'], // Link a tables
      customer_name: 'Juan Pérez',
      customer_phone: '+34600123456',
      guest_count: 4,
      service_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      service_time: '21:00',
      status: 'pendiente',
      confirmation_code: Math.random().toString(36).substring(2, 10).toUpperCase(),
      confirmation_sent_at: null,
      confirmed_at: null,
      special_requests: JSON.stringify([]),
      source: 'VAPI',
      created_by: 'system',
      origin_system: 'VAPI',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  };

  return {
    ...defaults,
    fields: { ...defaults.fields, ...(overrides.fields || {}) },
    ...overrides,
  };
};

/**
 * Genera un registro de mesa de Airtable
 */
export const mockAirtableTable = (overrides = {}) => {
  const defaults = {
    id: `rec${Math.random().toString(36).substring(2, 17)}`,
    createdTime: new Date().toISOString(),
    fields: {
      table_id: 'A1',
      capacity_min: 2,
      capacity_max: 4,
      zone: 'interior',
      notes: '',
      is_auxiliary: false,
      priority: 1,
      coordinates_x: 0,
      coordinates_y: 0,
      sillas_nino: false,
      accesibilidad_ruedas: false,
      cerca_ventana: true,
      preferencia_grupos: false,
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  };

  return {
    ...defaults,
    fields: { ...defaults.fields, ...(overrides.fields || {}) },
    ...overrides,
  };
};

/**
 * Genera un registro de slot de disponibilidad
 */
export const mockAirtableAvailabilitySlot = (overrides = {}) => {
  const defaults = {
    id: `rec${Math.random().toString(36).substring(2, 17)}`,
    createdTime: new Date().toISOString(),
    fields: {
      id: `slot_${Date.now()}`,
      table_id: ['recYYYYYYYYYYYYYYY'], // Link a tables
      service_date: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      service_time: '21:00',
      available: true,
      locked_by_reservation_id: null,
      created_at: new Date().toISOString(),
    },
  };

  return {
    ...defaults,
    fields: { ...defaults.fields, ...(overrides.fields || {}) },
    ...overrides,
  };
};

/**
 * Genera un registro de audit log
 */
export const mockAirtableAuditLog = (overrides = {}) => {
  const defaults = {
    id: `rec${Math.random().toString(36).substring(2, 17)}`,
    createdTime: new Date().toISOString(),
    fields: {
      id: `audit_${Date.now()}`,
      action: 'create_reservation',
      entity_type: 'reservation',
      entity_id: `res_${Date.now()}`,
      user_id: 'system',
      changes: JSON.stringify({
        status: { old: null, new: 'pendiente' },
      }),
      ip_address: '127.0.0.1',
      user_agent: 'n8n/1.0',
      timestamp: new Date().toISOString(),
    },
  };

  return {
    ...defaults,
    fields: { ...defaults.fields, ...(overrides.fields || {}) },
    ...overrides,
  };
};

/**
 * Mock de respuesta de listado de Airtable
 */
export const mockAirtableList = (records = [], offset = null) => {
  return {
    records,
    offset,
  };
};

/**
 * Mock de respuesta de creación de Airtable
 */
export const mockAirtableCreate = (fields = {}) => {
  return {
    id: `rec${Math.random().toString(36).substring(2, 17)}`,
    createdTime: new Date().toISOString(),
    fields,
  };
};

/**
 * Mock de respuesta de actualización de Airtable
 */
export const mockAirtableUpdate = (id, fields = {}) => {
  return {
    id,
    fields: {
      ...fields,
      updated_at: new Date().toISOString(),
    },
  };
};

/**
 * Mock de error de Airtable
 */
export const mockAirtableError = (type = 'INVALID_REQUEST_BODY') => {
  const errors = {
    INVALID_REQUEST_BODY: {
      type: 'INVALID_REQUEST_BODY',
      message: 'Invalid request body',
    },
    NOT_FOUND: {
      type: 'MODEL_ID_NOT_FOUND',
      message: 'Record not found',
    },
    INVALID_PERMISSIONS: {
      type: 'INVALID_PERMISSIONS',
      message: 'You do not have permission to perform this operation',
    },
    RATE_LIMIT: {
      type: 'RATE_LIMIT',
      message: 'Rate limit exceeded',
    },
  };

  return {
    error: errors[type] || errors.INVALID_REQUEST_BODY,
  };
};

/**
 * Mock del cliente de Airtable completo
 */
export class MockAirtableClient {
  constructor() {
    this.records = new Map();
  }

  base(baseId) {
    return {
      table: (tableName) => ({
        select: (options = {}) => ({
          all: async () => {
            const records = Array.from(this.records.values())
              .filter(r => r.table === tableName);

            if (options.filterByFormula) {
              // Implementación simplificada de filtro
              return records;
            }

            return records.map(r => r.record);
          },
        }),
        create: async (fields) => {
          const record = mockAirtableCreate(fields);
          this.records.set(record.id, { table: tableName, record });
          return record;
        },
        update: async (id, fields) => {
          const existing = this.records.get(id);
          if (!existing) throw new Error('NOT_FOUND');

          const updated = mockAirtableUpdate(id, fields);
          this.records.set(id, { table: tableName, record: updated });
          return updated;
        },
        find: async (id) => {
          const existing = this.records.get(id);
          if (!existing) throw new Error('NOT_FOUND');
          return existing.record;
        },
        destroy: async (id) => {
          const existing = this.records.get(id);
          if (!existing) throw new Error('NOT_FOUND');

          this.records.delete(id);
          return { id, deleted: true };
        },
      }),
    };
  }

  reset() {
    this.records.clear();
  }
}

export default {
  mockAirtableCustomer,
  mockAirtableReservation,
  mockAirtableTable,
  mockAirtableAvailabilitySlot,
  mockAirtableAuditLog,
  mockAirtableList,
  mockAirtableCreate,
  mockAirtableUpdate,
  mockAirtableError,
  MockAirtableClient,
};
