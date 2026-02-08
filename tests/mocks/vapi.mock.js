/**
 * Mock de VAPI para testing
 * Simula las respuestas del webhook de VAPI
 */

/**
 * Genera un webhook payload de VAPI
 * @param {Object} overrides - Propiedades a sobrescribir
 * @returns {Object} Payload del webhook
 */
export const mockVAPIWebhook = (overrides = {}) => {
  const defaults = {
    call_id: `call_${Date.now()}`,
    type: 'end-of-call-report',
    timestamp: new Date().toISOString(),
    call: {
      id: `call_${Date.now()}`,
      phoneNumber: '+34600123456',
      customer: {
        number: '+34600123456',
      },
      startedAt: new Date(Date.now() - 180000).toISOString(), // Llamada de 3 minutos
      endedAt: new Date().toISOString(),
      duration: 180,
      cost: 0.15,
    },
    transcript: 'Hola, quiero hacer una reserva para 4 personas el sábado a las 21:00',
    recordingUrl: 'https://vapi.example.com/recordings/test123.mp3',
    summary: 'Cliente solicita reserva para 4 personas',
    // Análisis del agente
    analysis: {
      structuredData: {
        intent: 'reserva',
        guest_count: 4,
        service_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // Pasado mañana
        service_time: '21:00',
        customer_name: 'Juan Pérez',
        customer_phone: '+34600123456',
        special_requests: [],
      },
    },
  };

  return { ...defaults, ...overrides };
};

/**
 * Mock de webhook para FAQ
 */
export const mockVAPIFAQWebhook = () => {
  return mockVAPIWebhook({
    transcript: '¿Cuál es el horario del restaurante?',
    analysis: {
      structuredData: {
        intent: 'faq',
        faq_category: 'horarios',
        question: 'horario',
      },
    },
  });
};

/**
 * Mock de webhook para intención desconocida
 */
export const mockVAPIUnknownWebhook = () => {
  return mockVAPIWebhook({
    transcript: 'Quiero comprar acciones de la empresa',
    analysis: {
      structuredData: {
        intent: 'desconocido',
        requires_human: true,
      },
    },
  });
};

/**
 * Mock de webhook para reserva en día cerrado (lunes)
 */
export const mockVAPIClosedDayWebhook = () => {
  // Calcular próximo lunes
  const nextMonday = new Date();
  nextMonday.setDate(nextMonday.getDate() + ((1 + 7 - nextMonday.getDay()) % 7 || 7));

  return mockVAPIWebhook({
    transcript: 'Quiero reservar para el lunes',
    analysis: {
      structuredData: {
        intent: 'reserva',
        guest_count: 2,
        service_date: nextMonday.toISOString().split('T')[0],
        service_time: '21:00',
      },
    },
  });
};

/**
 * Mock de webhook para grupo grande (≥7 personas)
 */
export const mockVAPILargeGroupWebhook = () => {
  return mockVAPIWebhook({
    transcript: 'Necesito reservar para 10 personas el viernes',
    analysis: {
      structuredData: {
        intent: 'reserva',
        guest_count: 10,
        service_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        service_time: '21:00',
      },
    },
  });
};

/**
 * Mock de webhook con solicitud especial (cachopo sin gluten)
 */
export const mockVAPISpecialRequestWebhook = () => {
  return mockVAPIWebhook({
    transcript: 'Reserva para 2, queremos cachopo sin gluten',
    analysis: {
      structuredData: {
        intent: 'reserva',
        guest_count: 2,
        service_date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        service_time: '21:00',
        special_requests: ['cachopo_sin_gluten'],
      },
    },
  });
};

/**
 * Mock de webhook con solicitud de trona
 */
export const mockVAPIHighchairRequestWebhook = () => {
  return mockVAPIWebhook({
    transcript: 'Reserva para 4 personas con un bebé, necesitamos trona',
    analysis: {
      structuredData: {
        intent: 'reserva',
        guest_count: 4,
        service_date: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        service_time: '14:00',
        special_requests: ['trona'],
      },
    },
  });
};

export default {
  mockVAPIWebhook,
  mockVAPIFAQWebhook,
  mockVAPIUnknownWebhook,
  mockVAPIClosedDayWebhook,
  mockVAPILargeGroupWebhook,
  mockVAPISpecialRequestWebhook,
  mockVAPIHighchairRequestWebhook,
};
