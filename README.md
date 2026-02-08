# Cerebro En Las Nubes 🧠☁️

AI-powered booking and customer service system for **En Las Nubes Restobar** (Logroño).

Sistema multi-agente de inteligencia artificial construido con Python, FastAPI, VAPI, y Redis cache.

---

## 🏗️ Architecture

```
┌──────────────┐    ┌──────────────────────────┐
│   VAPI      │───▶│  FastAPI (Cerebro)     │
│  (Voice AI)  │    │  - Multi-Agent Orchestrator │
└──────────────┘    │  - Business Logic Layer   │
  GPT-4o + ElevenLabs│  - API Routers             │
  (GPT-4o Voice)   └──────────────────────────┘
                      ▲
┌──────────────┐    ┌──────────────────────────┐
│  Twilio     │───▶│  Airtable (Database)     │
│ (WhatsApp/  │    │  - Reservas               │
│   SMS)       │    │  - Mesas                  │
└──────────────┘    │  - Clientes                │
  SMS Gateway       │  - FAQ Knowledge            │
                    └──────────────────────────┘
                      ▲
┌──────────────┐    ┌──────────────────────────┐
│   Redis     │───▶│  Coolify (Deployment)    │
│  (Cache)     │    │  - Docker Container       │
└──────────────┘    │  - Auto-scaling           │
  Persistent Cache    │  - HTTPS                 │
                    └──────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Cuentas en: VAPI, Airtable, Twilio, Coolify
- (Opcional) Redis server o Redis cloud

### Local Development

```bash
# 1. Clonar repositorio
git clone https://github.com/YOUR_USERNAME/copia-asistente-voz-en-las-nubes-opencode.git
cd copia-asistente-voz-en-las-nubes-opencode

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys reales

# 4. (Opcional) Iniciar Redis local
docker run -d -p 6379:6379 redis:7-alpine

# 5. Ejecutar servidor
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment

```bash
# Docker Compose (desarrollo local)
docker-compose up -d

# Coolify (producción - ver DEPLOYMENT.md)
https://coolify.io
```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/health` | GET | Health check |
| `/vapi/webhook` | POST | VAPI voice calls & transcriptions |
| `/whatsapp/webhook` | POST | WhatsApp messages & confirmations |

**Documentación completa**: [API.md](./API.md)

---

## 🤖 Agents

Sistema multi-agente con 3 roles especializados:

- **Router Agent** (`gpt-4o-mini`): Clasificación de intención (reserva/FAQ/desconocido)
- **Logic Agent** (`deepseek-chat`): Razonamiento de disponibilidad y asignación de mesas
- **Human Agent** (`gpt-4o`): Generación de lenguaje natural para respuestas

---

## 📁 Project Structure

```
src/
├── api/                      # FastAPI routers
│   ├── vapi_router.py         # VAPI webhook endpoints
│   └── whatsapp_router.py     # Twilio webhook endpoints
├── application/              # Business logic layer
│   ├── agents/              # AI Agents (Router, Logic, Human)
│   ├── services/            # Services (Availability, Schedules)
│   └── orchestrator.py      # Multi-agent orchestrator
├── core/                     # Domain layer
│   ├── logging.py            # Structured logging (Loguru)
│   ├── config/              # Configuration (restaurant, airtable)
│   ├── entities/            # Pydantic models
│   ├── logic/               # Booking engine, table assignment
│   └── ports/               # Interfaces (IBookingRepository, etc.)
├── infrastructure/          # External services
│   ├── cache/               # Redis cache layer
│   │   └── redis_cache.py   # RedisCache implementation
│   ├── repositories/        # Airtable adapter
│   ├── external/            # External service clients
│   │   └── airtable_service.py  # AirtableService with cache
│   └── persistence/         # Database adapters
└── main.py                   # FastAPI app entry point
```

---

## 🔧 Environment Variables

Variables de entorno requeridas (ver `.env.example`):

```env
# --- LLM Services ---
OPENAI_API_KEY=sk-proj-YOUR_OPENAI_KEY_HERE
DEEPSEEK_API_KEY=sk-YOUR_DEEPSEEK_KEY_HERE

# --- VAPI (Voice AI) ---
VAPI_API_KEY=YOUR_VAPI_API_KEY
VAPI_ASSISTANT_ID=YOUR_VAPI_ASSISTANT_ID

# --- Airtable (Database) ---
AIRTABLE_API_KEY=patYOUR_AIRTABLE_API_KEY_HERE
AIRTABLE_BASE_ID=appYOUR_AIRTABLE_BASE_ID

# --- Twilio (WhatsApp/SMS) ---
TWILIO_ACCOUNT_SID=ACYOUR_TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN=YOUR_TWILIO_AUTH_TOKEN
TWILIO_WHATSAPP_NUMBER=+YOUR_TWILIO_WHATSAPP_NUMBER

# --- Coolify (Deployment) ---
COOLIFY_API_TOKEN=YOUR_COOLIFY_API_TOKEN

# --- Redis (Cache) ---
REDIS_URL=redis://:YOUR_REDIS_PASSWORD@localhost:6379
REDIS_PASSWORD=your_redis_password_here

# --- Server ---
HOST=0.0.0.0
PORT=8000

# --- Environment ---
ENVIRONMENT=development
DEBUG=False

# --- CORS ---
ALLOWED_ORIGINS=*  # En producción: https://tudominio.com
```

**⚠️ IMPORTANTE**: No comitear `.env` (está en `.gitignore`)

---

## 🔧 Características Recientes (v1.0.0)

### **✅ Implementado**
- ✅ Logging estructurado con Loguru (STDOUT + archivos rotativos)
- ✅ CORS restringido a dominios específicos (seguridad mejorada)
- ✅ Redis cache para Airtable queries (reducción de llamadas API)
- ✅ Healthcheck endpoint con versión y environment
- ✅ Python 3.11 + Docker actualizado
- ✅ Redis persistence configurado (AOF + RDB snapshots)

### **📝 Documentación**
- ✅ [DEPLOYMENT.md](./DEPLOYMENT.md) - Guía completa de deployment en Coolify
- ✅ [API.md](./API.md) - Documentación completa de endpoints
- ✅ [tests/README.md](./tests/README.md) - Guía de testing con Pytest
- ✅ `.env.example` actualizado con todas las variables requeridas

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Solo unit tests
pytest tests/unit/ -v

# Con coverage
pytest --cov=src --cov-report=html tests/
```

**Documentación completa**: [tests/README.md](./tests/README.md)

---

## 🚀 Deployment

**Coolify** (recomendado para producción):

1. Configurar repositorio en Coolify
2. Añadir variables de entorno (ver DEPLOYMENT.md)
3. Deploy automático en push a `main`

**Guía completa**: [DEPLOYMENT.md](./DEPLOYMENT.md)

---

## 📊 Features

- ✅ **Reservas por voz**: Procesamiento de llamadas con VAPI (GPT-4o + ElevenLabs)
- ✅ **Asignación inteligente de mesas**: Algoritmo basado en capacidad y disponibilidad
- ✅ **WhatsApp confirmations**: Envío automático de confirmaciones por Twilio
- ✅ **FAQs automáticas**: Respuestas a preguntas frecuentes del restaurante
- ✅ **Redis cache**: Cache de Airtable para reducir latencia
- ✅ **Logging estructurado**: Logs con timestamp, level, y función para debugging
- ✅ **CORS restringido**: Seguridad mejorada para producción

---

## 📁 Documentación del Restaurante

Información completa del restaurante preservada en:

- [`DATOS RESTOBAR EN LAS NUBES/CASOS_USO_RESTOBAR.md`](./DATOS%20RESTOBAR%20EN%20LAS%20NUBES/CASOS_USO_RESTOBAR.md) - Casos de uso completos
- [`DATOS RESTOBAR EN LAS NUBES/FAQS_RESTOBAR.md`](./DATOS%20RESTOBAR%20EN%20LAS%20NUBES/FAQS_RESTOBAR.md) - FAQs del restaurante

---

## 🔧 Troubleshooting

### **Redis connection issues**
```bash
# Verificar que Redis está corriendo
docker ps | grep redis

# Verificar URL en .env
echo $REDIS_URL
# Debe ser: redis://:password@host:6379
```

### **API rate limits**
- VAPI: 10 webhooks/minute por IP
- Airtable: 5 requests/second

Ver logs en `logs/` o Docker logs.

---

## 📝 License

Private - En Las Nubes Restobar

---

## 📚 Links

- [Deployment Guide](./DEPLOYMENT.md)
- [API Documentation](./API.md)
- [Tests Guide](./tests/README.md)
- [VAPI Documentation](https://docs.vapi.ai)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-25  
**Python**: 3.11+
