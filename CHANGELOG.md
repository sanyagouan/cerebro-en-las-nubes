# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-03-07

### 🚀 Release de Producción

Primera versión lista para producción del sistema **Cerebro En Las Nubes**.

### Added

#### Seguridad
- **Validación de firma Twilio** en webhook WhatsApp ([`src/api/whatsapp_router.py`](src/api/whatsapp_router.py))
  - Verificación de `X-Twilio-Signature` usando HMAC-SHA1
  - Rechazo de solicitudes sin firma válida
- **Sanitización de inputs** para prevenir formula injection ([`src/core/utils/sanitization.py`](src/core/utils/sanitization.py))
  - Escape de caracteres peligrosos (`=`, `+`, `-`, `@`)
  - Protección contra inyección en celdas de Airtable
- **Rate limiting con Redis** ([`src/api/middleware/rate_limiting.py`](src/api/middleware/rate_limiting.py))
  - Límite de 10 requests por minuto por IP
  - Respuesta 429 con headers `Retry-After`
  - Almacenamiento en Redis con TTL automático

#### Infraestructura
- **Health checks profundos** ([`src/main.py`](src/main.py))
  - Verificación de conexión a Redis
  - Verificación de conexión a Airtable
  - Respuesta JSON con estado de servicios
- **Workflow CI/CD con GitHub Actions** ([`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml))
  - Linting con Ruff
  - Ejecución de tests unitarios
  - Build de imagen Docker
  - Deploy automático a Coolify
- **Workflow de PR checks** ([`.github/workflows/pr-check.yml`](.github/workflows/pr-check.yml))
  - Verificaciones antes de merge
  - Tests obligatorios

#### Documentación
- **Plan de rollback** ([`docs/ROLLBACK_PLAN.md`](docs/ROLLBACK_PLAN.md))
- **Checklist pre-producción** ([`docs/CHECKLIST_PRE_PRODUCCION.md`](docs/CHECKLIST_PRE_PRODUCCION.md))
- **README actualizado** con estado production-ready
- **CHANGELOG.md** (este archivo)

#### Testing
- **Tests de seguridad** ([`tests/unit/test_security.py`](tests/unit/test_security.py))
  - Tests de validación de firma Twilio
  - Tests de sanitización de inputs
  - Tests de rate limiting
- **+75 tests unitarios** totales

### Fixed

#### Compatibilidad Redis
- **3 bugs de compatibilidad** con versión de Redis
  - Corrección de método `set()` con parámetros deprecados
  - Actualización de `expire()` a nueva sintaxis
  - Fix de conexión pool en entorno async

#### Tests
- **14 tests rotos** reparados
  - Tests de booking engine actualizados
  - Mocks de Airtable corregidos
  - Fixtures de pytest actualizadas

#### Rendimiento
- **Timeouts en llamadas LLM**
  - Configuración de timeout de 30s para OpenAI
  - Configuración de timeout de 60s para DeepSeek
  - Manejo de excepciones con fallback
- **Memory leak en sesiones Twilio**
  - Limpieza automática de sesiones expiradas
  - TTL de 1 hora para contexto de conversación

#### Lógica de Negocio
- **Disponibilidad real de mesas** en `check_availability`
  - Consulta correcta a Airtable por fecha y hora
  - Consideración de capacidad ampliada
  - Fix de timezone handling (Europe/Madrid)

### Changed

#### Deprecaciones
- **Migrado de `@app.on_event` a lifespan**
  - Uso de context manager de FastAPI
  - Mejor manejo de startup/shutdown
  - Compatibilidad con FastAPI 0.115+

#### Logging
- **Reemplazado `print()` por logger estructurado**
  - Uso de Loguru para todos los logs
  - Formato JSON para producción
  - Niveles de log configurables por entorno

### Security

- **CORS restringido** a dominios específicos
  - No más `*` en producción
  - Lista blanca de orígenes permitidos
- **Secrets en Coolify** (no en código)
  - Todas las API keys en variables de entorno
  - Sin credenciales hardcodeadas

---

## [0.9.0] - 2026-02-20

### Added
- Sistema multi-agente (Router, Logic, Human)
- Integración con VAPI para voz
- Integración con Twilio para WhatsApp
- Dashboard React básico
- Cache Redis para Airtable

### Fixed
- Asignación de mesas por capacidad
- Manejo de horarios especiales

---

## [0.8.0] - 2026-02-01

### Added
- Estructura inicial del proyecto
- API FastAPI básica
- Conexión a Airtable
- Primeros tests unitarios

---

## Tipos de Cambios

- `Added` - Nuevas funcionalidades
- `Changed` - Cambios en funcionalidades existentes
- `Deprecated` - Funcionalidades que serán eliminadas
- `Removed` - Funcionalidades eliminadas
- `Fixed` - Corrección de bugs
- `Security` - Correcciones de vulnerabilidades

---

## Enlaces

- [README.md](README.md) - Documentación principal
- [API.md](API.md) - Documentación de API
- [docs/CHECKLIST_PRE_PRODUCCION.md](docs/CHECKLIST_PRE_PRODUCCION.md) - Checklist
- [docs/ROLLBACK_PLAN.md](docs/ROLLBACK_PLAN.md) - Plan de rollback
