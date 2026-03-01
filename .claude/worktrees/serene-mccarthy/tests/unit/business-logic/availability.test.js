/**
 * Pruebas unitarias para la lógica de disponibilidad
 */

import { describe, test, expect, beforeEach } from '@jest/globals';
import {
  isClosedDay,
  isClosedTuesdayAfterHoliday,
  calculateAvailableTurns,
  canBookTurn,
  validateSpecialRequests,
  checkLimitedResources,
  checkAvailability,
  CLOSED_DAYS,
  TURN_CONFIG,
  LARGE_GROUP_CONFIG,
} from '../../../src/business-logic/availability.js';

describe('Availability Business Logic', () => {
  describe('isClosedDay', () => {
    test('debe retornar closed=true para lunes', () => {
      // 2025-01-06 es lunes
      const result = isClosedDay('2025-01-06');

      expect(result.closed).toBe(true);
      expect(result.reason).toBe('closed_monday');
      expect(result.message).toContain('lunes');
    });

    test('debe retornar closed=false para martes', () => {
      // 2025-01-07 es martes
      const result = isClosedDay('2025-01-07');

      expect(result.closed).toBe(false);
      expect(result.reason).toBeNull();
    });

    test('debe retornar closed=false para viernes', () => {
      // 2025-01-10 es viernes
      const result = isClosedDay('2025-01-10');

      expect(result.closed).toBe(false);
      expect(result.reason).toBeNull();
    });

    test('debe retornar closed=false para sábado', () => {
      // 2025-01-11 es sábado
      const result = isClosedDay('2025-01-11');

      expect(result.closed).toBe(false);
      expect(result.reason).toBeNull();
    });

    test('debe retornar closed=false para domingo', () => {
      // 2025-01-12 es domingo
      const result = isClosedDay('2025-01-12');

      expect(result.closed).toBe(false);
      expect(result.reason).toBeNull();
    });
  });

  describe('isClosedTuesdayAfterHoliday', () => {
    test('debe retornar closed=true para martes tras festivo en lunes', () => {
      // 2025-01-07 es martes, 2025-01-06 es lunes (festivo)
      const holidays = ['2025-01-06'];
      const result = isClosedTuesdayAfterHoliday('2025-01-07', holidays);

      expect(result.closed).toBe(true);
      expect(result.reason).toBe('closed_tuesday_after_holiday');
    });

    test('debe retornar closed=false para martes normal', () => {
      const holidays = [];
      const result = isClosedTuesdayAfterHoliday('2025-01-07', holidays);

      expect(result.closed).toBe(false);
    });

    test('debe retornar closed=false para día que no es martes', () => {
      const holidays = ['2025-01-06'];
      // 2025-01-08 es miércoles
      const result = isClosedTuesdayAfterHoliday('2025-01-08', holidays);

      expect(result.closed).toBe(false);
    });
  });

  describe('calculateAvailableTurns', () => {
    test('debe retornar 2 turnos para viernes', () => {
      // 2025-01-10 es viernes
      const turns = calculateAvailableTurns('2025-01-10');

      expect(turns).toHaveLength(2);
      expect(turns[0].id).toBe('turno_1');
      expect(turns[1].id).toBe('turno_2');
    });

    test('debe retornar 2 turnos para sábado', () => {
      // 2025-01-11 es sábado
      const turns = calculateAvailableTurns('2025-01-11');

      expect(turns).toHaveLength(2);
      expect(turns[0].id).toBe('turno_1');
      expect(turns[1].id).toBe('turno_2');
    });

    test('debe retornar 1 turno para martes', () => {
      // 2025-01-07 es martes
      const turns = calculateAvailableTurns('2025-01-07');

      expect(turns).toHaveLength(1);
      expect(turns[0].id).toBe('turno_1');
    });

    test('debe retornar 1 turno para miércoles', () => {
      // 2025-01-08 es miércoles
      const turns = calculateAvailableTurns('2025-01-08');

      expect(turns).toHaveLength(1);
      expect(turns[0].id).toBe('turno_1');
    });

    test('debe retornar 1 turno para jueves', () => {
      // 2025-01-09 es jueves
      const turns = calculateAvailableTurns('2025-01-09');

      expect(turns).toHaveLength(1);
      expect(turns[0].id).toBe('turno_1');
    });

    test('debe retornar 1 turno para domingo', () => {
      // 2025-01-12 es domingo
      const turns = calculateAvailableTurns('2025-01-12');

      expect(turns).toHaveLength(1);
      expect(turns[0].id).toBe('turno_1');
    });
  });

  describe('canBookTurn', () => {
    test('grupo pequeño (<7) puede reservar cualquier turno', () => {
      // Viernes con grupo de 4
      const result = canBookTurn('2025-01-10', 4, 'turno_2');

      expect(result.allowed).toBe(true);
      expect(result.reason).toBeNull();
    });

    test('grupo grande (≥7) puede reservar turno_1 en viernes', () => {
      const result = canBookTurn('2025-01-10', 8, 'turno_1');

      expect(result.allowed).toBe(true);
      expect(result.reason).toBeNull();
    });

    test('grupo grande (≥7) NO puede reservar turno_2 en viernes', () => {
      const result = canBookTurn('2025-01-10', 8, 'turno_2');

      expect(result.allowed).toBe(false);
      expect(result.reason).toBe('large_group_turn_restriction');
      expect(result.message).toContain('7+');
    });

    test('grupo grande (≥7) puede reservar turno_1 en sábado', () => {
      const result = canBookTurn('2025-01-11', 10, 'turno_1');

      expect(result.allowed).toBe(true);
      expect(result.reason).toBeNull();
    });

    test('grupo grande (≥7) NO puede reservar turno_2 en sábado', () => {
      const result = canBookTurn('2025-01-11', 10, 'turno_2');

      expect(result.allowed).toBe(false);
      expect(result.reason).toBe('large_group_turn_restriction');
    });

    test('grupo grande (≥7) puede reservar turno_1 en martes (no alta demanda)', () => {
      const result = canBookTurn('2025-01-07', 8, 'turno_1');

      expect(result.allowed).toBe(true);
      expect(result.reason).toBeNull();
    });

    test('exactamente 7 personas es considerado grupo grande', () => {
      const result = canBookTurn('2025-01-10', 7, 'turno_2');

      expect(result.allowed).toBe(false);
      expect(result.reason).toBe('large_group_turn_restriction');
    });

    test('6 personas NO es grupo grande', () => {
      const result = canBookTurn('2025-01-10', 6, 'turno_2');

      expect(result.allowed).toBe(true);
      expect(result.reason).toBeNull();
    });
  });

  describe('validateSpecialRequests', () => {
    test('cachopo sin gluten con 24h de antelación es válido', () => {
      const reservationDate = '2025-01-10T21:00:00';
      const currentDate = '2025-01-08T21:00:00'; // 48 horas antes

      const result = validateSpecialRequests(
        ['cachopo_sin_gluten'],
        reservationDate,
        currentDate
      );

      expect(result.valid).toBe(true);
      expect(result.issues).toHaveLength(0);
    });

    test('cachopo sin gluten con menos de 24h es inválido', () => {
      const reservationDate = '2025-01-10T21:00:00';
      const currentDate = '2025-01-10T10:00:00'; // 11 horas antes

      const result = validateSpecialRequests(
        ['cachopo_sin_gluten'],
        reservationDate,
        currentDate
      );

      expect(result.valid).toBe(false);
      expect(result.issues).toHaveLength(1);
      expect(result.issues[0].reason).toBe('insufficient_advance_time');
      expect(result.issues[0].required_hours).toBe(24);
    });

    test('solicitudes no especiales no generan issues', () => {
      const result = validateSpecialRequests(
        ['trona', 'accesibilidad_silla_ruedas'],
        '2025-01-10T21:00:00',
        '2025-01-10T10:00:00'
      );

      expect(result.valid).toBe(true);
      expect(result.issues).toHaveLength(0);
    });

    test('múltiples solicitudes especiales se validan todas', () => {
      const reservationDate = '2025-01-10T21:00:00';
      const currentDate = '2025-01-10T10:00:00'; // Solo 11 horas

      const result = validateSpecialRequests(
        ['cachopo_sin_gluten'],
        reservationDate,
        currentDate
      );

      expect(result.valid).toBe(false);
      expect(result.issues).toHaveLength(1);
    });
  });

  describe('checkLimitedResources', () => {
    test('trona disponible cuando no hay uso actual', () => {
      const result = checkLimitedResources(['trona'], {});

      expect(result.available).toBe(true);
      expect(result.issues).toHaveLength(0);
    });

    test('trona disponible cuando hay 1 en uso (max 2)', () => {
      const result = checkLimitedResources(['trona'], { tronas: 1 });

      expect(result.available).toBe(true);
      expect(result.issues).toHaveLength(0);
    });

    test('trona NO disponible cuando ya hay 2 en uso', () => {
      const result = checkLimitedResources(['trona'], { tronas: 2 });

      expect(result.available).toBe(false);
      expect(result.issues).toHaveLength(1);
      expect(result.issues[0].reason).toBe('resource_exhausted');
      expect(result.issues[0].resource).toBe('tronas');
      expect(result.issues[0].max).toBe(2);
    });

    test('sin solicitudes de recursos retorna available', () => {
      const result = checkLimitedResources([], { tronas: 2 });

      expect(result.available).toBe(true);
      expect(result.issues).toHaveLength(0);
    });
  });

  describe('checkAvailability - Integración completa', () => {
    test('reserva válida en viernes con 4 personas', () => {
      const result = checkAvailability({
        date: '2025-01-10',
        guestCount: 4,
        turnId: 'turno_1',
        specialRequests: [],
        currentDate: '2025-01-08',
      });

      expect(result.available).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
    });

    test('reserva rechazada en lunes', () => {
      const result = checkAvailability({
        date: '2025-01-06', // Lunes
        guestCount: 4,
        turnId: 'turno_1',
        specialRequests: [],
        currentDate: '2025-01-05',
      });

      expect(result.available).toBe(false);
      expect(result.errors).toHaveLength(1);
      expect(result.errors[0].reason).toBe('closed_monday');
    });

    test('reserva rechazada para grupo grande en turno_2 de sábado', () => {
      const result = checkAvailability({
        date: '2025-01-11', // Sábado
        guestCount: 8,
        turnId: 'turno_2',
        specialRequests: [],
        currentDate: '2025-01-09',
      });

      expect(result.available).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
      const groupError = result.errors.find(e => e.reason === 'large_group_turn_restriction');
      expect(groupError).toBeDefined();
    });

    test('reserva con warning para cachopo sin gluten sin tiempo suficiente', () => {
      const result = checkAvailability({
        date: '2025-01-10T21:00:00',
        guestCount: 2,
        turnId: 'turno_1',
        specialRequests: ['cachopo_sin_gluten'],
        currentDate: '2025-01-10T10:00:00', // Solo 11 horas
      });

      expect(result.available).toBe(true); // No es error, es warning
      expect(result.warnings).toHaveLength(1);
      expect(result.warnings[0].reason).toBe('insufficient_advance_time');
    });

    test('reserva rechazada cuando no hay tronas disponibles', () => {
      const result = checkAvailability({
        date: '2025-01-10',
        guestCount: 4,
        turnId: 'turno_1',
        specialRequests: ['trona'],
        currentDate: '2025-01-09',
        currentResourceUsage: { tronas: 2 },
      });

      expect(result.available).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
      const resourceError = result.errors.find(e => e.reason === 'resource_exhausted');
      expect(resourceError).toBeDefined();
    });

    test('reserva rechazada en turno inexistente para martes', () => {
      const result = checkAvailability({
        date: '2025-01-07', // Martes (solo 1 turno)
        guestCount: 4,
        turnId: 'turno_2', // No existe en martes
        specialRequests: [],
        currentDate: '2025-01-06',
      });

      expect(result.available).toBe(false);
      const turnError = result.errors.find(e => e.reason === 'turn_not_available');
      expect(turnError).toBeDefined();
    });

    test('metadata contiene información correcta', () => {
      const result = checkAvailability({
        date: '2025-01-10',
        guestCount: 4,
        turnId: 'turno_1',
        specialRequests: [],
        currentDate: '2025-01-09',
      });

      expect(result.metadata).toBeDefined();
      expect(result.metadata.date).toBe('2025-01-10');
      expect(result.metadata.guestCount).toBe(4);
      expect(result.metadata.turnId).toBe('turno_1');
      expect(result.metadata.availableTurns).toContain('turno_1');
      expect(result.metadata.availableTurns).toContain('turno_2');
    });
  });
});
