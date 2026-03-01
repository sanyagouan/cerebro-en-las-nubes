/**
 * Mock de Twilio WhatsApp para testing
 * Simula las respuestas del webhook de Twilio
 */

/**
 * Genera un webhook payload de Twilio WhatsApp
 * @param {Object} overrides - Propiedades a sobrescribir
 * @returns {Object} Payload del webhook
 */
export const mockTwilioWebhook = (overrides = {}) => {
  const defaults = {
    MessageSid: `SM${Math.random().toString(36).substring(2, 15)}`,
    AccountSid: 'AC0000000000000000000000000000',
    MessagingServiceSid: 'MG0000000000000000000000000000',
    From: 'whatsapp:+34600123456',
    To: 'whatsapp:+14155238886',
    Body: 'CONFIRMAR',
    NumMedia: '0',
    NumSegments: '1',
    MessageStatus: 'received',
    ApiVersion: '2010-04-01',
    SmsMessageSid: `SM${Math.random().toString(36).substring(2, 15)}`,
    SmsSid: `SM${Math.random().toString(36).substring(2, 15)}`,
    SmsStatus: 'received',
    Timestamp: new Date().toISOString(),
  };

  return { ...defaults, ...overrides };
};

/**
 * Mock de respuesta CONFIRMAR
 */
export const mockTwilioConfirmWebhook = (phone = '+34600123456') => {
  return mockTwilioWebhook({
    From: `whatsapp:${phone}`,
    Body: 'CONFIRMAR',
  });
};

/**
 * Mock de respuesta CANCELAR
 */
export const mockTwilioCancelWebhook = (phone = '+34600123456') => {
  return mockTwilioWebhook({
    From: `whatsapp:${phone}`,
    Body: 'CANCELAR',
  });
};

/**
 * Mock de respuesta con variaciones de CONFIRMAR
 */
export const mockTwilioConfirmVariationsWebhook = () => {
  const variations = ['confirmar', 'Confirmar', 'CONFIRMAR', 'Si', 'Sí', 'OK', 'Vale', 'Confirmado'];
  const randomVariation = variations[Math.floor(Math.random() * variations.length)];

  return mockTwilioWebhook({
    Body: randomVariation,
  });
};

/**
 * Mock de respuesta con variaciones de CANCELAR
 */
export const mockTwilioCancelVariationsWebhook = () => {
  const variations = ['cancelar', 'Cancelar', 'CANCELAR', 'No', 'Anular', 'Eliminar'];
  const randomVariation = variations[Math.floor(Math.random() * variations.length)];

  return mockTwilioWebhook({
    Body: randomVariation,
  });
};

/**
 * Mock de respuesta ambigua (requiere revisión manual)
 */
export const mockTwilioAmbiguousWebhook = () => {
  return mockTwilioWebhook({
    Body: 'Quizás, déjame confirmar con mi esposa',
  });
};

/**
 * Mock de respuesta con emoji
 */
export const mockTwilioEmojiWebhook = () => {
  return mockTwilioWebhook({
    Body: '✅ Confirmo',
  });
};

/**
 * Mock de respuesta fuera de tiempo (después de 24h)
 */
export const mockTwilioLateResponseWebhook = () => {
  const yesterday = new Date(Date.now() - 48 * 60 * 60 * 1000);
  return mockTwilioWebhook({
    Body: 'CONFIRMAR',
    Timestamp: yesterday.toISOString(),
  });
};

/**
 * Mock de mensaje saliente (enviado por el sistema)
 */
export const mockTwilioOutgoingMessage = (overrides = {}) => {
  const defaults = {
    sid: `SM${Math.random().toString(36).substring(2, 15)}`,
    date_created: new Date().toISOString(),
    date_updated: new Date().toISOString(),
    date_sent: new Date().toISOString(),
    account_sid: 'AC0000000000000000000000000000',
    to: 'whatsapp:+34600123456',
    from: 'whatsapp:+14155238886',
    messaging_service_sid: 'MG0000000000000000000000000000',
    body: 'Tu reserva ha sido confirmada',
    status: 'sent',
    num_segments: '1',
    num_media: '0',
    direction: 'outbound-api',
    api_version: '2010-04-01',
    price: '-0.0050',
    price_unit: 'USD',
    error_code: null,
    error_message: null,
    uri: '/2010-04-01/Accounts/AC0000000000000000000000000000/Messages/SM123.json',
    subresource_uris: {
      media: '/2010-04-01/Accounts/AC0000000000000000000000000000/Messages/SM123/Media.json',
    },
  };

  return { ...defaults, ...overrides };
};

/**
 * Mock de error de Twilio
 */
export const mockTwilioError = (errorCode = 21211) => {
  const errors = {
    21211: 'Invalid "To" Phone Number',
    21408: '"From" Phone Number not verified',
    21610: 'Message cannot be sent to this number',
    30007: 'Message Filtered',
  };

  return {
    status: 400,
    message: errors[errorCode] || 'Unknown error',
    code: errorCode,
    more_info: `https://www.twilio.com/docs/errors/${errorCode}`,
  };
};

export default {
  mockTwilioWebhook,
  mockTwilioConfirmWebhook,
  mockTwilioCancelWebhook,
  mockTwilioConfirmVariationsWebhook,
  mockTwilioCancelVariationsWebhook,
  mockTwilioAmbiguousWebhook,
  mockTwilioEmojiWebhook,
  mockTwilioLateResponseWebhook,
  mockTwilioOutgoingMessage,
  mockTwilioError,
};
