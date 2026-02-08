# Tests Suite - Cerebro En Las Nubes

Estructura de tests para el sistema de reservas con FastAPI, VAPI, Airtable y Multi-Agent system.

---

## 📂 **Estructura de Directorios**

```
tests/
├── unit/                    # Unit Tests (Python pytest)
│   ├── test_booking_engine.py      # Motor de reservas
│   └── utils/                    # Utilidades y helpers
│
├── integration/             # Integration Tests (Python pytest + JS tests)
│   ├── test_airtable_integration.py      # Integración real con Airtable
│   ├── test_orchestrator.py             # Orchestrator de agentes
│   ├── workflows/                        # Tests de workflows JS (heredado de n8n era)
│   │   ├── vapi-workflow.test.js
│   │   ├── whatsapp-workflow.test.js
│   │   └── error-handler-workflow.test.js
│   └── database/                        # Migraciones de DB
│       └── migration.test.js
│
├── e2e/                   # End-to-End Tests (JS - Playwright/Cypress ready)
│   └── complete-reservation-flow.test.js
│
├── mocks/                  # Mocks para tests
│   ├── vapi.mock.js                # Mocks de webhooks VAPI
│   ├── airtable.mock.js             # Mocks de respuestas Airtable
│   └── twilio.mock.js               # Mocks de SMS/WhatsApp
│
├── fixtures/               # Data fixtures para tests
│   └── bookings.json               # Datos de prueba
│
├── helpers/               # Helper functions
│   └── workflow-executor.js         # Ejecutor de workflows
│
├── performance/            # Performance & Load Tests
│   ├── benchmark.test.js
│   ├── load-test.yml
│   └── processor.js
│
└── setup.js               # Configuración de tests
```

---

## 🧪 **Framework de Testing**

### **Python Tests (Nuevo - FastAPI)**
- **Framework**: Pytest
- **Runner**: `pytest tests/ -v`
- **Coverage**: `pytest --cov=src --cov-report=html tests/`
- **Mocking**: `unittest.mock` + `pytest-mock`

#### **Comandos Utiles**
```bash
# Ejecutar todos los tests de Python
pytest tests/ -v

# Solo unit tests
pytest tests/unit/ -v

# Solo integration tests
pytest tests/integration/ -v

# Con coverage
pytest --cov=src --cov-report=html tests/
open htmlcov/index.html

# Tests específicos
pytest tests/unit/test_booking_engine.py -v -k "test_find_best_table"
```

### **JavaScript Tests (Heradado - Workflows/E2E)**
- **Framework**: Jest (heredado de sistema n8n)
- **Runner**: `npm test`
- **Coverage**: `npm run test:coverage`

#### **Comandos Utiles**
```bash
# Ejecutar todos los tests de JS
npm test

# Solo E2E tests
npm test tests/e2e/

# Solo workflow tests
npm test tests/integration/workflows/

# Tests de performance
npm test tests/performance/
```

---

## 📝 **Tipos de Tests**

### **1. Unit Tests (Python)**
Prueban componentes individuales en aislamiento.
- **booking_engine.py**: Algoritmos de asignación de mesas
- **date_helpers.py**: Utilidades de fechas
- **utils/**: Helper functions

**Ejemplo**:
```python
def test_booking_engine_finds_table():
    booking = Booking(
        client_name="Juan",
        client_phone="+34600123456",
        date_time=datetime(2024, 1, 25, 21, 0),
        pax=4
    )
    result = engine.find_best_table(booking)
    assert result is not None
    assert result.capacity_min <= 4 <= result.capacity_max
```

### **2. Integration Tests (Python)**
Prueban integración entre múltiples componentes con servicios reales.
- **Airtable + BookingEngine**: Flujo completo de reserva
- **Orchestrator + Agents**: Flujo multi-agente

**Ejemplo**:
```python
def test_airtable_booking_flow():
    repo = AirtableBookingRepository()
    engine = BookingEngine(repo)
    
    # Crear booking y asignar mesa
    booking = Booking(...)
    result = engine.find_best_table(booking)
    
    # Verificar que se creó en Airtable
    assert result.table_id in repo.get_all_tables()
```

### **3. Integration Tests (JavaScript - Workflows)**
Prueban workflows heredados del sistema n8n.
- **vapi-workflow.test.js**: Procesamiento de llamadas VAPI
- **whatsapp-workflow.test.js**: Manejo de mensajes WhatsApp

**Ejemplo**:
```javascript
test('VAPI webhook reserva mesa', async () => {
  const webhook = mockVAPIWebhook();
  const result = await processVAPIWebhook(webhook);
  
  expect(result.status).toBe('success');
  expect(result.assigned_table).toBeDefined();
});
```

### **4. E2E Tests (JavaScript)**
Prueban el flujo completo desde inicio a fin.
- **complete-reservation-flow.test.js**: Reserva completa

**Ejemplo**:
```javascript
test('Flujo completo de reserva', async () => {
  // 1. Llamada entra por VAPI
  const webhook = mockVAPIWebhook();
  
  // 2. Procesamiento por agentes
  const orchestration = await orchestrate(webhook);
  
  // 3. Asignación de mesa
  const table = await assignTable(orchestration.booking);
  
  // 4. Creación en Airtable
  const record = await createAirtableRecord(orchestration.booking, table);
  
  // 5. Confirmación por WhatsApp
  const sms = await sendWhatsAppSMS(record);
  
  expect(sms.status).toBe('sent');
});
```

### **5. Performance Tests**
Prueban rendimiento bajo carga.
- **benchmark.test.js**: Benchmarks de rendimiento
- **load-test.yml**: Tests de carga simultánea

**Ejemplo**:
```javascript
test('Asignación de 1000 mesas en <1s', () => {
  const start = Date.now();
  
  for (let i = 0; i < 1000; i++) {
    engine.find_best_table(mock_booking(i));
  }
  
  const duration = Date.now() - start;
  expect(duration).toBeLessThan(1000);
});
```

---

## 🎯 **Guía de Testing**

### **Antes de Ejecutar Tests**

1. **Configurar variables de entorno**:
   ```bash
   cp .env.example .env
   # Editar .env con tus credenciales de desarrollo
   ```

2. **Instalar dependencias**:
   ```bash
   # Python
   pip install -r requirements.txt
   pip install pytest pytest-cov pytest-mock
   
   # Node.js (para tests JS heredados)
   npm install
   ```

3. **Iniciar servicios** (para tests de integración):
   ```bash
   # Redis (opcional - cache)
   docker run -d -p 6379:6379 redis:7-alpine
   
   # Airtable (necesario solo para tests reales)
   # Airtable usa cloud, no requiere setup local
   ```

### **Ejecutar Tests por Tipo**

#### **Desarrollo Rápido**
```bash
# Solo unit tests (más rápidos)
pytest tests/unit/ -v --tb=short

# Con filtrado de tests específicos
pytest tests/unit/test_booking_engine.py -v -k "table"
```

#### **Integración Completa**
```bash
# Todos los tests (Python + JS)
pytest tests/ -v && npm test

# Solo tests de integración que requieren servicios externos
pytest tests/integration/test_airtable_integration.py -v
```

#### **Pre-Commit Hook** (recomendado)
```bash
# Ejecutar tests rápidos antes de commit
pytest tests/unit/ -v --tb=line
```

---

## 📊 **Cobertura de Tests**

### **Objetivos de Cobertura**
- **Unit Tests**: >80% de código cubierto
- **Integration Tests**: >60% de caminos críticos
- **E2E Tests**: >50% de flujos de usuario

### **Ver Cobertura Actual**
```bash
# Python
pytest --cov=src --cov-report=term-missing tests/

# JavaScript (si se añade coverage en futuro)
npm run test:coverage
```

---

## 🐛 **Tests Fallando**

### **Problemas Comunes**

1. **Airtable no responde en tests de integración**:
   ```bash
   # Verificar .env tiene credenciales correctas
   cat .env | grep AIRTABLE
   
   # Airtable puede estar con rate limits, espera unos minutos
   ```

2. **Tests de JS fallan con Jest no configurado**:
   ```bash
   # Instalar Jest
   npm install --save-dev jest
   
   # Configurar en package.json
   # Añadir "jest": {"testEnvironment": "node"}
   ```

3. **Redis no conecta en tests**:
   ```bash
   # Verificar que Redis está corriendo
   docker ps | grep redis
   
   # Iniciar Redis si no está corriendo
   docker run -d -p 6379:6379 redis:7-alpine
   ```

---

## 🚀 **Próximos Pasos**

1. **Migrar tests JS heredados a Python pytest**:
   - vapi-workflow.test.js → test_vapi_integration.py
   - whatsapp-workflow.test.js → test_whatsapp_integration.py

2. **Añadir E2E tests con Playwright**:
   - Tests automatizados de navegador para UI (si se implementa)

3. **CI/CD Integration**:
   - Ejecutar tests automáticamente en GitHub Actions
   - Bloquear PRs si tests fallan

---

## 📚 **Recursos**

- [Pytest Documentation](https://docs.pytest.org/)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Testing FastAPI](https://fastapi.tiangolo.com/tutorial/testing/)

---

**Last Updated**: 2026-01-25  
**Framework**: Pytest (Python) + Jest (JS heredado)
**Coverage Goal**: >80% (unit), >60% (integration)
