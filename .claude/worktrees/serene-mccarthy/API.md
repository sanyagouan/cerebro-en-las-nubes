# API Documentation - Cerebro En Las Nubes

Documentación completa de endpoints API para el sistema de reservas por voz.

**Base URL**: `https://cerebro-en-las-nubes.com` (producción) o `http://localhost:8000` (desarrollo)

---

## 📋 **Tabla de Contenidos**

- [Endpoints](#endpoints)
  - [Health Check](#health-check)
  - [Root](#root)
  - [VAPI Webhook](#vapi-webhook)
  - [WhatsApp Webhook](#whatsapp-webhook)
- [Request/Response Formats](#requestresponse-formats)
- [Error Codes](#error-codes)
- [Rate Limiting](#rate-limiting)
- [Authentication](#authentication)

---

## 🔗 **Endpoints**

### **Health Check**

**Endpoint**: `GET /health`

**Descripción**: Verifica que el servicio está funcionando correctamente.

**Response**:
```json
{
  "status": "healthy",
  "service": "Cerebro En Las Nubes",
  "version": "1.0.0",
  "environment": "production"
}
```

**Status Codes**:
- `200 OK`: Servicio saludable
- `503 Service Unavailable`: Servicio no disponible (raro)

**Example**:
```bash
curl https://cerebro-en-las-nubes.com/health
```

---

### **Root**

**Endpoint**: `GET /`

**Descripción**: Retorna información sobre el servicio y endpoints disponibles.

**Response**:
```json
{
  "message": "Cerebro Logic is Running. Agents are standing by.",
  "endpoints": {
    "vapi": "/vapi/webhook",
    "whatsapp": "/whatsapp/webhook",
    "health": "/health"
  }
}
```

**Status Codes**:
- `200 OK`: Información retornada correctamente

**Example**:
```bash
curl https://cerebro-en-las-nubes.com/
```

---

### **VAPI Webhook**

**Endpoint**: `POST /vapi/webhook`

**Descripción**: Procesa webhooks de VAPI (llamadas de voz finalizadas, transcripciones, análisis de intención).

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "call_id": "call_1234567890",
  "type": "end-of-call-report",
  "timestamp": "2026-01-25T13:45:22.123Z",
  "call": {
    "id": "call_1234567890",
    "phoneNumber": "+34600123456",
    "customer": {
      "number": "+34600123456",
      "name": "Juan Pérez"
    },
    "startedAt": "2026-01-25T13:42:22.123Z",
    "endedAt": "2026-01-25T13:45:22.123Z",
    "duration": 180,
    "cost": 0.15
  },
  "transcript": "Hola, quiero hacer una reserva para 4 personas el sábado a las 21:00",
  "recordingUrl": "https://vapi.example.com/recordings/test123.mp3",
  "summary": "Cliente solicita reserva para 4 personas",
  "analysis": {
    "structuredData": {
      "intent": "reserva",
      "guest_count": 4,
      "service_date": "2026-01-27",
      "service_time": "21:00",
      "customer_name": "Juan Pérez",
      "customer_phone": "+34600123456",
      "special_requests": []
    }
  }
}
```

**Request Fields**:
| Field | Type | Descripción |
|-------|------|-------------|
| `call_id` | string | ID único de la llamada |
| `type` | string | Tipo de webhook (`end-of-call-report`, `function-call`, etc.) |
| `timestamp` | string | ISO 8601 timestamp |
| `call.id` | string | ID de la llamada |
| `call.phoneNumber` | string | Número de teléfono del cliente |
| `customer.number` | string | Número del cliente (puede diferir de phoneNumber) |
| `customer.name` | string | Nombre del cliente (opcional) |
| `call.startedAt` | string | Hora inicio de llamada (ISO 8601) |
| `call.endedAt` | string | Hora fin de llamada (ISO 8601) |
| `call.duration` | number | Duración en segundos |
| `call.cost` | number | Costo de la llamada |
| `transcript` | string | Transcripción completa de la conversación |
| `recordingUrl` | string | URL de grabación de audio (opcional) |
| `summary` | string | Resumen generado por VAPI |
| `analysis.structuredData` | object | Datos estructurados del análisis |

**Response**:
```json
{
  "status": "success",
  "message": "Webhook procesado correctamente",
  "booking": {
    "id": "rec7890123456",
    "client_name": "Juan Pérez",
    "client_phone": "+34600123456",
    "date_time": "2026-01-27T21:00:00",
    "pax": 4,
    "table": "Mesa 4 (Interior, 4 pax)",
    "status": "confirmed",
    "created_at": "2026-01-25T13:45:22.123Z"
  },
  "actions": [
    {
      "type": "whatsapp_confirmation",
      "status": "sent",
      "to": "+34600123456",
      "message": "✅ Reserva confirmada: 4 personas, sábado 27/01 a las 21:00. Mesa: Mesa 4 (Interior, 4 pax)"
    }
  ],
  "agent_trace": [
    {
      "agent": "Router Agent",
      "action": "classify_intent",
      "result": "reserva",
      "duration_ms": 250
    },
    {
      "agent": "Logic Agent",
      "action": "extract_booking_data",
      "result": {"guest_count": 4, "date": "2026-01-27", "time": "21:00"},
      "duration_ms": 520
    },
    {
      "agent": "Logic Agent",
      "action": "check_availability",
      "result": true,
      "duration_ms": 310
    },
    {
      "agent": "Human Agent",
      "action": "confirm_booking",
      "result": "confirmed",
      "duration_ms": 180
    }
  ]
}
```

**Response Fields**:
| Field | Type | Descripción |
|-------|------|-------------|
| `status` | string | Estado del procesamiento (`success`, `error`, `requires_human`) |
| `message` | string | Mensaje descriptivo |
| `booking` | object | Datos de la reserva creada (si aplica) |
| `booking.id` | string | ID de la reserva en Airtable |
| `booking.client_name` | string | Nombre del cliente |
| `booking.client_phone` | string | Teléfono del cliente |
| `booking.date_time` | string | Fecha y hora de la reserva (ISO 8601) |
| `booking.pax` | number | Número de comensales |
| `booking.table` | string | Mesa asignada |
| `booking.status` | string | Estado de reserva (`confirmed`, `pending`, `cancelled`) |
| `booking.created_at` | string | Timestamp de creación |
| `actions` | array | Acciones ejecutadas (WhatsApp SMS, etc.) |
| `agent_trace` | array | Traza de ejecución de agentes |

**Status Codes**:
- `200 OK`: Webhook procesado correctamente
- `400 Bad Request`: Payload inválido
- `500 Internal Server Error`: Error en procesamiento

**Examples**:

**Reserva exitosa**:
```bash
curl -X POST https://cerebro-en-las-nubes.com/vapi/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "call_1234567890",
    "type": "end-of-call-report",
    "call": {
      "id": "call_1234567890",
      "phoneNumber": "+34600123456"
    },
    "transcript": "Hola, quiero reservar para 4 personas el sábado a las 21:00",
    "analysis": {
      "structuredData": {
        "intent": "reserva",
        "guest_count": 4,
        "service_date": "2026-01-27",
        "service_time": "21:00",
        "customer_name": "Juan Pérez",
        "customer_phone": "+34600123456"
      }
    }
  }'
```

**FAQ pregunta**:
```bash
curl -X POST https://cerebro-en-las-nubes.com/vapi/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "call_9876543210",
    "type": "end-of-call-report",
    "call": {
      "id": "call_9876543210",
      "phoneNumber": "+34600987654"
    },
    "transcript": "¿Cuál es el horario del restaurante?",
    "analysis": {
      "structuredData": {
        "intent": "faq",
        "faq_category": "horarios",
        "question": "horario"
      }
    }
  }'
```

**Intent desconocido (requiere humano)**:
```bash
curl -X POST https://cerebro-en-las-nubes.com/vapi/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "call_1112223330",
    "type": "end-of-call-report",
    "call": {
      "id": "call_1112223330",
      "phoneNumber": "+34600987654"
    },
    "transcript": "Quiero comprar acciones de la empresa",
    "analysis": {
      "structuredData": {
        "intent": "desconocido",
        "requires_human": true
      }
    }
  }'
```

---

### **WhatsApp Webhook**

**Endpoint**: `POST /whatsapp/webhook`

**Descripción**: Procesa webhooks de Twilio para mensajes de WhatsApp (opcional - usado para confirmaciones o respuestas de clientes).

**Headers**:
```
Content-Type: application/x-www-form-urlencoded
X-Twilio-Signature: HMAC_SHA256 (opcional - verificación)
```

**Request Body**:
```json
{
  "MessageSid": "SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "SmsSid": "SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "AccountSid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "MessagingServiceSid": "MGXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "MessagingServiceSid": "MGXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "From": "whatsapp:+14155238886",
  "To": "whatsapp:+34600123456",
  "MessageStatus": "delivered",
  "MessageType": "text",
  "Body": "Gracias por la confirmación, hasta el sábado!",
  "NumMedia": "0",
  "NumSegments": "1"
}
```

**Request Fields**:
| Field | Type | Descripción |
|-------|------|-------------|
| `MessageSid` | string | ID único del mensaje |
| `From` | string | Número de Twilio (WhatsApp sender) |
| `To` | string | Número del cliente |
| `MessageStatus` | string | Estado del mensaje (`queued`, `sent`, `delivered`, `read`, `failed`) |
| `Body` | string | Contenido del mensaje |
| `MessageType` | string | Tipo de mensaje (`text`, `media`, etc.) |

**Response**:
```json
{
  "status": "success",
  "message": "WhatsApp webhook procesado"
}
```

**Status Codes**:
- `200 OK`: Webhook procesado
- `400 Bad Request`: Payload inválido
- `403 Forbidden`: Firma de Twilio inválida (si está habilitada verificación)

**Example**:
```bash
# Esta es una llamada desde Twilio, no un curl directo
# Twilio llama a este endpoint cuando hay actualizaciones de mensajes
```

---

## 📦 **Request/Response Formats**

### **VAPI Webhook Payload Structure**

```typescript
interface VAPIWebhookPayload {
  call_id: string;
  type: 'end-of-call-report' | 'function-call' | 'status-update';
  timestamp: string; // ISO 8601
  call: {
    id: string;
    phoneNumber: string;
    customer?: {
      number: string;
      name?: string;
    };
    startedAt: string;
    endedAt: string;
    duration: number;
    cost: number;
  };
  transcript: string;
  recordingUrl?: string;
  summary?: string;
  analysis: {
    structuredData: {
      intent: 'reserva' | 'faq' | 'desconocido' | 'cancelacion';
      guest_count?: number;
      service_date?: string; // YYYY-MM-DD
      service_time?: string; // HH:MM
      customer_name?: string;
      customer_phone?: string;
      special_requests?: string[];
      faq_category?: string;
      question?: string;
      requires_human?: boolean;
    };
  };
}
```

### **Booking Object**

```typescript
interface Booking {
  id: string; // Airtable record ID
  client_name: string;
  client_phone: string;
  date_time: string; // ISO 8601
  pax: number;
  table?: string;
  status: 'confirmed' | 'pending' | 'cancelled';
  created_at: string; // ISO 8601
}
```

### **Action Object**

```typescript
interface Action {
  type: 'whatsapp_confirmation' | 'whatsapp_reminder' | 'airtable_create';
  status: 'sent' | 'pending' | 'failed';
  to?: string;
  message?: string;
  record_id?: string;
}
```

### **Agent Trace Object**

```typescript
interface AgentTrace {
  agent: 'Router Agent' | 'Logic Agent' | 'Human Agent';
  action: string;
  result: any;
  duration_ms: number;
}
```

---

## ❌ **Error Codes**

| Code | Descripción | Ejemplo Response |
|------|-------------|------------------|
| `400 Bad Request` | Payload inválido o faltan campos requeridos | `{"error": "Invalid payload", "details": "Missing 'call_id' field"}` |
| `401 Unauthorized` | Firma de Twilio inválida | `{"error": "Invalid signature"}` |
| `429 Too Many Requests` | Rate limit excedido | `{"error": "Rate limit exceeded", "retry_after": 60}` |
| `500 Internal Server Error` | Error inesperado en servidor | `{"error": "Internal server error", "details": "..."}` |
| `503 Service Unavailable` | Servicio temporalmente no disponible | `{"error": "Service unavailable", "retry_after": 30}` |

### **Error Response Format**

```typescript
interface ErrorResponse {
  error: string;
  details?: string;
  timestamp: string; // ISO 8601
  request_id?: string; // Para tracking en logs
}
```

**Example**:
```json
{
  "error": "Invalid payload",
  "details": "Missing required field: 'call_id'",
  "timestamp": "2026-01-25T13:45:22.123Z",
  "request_id": "req_abc123def456"
}
```

---

## 🚦 **Rate Limiting**

### **VAPI Webhook**
- **Límite**: 10 requests por minuto por IP
- **Headers**:
  ```
  X-RateLimit-Limit: 10
  X-RateLimit-Remaining: 7
  X-RateLimit-Reset: 60
  ```
- **Excedido**: Retorna `429 Too Many Requests` con `retry_after` en segundos

### **WhatsApp Webhook**
- **Límite**: 5 requests por segundo por número de Twilio
- **Excedido**: Retorna `429 Too Many Requests`

---

## 🔐 **Authentication**

### **VAPI Webhook**
- **No requiere autenticación** (VAPI valida el endpoint desde su panel)
- **Opcional**: Añadir header secreto en `.env` y verificar en el endpoint:
  ```python
  SECRET_KEY = os.getenv("VAPI_WEBHOOK_SECRET")
  ```

### **WhatsApp Webhook**
- **Verificación de firma de Twilio** (recomendado):
  ```python
  # Twilio envía header: X-Twilio-Signature
  # Usar library: twilio-request-validator
  ```

---

## 🧪 **Testing API Localmente**

### **Setup Local**
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar .env
cp .env.example .env
# Editar .env con tus credenciales de desarrollo

# 3. Iniciar servidor
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### **Test Health Endpoint**
```bash
curl http://localhost:8000/health
```

### **Test VAPI Webhook**
```bash
# Usar mock de VAPI
curl -X POST http://localhost:8000/vapi/webhook \
  -H "Content-Type: application/json" \
  -d @tests/mocks/vapi.mock.js
```

### **Test con pytest**
```bash
# Tests de integración
pytest tests/integration/test_airtable_integration.py -v

# Tests unitarios
pytest tests/unit/test_booking_engine.py -v
```

---

## 📚 **Documentación Relacionada**

- [Deployment Guide](./DEPLOYMENT.md)
- [Tests Guide](./tests/README.md)
- [VAPI Documentation](https://docs.vapi.ai)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Airtable API](https://airtable.com/developers/web/api)

---

**Last Updated**: 2026-01-25  
**API Version**: 1.0.0  
**Base URL**: https://cerebro-en-las-nubes.com
