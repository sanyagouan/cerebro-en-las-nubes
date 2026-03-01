/**
 * Utilidades para manejo de fechas
 */

import { format, parse, addDays, addHours, isAfter, isBefore, parseISO, getDay } from 'date-fns';
import { zonedTimeToUtc, utcToZonedTime, format as formatTz } from 'date-fns-tz';

const TIMEZONE = 'Europe/Madrid';

/**
 * Obtiene la fecha actual en timezone de Madrid
 * @returns {Date}
 */
export function getCurrentDateInTimezone() {
  return utcToZonedTime(new Date(), TIMEZONE);
}

/**
 * Formatea una fecha en formato ISO (YYYY-MM-DD)
 * @param {Date|string} date
 * @returns {string}
 */
export function formatDateISO(date) {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return format(dateObj, 'yyyy-MM-dd');
}

/**
 * Formatea una hora en formato HH:mm
 * @param {Date|string} time
 * @returns {string}
 */
export function formatTimeHHMM(time) {
  if (typeof time === 'string') {
    // Si ya está en formato HH:mm, retornar tal cual
    if (/^\d{2}:\d{2}$/.test(time)) {
      return time;
    }
    // Si es ISO string, parsear y formatear
    return format(parseISO(time), 'HH:mm');
  }
  return format(time, 'HH:mm');
}

/**
 * Convierte una fecha y hora a timestamp UTC
 * @param {string} dateStr - Fecha en formato YYYY-MM-DD
 * @param {string} timeStr - Hora en formato HH:mm
 * @returns {Date}
 */
export function dateTimeToUTC(dateStr, timeStr) {
  const localDateTime = `${dateStr}T${timeStr}:00`;
  const localDate = parseISO(localDateTime);
  return zonedTimeToUtc(localDate, TIMEZONE);
}

/**
 * Obtiene el nombre del día de la semana
 * @param {Date|string} date
 * @param {string} locale - 'es' o 'en'
 * @returns {string}
 */
export function getDayName(date, locale = 'es') {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  const dayOfWeek = getDay(dateObj);

  const names = {
    es: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
    en: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
  };

  return names[locale][dayOfWeek];
}

/**
 * Verifica si una fecha es fin de semana
 * @param {Date|string} date
 * @returns {boolean}
 */
export function isWeekend(date) {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  const dayOfWeek = getDay(dateObj);
  return dayOfWeek === 0 || dayOfWeek === 6; // Domingo=0, Sábado=6
}

/**
 * Obtiene la fecha dentro de N días
 * @param {number} days
 * @returns {string} Fecha en formato YYYY-MM-DD
 */
export function getFutureDateISO(days) {
  const futureDate = addDays(getCurrentDateInTimezone(), days);
  return formatDateISO(futureDate);
}

/**
 * Calcula las horas entre dos fechas
 * @param {Date|string} startDate
 * @param {Date|string} endDate
 * @returns {number} Horas de diferencia
 */
export function getHoursDifference(startDate, endDate) {
  const start = typeof startDate === 'string' ? parseISO(startDate) : startDate;
  const end = typeof endDate === 'string' ? parseISO(endDate) : endDate;

  return (end - start) / (1000 * 60 * 60);
}

/**
 * Verifica si una fecha está en el pasado
 * @param {Date|string} date
 * @returns {boolean}
 */
export function isPastDate(date) {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  const now = getCurrentDateInTimezone();

  return isBefore(dateObj, now);
}

/**
 * Verifica si una fecha está en el futuro
 * @param {Date|string} date
 * @returns {boolean}
 */
export function isFutureDate(date) {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  const now = getCurrentDateInTimezone();

  return isAfter(dateObj, now);
}

/**
 * Genera código de confirmación de 8 caracteres
 * @returns {string}
 */
export function generateConfirmationCode() {
  return Math.random().toString(36).substring(2, 10).toUpperCase();
}

/**
 * Formatea una fecha para mensajes al usuario
 * @param {Date|string} date
 * @param {string} locale
 * @returns {string} Ej: "Viernes 10 de Enero de 2025"
 */
export function formatDateForUser(date, locale = 'es') {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;

  if (locale === 'es') {
    const dayName = getDayName(dateObj, 'es');
    const day = format(dateObj, 'd');
    const monthNames = [
      'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];
    const month = monthNames[dateObj.getMonth()];
    const year = format(dateObj, 'yyyy');

    return `${dayName} ${day} de ${month} de ${year}`;
  }

  return format(dateObj, 'EEEE, MMMM d, yyyy');
}

export default {
  getCurrentDateInTimezone,
  formatDateISO,
  formatTimeHHMM,
  dateTimeToUTC,
  getDayName,
  isWeekend,
  getFutureDateISO,
  getHoursDifference,
  isPastDate,
  isFutureDate,
  generateConfirmationCode,
  formatDateForUser,
  TIMEZONE,
};
