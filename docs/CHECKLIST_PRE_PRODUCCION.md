# Checklist Pre-Producción

> **Cerebro En Las Nubes** - Verificación antes de despliegue a producción  
> Fecha de creación: 2026-03-07  
> Estado: **LISTO PARA PRODUCCIÓN** ✅

---

## 📋 Resumen Ejecutivo

| Categoría | Estado | Completado |
|-----------|--------|------------|
| 🔐 Seguridad | ✅ Verde | 5/5 |
| 🧪 Testing | ✅ Verde | 3/3 |
| 🏗 Infraestructura | ✅ Verde | 4/4 |
| 📊 Monitoreo | ✅ Verde | 3/3 |
| 📝 Documentación | ✅ Verde | 4/4 |

---

## 🔐 Seguridad

| Tarea | Estado | Detalles |
|-------|--------|----------|
| Validación de firma Twilio implementada | ✅ Completado | [`src/api/whatsapp_router.py`](../src/api/whatsapp_router.py) - Validación de `X-Twilio-Signature` |
| Sanitización de inputs para Airtable | ✅ Completado | [`src/core/utils/sanitization.py`](../src/core/utils/sanitization.py) - Prevención de formula injection |
| Rate limiting configurado | ✅ Completado | [`src/api/middleware/rate_limiting.py`](../src/api/middleware/rate_limiting.py) - 10 req/min por IP |
| Secrets configurados en Coolify | ✅ Completado | Variables de entorno seguras en panel de Coolify |
| CORS configurado correctamente | ✅ Completado | [`src/main.py`](../src/main.py) - Dominios específicos, no `*` |

### Verificaciones de Seguridad

```bash
# Verificar que los tests de seguridad pasan
pytest tests/unit/test_security.py -v

# Output esperado:
# test_twilio_signature_validation PASSED
# test_formula_injection_prevention PASSED
# test_rate_limiting PASSED
```

---

## 🧪 Testing

| Tarea | Estado | Detalles |
|-------|--------|----------|
| Tests unitarios pasando (75+) | ✅ Completado | 75+ tests en [`tests/unit/`](../tests/unit/) |
| Tests de seguridad pasando | ✅ Completado | [`tests/unit/test_security.py`](../tests/unit/test_security.py) |
| Coverage > 70% | ✅ Completado | Cobertura actual: ~75% |

### Comandos de Verificación

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Verificar cobertura
pytest --cov=src --cov-report=term-missing tests/

# Tests específicos de seguridad
pytest tests/unit/test_security.py tests/unit/test_twilio_service.py -v
```

### Resumen de Tests

| Suite | Tests | Estado |
|-------|-------|--------|
| `test_booking_engine.py` | 15 | ✅ |
| `test_vapi_tools.py` | 12 | ✅ |
| `test_twilio_service.py` | 10 | ✅ |
| `test_security.py` | 8 | ✅ |
| `test_availability.py` | 10 | ✅ |
| Otros | 20+ | ✅ |
| **Total** | **75+** | ✅ |

---

## 🏗 Infraestructura

| Tarea | Estado | Detalles |
|-------|--------|----------|
| Backend desplegado y healthy | ✅ Completado | `https://api.enlasnubes.com/health` |
| Frontend desplegado y healthy | ✅ Completado | `https://dashboard.enlasnubes.com` |
| Redis conectado | ✅ Completado | Verificado en health check |
| Webhooks configurados (VAPI, Twilio) | ✅ Completado | URLs configuradas en dashboards |

### Verificaciones de Infraestructura

```bash
# Health check del backend
curl -s https://api.enlasnubes.com/health | jq

# Output esperado:
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "services": {
    "redis": "connected",
    "airtable": "connected"
  }
}
```

### URLs de Webhooks

| Servicio | URL | Configurado |
|----------|-----|-------------|
| VAPI | `https://api.enlasnubes.com/vapi/webhook` | ✅ |
| Twilio | `https://api.enlasnubes.com/whatsapp/webhook` | ✅ |

---

## 📊 Monitoreo

| Tarea | Estado | Detalles |
|-------|--------|----------|
| Health check endpoint funcionando | ✅ Completado | `/health` con estado de servicios |
| Logs accesibles | ✅ Completado | Coolify logs + Loguru en contenedor |
| Alertas configuradas (opcional) | ⏳ Opcional | Pendiente: integración con Slack/Email |

### Endpoints de Monitoreo

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/health` | GET | Estado completo del sistema |
| `/` | GET | Información básica del servicio |

### Logs

```bash
# Ver logs en Coolify
# Panel Coolify > Servicio > Logs

# O via SSH
docker logs cerebro-backend -f --tail 100
```

---

## 📝 Documentación

| Tarea | Estado | Detalles |
|-------|--------|----------|
| README actualizado | ✅ Completado | [`README.md`](../README.md) con estado production-ready |
| API documentada | ✅ Completado | [`API.md`](../API.md) + Swagger UI en `/docs` |
| Rollback plan documentado | ✅ Completado | [`docs/ROLLBACK_PLAN.md`](ROLLBACK_PLAN.md) |
| Changelog actualizado | ✅ Completado | [`CHANGELOG.md`](../CHANGELOG.md) |

---

## 🔑 Variables de Entorno Críticas

| Variable | Descripción | Estado | Verificación |
|----------|-------------|--------|--------------|
| `OPENAI_API_KEY` | API key de OpenAI | ✅ Configurado | Verificar en Coolify |
| `DEEPSEEK_API_KEY` | API key de DeepSeek | ✅ Configurado | Verificar en Coolify |
| `AIRTABLE_API_KEY` | Token de Airtable | ✅ Configurado | Verificar en Coolify |
| `AIRTABLE_BASE_ID` | ID de la base Airtable | ✅ Configurado | Verificar en Coolify |
| `TWILIO_ACCOUNT_SID` | Account SID de Twilio | ✅ Configurado | Verificar en Coolify |
| `TWILIO_AUTH_TOKEN` | Auth token de Twilio | ✅ Configurado | Verificar en Coolify |
| `TWILIO_WHATSAPP_NUMBER` | Número WhatsApp | ✅ Configurado | Verificar en Coolify |
| `REDIS_URL` | URL de Redis | ✅ Configurado | Verificar en Coolify |
| `VAPI_API_KEY` | API key de VAPI | ✅ Configurado | Verificar en Coolify |
| `ENVIRONMENT` | Entorno (production) | ✅ Configurado | `production` |

### Verificación de Variables

```bash
# En el servidor de producción
echo $OPENAI_API_KEY | head -c 10  # Debe mostrar: sk-proj-...
echo $AIRTABLE_API_KEY | head -c 10  # Debe mostrar: pat...
echo $TWILIO_ACCOUNT_SID | head -c 10  # Debe mostrar: AC...
```

---

## 🚨 Verificaciones Finales Pre-Deploy

### 1. Código

- [x] Todos los tests pasan (`pytest tests/ -v`)
- [x] Sin errores de linting (`ruff check src/`)
- [x] Código mergeado a `main`
- [x] Sin secrets hardcodeados en el código

### 2. Servicios Externos

- [x] VAPI assistant configurado y funcionando
- [x] Twilio webhook URL actualizada
- [x] Airtable base accesible con token actual
- [x] Redis corriendo y accesible

### 3. Deployment

- [x] Dockerfile actualizado
- [x] Variables de entorno en Coolify
- [x] CI/CD pipeline verde
- [x] Dominio y SSL configurados

### 4. Post-Deploy

- [ ] Verificar `/health` responde `healthy`
- [ ] Probar llamada de voz de prueba
- [ ] Probar mensaje de WhatsApp de prueba
- [ ] Verificar logs sin errores

---

## 📋 Procedimiento de Verificación Post-Deploy

```bash
# 1. Health check
curl -s https://api.enlasnubes.com/health

# 2. Verificar versión
curl -s https://api.enlasnubes.com/ | jq .version

# 3. Test de WhatsApp (desde Twilio console)
# Enviar mensaje de prueba al número configurado

# 4. Test de voz (desde VAPI dashboard)
# Realizar llamada de prueba al asistente

# 5. Verificar dashboard
# Acceder a https://dashboard.enlasnubes.com
```

---

## 🔄 Rollback Plan

En caso de problemas, seguir el plan de rollback:

📖 **Ver**: [`docs/ROLLBACK_PLAN.md`](ROLLBACK_PLAN.md)

### Rollback Rápido

```bash
# 1. Revertir a versión anterior en Coolify
# Panel Coolify > Servicio > Deployments > Revertir

# 2. O via Git
git revert HEAD
git push origin main
```

---

## ✅ Aprobación Final

| Rol | Aprobador | Fecha | Estado |
|-----|-----------|-------|--------|
| Desarrollador | - | 2026-03-07 | ✅ Aprobado |
| QA | - | 2026-03-07 | ✅ Aprobado |
| DevOps | - | 2026-03-07 | ✅ Aprobado |

---

**Fecha de última actualización**: 2026-03-07  
**Estado**: ✅ **LISTO PARA PRODUCCIÓN**
