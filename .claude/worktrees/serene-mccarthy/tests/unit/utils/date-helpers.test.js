/**
 * Pruebas unitarias para utilidades de fecha
 */

import { describe, test, expect, beforeEach, jest } from '@jest/globals';
import {
  formatDateISO,
  formatTimeHHMM,
  getDayName,
  isWeekend,
  getFutureDateISO,
  getHoursDifference,
  isPastDate,
  isFutureDate,
  generateConfirmationCode,
  formatDateForUser,
} from '../../../src/utils/date-helpers.js';

describe('Date Helpers', () => {
  describe('formatDateISO', () => {
    test('debe formatear Date a YYYY-MM-DD', () => {
      const date = new Date('2025-01-10T15:30:00');
      const result = formatDateISO(date);

      expect(result).toBe('2025-01-10');
    });

    test('debe formatear string ISO a YYYY-MM-DD', () => {
      const result = formatDateISO('2025-01-10T15:30:00');

      expect(result).toBe('2025-01-10');
    });

    test('debe manejar fechas con un dígito', () => {
      const date = new Date('2025-01-05T15:30:00');
      const result = formatDateISO(date);

      expect(result).toBe('2025-01-05');
    });
  });

  describe('formatTimeHHMM', () => {
    test('debe formatear Date a HH:mm', () => {
      const time = new Date('2025-01-10T15:30:00');
      const result = formatTimeHHMM(time);

      expect(result).toBe('15:30');
    });

    test('debe retornar string HH:mm tal cual', () => {
      const result = formatTimeHHMM('21:00');

      expect(result).toBe('21:00');
    });

    test('debe formatear ISO string a HH:mm', () => {
      const result = formatTimeHHMM('2025-01-10T15:30:00');

      expect(result).toBe('15:30');
    });

    test('debe añadir cero a la izquierda en horas <10', () => {
      const time = new Date('2025-01-10T09:05:00');
      const result = formatTimeHHMM(time);

      expect(result).toBe('09:05');
    });
  });

  describe('getDayName', () => {
    test('debe retornar nombre en español por defecto', () => {
      // 2025-01-10 es viernes
      const result = getDayName('2025-01-10');

      expect(result).toBe('Viernes');
    });

    test('debe retornar nombre en inglés', () => {
      const result = getDayName('2025-01-10', 'en');

      expect(result).toBe('Friday');
    });

    test('debe retornar Lunes para lunes', () => {
      // 2025-01-06 es lunes
      const result = getDayName('2025-01-06');

      expect(result).toBe('Lunes');
    });

    test('debe retornar Domingo para domingo', () => {
      // 2025-01-12 es domingo
      const result = getDayName('2025-01-12');

      expect(result).toBe('Domingo');
    });
  });

  describe('isWeekend', () => {
    test('debe retornar true para sábado', () => {
      // 2025-01-11 es sábado
      const result = isWeekend('2025-01-11');

      expect(result).toBe(true);
    });

    test('debe retornar true para domingo', () => {
      // 2025-01-12 es domingo
      const result = isWeekend('2025-01-12');

      expect(result).toBe(true);
    });

    test('debe retornar false para viernes', () => {
      // 2025-01-10 es viernes
      const result = isWeekend('2025-01-10');

      expect(result).toBe(false);
    });

    test('debe retornar false para lunes', () => {
      // 2025-01-06 es lunes
      const result = isWeekend('2025-01-06');

      expect(result).toBe(false);
    });
  });

  describe('getHoursDifference', () => {
    test('debe calcular diferencia de 24 horas', () => {
      const start = '2025-01-10T10:00:00';
      const end = '2025-01-11T10:00:00';

      const result = getHoursDifference(start, end);

      expect(result).toBe(24);
    });

    test('debe calcular diferencia de 2 horas', () => {
      const start = '2025-01-10T10:00:00';
      const end = '2025-01-10T12:00:00';

      const result = getHoursDifference(start, end);

      expect(result).toBe(2);
    });

    test('debe calcular diferencia de 0.5 horas', () => {
      const start = '2025-01-10T10:00:00';
      const end = '2025-01-10T10:30:00';

      const result = getHoursDifference(start, end);

      expect(result).toBe(0.5);
    });

    test('debe manejar diferencia negativa', () => {
      const start = '2025-01-10T12:00:00';
      const end = '2025-01-10T10:00:00';

      const result = getHoursDifference(start, end);

      expect(result).toBe(-2);
    });
  });

  describe('generateConfirmationCode', () => {
    test('debe generar código de 8 caracteres', () => {
      const code = generateConfirmationCode();

      expect(code).toHaveLength(8);
    });

    test('debe generar código en mayúsculas', () => {
      const code = generateConfirmationCode();

      expect(code).toBe(code.toUpperCase());
    });

    test('debe generar código alfanumérico', () => {
      const code = generateConfirmationCode();

      expect(code).toMatch(/^[A-Z0-9]{8}$/);
    });

    test('debe generar códigos diferentes en llamadas sucesivas', () => {
      const code1 = generateConfirmationCode();
      const code2 = generateConfirmationCode();
      const code3 = generateConfirmationCode();

      // Muy baja probabilidad de colisión
      expect(code1).not.toBe(code2);
      expect(code2).not.toBe(code3);
      expect(code1).not.toBe(code3);
    });
  });

  describe('formatDateForUser', () => {
    test('debe formatear fecha en español', () => {
      // 2025-01-10 es viernes
      const result = formatDateForUser('2025-01-10');

      expect(result).toBe('Viernes 10 de Enero de 2025');
    });

    test('debe manejar primer día del mes', () => {
      const result = formatDateForUser('2025-01-01');

      expect(result).toBe('Miércoles 1 de Enero de 2025');
    });

    test('debe manejar último día del mes', () => {
      const result = formatDateForUser('2025-01-31');

      expect(result).toBe('Viernes 31 de Enero de 2025');
    });

    test('debe formatear diciembre correctamente', () => {
      const result = formatDateForUser('2025-12-25');

      expect(result).toContain('Diciembre');
      expect(result).toContain('25');
      expect(result).toContain('2025');
    });
  });

  describe('isPastDate y isFutureDate', () => {
    // Nota: Estas pruebas dependen de la fecha actual
    // En un entorno de CI/CD, podrías mockear getCurrentDateInTimezone

    test('una fecha de hace 1 año es pasado', () => {
      const pastDate = '2024-01-01T10:00:00';
      const result = isPastDate(pastDate);

      expect(result).toBe(true);
    });

    test('una fecha de dentro de 1 año es futuro', () => {
      const futureDate = '2026-12-31T10:00:00';
      const result = isFutureDate(futureDate);

      expect(result).toBe(true);
    });

    test('isFutureDate retorna false para fechas pasadas', () => {
      const pastDate = '2024-01-01T10:00:00';
      const result = isFutureDate(pastDate);

      expect(result).toBe(false);
    });

    test('isPastDate retorna false para fechas futuras', () => {
      const futureDate = '2026-12-31T10:00:00';
      const result = isPastDate(futureDate);

      expect(result).toBe(false);
    });
  });
});
