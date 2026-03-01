/**
 * Procesador de Artillery para generación de datos de prueba
 */

export function randomString() {
  return Math.random().toString(36).substring(2, 15);
}

export function randomNumber(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

export function randomDate() {
  const today = new Date();
  const futureDate = new Date(today.getTime() + Math.random() * 30 * 24 * 60 * 60 * 1000);
  return futureDate.toISOString().split('T')[0];
}

export function pick(array) {
  return array[Math.floor(Math.random() * array.length)];
}

// Custom metrics
export function recordMetrics(requestParams, response, context, ee, next) {
  // Registrar métricas personalizadas
  const duration = response.timings ? response.timings.response : 0;

  if (duration > 5000) {
    ee.emit('counter', 'requests.slow', 1);
  }

  if (response.statusCode >= 500) {
    ee.emit('counter', 'errors.server', 1);
  } else if (response.statusCode >= 400) {
    ee.emit('counter', 'errors.client', 1);
  }

  return next();
}

export default {
  randomString,
  randomNumber,
  randomDate,
  pick,
  recordMetrics,
};
