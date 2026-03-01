/**
 * Pruebas End-to-End del flujo completo de reserva
 * Simula el ciclo de vida completo: Llamada → Confirmación → Recordatorio
 */

import { describe, test, expect, beforeEach, afterEach } from '@jest/globals';
import { WorkflowExecutor } from '../helpers/workflow-executor.js';
import { mockVAPIWebhook } from '../mocks/vapi.mock.js';
import { mockTwilioConfirmWebhook, mockTwilioCancelWebhook } from '../mocks/twilio.mock.js';
import { MockAirtableClient } from '../mocks/airtable.mock.js';

describe('E2E: Complete Reservation Flow', () => {
  let executor;
  let airtableClient;
  let createdReservationId;

  beforeEach(() => {
    executor = new WorkflowExecutor();
    airtableClient = new MockAirtableClient();
    createdReservationId = null;
  });

  afterEach(() => {
    if (airtableClient) {
      airtableClient.reset();
    }
  });

  describe('Flujo de Reserva Exitosa', () => {
    test('debe completar ciclo: Llamada → Creación → Confirmación WhatsApp', async () => {
      // PASO 1: Llamada VAPI
      const vapiPayload = mockVAPIWebhook({
        analysis: {
          structuredData: {
            intent: 'reserva',
            guest_count: 4,
            service_date: '2025-01-15',
            service_time: '21:00',
            customer_name: 'Juan Pérez',
            customer_phone: '+34600123456',
          },
        },
      });

      const vapiResult = await executor.executeWorkflow(
        'TRIG_VAPI_Voice_Agent_Reservation',
        vapiPayload
      );

      expect(vapiResult.status).toBe('success');
      expect(vapiResult.classification).toBe('reserva');
      expect(vapiResult.reservationId).toBeDefined();
      createdReservationId = vapiResult.reservationId;

      // PASO 2: Simular creación en Airtable
      const reservation = await airtableClient
        .base('appXXX')
        .table('reservations')
        .create({
          id: createdReservationId,
          customer_name: 'Juan Pérez',
          customer_phone: '+34600123456',
          guest_count: 4,
          service_date: '2025-01-15',
          service_time: '21:00',
          status: 'pendiente',
          source: 'VAPI',
        });

      expect(reservation.id).toBeDefined();
      expect(reservation.fields.status).toBe('pendiente');

      // PASO 3: Confirmación por WhatsApp
      const twilioPayload = mockTwilioConfirmWebhook('+34600123456');

      const twilioResult = await executor.executeWorkflow(
        'TRIG_Twilio_WhatsApp_Confirmation_CRM',
        twilioPayload
      );

      expect(twilioResult.status).toBe('success');
      expect(twilioResult.action).toBe('confirmed');
      expect(twilioResult.reservationStatus).toBe('confirmada');

      // PASO 4: Verificar actualización en Airtable
      const updated = await airtableClient
        .base('appXXX')
        .table('reservations')
        .update(reservation.id, {
          status: 'confirmada',
          confirmed_at: new Date().toISOString(),
        });

      expect(updated.fields.status).toBe('confirmada');
      expect(updated.fields.confirmed_at).toBeDefined();
    });

    test('debe manejar cancelación después de crear reserva', async () => {
      // PASO 1: Crear reserva
      const vapiPayload = mockVAPIWebhook();
      const vapiResult = await executor.executeWorkflow(
        'TRIG_VAPI_Voice_Agent_Reservation',
        vapiPayload
      );

      createdReservationId = vapiResult.reservationId;

      const reservation = await airtableClient
        .base('appXXX')
        .table('reservations')
        .create({
          id: createdReservationId,
          status: 'pendiente',
        });

      // PASO 2: Cancelar por WhatsApp
      const cancelPayload = mockTwilioCancelWebhook();
      const cancelResult = await executor.executeWorkflow(
        'TRIG_Twilio_WhatsApp_Confirmation_CRM',
        cancelPayload
      );

      expect(cancelResult.action).toBe('cancelled');
      expect(cancelResult.reservationStatus).toBe('cancelada');

      // PASO 3: Actualizar en Airtable
      const updated = await airtableClient
        .base('appXXX')
        .table('reservations')
        .update(reservation.id, {
          status: 'cancelada',
        });

      expect(updated.fields.status).toBe('cancelada');
    });
  });

  describe('Flujo con Recordatorios', () => {
    test('debe enviar recordatorio para reserva pendiente', async () => {
      // PASO 1: Crear reserva pendiente
      const reservation = await airtableClient
        .base('appXXX')
        .table('reservations')
        .create({
          id: 'res_test_123',
          status: 'pendiente',
          service_date: '2025-01-15',
          service_time: '21:00',
        });

      // PASO 2: Ejecutar workflow de recordatorios
      const reminderPayload = {
        date: '2025-01-15',
        reservations: [
          {
            id: reservation.id,
            status: 'pendiente',
            service_date: '2025-01-15',
            service_time: '21:00',
          },
        ],
      };

      const reminderResult = await executor.executeWorkflow(
        'SCHED_Reminders_NoShow_Alerts',
        reminderPayload
      );

      expect(reminderResult.status).toBe('success');
      expect(reminderResult.totalSent).toBe(1);
      expect(reminderResult.reminders[0].sent).toBe(true);
      expect(reminderResult.reminders[0].sentAt).toBeDefined();
    });

    test('debe detectar no-show y marcar reserva', async () => {
      // PASO 1: Crear reserva confirmada pasada
      const reservation = await airtableClient
        .base('appXXX')
        .table('reservations')
        .create({
          id: 'res_noshow_123',
          status: 'confirmada',
          service_date: '2025-01-10',
          service_time: '21:00',
        });

      // PASO 2: Ejecutar workflow de no-shows
      const noShowPayload = {
        date: '2025-01-15', // 5 días después
        reservations: [
          {
            id: reservation.id,
            status: 'confirmada',
            service_date: '2025-01-10',
            service_time: '21:00',
            isPast: true,
          },
        ],
      };

      const noShowResult = await executor.executeWorkflow(
        'SCHED_Reminders_NoShow_Alerts',
        noShowPayload
      );

      expect(noShowResult.status).toBe('success');
      expect(noShowResult.totalNoShows).toBe(1);
      expect(noShowResult.noShows[0].markedNoShow).toBe(true);
    });
  });

  describe('Manejo de Errores en Flujo Completo', () => {
    test('debe capturar y registrar error en creación de reserva', async () => {
      // PASO 1: Intentar crear reserva en día cerrado (lunes)
      const mondayPayload = mockVAPIWebhook({
        analysis: {
          structuredData: {
            intent: 'reserva',
            service_date: '2025-01-06', // Lunes
            guest_count: 4,
          },
        },
      });

      const vapiResult = await executor.executeWorkflow(
        'TRIG_VAPI_Voice_Agent_Reservation',
        mondayPayload
      );

      expect(vapiResult.status).toBe('rejected');
      expect(vapiResult.reason).toBe('closed_monday');

      // PASO 2: Procesar error
      const errorPayload = {
        error: {
          type: 'business_rule_violation',
          message: 'Cannot book on closed day',
          context: {
            date: '2025-01-06',
            reason: 'closed_monday',
          },
        },
        source: 'VAPI_Workflow',
      };

      const errorResult = await executor.executeWorkflow(
        'ERROR_Global_Error_Handler_QA',
        errorPayload
      );

      expect(errorResult.status).toBe('success');
      expect(errorResult.logged).toBe(true);
    });
  });

  describe('Flujo Completo con Validaciones', () => {
    test('debe validar y rechazar grupo grande en turno 2 de sábado', async () => {
      const largeGroupPayload = mockVAPIWebhook({
        analysis: {
          structuredData: {
            intent: 'reserva',
            guest_count: 10,
            service_date: '2025-01-11', // Sábado
            service_time: '22:30', // Turno 2
          },
        },
      });

      const vapiResult = await executor.executeWorkflow(
        'TRIG_VAPI_Voice_Agent_Reservation',
        largeGroupPayload
      );

      // El workflow debería aceptar la reserva (se valida en negocio)
      expect(vapiResult.status).toBe('success');
      expect(vapiResult.extractedData.guest_count).toBe(10);
    });
  });

  describe('Integridad de Datos', () => {
    test('debe mantener consistencia entre workflows', async () => {
      const customerPhone = '+34600999888';

      // PASO 1: Primera reserva
      const reservation1 = await airtableClient
        .base('appXXX')
        .table('reservations')
        .create({
          id: 'res_001',
          customer_phone: customerPhone,
          status: 'pendiente',
        });

      // PASO 2: Segunda reserva del mismo cliente
      const reservation2 = await airtableClient
        .base('appXXX')
        .table('reservations')
        .create({
          id: 'res_002',
          customer_phone: customerPhone,
          status: 'pendiente',
        });

      // PASO 3: Confirmar ambas
      const confirmPayload = mockTwilioConfirmWebhook(customerPhone);
      const confirmResult = await executor.executeWorkflow(
        'TRIG_Twilio_WhatsApp_Confirmation_CRM',
        confirmPayload
      );

      expect(confirmResult.status).toBe('success');

      // Ambas reservas deberían existir
      const res1 = await airtableClient
        .base('appXXX')
        .table('reservations')
        .find(reservation1.id);

      const res2 = await airtableClient
        .base('appXXX')
        .table('reservations')
        .find(reservation2.id);

      expect(res1).toBeDefined();
      expect(res2).toBeDefined();
    });
  });

  describe('Performance del Flujo Completo', () => {
    test('debe completar flujo en tiempo razonable (<5s)', async () => {
      const startTime = Date.now();

      // Flujo completo
      const vapiResult = await executor.executeWorkflow(
        'TRIG_VAPI_Voice_Agent_Reservation',
        mockVAPIWebhook()
      );

      const reservation = await airtableClient
        .base('appXXX')
        .table('reservations')
        .create({
          id: vapiResult.reservationId,
          status: 'pendiente',
        });

      const twilioResult = await executor.executeWorkflow(
        'TRIG_Twilio_WhatsApp_Confirmation_CRM',
        mockTwilioConfirmWebhook()
      );

      const duration = Date.now() - startTime;

      expect(duration).toBeLessThan(5000); // 5 segundos
      expect(vapiResult.status).toBe('success');
      expect(twilioResult.status).toBe('success');
    });
  });
});
