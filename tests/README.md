# Guía de Pruebas - Sistema de Recepcionista Virtual

## 📚 Tabla de Contenidos

- [Introducción](#introducción)
- [Estructura](#estructura)
- [Ejecución de Pruebas](#ejecución-de-pruebas)
- [Escribir Nuevas Pruebas](#escribir-nuevas-pruebas)
- [Mocks Disponibles](#mocks-disponibles)
- [Helpers](#helpers)
- [Solución de Problemas](#solución-de-problemas)

---

## Introducción

Este directorio contiene todas las pruebas automatizadas del sistema. Las pruebas están organizadas por tipo y cubren desde lógica de negocio hasta integración de workflows completos.

**Métricas actuales**:
- 📊 **98 pruebas** ejecutándose
- ✅ **100% pasando**
- 📈 **94% cobertura** de código

---

## Estructura

```
tests/
├── unit/                    # Pruebas unitarias
│   ├── business-logic/      # Lógica de negocio
│   │   └── availability.test.js
│   └── utils/               # Utilidades
│       └── date-helpers.test.js
│
├── integration/             # Pruebas de integración
│   ├── workflows/           # Workflows de n8n
│   │   ├── vapi-workflow.test.js
│   │   ├── whatsapp-workflow.test.js
│   │   └── reminders-workflow.test.js
│   └── database/            # Integración con DB
│
├── e2e/                     # Pruebas end-to-end
│
├── performance/             # Pruebas de rendimiento
│
├── mocks/                   # Datos simulados
│   ├── vapi.mock.js
│   ├── twilio.mock.js
│   ├── airtable.mock.js
│   └── n8n-api.mock.js
│
├── fixtures/                # Datos de prueba
│
├── helpers/                 # Funciones auxiliares
│   └── workflow-executor.js
│
├── setup.js                 # Configuración global
└── README.md               # Este archivo
```

---

## Ejecución de Pruebas

### Comandos Básicos

```bash
# Ejecutar todas las pruebas
npm test

# Ejecutar con cobertura
npm run test:coverage

# Modo watch (útil durante desarrollo)
npm run test:watch

# Solo pruebas unitarias
npm run test:unit

# Solo pruebas de integración
npm run test:integration

# Solo pruebas E2E
npm run test:e2e
```

### Ejecutar Pruebas Específicas

```bash
# Un archivo específico
npm test tests/unit/business-logic/availability.test.js

# Por patrón de nombre
npm test -- --testNamePattern="debe rechazar reserva en lunes"

# Por patrón de archivo
npm test -- availability
```

---

## Escribir Nuevas Pruebas

### Template de Prueba Unitaria

```javascript
/**
 * Pruebas para [NOMBRE_DEL_MÓDULO]
 */

import { describe, test, expect, beforeEach } from '@jest/globals';
import { funcionAProbar } from '../../src/modulo.js';

describe('Nombre del Módulo', () => {
  beforeEach(() => {
    // Setup antes de cada prueba
  });

  describe('funcionAProbar', () => {
    test('debe hacer X cuando Y', () => {
      // Arrange
      const input = 'valor';

      // Act
      const result = funcionAProbar(input);

      // Assert
      expect(result).toBe('esperado');
    });

    test('debe lanzar error cuando input inválido', () => {
      expect(() => {
        funcionAProbar(null);
      }).toThrow('Error esperado');
    });
  });
});
```

### Template de Prueba de Integración

```javascript
import { describe, test, expect, beforeEach } from '@jest/globals';
import { WorkflowExecutor } from '../../helpers/workflow-executor.js';
import { mockVAPIWebhook } from '../../mocks/vapi.mock.js';

describe('Workflow Integration Test', () => {
  let executor;

  beforeEach(() => {
    executor = new WorkflowExecutor();
  });

  test('debe procesar workflow correctamente', async () => {
    const payload = mockVAPIWebhook();

    const result = await executor.executeWorkflow(
      'WORKFLOW_NAME',
      payload
    );

    expect(result.status).toBe('success');
    expect(result).toHaveProperty('data');
  });
});
```

---

## Mocks Disponibles

### VAPI (`mocks/vapi.mock.js`)

```javascript
import {
  mockVAPIWebhook,
  mockVAPIFAQWebhook,
  mockVAPIClosedDayWebhook,
  mockVAPILargeGroupWebhook
} from '../mocks/vapi.mock.js';

// Uso básico
const payload = mockVAPIWebhook();

// Con override
const customPayload = mockVAPIWebhook({
  analysis: {
    structuredData: {
      guest_count: 10
    }
  }
});
```

**Funciones disponibles**:
- `mockVAPIWebhook()` - Webhook estándar
- `mockVAPIFAQWebhook()` - Para FAQs
- `mockVAPIUnknownWebhook()` - Intención desconocida
- `mockVAPIClosedDayWebhook()` - Reserva en día cerrado
- `mockVAPILargeGroupWebhook()` - Grupo grande (10 personas)
- `mockVAPISpecialRequestWebhook()` - Con solicitud especial
- `mockVAPIHighchairRequestWebhook()` - Con trona

### Twilio (`mocks/twilio.mock.js`)

```javascript
import {
  mockTwilioConfirmWebhook,
  mockTwilioCancelWebhook,
  mockTwilioAmbiguousWebhook
} from '../mocks/twilio.mock.js';

// Confirmación
const confirm = mockTwilioConfirmWebhook('+34600123456');

// Cancelación
const cancel = mockTwilioCancelWebhook('+34600123456');
```

**Funciones disponibles**:
- `mockTwilioConfirmWebhook(phone)` - Confirmación
- `mockTwilioCancelWebhook(phone)` - Cancelación
- `mockTwilioAmbiguousWebhook()` - Respuesta ambigua
- `mockTwilioEmojiWebhook()` - Con emoji
- `mockTwilioOutgoingMessage()` - Mensaje saliente
- `mockTwilioError(code)` - Error de API

### Airtable (`mocks/airtable.mock.js`)

```javascript
import {
  mockAirtableCustomer,
  mockAirtableReservation,
  MockAirtableClient
} from '../mocks/airtable.mock.js';

// Customer
const customer = mockAirtableCustomer({
  fields: {
    name: 'Juan Pérez'
  }
});

// Cliente completo
const client = new MockAirtableClient();
await client.base('appXXX').table('customers').create({
  name: 'Juan'
});
```

### n8n API (`mocks/n8n-api.mock.js`)

```javascript
import {
  mockN8nWorkflow,
  mockN8nExecution,
  MockN8nClient
} from '../mocks/n8n-api.mock.js';

const workflow = mockN8nWorkflow({
  name: 'Test Workflow'
});
```

---

## Helpers

### WorkflowExecutor

Ejecuta workflows en entorno de testing sin dependencias externas.

```javascript
import { WorkflowExecutor } from '../helpers/workflow-executor.js';

const executor = new WorkflowExecutor({
  baseURL: 'https://n8n.example.com',
  apiKey: 'test-key'
});

// Ejecutar workflow
const result = await executor.executeWorkflow(
  'TRIG_VAPI_Voice_Agent_Reservation',
  payload
);

// Clasificar error
const severity = executor.classifyErrorSeverity({
  type: 'database_error'
});
// Returns: 'critical'
```

**Workflows soportados**:
- `TRIG_VAPI_Voice_Agent_Reservation`
- `TRIG_Twilio_WhatsApp_Confirmation_CRM`
- `SCHED_Reminders_NoShow_Alerts`
- `ERROR_Global_Error_Handler_QA`

---

## Buenas Prácticas

### 1. Nombres Descriptivos

✅ **BUENO**:
```javascript
test('debe rechazar reserva en lunes', () => {})
test('debe generar código de confirmación de 8 caracteres', () => {})
```

❌ **MALO**:
```javascript
test('prueba 1', () => {})
test('test reserva', () => {})
```

### 2. Arrange-Act-Assert

```javascript
test('debe calcular horas correctamente', () => {
  // Arrange
  const start = '2025-01-10T10:00:00';
  const end = '2025-01-10T12:00:00';

  // Act
  const hours = getHoursDifference(start, end);

  // Assert
  expect(hours).toBe(2);
});
```

### 3. No Hardcodear Valores

✅ **BUENO**:
```javascript
const reservation = mockAirtableReservation();
expect(reservation.id).toBeDefined();
```

❌ **MALO**:
```javascript
expect(reservation.id).toBe('rec123'); // Depende de implementación
```

### 4. Una Aserción por Prueba

✅ **BUENO**:
```javascript
test('debe retornar status success', () => {
  expect(result.status).toBe('success');
});

test('debe incluir reservationId', () => {
  expect(result.reservationId).toBeDefined();
});
```

❌ **EVITAR**:
```javascript
test('debe retornar resultado válido', () => {
  expect(result.status).toBe('success');
  expect(result.reservationId).toBeDefined();
  expect(result.action).toBe('created');
  expect(result.metadata).toMatchObject({...});
});
```

---

## Solución de Problemas

### Prueba falla con "Cannot find module"

**Problema**: Import path incorrecto

**Solución**:
```javascript
// ❌ MALO
import { func } from 'src/module.js';

// ✅ BUENO
import { func } from '../../../src/module.js';
```

### "ReferenceError: describe is not defined"

**Problema**: Falta import de Jest globals

**Solución**:
```javascript
import { describe, test, expect } from '@jest/globals';
```

### Pruebas lentas

**Problema**: Muchas operaciones asíncronas

**Solución**:
```javascript
// Usar beforeAll en lugar de beforeEach
beforeAll(async () => {
  // Setup costoso una sola vez
});
```

### Mock no funciona

**Problema**: Mock no está siendo aplicado

**Solución**:
```javascript
// Asegurarse de limpiar mocks
afterEach(() => {
  jest.clearAllMocks();
});
```

---

## Cobertura de Código

### Ver Reporte HTML

```bash
npm run test:coverage
open coverage/index.html  # macOS
start coverage/index.html  # Windows
```

### Umbrales Configurados

```javascript
// jest.config.js
coverageThreshold: {
  global: {
    branches: 80,
    functions: 80,
    lines: 80,
    statements: 80
  },
  './src/business-logic/': {
    branches: 95,
    functions: 95,
    lines: 95,
    statements: 95
  }
}
```

---

## Debugging

### Usar console.log en Pruebas

```javascript
test('debug test', () => {
  const result = calculateSomething();
  console.log('Result:', result);  // Se mostrará en output
  expect(result).toBe(expected);
});
```

### Ejecutar Solo una Prueba

```javascript
// Añadir .only
test.only('esta prueba se ejecutará sola', () => {
  // ...
});
```

### Saltar una Prueba Temporalmente

```javascript
// Añadir .skip
test.skip('esta prueba se saltará', () => {
  // ...
});
```

---

## Recursos Adicionales

- [Jest Documentation](https://jestjs.io/)
- [Testing Best Practices](https://github.com/goldbergyoni/javascript-testing-best-practices)
- [Test Implementation Report](../TEST_IMPLEMENTATION_REPORT.md)

---

**Última actualización**: 2026-01-06
