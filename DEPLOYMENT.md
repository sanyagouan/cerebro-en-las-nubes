# Guía de Deployment - Cerebro En Las Nubes

Guía paso a paso para desplegar el sistema de reservas por voz del restaurante en producción.

---

## 📋 **Resumen de Arquitectura**

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA DE PRODUCCIÓN                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────────────────────────┐  │
│  │   VAPI      │───▶│  FastAPI (Cerebro)       │  │
│  │  (Voice AI)  │    │  - Multi-Agent Orchestrator   │  │
│  └──────────────┘    │  - Business Logic Layer     │  │
│  (OpenAI GPT-4o)   │  - API Routers               │  │
│                      └──────────────────────────────────┘  │
│                                ▼                        │
│  ┌──────────────┐    ┌──────────────────────────────────┐  │
│  │   Twilio   │◀───│  Airtable (Database)         │  │
│  │ (WhatsApp/   │    │  - Reservas                 │  │
│  │   SMS)       │    │  - Mesas                    │  │
│  └──────────────┘    │  - Clientes                 │  │
│  (SMS Gateway)      │  - FAQ Knowledge             │  │
│                      └──────────────────────────────────┘  │
│                                ▲                        │
│  ┌──────────────┐    ┌──────────────────────────────────┐  │
│  │   Redis     │◀───│  Coolify (Deployment)       │  │
│  │  (Cache)     │    │  - Docker Container         │  │
│  └──────────────┘    │  - Auto-scaling              │  │
│  (Persistent Cache)  │  - HTTPS                    │  │
│                      └──────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 **Prerequisitos**

### **1. Servicios Externos (Cuentas Necesarias)**

#### **VAPI** - Inteligencia de Voz
- Crear cuenta en [https://vapi.ai](https://vapi.ai)
- Configurar asistente con:
  - LLM: GPT-4o
  - Voice: ElevenLabs (voz natural)
  - Transcriber: Deepgram Nova-3
- **API Key**: Necesaria para `.env`
- **Assistant ID**: Necesario para `.env`

#### **OpenAI** - LLM
- Crear cuenta en [https://platform.openai.com](https://platform.openai.com)
- Configurar GPT-4o
- **API Key**: Necesaria para `.env`

#### **Airtable** - Base de Datos Principal
- Crear base en [https://airtable.com](https://airtable.com)
- Crear tablas:
  - **Reservas**: Campos (id, client_name, client_phone, date_time, pax, table, status)
  - **Mesas**: Campos (id, name, capacity_min, capacity_max, location)
  - **Clientes**: Campos (id, name, phone, email, preferences)
- **API Key**: Necesaria para `.env` (Personal Access Token)
- **Base ID**: Necesario para `.env`

#### **Twilio** - WhatsApp/SMS
- Crear cuenta en [https://www.twilio.com](https://www.twilio.com)
- Comprar número de WhatsApp (en Espa: +34...)
- **Account SID**: Necesario para `.env`
- **Auth Token**: Necesario para `.env`

#### **Coolify** - Plataforma de Deployment
- Crear cuenta en [https://coolify.io](https://coolify.io)
- Conectar repositorio GitHub
- **API Token**: Necesario para `.env`

### **2. Herramientas Locales**
```bash
# Git
git --version  # >= 2.0

# Docker
docker --version  # >= 20.0

# Python 3.11+
python --version  # 3.11 o superior

# Node.js 18+ (para tests heredados)
node --version  # 18 o superior
npm --version   # 9 o superior
```

---

## 🌍 **Deployment en Coolify**

### **Paso 1: Configurar Repositorio**

1. **Fork el repositorio**:
   ```bash
   # En GitHub, click "Fork" en tu cuenta
   # Clonar tu fork
   git clone https://github.com/TU_USUARIO/copia-asistente-voz-en-las-nubes-opencode.git
   cd copia-asistente-voz-en-las-nubes-opencode
   ```

2. **Configurar remoto**:
   ```bash
   git remote add origin https://github.com/TU_USUARIO/copia-asistente-voz-en-las-nubes-opencode.git
   ```

### **Paso 2: Preparar Variables de Entorno**

1. **Crear archivo `.env`**:
   ```bash
   cp .env.example .env
   ```

2. **Editar `.env` con tus credenciales reales**:
   ```bash
   # --- OpenAI ---
   OPENAI_API_KEY=sk-proj-TU_OPENAI_KEY_REAL

   # --- VAPI ---
   VAPI_API_KEY=TU_VAPI_API_KEY_REAL
   VAPI_ASSISTANT_ID=TU_ASSISTANT_ID_REAL

   # --- Airtable ---
   AIRTABLE_API_KEY=patTU_AIRTABLE_KEY_REAL
   AIRTABLE_BASE_ID=appTU_BASE_ID_REAL

   # --- Twilio ---
   TWILIO_ACCOUNT_SID=ACTU_TWILIO_SID_REAL
   TWILIO_AUTH_TOKEN=TU_TWILIO_TOKEN_REAL
   TWILIO_WHATSAPP_NUMBER=+34TU_NUMERO_TWILIO

   # --- Coolify ---
   COOLIFY_API_TOKEN=TU_COOLIFY_TOKEN_REAL

   # --- Redis ---
   REDIS_URL=redis://:TU_REDIS_PASSWORD@localhost:6379
   REDIS_PASSWORD=TU_REDIS_PASSWORD_SEGURO

   # --- Server ---
   HOST=0.0.0.0
   PORT=8000

   # --- Environment ---
   ENVIRONMENT=production
   DEBUG=False

   # --- CORS ---
   # IMPORTANTE: En producción, lista dominios específicos
   ALLOWED_ORIGINS=https://cerebro-en-las-nubes.com,https://admin.cerebro-en-las-nubes.com
   ```

3. **NO COMMITEAR `.env`** (add a `.gitignore`):
   ```bash
   echo ".env" >> .gitignore
   git add .gitignore
   git commit -m "chore: añadir .env a .gitignore"
   ```

### **Paso 3: Deploy en Coolify**

1. **Login en Coolify**:
   - Visita [https://coolify.io](https://coolify.io)
   - Conecta tu cuenta de GitHub
   - Selecciona el repositorio

2. **Configurar Servicio**:
   - **Type**: Docker (por el Dockerfile)
   - **Dockerfile**: Seleccióna `Dockerfile` en la raíz
   - **Branch**: `main` (o `production`)
   - **Environment Variables**: Copia todas las de `.env`:
     ```
     OPENAI_API_KEY=sk-proj-...
     VAPI_API_KEY=...
     VAPI_ASSISTANT_ID=...
     AIRTABLE_API_KEY=pat...
     AIRTABLE_BASE_ID=app...
     TWILIO_ACCOUNT_SID=AC...
     TWILIO_AUTH_TOKEN=...
     TWILIO_WHATSAPP_NUMBER=+34...
     COOLIFY_API_TOKEN=...
     REDIS_URL=redis://:...
     REDIS_PASSWORD=...
     HOST=0.0.0.0
     PORT=8000
     ENVIRONMENT=production
     DEBUG=False
     ALLOWED_ORIGINS=https://cerebro-en-las-nubes.com
     ```

3. **Configurar Domains**:
   - **Principal Domain**: `cerebro-en-las-nubes.com`
   - **Admin Domain**: `admin.cerebro-en-las-nubes.com` (opcional)
   - **SSL**: Coolify genera certificados SSL automáticamente

4. **Deploy**:
   - Click "Deploy"
   - Espera ~2-3 minutos para que el build complete
   - Verifica logs en la consola de Coolify

### **Paso 4: Configurar Redis (Opcional - Recomendado)**

Coolify tiene servicio Redis disponible, o puedes usar externo:

#### **Opción A: Redis de Coolify**
1. En el panel de Coolify, ve a "Databases"
2. Crea nuevo Redis:
   - Name: `cerebro-redis`
   - Plan: Free (suficiente para MVP)
   - Password: Copiarla
3. Copiar la URL de conexión a `.env`:
   ```
   REDIS_URL=redis://:PASSWORD_DE_COOLIFY@host:port
   ```

#### **Opción B: Redis Externo**
1. Crear Redis en [Upstash](https://upstash.com) o [Redis Cloud](https://redis.io)
2. Copiar URL de conexión a `.env`
3. Actualizar `ENVIRONMENT=production` en Coolify

### **Paso 5: Configurar Webhooks**

#### **VAPI Webhook**
1. En el panel de VAPI, ve a tu asistente
2. "Webhook URL":
   ```
   https://cerebro-en-las-nubes.com/vapi/webhook
   ```
3. Guardar cambios

#### **Twilio Webhook (WhatsApp)**
1. En el panel de Twilio, ve a WhatsApp → Messaging → Sandbox
2. "Webhook URL":
   ```
   https://cerebro-en-las-nubes.com/whatsapp/webhook
   ```
3. Guardar cambios

### **Paso 6: Verificar Deployment**

1. **Healthcheck**:
   ```bash
   curl https://cerebro-en-las-nubes.com/health
   ```
   Respuesta esperada:
   ```json
   {
     "status": "healthy",
     "service": "Cerebro En Las Nubes",
     "version": "1.0.0",
     "environment": "production"
   }
   ```

2. **Probar API Endpoints**:
   ```bash
   # Root endpoint
   curl https://cerebro-en-las-nubes.com/

   # Probar VAPI webhook (test local)
   curl -X POST https://cerebro-en-las-nubes.com/vapi/webhook \
     -H "Content-Type: application/json" \
     -d '{"call_id": "test123", "type": "end-of-call-report"}'
   ```

3. **Verificar Logs en Coolify**:
   - Dashboard → Your Service → Logs
   - Buscar errores o warnings

---

## 🔍 **Troubleshooting**

### **Problema 1: "Module not found" errors**

**Causa**: Dependencias no instaladas

**Solución**:
1. Verifica `requirements.txt`:
   ```bash
   cat requirements.txt
   ```
2. En Coolify, agrega "Build Command":
   ```bash
   pip install -r requirements.txt
   ```

### **Problema 2: Redis connection refused**

**Causa**: Redis no iniciado o URL incorrecta

**Solución**:
1. Verifica que Redis URL es correcta:
   ```bash
   echo $REDIS_URL
   # Debe ser: redis://:password@host:6379
   ```
2. En Coolify, verifica que Redis service está running:
   - Dashboard → Databases → cerebro-redis → Status

### **Problema 3: Webhook 500 error**

**Causa**: Error en procesamiento de webhook

**Solución**:
1. Revisar logs en Coolify:
   - Dashboard → Your Service → Logs
2. Verificar payload del webhook:
   - En VAPI/Twilio panel, ver "Webhook Logs"
3. Probar localmente:
   ```bash
   # Ejecutar FastAPI local
   python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

   # Enviar test payload
   curl -X POST http://localhost:8000/vapi/webhook \
     -H "Content-Type: application/json" \
     -d @tests/mocks/vapi.mock.js
   ```

### **Problema 4: CORS errors en frontend**

**Causa**: Dominios no permitidos

**Solución**:
1. En `.env` (Coolify env vars), verificar `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://tudominio.com
   ```
2. En Coolify, actualizar env var y redeploy

---

## 📊 **Monitoring & Observabilidad**

### **Logs**
- **Coolify Logs**: Dashboard → Your Service → Logs
- **Loguru logs**: Estructurados con timestamp, level, función
- **Format**:
  ```
  2026-01-25 13:45:22.123 | INFO | main:app:45 | Cerebro starting - Environment: production
  2026-01-25 13:45:23.456 | INFO | airtable_service:30 | Cached record 'rec123' from table 'Reservas'
  ```

### **Alertas (Pendientes de implementar)**
- [ ] Monitor de uptime (UptimeRobot, Pingdom)
- [ ] Alertas de Slack/Discord para errores críticos
- [ ] Airtable API rate limits alertas
- [ ] Twilio balance alerta

### **Métricas (Pendientes de implementar)**
- [ ] Número de llamadas procesadas/día
- [ ] Tasa de conversión (reservas exitosas / total llamadas)
- [ ] Tiempo de respuesta promedio
- [ ] Cache hit rate

---

## 🔐 **Seguridad en Producción**

### **1. Variables de Entorno**
- ✅ NO commitear `.env`
- ✅ Usar variables de entorno para todas las credenciales
- ✅ Rotar claves API regularmente (90 días recomendado)

### **2. CORS Restringido**
- ✅ NO usar `ALLOWED_ORIGINS=*` en producción
- ✅ Lista solo dominios específicos
- ✅ Verificar HTTPS está activo (Coolify automático)

### **3. Rate Limiting (Pendiente)**
```python
# En src/main.py, añadir middleware de rate limit
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/vapi/webhook")
@limiter.limit("10/minute")
async def vapi_webhook(request: Request):
    ...
```

### **4. Redis Password**
- ✅ Usar password fuerte para Redis
- ✅ Cambiar regularmente
- ✅ No exponer REDIS_PASSWORD en logs

---

## 🚀 **Rollback & Updates**

### **Update del Servicio**
1. **Actualizar código**:
   ```bash
   git pull origin main
   ```

2. **Coolify auto-redeploy**:
   - Coolify detecta nuevos commits
   - Build y deploy automáticos
   - ~2-3 minutos de downtime

### **Rollback**
Si algo sale mal:
1. **En Coolify**, ve a "Deployments"
2. **Selecciona previous deployment**
3. **Click "Rollback"**
4. Downtime: <1 minuto

---

## 📝 **Checklist Pre-Producción**

- [ ] Todas las variables de entorno configuradas en Coolify
- [ ] `.env` añadido a `.gitignore`
- [ ] Webhooks de VAPI y Twilio apuntando a URLs HTTPS
- [ ] Redis service creado y URL configurada
- [ ] DNS apuntando a Coolify service URL
- [ ] SSL certificado verificado (HTTPS)
- [ ] Healthcheck endpoint respondiendo correctamente
- [ ] Logs visibles en Coolify dashboard
- [ ] CORS restringido a dominios específicos
- [ ] Tests unitarios pasando (`pytest tests/unit/ -v`)
- [ ] Backup de Airtable creado
- [ ] Documentación actualizada (API.md, README.md)

---

## 📚 **Recursos**

- [Coolify Documentation](https://coolify.io/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [VAPI Documentation](https://docs.vapi.ai)
- [Airtable API Docs](https://airtable.com/developers/web/api)
- [Twilio WhatsApp Docs](https://www.twilio.com/docs/whatsapp)

---

**Last Updated**: 2026-01-25  
**Version**: 1.0.0  
**Environment**: Production
