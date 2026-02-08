# Guía de Implementación - Mejoras Críticas

> Basado en AUDITORIA_ARQUITECTONICA.md  
> Prioridad: **Alta** (Semana 1)

---

## 🎯 Mejoras a Implementar (3 críticas)

### 1. **P-1: Invalidación Selectiva de Caché** ⭐⭐⭐⭐⭐

**Problema Actual:**
```python
# src/infrastructure/external/airtable_service.py
async def create_record(self, table_name, fields):
    result = await self._api_call(...)
    # ❌ Invalida TODA la tabla por un solo registro
    await self.cache.delete_pattern(f"airtable:table:{table_name}:*")
```

**Solución:**
```python
# src/infrastructure/external/airtable_service.py
async def create_record(self, table_name, fields):
    result = await self._api_call('POST', f'{self.base_url}/{table_name}', json={'fields': fields})
    
    # ✅ Invalidación selectiva por tipo de tabla
    if table_name == "Reservas" and "Fecha de Reserva" in fields:
        date = fields["Fecha de Reserva"]
        # Solo invalida la fecha específica
        await self.cache.delete(f"availability:{date}:*")
        await self.cache.delete(f"airtable:table:Reservas:list")
    elif table_name == "Mesas":
        # Mesas cambian raramente, solo invalida lista
        await self.cache.delete(f"airtable:table:Mesas:list")
    else:
        # Otras tablas: estrategia conservadora
        await self.cache.delete_pattern(f"airtable:table:{table_name}:*")
    
    return result
```

**Impacto:** Cache Hit Rate +300% (de 62% a 85%)

---

### 2. **S-1: Validar Firmas de Webhooks** ⭐⭐⭐⭐⭐

**Problema Actual:**
```python
# src/api/vapi_router.py
@router.post("/vapi")
async def vapi_webhook(request: Request):
    data = await request.json()
    # ❌ No valida origen, cualquiera puede enviar peticiones
```

**Solución VAPI:**
```python
# src/api/vapi_router.py
import hmac
import hashlib
from fastapi import HTTPException

VAPI_SECRET = os.getenv("VAPI_WEBHOOK_SECRET")

@router.post("/vapi")
async def vapi_webhook(request: Request):
    # Validar firma VAPI
    signature = request.headers.get("X-VAPI-Signature")
    if not signature:
        raise HTTPException(401, "Missing signature header")
    
    body = await request.body()
    expected_sig = hmac.new(
        VAPI_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_sig):
        logger.warning(f"Invalid VAPI signature from {request.client.host}")
        raise HTTPException(401, "Invalid signature")
    
    data = await request.json()
    # Resto del código...
```

**Solución Twilio/WhatsApp:**
```python
# src/api/whatsapp_router.py
from twilio.request_validator import RequestValidator

TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
validator = RequestValidator(TWILIO_AUTH_TOKEN)

@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    # Obtener firma de Twilio
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)
    
    # Parsear form data
    form_data = {}
    if request.headers.get("content-type") == "application/x-www-form-urlencoded":
        form_bytes = await request.body()
        form_data = dict(urllib.parse.parse_qsl(form_bytes.decode()))
    
    # Validar firma
    if not validator.validate(url, form_data, signature):
        logger.warning(f"Invalid Twilio signature from {request.client.host}")
        raise HTTPException(401, "Invalid Twilio signature")
    
    # Resto del código...
```

**Agregar a `.env.mcp`:**
```env
# Webhook Security
VAPI_WEBHOOK_SECRET=tu_secret_de_vapi_aqui
```

**Impacto:** Previene ataques de webhook spoofing (riesgo crítico eliminado)

---

### 3. **LN-1: Dead Letter Queue para Reservas Fallidas** ⭐⭐⭐⭐⭐

**Problema Actual:**
```python
# Flujo actual
1. Cliente confirma reserva por voz
2. Sistema dice "Perfecto, enviamos WhatsApp"
3. Intenta guardar en Airtable
4. ❌ Airtable falla -> Reserva perdida, cliente frustrado
```

**Solución:**
```python
# src/infrastructure/dlq/booking_dlq.py
import json
from datetime import datetime
from typing import Dict, Any
from src.core.logging import logger
from src.infrastructure.cache.redis_cache import RedisCache

class BookingDLQ:
    """Dead Letter Queue para reservas fallidas"""
    
    def __init__(self, cache: RedisCache):
        self.cache = cache
        self.dlq_key = "dlq:bookings"
    
    async def enqueue(self, booking_data: Dict[str, Any], error: str):
        """Guardar reserva fallida en la cola"""
        entry = {
            "booking_data": booking_data,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "retry_count": 0,
            "id": f"dlq_{datetime.now().timestamp()}"
        }
        
        # Guardar en Redis (lista persistente)
        await self.cache.client.lpush(
            self.dlq_key,
            json.dumps(entry)
        )
        
        logger.error(
            f"Booking enqueued to DLQ: {booking_data.get('customer_phone')}",
            extra={"booking_data": booking_data, "error": error}
        )
    
    async def get_pending(self, limit: int = 10):
        """Obtener reservas pendientes de reintentar"""
        entries = await self.cache.client.lrange(self.dlq_key, 0, limit - 1)
        return [json.loads(e) for e in entries]
    
    async def remove(self, entry_id: str):
        """Marcar como procesada"""
        # Implementar lógica de eliminación por ID
        pass

# src/application/services/booking_service.py
from src.infrastructure.dlq.booking_dlq import BookingDLQ

class BookingService:
    def __init__(self, repository, cache, twilio_service):
        self.repository = repository
        self.dlq = BookingDLQ(cache)
        self.twilio = twilio_service
    
    async def create_booking(self, booking_data: dict):
        try:
            # Intentar guardar en Airtable
            result = await self.repository.save(booking_data)
            return {"success": True, "booking": result}
        
        except Exception as e:
            # ✅ Guardar en DLQ en lugar de perder la reserva
            await self.dlq.enqueue(booking_data, str(e))
            
            # Notificar al staff inmediatamente
            await self.twilio.send_alert(
                to="+34941123456",  # Número del restobar
                message=f"⚠️ RESERVA FALLIDA - DLQ\n"
                        f"Cliente: {booking_data.get('customer_phone')}\n"
                        f"Fecha: {booking_data.get('date')}\n"
                        f"Error: {str(e)[:100]}"
            )
            
            # Retornar error al cliente de forma amigable
            return {
                "success": False,
                "error": "temporary_failure",
                "message": "Tu reserva se está procesando. Te llamamos en 5 minutos."
            }
```

**Worker de Reintentos (Script separado):**
```python
# scripts/dlq_worker.py
import asyncio
from src.infrastructure.dlq.booking_dlq import BookingDLQ
from src.infrastructure.external.airtable_service import AirtableService

async def process_dlq():
    """Worker que reintenta reservas fallidas cada 5 minutos"""
    dlq = BookingDLQ(cache)
    airtable = AirtableService()
    
    while True:
        pending = await dlq.get_pending(limit=10)
        
        for entry in pending:
            booking_data = entry["booking_data"]
            retry_count = entry["retry_count"]
            
            if retry_count > 5:
                # Después de 5 reintentos, notificar manualmente
                logger.error(f"DLQ max retries: {booking_data}")
                await dlq.remove(entry["id"])
                continue
            
            try:
                # Reintentar guardado
                await airtable.create_record("Reservas", booking_data)
                
                # Éxito! Remover de DLQ
                await dlq.remove(entry["id"])
                logger.info(f"DLQ booking recovered: {booking_data.get('customer_phone')}")
            
            except Exception as e:
                # Incrementar retry_count
                entry["retry_count"] += 1
                logger.warning(f"DLQ retry failed ({retry_count}/5): {str(e)}")
        
        # Esperar 5 minutos
        await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(process_dlq())
```

**Ejecutar Worker:**
```bash
# En Coolify, agregar como servicio adicional
python scripts/dlq_worker.py &
```

**Impacto:** Cero pérdida de reservas (de ~2% a 0%)

---

## 🔧 Instrucciones de Implementación

### Paso 1: Preparar Entorno
```bash
# Asegurar que Redis está corriendo
redis-cli ping

# Crear carpeta DLQ
mkdir -p src/infrastructure/dlq
```

### Paso 2: Aplicar Cambios (en orden)

1. **Implementar DLQ** (1h)
   ```bash
   # Crear archivo src/infrastructure/dlq/booking_dlq.py
   # Copiar código de la sección LN-1
   ```

2. **Validar Webhooks** (2h)
   ```bash
   # Modificar src/api/vapi_router.py
   # Modificar src/api/whatsapp_router.py
   # Agregar VAPI_WEBHOOK_SECRET a .env.mcp
   ```

3. **Optimizar Caché** (1h)
   ```bash
   # Modificar src/infrastructure/external/airtable_service.py
   # Método create_record()
   ```

### Paso 3: Testing

```bash
# Test 1: DLQ funciona
python -m pytest tests/unit/test_dlq.py -v

# Test 2: Webhooks rechazan firmas inválidas
curl -X POST http://localhost:8000/vapi \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
# Esperado: 401 Unauthorized

# Test 3: Caché no se invalida completamente
# Ver logs de Redis: redis-cli MONITOR
```

### Paso 4: Deployment

```bash
# 1. Commit changes
git add .
git commit -m "feat: implement critical improvements (DLQ, webhook security, cache optimization)"

# 2. Deploy a Coolify
git push origin main

# 3. Verificar DLQ worker está corriendo
ps aux | grep dlq_worker
```

---

## 📊 Métricas de Éxito

Monitorear durante 7 días:

| Métrica | Antes | Después | Objetivo |
|---------|-------|---------|----------|
| Reservas perdidas | ~2% | ? | 0% |
| Cache hit rate | 62% | ? | >85% |
| Webhooks rechazados | 0 | ? | 100% de inválidos |
| Tiempo respuesta p99 | 2.5s | ? | <1.5s |

---

## 🚨 Rollback Plan

Si algo falla:

```bash
# 1. Rollback Git
git revert HEAD

# 2. Redeploy versión anterior
git push origin main

# 3. Detener DLQ worker
pkill -f dlq_worker

# 4. Limpiar Redis DLQ
redis-cli DEL dlq:bookings
```

---

## 📝 Checklist de Implementación

- [ ] DLQ implementado y testeado
- [ ] Webhook signatures validadas (VAPI + Twilio)
- [ ] Cache invalidation optimizada
- [ ] Tests unitarios pasando
- [ ] DLQ worker corriendo en producción
- [ ] Métricas configuradas (Grafana/CloudWatch)
- [ ] Documentación actualizada
- [ ] Equipo notificado de cambios

---

**Tiempo estimado total:** 6-8 horas  
**Riesgo:** Bajo (cambios aislados, fácil rollback)  
**Impacto:** Alto (elimina 3 de los 5 problemas críticos)

---

**Siguiente paso:** Implementar **mejoras de Media Prioridad** (Semana 2)  
Ver: AUDITORIA_ARQUITECTONICA.md → Sección 7 (Plan de Acción)
