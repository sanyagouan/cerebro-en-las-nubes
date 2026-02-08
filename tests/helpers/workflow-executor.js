/**
 * Helper para ejecutar y probar workflows de n8n
 */

import axios from 'axios';

/**
 * Clase para ejecutar workflows de n8n en entorno de testing
 */
export class WorkflowExecutor {
  constructor(config = {}) {
    this.baseURL = config.baseURL || process.env.N8N_API_URL;
    this.apiKey = config.apiKey || process.env.N8N_API_KEY;
    this.client = axios.create({
      baseURL: this.baseURL,
      headers: {
        'X-N8N-API-KEY': this.apiKey,
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Simula la ejecución de un workflow con un payload
   * @param {string} workflowName - Nombre del workflow
   * @param {Object} payload - Datos de entrada
   * @returns {Object} Resultado de la ejecución
   */
  async executeWorkflow(workflowName, payload) {
    // En testing, simulamos la lógica del workflow
    const workflows = {
      'TRIG_VAPI_Voice_Agent_Reservation': this.simulateVAPIWorkflow,
      'TRIG_Twilio_WhatsApp_Confirmation_CRM': this.simulateTwilioWorkflow,
      'SCHED_Reminders_NoShow_Alerts': this.simulateRemindersWorkflow,
      'ERROR_Global_Error_Handler_QA': this.simulateErrorHandlerWorkflow,
    };

    const workflowFn = workflows[workflowName];
    if (!workflowFn) {
      throw new Error(`Workflow ${workflowName} no encontrado`);
    }

    return workflowFn.call(this, payload);
  }

  /**
   * Simula el workflow VAPI de clasificación y reserva
   */
  async simulateVAPIWorkflow(payload) {
    const { analysis } = payload;

    if (!analysis || !analysis.structuredData) {
      return {
        status: 'error',
        error: 'Missing analysis data',
      };
    }

    const { intent } = analysis.structuredData;

    // Clasificación de intención
    if (intent === 'faq') {
      return {
        status: 'success',
        classification: 'faq',
        action: 'respond_with_faq',
        response: 'FAQ response here',
      };
    }

    if (intent === 'desconocido') {
      return {
        status: 'success',
        classification: 'unknown',
        action: 'forward_to_human',
        message: 'Transferido a operador humano',
      };
    }

    if (intent === 'reserva') {
      const { service_date, guest_count, service_time, customer_phone } = analysis.structuredData;

      // Verificar disponibilidad
      const isMonday = new Date(service_date).getDay() === 1;
      if (isMonday) {
        return {
          status: 'rejected',
          classification: 'reserva',
          reason: 'closed_monday',
          message: 'Los lunes estamos cerrados',
        };
      }

      // Reserva exitosa
      return {
        status: 'success',
        classification: 'reserva',
        action: 'reservation_created',
        reservationId: `res_${Date.now()}`,
        extractedData: {
          guest_count,
          service_date,
          service_time,
          customer_phone,
        },
      };
    }

    return {
      status: 'error',
      error: 'Unknown intent',
    };
  }

  /**
   * Simula el workflow de WhatsApp
   */
  async simulateTwilioWorkflow(payload) {
    const { Body, From } = payload;

    const bodyLower = Body.toLowerCase().trim();

    // Detectar confirmación (palabras exactas o al inicio)
    const confirmPatterns = [/^confirmar$/i, /^confirmo$/i, /^si$/i, /^sí$/i, /^ok$/i, /^vale$/i, /^confirmado$/i, /✅/];
    const cancelPatterns = [/^cancelar$/i, /^cancelo$/i, /^no$/i, /^anular$/i, /^eliminar$/i];

    // Verificar confirmación exacta
    const isConfirm = confirmPatterns.some(pattern => pattern.test(bodyLower));
    if (isConfirm) {
      return {
        status: 'success',
        action: 'confirmed',
        reservationStatus: 'confirmada',
        airtableUpdated: true,
        message: 'Reserva confirmada',
      };
    }

    // Verificar cancelación exacta
    const isCancel = cancelPatterns.some(pattern => pattern.test(bodyLower));
    if (isCancel) {
      return {
        status: 'success',
        action: 'cancelled',
        reservationStatus: 'cancelada',
        airtableUpdated: true,
        message: 'Reserva cancelada',
      };
    }

    // Respuesta ambigua (cualquier otra cosa)
    return {
      status: 'success',
      action: 'requires_review',
      requiresManualReview: true,
      message: 'Respuesta ambigua, requiere revisión manual',
    };
  }

  /**
   * Simula el workflow de recordatorios
   */
  async simulateRemindersWorkflow(payload) {
    const { date, reservations } = payload;

    const reminders = [];
    const noShows = [];

    reservations.forEach(reservation => {
      if (reservation.status === 'pendiente') {
        reminders.push({
          reservationId: reservation.id,
          sent: true,
          sentAt: new Date().toISOString(),
        });
      }

      if (reservation.status === 'confirmada' && reservation.isPast) {
        noShows.push({
          reservationId: reservation.id,
          markedNoShow: true,
        });
      }
    });

    return {
      status: 'success',
      reminders,
      noShows,
      totalSent: reminders.length,
      totalNoShows: noShows.length,
    };
  }

  /**
   * Simula el workflow de manejo de errores
   */
  async simulateErrorHandlerWorkflow(payload) {
    const { error, source } = payload;

    const severity = this.classifyErrorSeverity(error);

    const alerts = [];

    if (severity === 'critical') {
      alerts.push({
        channel: 'slack_emergency',
        sent: true,
      });
      alerts.push({
        channel: 'telegram',
        sent: true,
      });
    } else if (severity === 'high') {
      alerts.push({
        channel: 'slack_operations',
        sent: true,
      });
    }

    return {
      status: 'success',
      severity,
      alerts,
      logged: true,
      reportScheduled: severity === 'critical',
    };
  }

  /**
   * Clasifica la severidad de un error
   */
  classifyErrorSeverity(error) {
    if (!error) return 'low';

    const criticalKeywords = ['database', 'connection', 'auth', 'timeout'];
    const highKeywords = ['validation', 'missing', 'failed'];

    const errorStr = JSON.stringify(error).toLowerCase();

    if (criticalKeywords.some(kw => errorStr.includes(kw))) {
      return 'critical';
    }

    if (highKeywords.some(kw => errorStr.includes(kw))) {
      return 'high';
    }

    return 'low';
  }
}

export default WorkflowExecutor;
