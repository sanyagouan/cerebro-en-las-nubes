# Plan: Pipeline CI/CD y Estrategia de Monitoreo

> **Proyecto:** Cerebro En Las Nubes - Backend
> **Fecha:** 2026-03-07
> **Estado:** Diseño - Pendiente de Implementación

---

## 1. Resumen Ejecutivo

Este documento define la estrategia completa de CI/CD y monitoreo para el sistema **Cerebro En Las Nubes**, incluyendo:

- **Pipeline CI/CD** automatizado con GitHub Actions
- **Health checks** mejorados para todos los servicios
- **Estrategia de monitoreo** con métricas clave y alertas
- **Plan de rollback** documentado

---

## 2. Estado Actual

### 2.1 GitHub Actions Existentes

| Workflow | Propósito | Estado |
|----------|-----------|--------|
| `build-dashboard.yml` | Build y deploy del dashboard | ✅ Activo |
| `build-apk.yml` | Build de APK Android | ✅ Activo |
| **CI/CD Backend** | Tests, build, deploy backend | ❌ **NO EXISTE** |

### 2.2 Health Check Actual

```python
# src/main.py - Endpoint actual
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Cerebro En Las Nubes",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
    }
```

**Limitaciones identificadas:**
- ❌ No verifica conexión a Redis
- ❌ No verifica conexión a Airtable
- ❌ No reporta métricas de rendimiento
- ❌ No hay health check profundo (`/health/deep`)

### 2.3 Infraestructura de Despliegue

```
┌─────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA ACTUAL                       │
└─────────────────────────────────────────────────────────────┘

GitHub Push ──────► Coolify Webhook ──────► Docker Build
                            │
                            ▼
                      Container Start
                            │
                            ▼
                      Health Check (básico)
```

**Problemas:**
- No hay tests automatizados antes del deploy
- No hay validación de calidad del código
- Rollback manual sin documentación

---

## 3. Pipeline CI/CD Propuesto

### 3.1 Diagrama del Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PIPELINE CI/CD PROPUESTO                              │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   on: push    │     │   on: PR     │     │   on: main   │     │   on: tag    │
│   to: main    │     │              │     │   push       │     │   v*         │
└───────┬──────┘     └───────┬──────┘     └───────┬──────┘     └───────┬──────┘
        │                    │                    │                    │
        ▼                    ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    TEST JOB   │     │    LINT JOB  │     │   BUILD JOB  │     │  DEPLOY JOB  │
│              │     │              │     │              │     │              │
│ - pytest      │     │ - ruff check │     │ - docker     │     │ - coolify    │
│ - coverage    │     │ - mypy       │     │   build      │     │   API        │
│ - security    │     │ - bandit     │     │ - push to    │     │ - health     │
│   tests       │     │              │     │   registry   │     │   check      │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
        │                    │                    │                    │
        └────────────────────┴────────────────────┴────────────────────┘
                                    │
                                    ▼
                         ┌──────────────────┐
                         │  NOTIFICACIONES   │
                         │  - Slack/Email    │
                         │  - GitHub Status  │
                         └──────────────────┘
```

### 3.2 Estructura del Workflow

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - '.github/workflows/build-*.yml'  # Excluir otros workflows
  pull_request:
    branches: [main]
    paths-ignore:
      - '**.md'
      - 'docs/**'
  release:
    types: [published]

env:
  PYTHON_VERSION: '3.11'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ============================================
  # JOB 1: Tests (siempre se ejecuta)
  # ============================================
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Run unit tests
        run: pytest tests/unit/ -v --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml

  # ============================================
  # JOB 2: Linting & Security (en PRs)
  # ============================================
  lint:
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Run Ruff (linter)
        uses: chartboost/ruff-action@v1
        with:
          args: check --output-format=github
      
      - name: Run MyPy (type checker)
        run: |
          pip install mypy
          mypy src/ --ignore-missing-imports
      
      - name: Run Bandit (security)
        uses: tj-actions/bandit@v5
        with:
          targets: src/

  # ============================================
  # JOB 3: Build Docker Image (en main)
  # ============================================
  build:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha,prefix=
            type=ref,event=branch
            type=semver,pattern={{version}}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            CACHEBUST=${{ github.sha }}

  # ============================================
  # JOB 4: Deploy to Coolify (en main)
  # ============================================
  deploy:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: ${{ vars.COOLIFY_APP_URL }}
    steps:
      - name: Trigger Coolify Deploy
        run: |
          curl -X POST "${{ secrets.COOLIFY_WEBHOOK_URL }}" \
            -H "Authorization: Bearer ${{ secrets.COOLIFY_API_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d '{"force": true}'
      
      - name: Wait for deployment
        run: sleep 30
      
      - name: Health check
        run: |
          for i in {1..10}; do
            RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${{ vars.COOLIFY_APP_URL }}/health")
            if [ "$RESPONSE" = "200" ]; then
              echo "✅ Health check passed!"
              exit 0
            fi
            echo "Attempt $i: Health check returned $RESPONSE, retrying..."
            sleep 10
          done
          echo "❌ Health check failed after 10 attempts"
          exit 1
      
      - name: Rollback on failure
        if: failure()
        run: |
          curl -X POST "${{ secrets.COOLIFY_WEBHOOK_URL }}/rollback" \
            -H "Authorization: Bearer ${{ secrets.COOLIFY_API_TOKEN }}"
```

### 3.3 Secrets Requeridos

| Secret | Descripción | Cómo obtenerlo |
|--------|-------------|----------------|
| `COOLIFY_WEBHOOK_URL` | URL del webhook de Coolify | Coolify UI → App → Webhooks |
| `COOLIFY_API_TOKEN` | Token de API de Coolify | Coolify UI → API Tokens |
| `GITHUB_TOKEN` | Token automático de GitHub | Automático (no configurar) |

---

## 4. Health Check Mejorado

### 4.1 Endpoint `/health/deep` Propuesto

```python
# src/main.py - Añadir después del endpoint /health actual

from datetime import datetime
from src.infrastructure.cache.redis_cache import get_cache
from src.infrastructure.external.airtable_service import AirtableService

@app.get("/health")
async def health_check():
    """
    Health check básico para Coolify load balancer.
    Responde rápidamente sin verificar dependencias.
    """
    return {
        "status": "healthy",
        "service": "Cerebro En Las Nubes",
        "version": os.getenv("BUILD_VERSION", "1.0.0"),
        "environment": os.getenv("ENVIRONMENT", "development"),
    }


@app.get("/health/deep")
async def deep_health_check():
    """
    Health check profundo que verifica todas las dependencias.
    Usado para monitoreo y alertas.
    """
    start_time = datetime.now()
    health_status = {
        "status": "healthy",
        "timestamp": start_time.isoformat(),
        "version": os.getenv("BUILD_VERSION", "1.0.0"),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "checks": {}
    }
    
    # 1. Verificar Redis
    try:
        cache = get_cache()
        redis_health = cache.health_check()
        health_status["checks"]["redis"] = redis_health
        
        if redis_health.get("status") != "healthy":
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # 2. Verificar Airtable
    try:
        airtable = AirtableService()
        if airtable.api:
            # Test simple query
            await airtable.get_all_records(max_records=1)
            health_status["checks"]["airtable"] = {
                "status": "healthy",
                "latency_ms": 0  # Could measure this
            }
        else:
            health_status["checks"]["airtable"] = {
                "status": "disabled",
                "reason": "API key not configured"
            }
    except Exception as e:
        health_status["checks"]["airtable"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # 3. Verificar memoria/sistema
    import psutil
    memory = psutil.virtual_memory()
    health_status["checks"]["system"] = {
        "memory_percent": memory.percent,
        "memory_available_mb": memory.available / (1024 * 1024),
        "status": "healthy" if memory.percent < 90 else "warning"
    }
    
    # Calcular latencia total
    end_time = datetime.now()
    health_status["latency_ms"] = (end_time - start_time).total_seconds() * 1000
    
    # Determinar status final
    if health_status["status"] == "unhealthy":
        return JSONResponse(
            content=health_status,
            status_code=503
        )
    
    return health_status


@app.get("/health/metrics")
async def health_metrics():
    """
    Métricas detalladas para monitoreo.
    Expone métricas de cache, requests, etc.
    """
    cache = get_cache()
    cache_stats = cache.get_stats()
    
    return {
        "cache": cache_stats,
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": get_uptime(),  # Implementar
    }
```

### 4.2 Dependencias a Añadir

```txt
# requirements.txt - Añadir
psutil>=5.9.0  # Para métricas de sistema
```

---

## 5. Estrategia de Monitoreo

### 5.1 Métricas Clave a Monitorear

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MÉTRICAS DE MONITOREO                                 │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  CATEGORÍA           │  MÉTRICA                    │  UMBRAL ALERTA     │
├─────────────────────────────────────────────────────────────────────────┤
│  DISPONIBILIDAD      │  Health check status        │  != 200 por >1m    │
│                      │  Uptime                     │  < 99.9%           │
├─────────────────────────────────────────────────────────────────────────┤
│  LATENCIA            │  Webhook VAPI response      │  > 5s (p95)        │
│                      │  Reserva creation time      │  > 3s (p95)        │
│                      │  WhatsApp send time         │  > 2s (p95)        │
│                      │  Airtable query time        │  > 1s (p95)        │
├─────────────────────────────────────────────────────────────────────────┤
│  ERRORES             │  Error rate                 │  > 5%              │
│                      │  5xx responses              │  > 1%              │
│                      │  Circuit breaker opens      │  > 0               │
├─────────────────────────────────────────────────────────────────────────┤
│  NEGOCIO             │  Reservas creadas/hora      │  Anomalía          │
│                      │  Confirmaciones WhatsApp    │  < 80%             │
│                      │  Handoffs a humano          │  > 10%             │
├─────────────────────────────────────────────────────────────────────────┤
│  RECURSOS            │  CPU usage                  │  > 80%             │
│                      │  Memory usage               │  > 85%             │
│                      │  Redis connections          │  > 80% del pool    │
│                      │  Cache hit rate             │  < 70%             │
├─────────────────────────────────────────────────────────────────────────┤
│  LLM                 │  Token usage/hora           │  Anomalía          │
│                      │  LLM latency                │  > 10s             │
│                      │  LLM error rate             │  > 1%              │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Dashboard de Monitoreo (Propuesto)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DASHBOARD PROPUESTO                                   │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  PANEL 1: SALUD DEL SISTEMA                                             │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   BACKEND   │  │    REDIS    │  │  AIRTABLE   │  │   VAPI      │   │
│  │   🟢 UP     │  │   🟢 UP     │  │   🟢 UP     │  │   🟢 UP     │   │
│  │  45ms avg   │  │  2ms avg    │  │  120ms avg  │  │  350ms avg  │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  PANEL 2: MÉTRICAS DE NEGOCIO                                           │
├─────────────────────────────────────────────────────────────────────────┤
│  Reservas hoy: 23    │    Confirmaciones: 85%    │    Handoffs: 2      │
│  ▁▁▁▁▁▁▁▁▁▁▁        │    ▓▓▓▓▓▓▓▓░░░        │    ▓░░░░░░░░░░      │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  PANEL 3: LATENCIA Y ERRORES                                            │
├─────────────────────────────────────────────────────────────────────────┤
│  P50: 120ms  │  P95: 450ms  │  P99: 1.2s  │  Error Rate: 0.3%          │
│  ────────────┼─────────────┼────────────┼────────────────────          │
│  [Gráfico de latencia últimos 60 minutos]                               │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Alertas Configuradas

| Alerta | Condición | Severidad | Notificación |
|--------|-----------|-----------|--------------|
| **ServiceDown** | Health check != 200 por >1min | 🔴 Critical | Slack + Email |
| **HighLatency** | P95 > 5s por >5min | 🟡 Warning | Slack |
| **HighErrorRate** | Error rate > 5% | 🔴 Critical | Slack + Email |
| **RedisDown** | Redis health != healthy | 🔴 Critical | Slack + Email |
| **AirtableDown** | Airtable query fail >3 veces | 🟡 Warning | Slack |
| **CacheDegraded** | Hit rate < 70% | 🟡 Warning | Slack |
| **MemoryHigh** | Memory > 85% | 🟡 Warning | Slack |
| **LLMHighLatency** | LLM response > 10s | 🟡 Warning | Slack |

### 5.4 Implementación de Monitoreo (Futura)

**Opción recomendada: Grafana + Prometheus**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    STACK DE MONITOREO                                    │
└─────────────────────────────────────────────────────────────────────────┘

FastAPI App ──────► /metrics endpoint ──────► Prometheus ──────► Grafana
     │                                          │                  │
     │                                          │                  │
     └──────────────────────────────────────────┴──────────────────┘
                              │
                              ▼
                         AlertManager
                              │
                              ▼
                         Slack/Email
```

**Dependencias a añadir:**
```txt
# requirements.txt
prometheus-fastapi-instrumentator>=6.0.0
```

---

## 6. Plan de Rollback

### 6.1 Escenarios de Rollback

| Escenario | Trigger | Acción |
|-----------|---------|--------|
| **Deploy fallido** | Health check falla después de deploy | Rollback automático |
| **Error rate alto** | >10% errores después de deploy | Rollback manual |
| **Performance degradado** | Latencia >10s sostenida | Rollback manual |
| **Bug crítico** | Reportado por usuario | Rollback manual + hotfix |

### 6.2 Procedimiento de Rollback

#### Opción A: Rollback vía Coolify UI

1. Acceder a Coolify Dashboard
2. Navegar a la aplicación `cerebro-backend`
3. Ir a la pestaña **Deployments**
4. Click en **Rollback** del deployment anterior
5. Confirmar rollback
6. Verificar health check

#### Opción B: Rollback vía API

```bash
# Script: scripts/rollback_deployment.ps1

# Configuración
$COOLIFY_URL = "https://tu-coolify.com"
$APP_UUID = "uuid-de-tu-app"
$API_TOKEN = $env:COOLIFY_API_TOKEN

# Obtener deployments
$deployments = Invoke-RestMethod -Uri "$COOLIFY_URL/api/v1/applications/$APP_UUID/deployments" -Headers @{Authorization = "Bearer $API_TOKEN"}

# Mostrar últimos 5 deployments
$deployments | Select-Object -First 5 | Format-Table uuid, status, created_at

# Seleccionar deployment anterior
$PREVIOUS_UUID = Read-Host "Introduce el UUID del deployment a restaurar"

# Ejecutar rollback
$rollbackBody = @{
    uuid = $PREVIOUS_UUID
} | ConvertTo-Json

Invoke-RestMethod -Method POST -Uri "$COOLIFY_URL/api/v1/deployments/rollback" -Body $rollbackBody -Headers @{Authorization = "Bearer $API_TOKEN"; "Content-Type" = "application/json"}

Write-Host "✅ Rollback iniciado. Verificar health check en 30 segundos."
```

#### Opción C: Rollback vía GitHub

```bash
# Revertir commit y forzar push
git revert HEAD
git push origin main

# O volver a commit específico
git reset --hard <commit-sha-seguro>
git push origin main --force  # ⚠️ Usar con cuidado
```

### 6.3 Versionado de Releases

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ESTRATEGIA DE VERSIONADO                              │
└─────────────────────────────────────────────────────────────────────────┘

Formato: v{MAJOR}.{MINOR}.{PATCH}-{PRERELEASE}

Ejemplos:
- v1.0.0        → Release estable producción
- v1.1.0        → Nueva funcionalidad (nuevo endpoint)
- v1.0.1        → Bug fix
- v2.0.0-beta.1 → Beta de versión mayor

Tags en Git:
- main → latest (producción)
- develop → edge (staging)
- v* → release (inmutable)
```

### 6.4 Checklist Pre-Deploy

```markdown
## Pre-Deploy Checklist

- [ ] Tests unitarios pasando (coverage > 80%)
- [ ] Linting sin errores
- [ ] Type checking (mypy) sin errores
- [ ] Security scan (bandit) sin vulnerabilidades críticas
- [ ] Cambios revisados en PR
- [ ] Documentación actualizada (si aplica)
- [ ] Migraciones de BD probadas (si aplica)
- [ ] Variables de entorno configuradas en Coolify
- [ ] Rollback plan documentado
```

---

## 7. Archivos a Crear/Modificar

### 7.1 Nuevos Archivos

| Archivo | Propósito |
|---------|-----------|
| `.github/workflows/ci-cd.yml` | Pipeline CI/CD principal |
| `docs/MONITOREO.md` | Documentación de estrategia de monitoreo |
| `docs/ROLLBACK_PLAN.md` | Plan de rollback detallado |
| `scripts/rollback_deployment.ps1` | Script de rollback automatizado |

### 7.2 Archivos a Modificar

| Archivo | Cambios |
|---------|---------|
| `src/main.py` | Añadir `/health/deep` y `/health/metrics` |
| `requirements.txt` | Añadir `psutil` y `prometheus-fastapi-instrumentator` |
| `Dockerfile` | Añadir `BUILD_VERSION` ARG |

---

## 8. Próximos Pasos

1. **Fase 1: Implementación CI/CD** (Prioridad Alta)
   - [ ] Crear `.github/workflows/ci-cd.yml`
   - [ ] Configurar secrets en GitHub
   - [ ] Probar pipeline con PR de prueba

2. **Fase 2: Health Checks Mejorados** (Prioridad Alta)
   - [ ] Implementar `/health/deep`
   - [ ] Implementar `/health/metrics`
   - [ ] Actualizar Coolify para usar deep health check

3. **Fase 3: Documentación** (Prioridad Media)
   - [ ] Crear `docs/MONITOREO.md`
   - [ ] Crear `docs/ROLLBACK_PLAN.md`
   - [ ] Crear script de rollback

4. **Fase 4: Monitoreo** (Prioridad Baja - Futuro)
   - [ ] Implementar endpoint `/metrics` para Prometheus
   - [ ] Configurar Grafana dashboard
   - [ ] Configurar alertas

---

## 9. Aprobación

¿Estás de acuerdo con este plan? ¿Hay algo que quieras modificar antes de proceder con la implementación?

**Opciones:**
1. ✅ Aprobar plan completo y proceder
2. 🔄 Modificar algún aspecto del pipeline
3. 📋 Priorizar solo CI/CD primero
4. ❌ Rechazar y replantear
