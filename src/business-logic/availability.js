/**
 * Lógica de negocio para gestión de disponibilidad
 * Implementa las reglas del restaurante En Las Nubes
 */

import { parse, format, addDays, getDay, isAfter, isBefore, parseISO } from 'date-fns';
import { zonedTimeToUtc, utcToZonedTime } from 'date-fns-tz';

const TIMEZONE = 'Europe/Madrid';

/**
 * Días cerrados del restaurante
 */
export const CLOSED_DAYS = {
  MONDAY: 1, // Lunes siempre cerrado
  SUNDAY_DINNER: 'sunday_dinner', // Domingo noche cerrado
};

/**
 * Horarios del restaurante
 */
export const BUSINESS_HOURS = {
  LUNCH: {
    start: '13:30',
    end: '17:30',
  },
  DINNER: {
    start: '21:00',
    end: '22:30',
  },
};

/**
 * Configuración de turnos
 */
export const TURN_CONFIG = {
  // Viernes y Sábado tienen 2 turnos
  DOUBLE_TURN_DAYS: [5, 6], // Viernes=5, Sábado=6
  TURNS: {
    TURN_1: {
      id: 'turno_1',
      name: 'Turno 1',
      time: '21:00',
    },
    TURN_2: {
      id: 'turno_2',
      name: 'Turno 2',
      time: '22:30',
    },
  },
};

/**
 * Configuración de grupos grandes
 */
export const LARGE_GROUP_CONFIG = {
  MIN_SIZE: 7,
  RESTRICTIONS: {
    // En alta demanda (Viernes/Sábado), grupos grandes solo Turno 1
    HIGH_DEMAND_DAYS: [5, 6],
    ALLOWED_TURNS: ['turno_1'],
  },
};

/**
 * Solicitudes especiales que requieren tiempo de preparación
 */
export const SPECIAL_REQUESTS_CONFIG = {
  cachopo_sin_gluten: {
    advance_hours: 24,
    message: 'El cachopo sin gluten requiere 24 horas de antelación',
  },
};

/**
 * Recursos limitados
 */
export const LIMITED_RESOURCES = {
  tronas: {
    max: 2,
    message: 'Máximo 2 tronas disponibles',
  },
};

/**
 * Verifica si una fecha es un día cerrado
 * @param {string|Date} date - Fecha a verificar
 * @returns {Object} { closed: boolean, reason: string }
 */
export function isClosedDay(date) {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  const dayOfWeek = getDay(dateObj);

  // Lunes cerrado
  if (dayOfWeek === CLOSED_DAYS.MONDAY) {
    return {
      closed: true,
      reason: 'closed_monday',
      message: 'Los lunes estamos cerrados',
    };
  }

  return {
    closed: false,
    reason: null,
    message: null,
  };
}

/**
 * Verifica si el martes siguiente a un festivo en lunes está cerrado
 * @param {string|Date} date - Fecha a verificar
 * @param {Array} holidays - Array de fechas festivas
 * @returns {Object} { closed: boolean, reason: string }
 */
export function isClosedTuesdayAfterHoliday(date, holidays = []) {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  const dayOfWeek = getDay(dateObj);

  // Si es martes
  if (dayOfWeek === 2) {
    // Verificar si el lunes anterior fue festivo
    const previousMonday = addDays(dateObj, -1);
    const isMondayHoliday = holidays.some(
      holiday => format(parseISO(holiday), 'yyyy-MM-dd') === format(previousMonday, 'yyyy-MM-dd')
    );

    if (isMondayHoliday) {
      return {
        closed: true,
        reason: 'closed_tuesday_after_holiday',
        message: 'Martes cerrado tras festivo en lunes',
      };
    }
  }

  return {
    closed: false,
    reason: null,
    message: null,
  };
}

/**
 * Calcula los turnos disponibles para una fecha
 * @param {string|Date} date - Fecha
 * @returns {Array} Array de turnos disponibles
 */
export function calculateAvailableTurns(date) {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  const dayOfWeek = getDay(dateObj);

  // Viernes (5) y Sábado (6) tienen 2 turnos
  if (TURN_CONFIG.DOUBLE_TURN_DAYS.includes(dayOfWeek)) {
    return [
      TURN_CONFIG.TURNS.TURN_1,
      TURN_CONFIG.TURNS.TURN_2,
    ];
  }

  // Resto de días solo Turno 1
  return [TURN_CONFIG.TURNS.TURN_1];
}

/**
 * Verifica si un grupo puede reservar un turno específico
 * @param {string|Date} date - Fecha
 * @param {number} guestCount - Número de personas
 * @param {string} turnId - ID del turno
 * @returns {Object} { allowed: boolean, reason: string }
 */
export function canBookTurn(date, guestCount, turnId) {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  const dayOfWeek = getDay(dateObj);

  // Si no es grupo grande, puede reservar cualquier turno disponible
  if (guestCount < LARGE_GROUP_CONFIG.MIN_SIZE) {
    return {
      allowed: true,
      reason: null,
      message: null,
    };
  }

  // Grupo grande en día de alta demanda
  if (LARGE_GROUP_CONFIG.RESTRICTIONS.HIGH_DEMAND_DAYS.includes(dayOfWeek)) {
    const allowed = LARGE_GROUP_CONFIG.RESTRICTIONS.ALLOWED_TURNS.includes(turnId);

    if (!allowed) {
      return {
        allowed: false,
        reason: 'large_group_turn_restriction',
        message: `Grupos de ${LARGE_GROUP_CONFIG.MIN_SIZE}+ personas solo pueden reservar ${LARGE_GROUP_CONFIG.RESTRICTIONS.ALLOWED_TURNS.join(', ')} en fin de semana`,
      };
    }
  }

  return {
    allowed: true,
    reason: null,
    message: null,
  };
}

/**
 * Valida solicitudes especiales
 * @param {Array} specialRequests - Array de solicitudes especiales
 * @param {string|Date} reservationDate - Fecha de la reserva
 * @param {string|Date} currentDate - Fecha actual
 * @returns {Object} { valid: boolean, issues: Array }
 */
export function validateSpecialRequests(specialRequests, reservationDate, currentDate = new Date()) {
  const issues = [];
  const reservationDateObj = typeof reservationDate === 'string' ? parseISO(reservationDate) : reservationDate;
  const currentDateObj = typeof currentDate === 'string' ? parseISO(currentDate) : currentDate;

  specialRequests.forEach(request => {
    const config = SPECIAL_REQUESTS_CONFIG[request];

    if (config) {
      // Calcular horas de antelación
      const hoursAdvance = (reservationDateObj - currentDateObj) / (1000 * 60 * 60);

      if (hoursAdvance < config.advance_hours) {
        issues.push({
          request,
          reason: 'insufficient_advance_time',
          message: config.message,
          required_hours: config.advance_hours,
          current_hours: Math.floor(hoursAdvance),
        });
      }
    }
  });

  return {
    valid: issues.length === 0,
    issues,
  };
}

/**
 * Verifica disponibilidad de recursos limitados
 * @param {Array} specialRequests - Array de solicitudes especiales
 * @param {Object} currentUsage - Uso actual de recursos { tronas: 1 }
 * @returns {Object} { available: boolean, issues: Array }
 */
export function checkLimitedResources(specialRequests, currentUsage = {}) {
  const issues = [];

  // Verificar tronas
  if (specialRequests.includes('trona')) {
    const currentTronas = currentUsage.tronas || 0;
    const maxTronas = LIMITED_RESOURCES.tronas.max;

    if (currentTronas >= maxTronas) {
      issues.push({
        resource: 'tronas',
        reason: 'resource_exhausted',
        message: LIMITED_RESOURCES.tronas.message,
        max: maxTronas,
        current: currentTronas,
      });
    }
  }

  return {
    available: issues.length === 0,
    issues,
  };
}

/**
 * Verificación completa de disponibilidad
 * @param {Object} params - Parámetros de la reserva
 * @returns {Object} Resultado de la verificación
 */
export function checkAvailability(params) {
  const {
    date,
    guestCount,
    turnId,
    specialRequests = [],
    currentDate = new Date(),
    holidays = [],
    currentResourceUsage = {},
  } = params;

  const errors = [];
  const warnings = [];

  // 1. Verificar día cerrado
  const closedCheck = isClosedDay(date);
  if (closedCheck.closed) {
    errors.push(closedCheck);
  }

  // 2. Verificar martes tras festivo
  const tuesdayCheck = isClosedTuesdayAfterHoliday(date, holidays);
  if (tuesdayCheck.closed) {
    errors.push(tuesdayCheck);
  }

  // 3. Verificar turnos disponibles
  const availableTurns = calculateAvailableTurns(date);
  const turnExists = availableTurns.some(t => t.id === turnId);

  if (!turnExists) {
    errors.push({
      reason: 'turn_not_available',
      message: `El turno ${turnId} no está disponible para esta fecha`,
      available_turns: availableTurns.map(t => t.id),
    });
  }

  // 4. Verificar restricciones de grupo grande
  const groupCheck = canBookTurn(date, guestCount, turnId);
  if (!groupCheck.allowed) {
    errors.push(groupCheck);
  }

  // 5. Validar solicitudes especiales
  const specialRequestsCheck = validateSpecialRequests(specialRequests, date, currentDate);
  if (!specialRequestsCheck.valid) {
    warnings.push(...specialRequestsCheck.issues);
  }

  // 6. Verificar recursos limitados
  const resourcesCheck = checkLimitedResources(specialRequests, currentResourceUsage);
  if (!resourcesCheck.available) {
    errors.push(...resourcesCheck.issues);
  }

  return {
    available: errors.length === 0,
    errors,
    warnings,
    metadata: {
      date: format(typeof date === 'string' ? parseISO(date) : date, 'yyyy-MM-dd'),
      guestCount,
      turnId,
      availableTurns: availableTurns.map(t => t.id),
    },
  };
}

export default {
  isClosedDay,
  isClosedTuesdayAfterHoliday,
  calculateAvailableTurns,
  canBookTurn,
  validateSpecialRequests,
  checkLimitedResources,
  checkAvailability,
  CLOSED_DAYS,
  BUSINESS_HOURS,
  TURN_CONFIG,
  LARGE_GROUP_CONFIG,
  SPECIAL_REQUESTS_CONFIG,
  LIMITED_RESOURCES,
};
