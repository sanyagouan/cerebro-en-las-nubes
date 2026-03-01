/**
 * Setup global para todas las pruebas
 * Se ejecuta una vez antes de todas las pruebas
 */

import { jest } from '@jest/globals';

// Configurar timezone a Europe/Madrid
process.env.TZ = 'Europe/Madrid';

// Variables de entorno para testing
process.env.NODE_ENV = 'test';
process.env.N8N_API_URL = 'https://n8n-test.example.com';
process.env.N8N_API_KEY = 'test-api-key';
process.env.AIRTABLE_BASE_ID = 'test-base-id';
process.env.AIRTABLE_API_KEY = 'test-airtable-key';

// Mock de console para reducir ruido en tests
global.console = {
  ...console,
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  // Mantener error para debugging
  error: console.error,
};

// Helpers globales para tests
global.testHelpers = {
  // Esperar X milisegundos
  sleep: (ms) => new Promise(resolve => setTimeout(resolve, ms)),

  // Generar fecha en formato ISO
  getISODate: (daysOffset = 0) => {
    const date = new Date();
    date.setDate(date.getDate() + daysOffset);
    return date.toISOString().split('T')[0];
  },

  // Generar timestamp
  getTimestamp: () => new Date().toISOString(),
};

// Aumentar timeout para tests de integración
jest.setTimeout(10000);

// Limpiar todos los mocks después de cada test
afterEach(() => {
  jest.clearAllMocks();
});

console.error('✅ Setup de pruebas inicializado');
