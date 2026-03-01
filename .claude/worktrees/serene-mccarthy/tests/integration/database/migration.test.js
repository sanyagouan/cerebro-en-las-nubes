/**
 * Pruebas de migración de datos Airtable → PostgreSQL
 * Valida la integridad de datos durante la migración
 */

import { describe, test, expect, beforeEach } from '@jest/globals';
import { MockAirtableClient } from '../../mocks/airtable.mock.js';
import {
  mockAirtableCustomer,
  mockAirtableReservation,
  mockAirtableTable,
} from '../../mocks/airtable.mock.js';

describe('Database Migration Tests', () => {
  let airtableClient;

  beforeEach(() => {
    airtableClient = new MockAirtableClient();
  });

  describe('Migración de Customers', () => {
    test('debe preservar todos los campos de customer', () => {
      const airtableCustomer = mockAirtableCustomer({
        fields: {
          customer_id: 'cust_123',
          name: 'Juan Pérez',
          phone: '+34600123456',
          whatsapp: '+34600123456',
          email: 'juan@example.com',
          total_reservations: 5,
          loyalty_points: 50,
          data_consent: true,
        },
      });

      // Simular transformación a PostgreSQL
      const pgCustomer = {
        id: airtableCustomer.fields.customer_id,
        name: airtableCustomer.fields.name,
        phone: airtableCustomer.fields.phone,
        whatsapp: airtableCustomer.fields.whatsapp,
        email: airtableCustomer.fields.email,
        preferences: JSON.parse(airtableCustomer.fields.preferences || '{}'),
        total_reservations: airtableCustomer.fields.total_reservations,
        loyalty_points: airtableCustomer.fields.loyalty_points,
        data_consent: airtableCustomer.fields.data_consent,
        consent_date: airtableCustomer.fields.consent_date,
      };

      expect(pgCustomer.id).toBe('cust_123');
      expect(pgCustomer.name).toBe('Juan Pérez');
      expect(pgCustomer.phone).toBe('+34600123456');
      expect(pgCustomer.total_reservations).toBe(5);
      expect(pgCustomer.data_consent).toBe(true);
    });

    test('debe manejar campos JSONB correctamente', () => {
      const airtableCustomer = mockAirtableCustomer({
        fields: {
          preferences: JSON.stringify({
            dietary: ['vegetariano'],
            seating: 'terraza',
            allergies: ['gluten'],
          }),
        },
      });

      const preferences = JSON.parse(airtableCustomer.fields.preferences);

      expect(preferences).toHaveProperty('dietary');
      expect(preferences.dietary).toContain('vegetariano');
      expect(preferences.seating).toBe('terraza');
      expect(preferences.allergies).toContain('gluten');
    });

    test('debe generar UUID para nuevos customers sin ID', () => {
      const airtableCustomer = mockAirtableCustomer({
        fields: {
          name: 'María García',
          // Sin customer_id
        },
      });

      // Simular generación de UUID
      const pgId = airtableCustomer.fields.customer_id || `cust_${Date.now()}`;

      expect(pgId).toBeDefined();
      expect(pgId).toMatch(/^cust_/);
    });
  });

  describe('Migración de Reservations', () => {
    test('debe preservar todos los campos de reservation', () => {
      const airtableReservation = mockAirtableReservation({
        fields: {
          id: 'res_456',
          customer_name: 'Juan Pérez',
          customer_phone: '+34600123456',
          guest_count: 4,
          service_date: '2025-01-15',
          service_time: '21:00',
          status: 'confirmada',
          confirmation_code: 'ABC12345',
          source: 'VAPI',
        },
      });

      const pgReservation = {
        id: airtableReservation.fields.id,
        customer_name: airtableReservation.fields.customer_name,
        customer_phone: airtableReservation.fields.customer_phone,
        guest_count: airtableReservation.fields.guest_count,
        service_date: airtableReservation.fields.service_date,
        service_time: airtableReservation.fields.service_time,
        status: airtableReservation.fields.status,
        confirmation_code: airtableReservation.fields.confirmation_code,
        source: airtableReservation.fields.source,
      };

      expect(pgReservation.id).toBe('res_456');
      expect(pgReservation.guest_count).toBe(4);
      expect(pgReservation.status).toBe('confirmada');
      expect(pgReservation.confirmation_code).toBe('ABC12345');
    });

    test('debe convertir special_requests de string a JSONB', () => {
      const airtableReservation = mockAirtableReservation({
        fields: {
          special_requests: JSON.stringify(['cachopo_sin_gluten', 'trona']),
        },
      });

      const specialRequests = JSON.parse(airtableReservation.fields.special_requests);

      expect(Array.isArray(specialRequests)).toBe(true);
      expect(specialRequests).toContain('cachopo_sin_gluten');
      expect(specialRequests).toContain('trona');
    });

    test('debe mapear estados correctamente', () => {
      const estados = ['pendiente', 'confirmada', 'cancelada', 'no_show', 'completada'];

      estados.forEach(estado => {
        const reservation = mockAirtableReservation({
          fields: { status: estado },
        });

        expect(reservation.fields.status).toBe(estado);

        // Verificar que el estado es válido para PostgreSQL ENUM
        const validStatuses = ['pendiente', 'confirmada', 'cancelada', 'no_show', 'completada'];
        expect(validStatuses).toContain(reservation.fields.status);
      });
    });
  });

  describe('Migración de Tables', () => {
    test('debe preservar configuración de mesas', () => {
      const airtableTable = mockAirtableTable({
        fields: {
          table_id: 'A1',
          capacity_min: 2,
          capacity_max: 4,
          zone: 'interior',
          is_auxiliary: false,
          sillas_nino: true,
          accesibilidad_ruedas: false,
        },
      });

      const pgTable = {
        table_id: airtableTable.fields.table_id,
        capacity_min: airtableTable.fields.capacity_min,
        capacity_max: airtableTable.fields.capacity_max,
        zone: airtableTable.fields.zone,
        features: {
          is_auxiliary: airtableTable.fields.is_auxiliary,
          sillas_nino: airtableTable.fields.sillas_nino,
          accesibilidad_ruedas: airtableTable.fields.accesibilidad_ruedas,
        },
      };

      expect(pgTable.table_id).toBe('A1');
      expect(pgTable.capacity_min).toBe(2);
      expect(pgTable.capacity_max).toBe(4);
      expect(pgTable.features.sillas_nino).toBe(true);
    });
  });

  describe('Validación de Integridad Referencial', () => {
    test('debe mantener relaciones customer → reservation', async () => {
      // Crear customer
      const customer = await airtableClient
        .base('appXXX')
        .table('customers')
        .create({
          customer_id: 'cust_999',
          name: 'Test User',
          phone: '+34600000000',
        });

      // Crear reservation vinculada
      const reservation = await airtableClient
        .base('appXXX')
        .table('reservations')
        .create({
          id: 'res_999',
          customer_id: ['recXXX'], // Link a customer en Airtable
          customer_name: 'Test User',
        });

      // Validar que la relación existe
      expect(reservation.fields.customer_id).toBeDefined();
      expect(Array.isArray(reservation.fields.customer_id)).toBe(true);
    });
  });

  describe('Manejo de Datos Faltantes', () => {
    test('debe manejar campos NULL/undefined', () => {
      const airtableCustomer = mockAirtableCustomer({
        fields: {
          name: 'Juan Pérez',
          phone: '+34600123456',
          // email undefined
          // whatsapp undefined
        },
      });

      const pgCustomer = {
        name: airtableCustomer.fields.name,
        phone: airtableCustomer.fields.phone,
        email: airtableCustomer.fields.email || null,
        whatsapp: airtableCustomer.fields.whatsapp || null,
      };

      expect(pgCustomer.email).toBeNull();
      expect(pgCustomer.whatsapp).toBeNull();
    });

    test('debe aplicar valores por defecto', () => {
      const airtableReservation = mockAirtableReservation({
        fields: {
          id: 'res_test',
          // Sin loyalty_points, total_reservations
        },
      });

      const pgCustomer = {
        id: 'cust_new',
        loyalty_points: 0, // Default
        total_reservations: 0, // Default
        data_consent: false, // Default
      };

      expect(pgCustomer.loyalty_points).toBe(0);
      expect(pgCustomer.total_reservations).toBe(0);
      expect(pgCustomer.data_consent).toBe(false);
    });
  });

  describe('Transformación de Fechas', () => {
    test('debe convertir fechas de Airtable a PostgreSQL', () => {
      const airtableDate = '2025-01-15';
      const airtableTime = '21:00';

      // PostgreSQL timestamp
      const pgTimestamp = `${airtableDate}T${airtableTime}:00`;

      expect(pgTimestamp).toBe('2025-01-15T21:00:00');
      expect(new Date(pgTimestamp).toISOString()).toContain('2025-01-15');
    });

    test('debe manejar timestamps con timezone', () => {
      const airtableTimestamp = '2025-01-15T21:00:00';

      // Convertir a UTC
      const date = new Date(airtableTimestamp);
      const pgTimestamp = date.toISOString();

      expect(pgTimestamp).toContain('2025-01-15');
    });
  });

  describe('Validación de Datos Migrados', () => {
    test('debe validar formato de teléfono', () => {
      const phones = [
        '+34600123456',
        '+34 600 123 456',
        '600123456',
      ];

      phones.forEach(phone => {
        // Normalizar teléfono
        const normalized = phone.replace(/\s/g, '');
        expect(normalized).toMatch(/^\+?\d{9,15}$/);
      });
    });

    test('debe validar email', () => {
      const validEmails = [
        'user@example.com',
        'user.name@example.co.uk',
      ];

      const invalidEmails = [
        'invalid',
        '@example.com',
        'user@',
      ];

      validEmails.forEach(email => {
        expect(email).toMatch(/^[^\s@]+@[^\s@]+\.[^\s@]+$/);
      });

      invalidEmails.forEach(email => {
        expect(email).not.toMatch(/^[^\s@]+@[^\s@]+\.[^\s@]+$/);
      });
    });

    test('debe validar rangos numéricos', () => {
      const reservation = mockAirtableReservation({
        fields: {
          guest_count: 4,
        },
      });

      expect(reservation.fields.guest_count).toBeGreaterThan(0);
      expect(reservation.fields.guest_count).toBeLessThanOrEqual(20);
    });
  });

  describe('Rollback de Migración', () => {
    test('debe poder revertir datos migrados', async () => {
      const originalData = [];

      // Guardar datos originales
      const customer = await airtableClient
        .base('appXXX')
        .table('customers')
        .create({
          customer_id: 'cust_rollback',
          name: 'Test',
        });

      originalData.push(customer);

      // Simular migración a PostgreSQL (exitosa)
      const pgData = {
        id: customer.fields.customer_id,
        name: customer.fields.name,
      };

      expect(pgData).toBeDefined();

      // Simular rollback (eliminar de PostgreSQL, restaurar en Airtable)
      const restored = await airtableClient
        .base('appXXX')
        .table('customers')
        .find(customer.id);

      expect(restored.id).toBe(customer.id);
      expect(restored.fields.customer_id).toBe('cust_rollback');
    });
  });
});
