/**
 * Pruebas de benchmarking de performance
 */

import { describe, test, expect } from '@jest/globals';
import { WorkflowExecutor } from '../helpers/workflow-executor.js';
import { mockVAPIWebhook } from '../mocks/vapi.mock.js';
import { mockTwilioConfirmWebhook } from '../mocks/twilio.mock.js';

describe('Performance Benchmarks', () => {
  let executor;

  beforeAll(() => {
    executor = new WorkflowExecutor();
  });

  describe('Workflow Execution Speed', () => {
    test('VAPI workflow debe completar en <500ms', async () => {
      const payload = mockVAPIWebhook();

      const start = Date.now();
      await executor.executeWorkflow('TRIG_VAPI_Voice_Agent_Reservation', payload);
      const duration = Date.now() - start;

      expect(duration).toBeLessThan(500);
    });

    test('WhatsApp workflow debe completar en <300ms', async () => {
      const payload = mockTwilioConfirmWebhook();

      const start = Date.now();
      await executor.executeWorkflow('TRIG_Twilio_WhatsApp_Confirmation_CRM', payload);
      const duration = Date.now() - start;

      expect(duration).toBeLessThan(300);
    });

    test('Error handler debe completar en <200ms', async () => {
      const payload = {
        error: { type: 'test' },
        source: 'Test',
      };

      const start = Date.now();
      await executor.executeWorkflow('ERROR_Global_Error_Handler_QA', payload);
      const duration = Date.now() - start;

      expect(duration).toBeLessThan(200);
    });
  });

  describe('Carga Concurrente', () => {
    test('debe manejar 50 reservas concurrentes', async () => {
      const promises = [];

      for (let i = 0; i < 50; i++) {
        const payload = mockVAPIWebhook();
        promises.push(
          executor.executeWorkflow('TRIG_VAPI_Voice_Agent_Reservation', payload)
        );
      }

      const start = Date.now();
      const results = await Promise.all(promises);
      const duration = Date.now() - start;

      expect(results).toHaveLength(50);
      expect(results.every(r => r.status === 'success')).toBe(true);
      expect(duration).toBeLessThan(5000); // 5 segundos para 50 requests
    });

    test('debe manejar 100 confirmaciones concurrentes', async () => {
      const promises = [];

      for (let i = 0; i < 100; i++) {
        const payload = mockTwilioConfirmWebhook();
        promises.push(
          executor.executeWorkflow('TRIG_Twilio_WhatsApp_Confirmation_CRM', payload)
        );
      }

      const start = Date.now();
      const results = await Promise.all(promises);
      const duration = Date.now() - start;

      expect(results).toHaveLength(100);
      expect(duration).toBeLessThan(10000); // 10 segundos para 100 requests
    });
  });

  describe('Memory Usage', () => {
    test('no debe tener memory leaks en ejecuciones repetidas', async () => {
      const initialMemory = process.memoryUsage().heapUsed;

      // Ejecutar 1000 veces
      for (let i = 0; i < 1000; i++) {
        await executor.executeWorkflow(
          'TRIG_VAPI_Voice_Agent_Reservation',
          mockVAPIWebhook()
        );
      }

      // Forzar garbage collection si está disponible
      if (global.gc) {
        global.gc();
      }

      const finalMemory = process.memoryUsage().heapUsed;
      const memoryIncrease = finalMemory - initialMemory;
      const mbIncrease = memoryIncrease / 1024 / 1024;

      // No debería aumentar más de 50MB
      expect(mbIncrease).toBeLessThan(50);
    });
  });

  describe('Throughput', () => {
    test('debe procesar >200 requests por segundo', async () => {
      const duration = 1000; // 1 segundo
      const startTime = Date.now();
      let requestCount = 0;

      while (Date.now() - startTime < duration) {
        await executor.executeWorkflow(
          'TRIG_VAPI_Voice_Agent_Reservation',
          mockVAPIWebhook()
        );
        requestCount++;
      }

      expect(requestCount).toBeGreaterThan(200);
    });
  });

  describe('Latency Percentiles', () => {
    test('debe medir latencias P50, P95, P99', async () => {
      const latencies = [];

      // Ejecutar 100 requests
      for (let i = 0; i < 100; i++) {
        const start = Date.now();
        await executor.executeWorkflow(
          'TRIG_VAPI_Voice_Agent_Reservation',
          mockVAPIWebhook()
        );
        latencies.push(Date.now() - start);
      }

      // Ordenar latencias
      latencies.sort((a, b) => a - b);

      const p50 = latencies[Math.floor(latencies.length * 0.5)];
      const p95 = latencies[Math.floor(latencies.length * 0.95)];
      const p99 = latencies[Math.floor(latencies.length * 0.99)];

      expect(p50).toBeLessThan(500); // P50 < 500ms
      expect(p95).toBeLessThan(1000); // P95 < 1s
      expect(p99).toBeLessThan(2000); // P99 < 2s
    });
  });

  describe('Error Rate under Load', () => {
    test('tasa de error debe ser <1% bajo carga', async () => {
      const total = 200;
      let errors = 0;

      const promises = [];
      for (let i = 0; i < total; i++) {
        promises.push(
          executor
            .executeWorkflow('TRIG_VAPI_Voice_Agent_Reservation', mockVAPIWebhook())
            .catch(() => {
              errors++;
            })
        );
      }

      await Promise.all(promises);

      const errorRate = (errors / total) * 100;
      expect(errorRate).toBeLessThan(1);
    });
  });
});
