# Cerebro En Las Nubes 🧠☁️

![Estado](https://img.shields.io/badge/Estado-Production%20Ready-brightgreen)
![Versión](https://img.shields.io/badge/Versión-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-yellow)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688)

> AI-powered booking and customer service system for **En Las Nubes Restobar** (Logroño, España)

Sistema multi-agente de inteligencia artificial construido con Python, FastAPI, VAPI, y Redis cache.

---

## 📋 Tabla de Contenidos

- [Arquitectura](#-arquitectura)
- [Quick Start](#-quick-start)
- [Variables de Entorno](#-variables-de-entorno)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [URLs de Producción](#-urls-de-producción)
- [Documentación](#-documentación)

---

## 🏗️ Arquitectura

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         ARQUITECTURA DEL SISTEMA                         │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────────────────────────────┐
│   VAPI       │───▶│  FastAPI (Cerebro Backend)           │
│  (Voice AI)  │    │  ├── Multi-Agent Orchestrator        │
└──────────────┘    │  ├── Business Logic Layer            │
  GPT-4o + ElevenLabs│  ├── Rate Limiting + Security        │
                    │  └── API Routers                     │
┌──────────────┐    └──────────────────────────────────────┘
│  Twilio      │───▶           │           │
│ (WhatsApp)   │               ▼           ▼
└──────────────┘    ┌──────────────┐  ┌──────────────────┐
                    │   Redis      │  │  Airtable        │
┌──────────────┐    │  (Cache +    │  │  (Database)      │
│  Dashboard   │───▶│  Rate Limit) │  │  ├── Reservas    │
│  (React)     │    └──────────────┘  │  ├── Mesas       │
└──────────────┘                      │  └── Clientes    │
                                      └──────────────────┘
                                              │
                                              ▼
                                    ┌──────────────────┐
                                    │  Coolify (VPS)   │
                                    │  ├── Backend     │
                                    │  ├── Frontend    │
                                    │  └── Redis       │
                                    └──────────────────┘
```

---

## 🚀 Quick Start

### Prerrequisitos

- **Python 3.11+**
- **Docker & Docker Compose**
- **Node.js 18+** (para dashboard)
- Cuentas en: VAPI, Airtable, Twilio, Coolify

### Instalación Local

```bash
# 1. Clonar repositorio
git clone https://github.com/YOUR_USERNAME/asistente-voz-en-las-nubes.git
cd asistente-voz-en-las-nubes

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys reales

# 5. Iniciar Redis local
docker run -d -p 6379:6379 redis:7-alpine

# 6. Ejecutar servidor
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Dashboard (Frontend)

```bash
# Desde el directorio raíz
cd dashboard

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env

# Ejecutar en desarrollo
npm run dev
```

### Docker Compose (Desarrollo)

```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar servicios
docker-compose down
```

---

## 🔧 Variables de Entorno

### Variables Requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `OPENAI_API_KEY` | API Key de OpenAI | `sk-proj-...` |
| `DEEPSEEK_API_KEY` | API Key de DeepSeek | `sk-...` |
| `AIRTABLE_API_KEY` | Token de Airtable | `pat...` |
| `AIRTABLE_BASE_ID` | ID de la base de Airtable | `app...` |
| `TWILIO_ACCOUNT_SID` | Account SID de Twilio | `AC...` |
| `TWILIO_AUTH_TOKEN` | Auth Token de Twilio | `...` |
| `TWILIO_WHATSAPP_NUMBER` | Número WhatsApp Twilio | `whatsapp:+14155238886` |
| `REDIS_URL` | URL de conexión Redis | `redis://:password@localhost:6379` |
| `VAPI_API_KEY` | API Key de VAPI | `...` |

### Variables Opcionales

| Variable | Descripción | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Entorno de ejecución | `development` |
| `DEBUG` | Modo debug | `False` |
| `HOST` | Host del servidor | `0.0.0.0` |
| `PORT` | Puerto del servidor | `8000` |
| `ALLOWED_ORIGINS` | Orígenes CORS permitidos | `*` |

### Archivo de Ejemplo

Ver [`.env.example`](.env.example) para configuración completa.

⚠️ **IMPORTANTE**: Nunca commitear `.env` al repositorio (está en `.gitignore`)

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest tests/ -v

# Solo tests unitarios
pytest tests/unit/ -v

# Solo tests de seguridad
pytest tests/unit/test_security.py -v

# Con cobertura
pytest --cov=src --cov-report=html tests/

# Tests específicos
pytest tests/unit/test_booking_engine.py -v
```

### Cobertura Actual

| Módulo | Cobertura |
|--------|-----------|
| `src/core/` | 85% |
| `src/api/` | 78% |
| `src/infrastructure/` | 72% |
| **Total** | **~75%** |

### Tests Incluidos

- **75+ tests unitarios**
- **Tests de seguridad** (validación Twilio, sanitización)
- **Tests de integración** (endpoints API)
- **Tests de lógica de negocio** (reservas, disponibilidad)

Ver documentación completa: [`tests/README.md`](tests/README.md)

---

## 🚀 Deployment

### Coolify (Producción)

1. **Configurar repositorio** en panel de Coolify
2. **Añadir variables de entorno** (ver sección anterior)
3. **Deploy automático** en push a `main`

### CI/CD Pipeline

El proyecto incluye GitHub Actions para:

- ✅ Linting (Ruff)
- ✅ Tests unitarios
- ✅ Security checks
- ✅ Build de Docker image
- ✅ Deploy automático a Coolify

Ver configuración: [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml)

### Documentación de Deployment

- [DEPLOYMENT.md](DEPLOYMENT.md) - Guía completa de deployment
- [docs/ROLLBACK_PLAN.md](docs/ROLLBACK_PLAN.md) - Plan de rollback
- [docs/CHECKLIST_PRE_PRODUCCION.md](docs/CHECKLIST_PRE_PRODUCCION.md) - Checklist pre-producción

---

## 🌐 URLs de Producción

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Backend API** | `https://api.enlasnubes.com` | API principal |
| **Dashboard** | `https://dashboard.enlasnubes.com` | Panel de administración |
| **Health Check** | `https://api.enlasnubes.com/health` | Estado del servicio |
| **API Docs** | `https://api.enlasnubes.com/docs` | Swagger UI |

### Webhooks Configurados

| Servicio | Endpoint | Descripción |
|----------|----------|-------------|
| **VAPI** | `/vapi/webhook` | Llamadas de voz |
| **Twilio** | `/whatsapp/webhook` | Mensajes WhatsApp |

---

## 🤖 Sistema Multi-Agente

| Agente | Modelo | Función |
|--------|--------|---------|
| **Router Agent** | `gpt-4o-mini` | Clasificación de intención |
| **Logic Agent** | `deepseek-chat` | Razonamiento y asignación de mesas |
| **Human Agent** | `gpt-4o` | Generación de respuestas naturales |

---

## 📡 API Endpoints

| Endpoint | Method | Descripción |
|----------|--------|-------------|
| `/` | GET | Información del servicio |
| `/health` | GET | Health check con estado de servicios |
| `/vapi/webhook` | POST | Webhook VAPI (llamadas de voz) |
| `/whatsapp/webhook` | POST | Webhook Twilio (WhatsApp) |
| `/api/reservations` | GET/POST | CRUD de reservas |
| `/api/tables` | GET | Listado de mesas |
| `/api/availability` | POST | Consulta de disponibilidad |

**Documentación completa**: [API.md](API.md)

---

## 🔐 Seguridad

### Implementaciones de Seguridad

- ✅ **Validación de firma Twilio** en webhooks
- ✅ **Sanitización de inputs** para prevenir formula injection
- ✅ **Rate limiting** con Redis (10 req/min por IP)
- ✅ **CORS configurado** para dominios específicos
- ✅ **Secrets gestionados** en Coolify (no en código)

Ver más detalles: [SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md)

---

## 📁 Estructura del Proyecto

```
.
├── src/
│   ├── api/                    # Routers FastAPI
│   │   ├── middleware/         # Rate limiting, CORS
│   │   ├── vapi_router.py      # Webhook VAPI
│   │   └── whatsapp_router.py  # Webhook Twilio
│   ├── application/            # Capa de aplicación
│   │   ├── agents/             # Agentes IA
│   │   └── orchestrator.py     # Orquestador
│   ├── core/                   # Dominio
│   │   ├── config/             # Configuración
│   │   ├── entities/           # Modelos Pydantic
│   │   ├── logic/              # Lógica de negocio
│   │   └── utils/              # Sanitización, helpers
│   ├── infrastructure/         # Servicios externos
│   │   ├── cache/              # Redis
│   │   └── external/           # Airtable, LLMs
│   └── main.py                 # Entry point
├── dashboard/                  # Frontend React
├── tests/                      # Tests (75+)
├── docs/                       # Documentación
├── scripts/                    # Scripts de utilidad
└── .github/workflows/          # CI/CD
```

---

## ✨ Características Principales

### ✅ Reservas por Voz
- Procesamiento de llamadas con VAPI (GPT-4o + ElevenLabs)
- Reconocimiento de voz en español
- Respuestas naturales y personalizadas

### ✅ Asignación Inteligente de Mesas
- Algoritmo de optimización de capacidad
- Gestión de preferencias (terraza, interior)
- Combinación automática para grupos grandes

### ✅ WhatsApp Integration
- Confirmaciones automáticas post-reserva
- Recordatorios 24h antes
- Cancelaciones bidireccionales
- Gestión de lista de espera

### ✅ Dashboard de Administración
- Panel React con visualización en tiempo real
- Gestión de reservas, mesas y clientes
- Logs de actividad y métricas

### ✅ Infraestructura Robusta
- Redis cache para baja latencia
- Rate limiting para protección
- Logging estructurado con Loguru
- Health checks profundos

---

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [API.md](API.md) | Documentación de endpoints |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Guía de deployment |
| [AGENTS.md](AGENTS.md) | Guía de agentes IA |
| [tests/README.md](tests/README.md) | Guía de testing |
| [docs/ROLLBACK_PLAN.md](docs/ROLLBACK_PLAN.md) | Plan de rollback |
| [docs/CHECKLIST_PRE_PRODUCCION.md](docs/CHECKLIST_PRE_PRODUCCION.md) | Checklist pre-producción |
| [CHANGELOG.md](CHANGELOG.md) | Historial de cambios |

---

## 🔧 Troubleshooting

### Redis connection issues
```bash
# Verificar que Redis está corriendo
docker ps | grep redis

# Test de conexión
redis-cli ping  # Esperado: PONG
```

### Webhooks no funcionan
```bash
# Verificar URLs en VAPI/Twilio dashboard
# Debe apuntar a: https://api.enlasnubes.com/vapi/webhook

# Ver logs del backend
docker logs cerebro-backend -f
```

### API rate limits
- VAPI: 10 webhooks/minute por IP
- Airtable: 5 requests/second
- Sistema: 10 requests/minute por IP

---

## 📝 Licencia

Private - En Las Nubes Restobar © 2026

---

## 📞 Contacto

- **Restaurante**: En Las Nubes Restobar, Logroño
- **Soporte Técnico**: Equipo de desarrollo

---

**Versión**: 1.0.0  
**Última Actualización**: 2026-03-07  
**Estado**: Production Ready ✅  
**Python**: 3.11+
