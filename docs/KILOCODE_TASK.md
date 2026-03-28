# KILOCODE AGENT TASK — cerebro-en-las-nubes
**Repositorio:** `https://github.com/sanyagouan/cerebro-en-las-nubes`  
**Stack:** FastAPI · Python 3.11 · Airtable · VAPI · Twilio · Redis · Docker · Coolify  
**Objetivo:** Dejar el repositorio y el código en estado de producción limpio, sin bugs críticos y bien organizado.

---

## CONTEXTO DEL SISTEMA

Sistema multi-agente de IA para gestión de reservas y atención al cliente del restaurante "En Las Nubes Restobar" (Logroño). Tiene dos canales de entrada:
1. **Canal Voz** → VAPI → Twilio → `/vapi/webhook` (FastAPI)
2. **Canal WhatsApp** → Twilio → `/twilio/whatsapp/incoming` o `/whatsapp/webhook` (FastAPI)

La lógica central usa tres agentes LLM encadenados: `RouterAgent (gpt-4o-mini)` → `LogicAgent (deepseek-chat)` → `HumanAgent (gpt-4o)`. Los datos de reservas se persisten en **Airtable**. Existe un dashboard web con WebSockets en tiempo real.

---

## FASE 1 — ORGANIZACIÓN GIT (Ejecutar primero)

El repositorio tiene **4 ramas desincronizadas**. `main` lleva 2 meses sin actualizar y contiene código obsoleto. La rama con el código de producción real es `dashboard-production` (+83 commits por delante de main).

### Paso 1.1 — Promover `dashboard-production` a `main`
```bash
# En tu máquina local, dentro del repositorio
git fetch --all

# Renombrar main actual como backup de seguridad
git branch -m main main-old-backup

# Traer dashboard-production como nueva main
git checkout -b main origin/dashboard-production
git push origin main --force-with-lease

# Actualizar rama por defecto en GitHub:
# Settings → Branches → Default branch → main

# Borrar el backup local cuando confirmes que todo está bien
git branch -D main-old-backup
git push origin --delete main-old-backup
```

### Paso 1.2 — Limpiar ramas muertas
```bash
# claude/serene-mccarthy contiene archivos .gradle de Android (basura de worktree)
# No merge nada de ella, borrar directamente
git push origin --delete claude/serene-mccarthy

# final-clean ya está integrado en dashboard-production
git push origin --delete final-clean

# Resultado final: solo 2 ramas
# main → producción estable
# (opcional) dev → desarrollo activo
```

### Paso 1.3 — Limpiar archivos de debug del repo
Estos archivos fueron commiteados por error y deben eliminarse:
```bash
git rm bypass_uploader_nb1.py bypass_uploader_nb2.py bypass_uploader_nb3.py \
       bypass_uploader_nb4.py bypass_uploader_nb5.py bypass_uploader_nb6.py \
       bypass_uploader_nb7.py verify_fix.py validate_dashboard.py \
       dockerfile_base64.txt dashboard_debug.html

git commit -m "chore: remove debug artifacts and bypass scripts from repo"
git push origin main
```

Añadir al `.gitignore`:
```
# Debug artifacts
bypass_uploader_nb*.py
verify_fix.py
validate_dashboard.py
dockerfile_base64.txt
dashboard_debug.html
```

---

## FASE 2 — BUGS CRÍTICOS P0 (Código nuevo base = `dashboard-production`)

> ⚠️ Todos los cambios de código a partir de aquí se hacen sobre el código de `dashboard-production` (que ahora es `main`).

### BUG P0-1 — `MockReservationRepository` aún activo en `vapi_router.py`

**Archivo:** `src/api/vapi_router.py`  
**Problema:** La verificación de disponibilidad y creación de reservas por voz usa un mock en memoria. Todas las reservas se pierden al reiniciar el contenedor y la disponibilidad nunca refleja la realidad de Airtable.

**Fix:** Reemplazar el mock por `ReservationService` (que ya existe en `src/application/services/reservation_service.py`):

```python
# ❌ ELIMINAR estas líneas del inicio de vapi_router.py:
from src.infrastructure.repositories.mock_reservation_repository import MockReservationRepository
reservation_repository = MockReservationRepository()

# ✅ AÑADIR en su lugar:
from src.application.services.reservation_service import ReservationService
reservation_service = ReservationService()
```

Busca en el archivo todas las llamadas a `reservation_repository.check_availability(...)` y `reservation_repository.create_reservation(...)` y sustitúyelas por los métodos equivalentes de `ReservationService`. El servicio ya tiene `check_availability` y `create_reservation` integrados con Airtable y Redis.

---

### BUG P0-2 — Rate limiters desactivados con `# TODO`

**Archivo:** `src/api/vapi_router.py` y `src/api/whatsapp_router.py`  
**Problema:** Los decoradores `@webhook_limit()` están comentados, dejando los endpoints de webhook completamente abiertos a spam.

```python
# ❌ ESTADO ACTUAL (comentado):
# from src.api.middleware.rate_limiting import webhook_limit
# @webhook_limit()

# ✅ ACTIVAR: descomentar las líneas de import y los decoradores
from src.api.middleware.rate_limiting import webhook_limit

@router.post("/webhook")
@webhook_limit()
async def whatsapp_webhook(...):
```

Verifica primero que `slowapi` esté correctamente registrado en `src/main.py` (ya lo está: `app.state.limiter = limiter`). Si hay un error de integración, revisa `src/api/middleware/rate_limiting.py` y asegúrate de que `webhook_limit` usa `request: Request` como primer parámetro de la función decorada.

---

### BUG P0-3 — `docker-compose.yml` inconsistente con `Dockerfile`

**Archivo:** `docker-compose.yml`  
**Problema:** El `docker-compose.yml` usa `poetry run uvicorn` pero el `Dockerfile` instala dependencias con `pip`. Además, falta la variable `REDIS_URL` en el servicio `brain` para que la caché funcione.

**Fix — reemplazar el `docker-compose.yml` completo:**
```yaml
version: '3.8'

services:
  brain:
    build:
      context: .
      args:
        CACHEBUST: ${CACHEBUST:-1}
        CACHEBUST_SRC: ${CACHEBUST_SRC:-1}
    container_name: cerebro-brain
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - REDIS_URL=redis://redis:6379/0
      - ENVIRONMENT=production
    depends_on:
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s

  redis:
    image: redis:7-alpine
    container_name: cerebro-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 128mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  redis_data:
```

---

### BUG P0-4 — `.env.example` incompleto

**Archivo:** `.env.example`  
**Problema:** Faltan variables de entorno que el código de `dashboard-production` requiere y que sin ellas la app no arranca (`settings.validate()` lanza `RuntimeError`).

**Fix — actualizar `.env.example`:**
```bash
# ===== CORE =====
ENVIRONMENT=production
PYTHONPATH=/app

# ===== LLM APIs =====
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=sk-...

# ===== VAPI (Voice AI) =====
VAPI_API_KEY=...
VAPI_ASSISTANT_ID=...

# ===== AIRTABLE =====
AIRTABLE_API_KEY=pat...
AIRTABLE_BASE_ID=app...

# ===== TWILIO (WhatsApp + SMS) =====
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+...

# ===== REDIS =====
REDIS_URL=redis://localhost:6379/0

# ===== SEGURIDAD =====
# Orígenes permitidos para CORS (separados por coma, sin espacios)
ALLOWED_ORIGINS=https://tudominio.com,http://localhost:3000

# Clave secreta para JWT del dashboard admin
SECRET_KEY=genera-una-clave-aleatoria-de-64-chars

# ===== COOLIFY (Opcional) =====
COOLIFY_API_URL=https://...
COOLIFY_API_TOKEN=...
```

---

## FASE 3 — OPTIMIZACIONES P1

### OPT-1 — Modelo VAPI demasiado caro

**Archivo:** `src/api/vapi_router.py` (función `get_assistant_config`)  
**Problema:** `gpt-4o` con `temperature: 0.7` para un asistente de voz de restaurante. Es 10x más caro de lo necesario y añade latencia.

```python
# ❌ ACTUAL
"model": "gpt-4o",
"temperature": 0.7,

# ✅ FIX
"model": "gpt-4o-mini",
"temperature": 0.3,
```

---

### OPT-2 — Logging dual (loguru + logging estándar)

**Problema:** `src/main.py` y varios archivos de infra usan `loguru`, pero `vapi_router.py`, `whatsapp_router.py` y `twilio_service.py` usan `logging` estándar de Python. En Docker genera dos streams distintos.

**Fix — en cada archivo que use `logging` estándar, reemplazar:**
```python
# ❌ ELIMINAR
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ AÑADIR
from src.core.logging import logger
```

Archivos afectados:
- `src/api/vapi_router.py`
- `src/api/whatsapp_router.py`
- `src/infrastructure/external/twilio_service.py`
- `src/infrastructure/repositories/booking_repo.py`

---

### OPT-3 — Escritura a Airtable bloqueante en canal de voz

**Archivo:** `src/api/vapi_router.py` (función `tool_create_reservation`)  
**Problema:** La escritura a Airtable y el envío de SMS son operaciones síncronas que bloquean la respuesta al cliente durante la llamada de voz (~800ms de silencio).

**Fix:**
```python
import asyncio

async def tool_create_reservation(request: Request):
    # ... validación y creación del objeto reserva (sin cambios) ...

    # Responder al cliente INMEDIATAMENTE
    respuesta_cliente = f"¡Perfecto, {nombre}! Ya está confirmada tu reserva. Te mando la confirmación ahora mismo."
    
    # Fire-and-forget: guardar en Airtable y enviar SMS sin bloquear
    async def _background_tasks():
        try:
            await airtable_service.create_record({...})
        except Exception as e:
            logger.error(f"Error guardando en Airtable: {e}")
        try:
            twilio_service.send_sms(telefono, mensaje_confirmacion)
        except Exception as e:
            logger.error(f"Error enviando SMS: {e}")

    asyncio.create_task(_background_tasks())

    return {
        "results": [{"toolCallId": tool_call["id"], "result": respuesta_cliente}]
    }
```

---

## FASE 4 — VERIFICACIÓN FINAL

Una vez aplicados todos los cambios, verificar:

```bash
# 1. Build limpio
docker compose build --no-cache

# 2. Arrancar servicios
docker compose up -d

# 3. Health check
curl http://localhost:8000/health
# Esperado: {"status": "healthy", "service": "Cerebro En Las Nubes", ...}

# 4. Test webhook WhatsApp (simular Twilio)
curl -X POST http://localhost:8000/whatsapp/webhook \
  -d "From=whatsapp:+34600000000&Body=Hola, quiero reservar&ProfileName=Test"
# Esperado: respuesta TwiML con texto del agente

# 5. Test disponibilidad VAPI
curl -X POST http://localhost:8000/vapi/tools/check_availability \
  -H "Content-Type: application/json" \
  -d '{"message": {"toolCalls": [{"id": "test1", "function": {"arguments": {"fecha": "2026-04-05", "hora": "14:00", "personas": 2}}}]}}'

# 6. Confirmar que Redis está conectado
curl http://localhost:8000/cache/health

# 7. Estado de ramas git (debe quedar solo main)
git branch -a
```

---

## RESUMEN DE PRIORIDADES

| # | Acción | Archivo | Tiempo estimado |
|---|--------|---------|----------------|
| P0 | Promover dashboard-production → main | Git | 5 min |
| P0 | Borrar ramas muertas + archivos debug | Git | 5 min |
| P0 | Sustituir MockReservationRepository | vapi_router.py | 30 min |
| P0 | Activar rate limiters | vapi_router.py, whatsapp_router.py | 15 min |
| P0 | Sincronizar docker-compose.yml | docker-compose.yml | 10 min |
| P0 | Completar .env.example | .env.example | 5 min |
| P1 | gpt-4o → gpt-4o-mini | vapi_router.py | 2 min |
| P1 | Unificar logging a loguru | 4 archivos | 20 min |
| P1 | Escrituras Airtable async | vapi_router.py | 20 min |

**Tiempo total estimado: ~2 horas.**
