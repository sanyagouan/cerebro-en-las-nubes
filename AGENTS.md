# AGENTS.md - Guía de Agentes Especializados

> **Cerebro En Las Nubes** - Sistema Multi-Agente para Restobar  
> Última actualización: 2026-02-08

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Arquitectura Multi-Agente](#arquitectura-multi-agente)
3. [Agentes Especializados](#agentes-especializados)
4. [Reglas de Negocio Críticas](#reglas-de-negocio-críticas)
5. [Flujos de Interacción](#flujos-de-interacción)
6. [Integraciones Externas](#integraciones-externas)
7. [Esquema de Base de Datos](#esquema-de-base-de-datos)
8. [Convenciones de Código](#convenciones-de-código)
9. [Troubleshooting](#troubleshooting)

---

## Introducción

**Cerebro En Las Nubes** es un asistente de voz multi-agente especializado en la gestión de reservas del restaurante **"En Las Nubes Restobar"** (Logroño, España).

### Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|------------|---------|
| **Runtime** | Python | 3.11+ |
| **Framework** | FastAPI | 0.115+ |
| **LLMs** | GPT-4o, GPT-4o-mini, DeepSeek | Latest |
| **Cache** | Redis | 5.0+ |
| **Base de Datos** | Airtable | API v0 |
| **Comunicación** | VAPI, Twilio | Latest |
| **Deployment** | Coolify | Docker |

### Objetivos del Sistema

1. ✅ **Automatizar reservas** por voz con validación de disponibilidad real
2. ✅ **Optimizar asignación de mesas** evitando desperdicio de capacidad
3. ✅ **Confirmar vía WhatsApp** con gestión de estados (Pendiente → Confirmada)
4. ✅ **Derivar situaciones complejas** a atención humana (handoff inteligente)

---

## Arquitectura Multi-Agente

```
┌─────────────────────────────────────────────────────────────┐
│                     FLUJO DE PROCESAMIENTO                  │
└─────────────────────────────────────────────────────────────┘

Cliente (Voz/WhatsApp)
         │
         ▼
    Orchestrator ────────────┐
         │                   │
         ▼                   │ (Coordina)
    RouterAgent              │
         │                   │
         ├─[reservation]─────▼─── LogicAgent ────▶ Airtable
         │                          │
         ├─[human]──────────────────┘
         │                          │
         ▼                          ▼
    HumanAgent ◀─────────────── Redis Cache
         │
         ▼
    Respuesta Final
```

### Componente Orchestrator

**Ubicación:** `src/application/orchestrator.py`

**Responsabilidades:**
1. **Recibir input** del cliente (voz vía VAPI o mensaje de WhatsApp vía Twilio)
2. **Coordinar agentes** en secuencia: Router → Logic/Human
3. **Gestionar estado** de la conversación
4. **Disparar notificaciones** WhatsApp para confirmaciones
5. **Decidir handoff** a humano cuando sea necesario

**Diagrama de Coordinación:**
```python
# Flujo simplificado del Orchestrator
async def process_message(self, input_text):
    # 1. Clasificar intención
    intent = await self.router_agent.classify(input_text)
    
    # 2. Rutear según intención
    if intent.needs_human:
        response = await self.human_agent.handle(input_text)
    else:
        # Validar lógica de negocio
        logic_result = await self.logic_agent.process(intent)
        
        # Generar respuesta natural
        response = await self.human_agent.craft_response(logic_result)
    
    # 3. Disparar notificaciones si aplica
    if intent.type == "reservation" and logic_result.success:
        await self.send_whatsapp_confirmation(logic_result.reservation)
    
    return response
```

---

## Agentes Especializados

### 1. RouterAgent

**Modelo:** `gpt-4o-mini` (bajo costo, alta velocidad)  
**Ubicación:** `src/application/agents/router_agent.py`

#### Responsabilidades

- ✅ **Clasificar intenciones** del cliente
- ✅ **Extraer parámetros** clave (número de personas, fecha, hora)
- ✅ **Decidir escalamiento** a humano si es necesario

#### Intenciones Reconocidas

| Intención | Descripción | Ejemplo de Input |
|-----------|-------------|------------------|
| `reservation` | Nueva reserva | "Quiero reservar para 4 personas mañana a las 21:00" |
| `confirmation` | Confirmar reserva existente | "SÍ confirmo la reserva" |
| `cancellation` | Cancelar reserva | "Necesito cancelar mi reserva de esta noche" |
| `notes` | Agregar notas especiales | "Tenemos un bebé, ¿hay trona?" |
| `faq` | Preguntas frecuentes | "¿Cuál es el horario?" |
| `human` | Derivar a humano | "Quiero hacer una reserva muy grande" |

#### Prompt System (Extracto)

```python
system_prompt = """
Eres el Router del sistema de reservas "En Las Nubes Restobar".

TAREA: Clasificar la intención del cliente y extraer parámetros.

INTENCIONES VÁLIDAS:
- reservation: Cliente quiere hacer una reserva nueva
- confirmation: Cliente confirma una reserva existente
- cancellation: Cliente cancela una reserva
- notes: Cliente agrega información adicional (alergias, bebés, etc)
- faq: Preguntas sobre horarios, ubicación, carta
- human: Situaciones complejas (>11 personas, combinaciones especiales)

EXTRACCIÓN DE PARÁMETROS:
- number_of_guests: int (obligatorio para reservations)
- date: ISO 8601 (inferir si dice "mañana", "esta noche")
- time: HH:MM (convertir "9 de la noche" a "21:00")
- special_requests: str (mascotas, tronas, accesibilidad)

REGLAS:
- Si >11 personas -> intención=human (requiere combinación de mesas)
- Si menciona "cachopo sin gluten" -> extraer y marcar aviso 24h
- Si input ambiguo o incompleto -> needs_clarification=true
"""
```

#### Ejemplo de Output

```json
{
  "intent": "reservation",
  "number_of_guests": 4,
  "date": "2026-02-09",
  "time": "21:00",
  "special_requests": "terraza si es posible",
  "needs_human": false,
  "confidence": 0.95
}
```

---

### 2. LogicAgent

**Modelo:** `deepseek-chat` (razonamiento profundo, bajo costo)  
**Ubicación:** `src/application/agents/logic_agent.py`

#### Responsabilidades

- ✅ **Validar disponibilidad real** consultando Airtable
- ✅ **Asignar mesa óptima** minimizando desperdicio de capacidad
- ✅ **Gestionar estados** de reservas (Pendiente, Confirmada, Cancelada)
- ✅ **Aplicar reglas de negocio** complejas (combinaciones, horarios especiales)

#### Algoritmo de Asignación de Mesas

```python
def assign_optimal_table(self, num_guests: int, prefer_terrace: bool = False):
    """
    CRITERIOS DE OPTIMIZACIÓN:
    1. Capacidad exacta > Capacidad ampliada > Siguiente capacidad superior
    2. Minimizar desperdicio (no asignar mesa de 8 a 2 personas si hay mesas de 4)
    3. Priorizar ubicación solicitada (terraza vs interior)
    4. Evitar combinaciones si no es necesario
    
    EJEMPLO:
    - 4 personas + prefer_terrace=True
      -> Buscar: Mesa 2T (cap 6) o Mesa 3T (cap 10) o Mesa 8T (cap 10)
      -> Prioridad: 2T (desperdicio mínimo)
    
    - 11 personas
      -> Requiere combinación: Mesa 3I (10) + Mesa 5I (2) = 12
      -> BLOQUEAR: Esta lógica requiere aprobación humana
    """
    available_tables = self.airtable_service.get_available_tables(date, time)
    
    # Filtrar por ubicación preferida
    if prefer_terrace:
        tables = [t for t in available_tables if t.location == "Terraza"]
    else:
        tables = available_tables
    
    # Ordenar por desperdicio mínimo
    tables.sort(key=lambda t: (
        abs(t.capacity - num_guests),      # Diferencia de capacidad
        t.capacity                         # Desempate: capacidad menor
    ))
    
    # Validar combinaciones solo si >11
    if num_guests > 11:
        return self._suggest_combination(num_guests, available_tables)
    
    return tables[0] if tables else None
```

#### Estados de Reserva

```python
class ReservationState(str, Enum):
    PENDIENTE = "Pendiente"        # Creada, esperando confirmación WhatsApp
    CONFIRMADA = "Confirmada"      # Cliente confirmó vía WhatsApp
    CANCELADA = "Cancelada"        # Cliente o sistema canceló
```

#### Reglas de Negocio Implementadas

1. **Validación de Horarios:**
   ```python
   if not self.is_open(date, time):
       return {"error": "Cerrado en ese horario"}
   ```

2. **Restricción Lunes/Festivos:**
   ```python
   if date.weekday() == 0 and not self.is_holiday(date):
       return {"error": "Cerrado los lunes (abre festivos)"}
   ```

3. **Aviso Cachopo Sin Gluten (24h):**
   ```python
   if "cachopo sin gluten" in special_requests:
       if (reservation_date - now).hours < 24:
           return {"error": "Cachopo sin gluten requiere aviso de 24h"}
   ```

---

### 3. HumanAgent

**Modelo:** `gpt-4o` (máxima calidad de lenguaje natural)  
**Ubicación:** `src/application/agents/human_agent.py`

#### Responsabilidades

- ✅ **Generar respuestas naturales** en tono cercano y profesional
- ✅ **Personificar "Alba"** (recepcionista del restobar)
- ✅ **Conocer TODA la carta** y detalles del menú
- ✅ **Responder FAQs** (horarios, ubicación, accesibilidad, mascotas)
- ✅ **Empatizar con el cliente** y manejar objeciones

#### Prompt de Personalidad

```python
system_prompt = """
Eres Alba, la recepcionista de "En Las Nubes Restobar" en Logroño.

PERSONALIDAD:
- Cercana pero profesional
- Proactiva: Ofreces alternativas si no hay disponibilidad
- Empática: Reconoces las necesidades del cliente (niños, mascotas, accesibilidad)
- Entusiasta: Recomiendas platos destacados del menú

TON DE VOZ:
✅ "¡Perfecto! Te he reservado la mesa 2T en la terraza para 4 personas."
✅ "Tenemos tronas disponibles, apuntado en tus notas."
❌ "Su solicitud ha sido procesada correctamente." (demasiado formal)
❌ "Vale, te lo apunto tío." (demasiado informal)

CONOCIMIENTO DE CARTA:
- Platos destacados: Cachopo (normal y sin gluten), Costillas al horno
- Menú del día: Solo martes-viernes mediodía (12:00-16:00)
- Cachopo sin gluten: SIEMPRE mencionar que requiere aviso de 24h

GESTIÓN DE OBJECIONES:
- No hay disponibilidad -> Ofrecer horarios alternativos (1h antes/después)
- Terraza llena + mascotas -> Sugerir interior con ventanas abiertas
- Grupo >11 -> Explicar que requiere validación manual y prometer callback
"""
```

#### Ejemplos de Respuestas

**Caso 1: Reserva Exitosa**
```
Input: "Quiero reservar para 4 esta noche a las 9"
Logic Result: Mesa 2T asignada (Terraza, Cap 6)

Output (HumanAgent):
"¡Perfecto! 🎉 Te he reservado la mesa 2T en la terraza para 4 personas 
esta noche a las 21:00. Te voy a mandar un WhatsApp para que confirmes, 
¿te parece bien? Si tienes alguna petición especial (tronas, alergias, 
etc.), dímelo ahora."
```

**Caso 2: No Hay Disponibilidad**
```
Input: "Mesa para 6 mañana a las 21:00"
Logic Result: No hay mesas disponibles

Output (HumanAgent):
"Vaya, a las 21:00 estamos completos para 6 personas 😕 Pero tengo 
disponibilidad a las 20:00 o a las 22:00. ¿Te viene bien alguno de 
esos horarios? También puedo apuntarte en lista de espera por si hay 
alguna cancelación."
```

**Caso 3: Derivación a Humano**
```
Input: "Somos 15 personas para una cena de empresa"
Router: intent=human

Output (HumanAgent):
"¡Qué bien que vengan en grupo! 🎊 Para reservas de más de 11 personas 
necesito coordinar la combinación de mesas y menú. ¿Me dejas un teléfono 
y te llamo yo en los próximos 15 minutos para confirmarte todo? Así me 
cuentas mejor qué necesitáis."
```

---

## Reglas de Negocio Críticas

### Gestión de Mesas

#### Mesas Interior (13 mesas, Cap total: 59)

| Mesa | Capacidad | Capacidad Ampliada | Notas |
|------|-----------|-------------------|-------|
| **Mesa 1I** | 4 | 6 | Junto a ventana |
| **Mesa 2I** | 4 | 6 | - |
| **Mesa 3I** | 8 | 10 | Ideal para grupos |
| **Mesa 4I** | 2 | 4 | Mesa alta |
| **Mesa 5I** | 2 | 4 | Rincón acogedor |
| **Mesa 6I** | 4 | 6 | - |
| **Mesa 7I** | 6 | 8 | - |
| **Mesa 8I** | 4 | 6 | - |
| **Mesa 9I** | 2 | 4 | - |
| **Mesa 10I** | 4 | 6 | - |
| **Mesa 11I** | 6 | 8 | - |
| **Mesa 12I** | 4 | 6 | - |
| **Mesa 13I** | 2 | 4 | Acceso adaptado |

#### Mesas Terraza (8 mesas, Cap total: 64)

| Mesa | Capacidad | Capacidad Ampliada | Notas |
|------|-----------|-------------------|-------|
| **Mesa 1T** | 10 | 12 | Mesa grande, vistas |
| **Mesa 2T** | 6 | 8 | Popular, reservada rápido |
| **Mesa 3T** | 8 | 10 | - |
| **Mesa 4T** | 4 | 6 | - |
| **Mesa 5T** | 6 | 8 | - |
| **Mesa 6T** | 6 | 8 | - |
| **Mesa 7T** | 10 | 12 | Mesa grande |
| **Mesa 8T** | 8 | 10 | - |

### Combinaciones de Mesas (Grupos >11)

⚠️ **REQUIERE APROBACIÓN HUMANA**

| Combinación | Capacidad Total | Notas |
|-------------|-----------------|-------|
| Mesa 3I + Mesa 5I | 12 | Interior, cerca del baño |
| Mesa 1T + Mesa 4T | 14 | Terraza, vistas |
| Mesa 3T + Mesa 8T | 18 | Terraza grande |
| Mesa 3I + Mesa 7I + Mesa 11I | 20 | Interior completo |

### Restricciones Temporales

#### Horarios de Apertura

| Día | Comidas | Cenas |
|-----|---------|-------|
| **Lunes** | ❌ Cerrado | ❌ Cerrado |
| **Martes - Viernes** | 13:00 - 17:00 | 20:00 - 23:00 |
| **Sábado** | 13:00 - 17:00 | 20:00 - 00:00 |
| **Domingo** | 13:00 - 17:00 | 20:00 - 23:00 |

**Excepciones:**
- **Festivos:** Si lunes es festivo → Abierto (cierra el martes)
- **Menú del día:** Solo martes-viernes mediodía (13:00-17:00)

#### Avisos Especiales

| Producto/Servicio | Aviso Requerido |
|-------------------|-----------------|
| **Cachopo sin gluten** | 24 horas |
| **Menú degustación** | 48 horas (grupos >6) |
| **Tarta personalizada** | 48 horas |

### Política de Mascotas

✅ **Permitido:** Terraza  
❌ **No permitido:** Interior

**Nota:** Perros pequeños/medianos bienvenidos. Disponibilidad de agua.

### Accesibilidad

- ✅ **Acceso adaptado:** Mesa 13I reservada preferente para PMR
- ✅ **Baño adaptado:** Planta baja
- ✅ **Tronas:** 6 disponibles (confirmar en reserva)

---

## Flujos de Interacción

### Flujo 1: Reserva por Voz (VAPI)

```
┌─────────────────────────────────────────────────────────────┐
│ FLUJO: RESERVA POR VOZ                                      │
└─────────────────────────────────────────────────────────────┘

1. Cliente llama al número VAPI
   └─> Audio Input: "Hola, quiero reservar para 4 personas mañana a las 9"

2. Orchestrator recibe transcripción
   └─> POST /vapi/webhook
       Body: {"text": "...", "session_id": "xxx"}

3. RouterAgent clasifica
   └─> intent=reservation, num_guests=4, date=tomorrow, time=21:00

4. LogicAgent valida disponibilidad
   ├─> Consulta Airtable: GET /v0/{base}/Mesas
   ├─> Filtra mesas disponibles para mañana 21:00
   ├─> Asigna Mesa 2T (Cap 6, Terraza)
   └─> Crea registro en Airtable:
       {
         "Nombre del Cliente": "Pendiente",
         "Teléfono": "+34XXX",
         "Fecha de Reserva": "2026-02-09",
         "Hora": "2026-02-09T21:00:00",
         "Cantidad de Personas": 4,
         "Estado de Reserva": "Pendiente",
         "Mesa": ["recXXX_Mesa2T"]
       }

5. HumanAgent genera respuesta
   └─> "¡Perfecto! Te he reservado la mesa 2T en la terraza para 4 
        personas mañana a las 21:00..."

6. Orchestrator dispara WhatsApp
   └─> POST Twilio API
       Body: {
         "to": "+34XXX",
         "body": "Hola! Tienes reserva en En Las Nubes para 4 personas 
                  el 09/02 a las 21:00. ¿CONFIRMAS? Responde SÍ o NO."
       }
```

### Flujo 2: Confirmación WhatsApp (Twilio)

```
┌─────────────────────────────────────────────────────────────┐
│ FLUJO: CONFIRMACIÓN WHATSAPP                                │
└─────────────────────────────────────────────────────────────┘

1. Cliente responde WhatsApp
   └─> "SÍ confirmo"

2. Twilio Webhook dispara
   └─> POST /twilio/webhook
       Body: {
         "From": "+34XXX",
         "Body": "SÍ confirmo"
       }

3. RouterAgent clasifica
   └─> intent=confirmation, phone=+34XXX

4. LogicAgent actualiza estado
   ├─> Busca reserva en Airtable: WHERE {Teléfono} = "+34XXX"
   ├─> Actualiza: PATCH /v0/{base}/Reservas/{rec_id}
   │   Body: {"Estado de Reserva": "Confirmada"}
   └─> Resultado: success=true

5. HumanAgent responde
   └─> "¡Listo! Tu reserva está confirmada. Nos vemos mañana a las 21:00. 
        Cualquier cosa, llámanos al 941 123 456."

6. Orchestrator envía respuesta WhatsApp
   └─> POST Twilio API (respuesta)
```

### Flujo 3: Derivación a Humano

```
┌─────────────────────────────────────────────────────────────┐
│ FLUJO: DERIVACIÓN A HUMANO (HANDOFF)                       │
└─────────────────────────────────────────────────────────────┘

CASOS QUE DISPARAN HANDOFF:
- Grupos >11 personas (requiere combinación de mesas)
- Solicitudes complejas (menú degustación para 20 personas)
- Clientes VIP identificados (teléfonos en whitelist)
- Errores técnicos (Airtable caído, Redis offline)
- Cliente frustrado (detectado por sentiment analysis)

1. RouterAgent detecta complejidad
   └─> intent=human, reason="group_size_exceeded"

2. Orchestrator marca handoff
   └─> Crea ticket en sistema interno
       {
         "type": "handoff",
         "reason": "Grupo de 15 personas",
         "customer_phone": "+34XXX",
         "original_message": "...",
         "timestamp": "2026-02-08T15:30:00Z"
       }

3. HumanAgent explica al cliente
   └─> "Para coordinar tu reserva de 15 personas necesito que te llame 
        mi compañera. ¿Me dejas tu teléfono y te llamamos en 15 minutos?"

4. Notificación interna
   └─> Email/Slack al staff del restobar
       Subject: "[HANDOFF] Reserva grupo grande - +34XXX"
```

---

## Integraciones Externas

### 1. VAPI (Voz)

**Endpoint:** `POST /vapi/webhook`  
**Documentación:** Interna (API.md)

**Request Body:**
```json
{
  "session_id": "vapi_sess_abc123",
  "text": "Quiero reservar para 4 personas",
  "audio_url": "https://vapi.ai/recordings/abc123.mp3",
  "timestamp": "2026-02-08T15:30:00Z"
}
```

**Response:**
```json
{
  "response": "¡Perfecto! ¿Para qué día y hora?",
  "next_action": "wait_for_details"
}
```

### 2. Twilio (WhatsApp & SMS)

**Webhook:** `POST /twilio/webhook`  
**Credenciales:** Ver `.env.mcp` (después de migración)

**Envío de Mensaje:**
```python
from twilio.rest import Client

client = Client(account_sid, auth_token)

message = client.messages.create(
    from_='whatsapp:+14155238886',
    body='Confirma tu reserva: SÍ o NO',
    to='whatsapp:+34600000000'
)
```

**Recepción de Webhook:**
```python
@router.post("/twilio/webhook")
async def twilio_webhook(request: Request):
    form_data = await request.form()
    from_number = form_data["From"]
    body = form_data["Body"]
    
    # Procesar con Orchestrator
    response = await orchestrator.process_message(body, from_number)
    
    # Responder TwiML
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Message>{response}</Message>
    </Response>"""
```

### 3. Airtable (Base de Datos)

**Base ID:** `appcUoRqLVqxQm7K2`  
**API Key:** Ver `.env.mcp` (⚠️ **REGENERAR** si falló)

**Tablas Principales:**

#### Tabla Reservas (`tblHPyRRo18IwBAUC`)
```python
from pyairtable import Api

api = Api(api_key)
table = api.table('appcUoRqLVqxQm7K2', 'tblHPyRRo18IwBAUC')

# Crear reserva
reservation = table.create({
    "Nombre del Cliente": "Juan Pérez",
    "Teléfono": "+34600000000",
    "Fecha de Reserva": "2026-02-09",
    "Hora": "2026-02-09T21:00:00.000Z",
    "Cantidad de Personas": 4,
    "Estado de Reserva": "Pendiente",
    "Mesa": ["recXXX_Mesa2T"]
})

# Actualizar estado
table.update(reservation['id'], {
    "Estado de Reserva": "Confirmada"
})
```

#### Tabla Mesas (`tblRSjdDIa5SrudL5`)
```python
# Consultar disponibilidad
mesas = table.all(formula="AND({Disponible}, {Ubicación}='Terraza')")

for mesa in mesas:
    print(f"{mesa['fields']['Nombre de Mesa']}: Cap {mesa['fields']['Capacidad']}")
```

### 4. Redis (Caché)

**Ubicación:** `src/infrastructure/cache/redis_cache.py`  
**Configuración:** Ver `src/core/config/redis.py`

**Casos de Uso:**

1. **Caché de Sesiones (Conversaciones):**
   ```python
   # Guardar contexto de conversación
   await redis.set(
       f"session:{session_id}",
       json.dumps({
           "last_intent": "reservation",
           "num_guests": 4,
           "partial_data": {...}
       }),
       ex=3600  # Expira en 1h
   )
   
   # Recuperar contexto
   context = json.loads(await redis.get(f"session:{session_id}"))
   ```

2. **Caché de Disponibilidad:**
   ```python
   # Cachear mesas disponibles (TTL 5 min)
   await redis.set(
       f"availability:{date}:{time}",
       json.dumps(available_tables),
       ex=300
   )
   ```

3. **Rate Limiting:**
   ```python
   # Limitar llamadas por teléfono (10/hour)
   key = f"rate_limit:{phone}"
   count = await redis.incr(key)
   if count == 1:
       await redis.expire(key, 3600)
   
   if count > 10:
       return {"error": "Demasiadas llamadas, intenta en 1h"}
   ```

### 5. Supabase (Backend & Auth)

**Ubicación:** Configurado en MCP `supabase-mcp-server`  
**Credenciales:** Ver `.env.mcp` (SUPABASE_URL, SUPABASE_ACCESS_TOKEN)

**Uso en el Proyecto:**

1. **Backend as a Service:**
   - Base de datos PostgreSQL gestionada
   - APIs REST auto-generadas
   - Real-time subscriptions

2. **Autenticación:**
   - Sistema de usuarios (si se implementa login de staff)
   - Row Level Security (RLS) para proteger datos
   - JWT tokens para autorización

3. **Storage:**
   - Almacenamiento de archivos (menús PDF, imágenes)
   - URLs públicas con CDN

**Conexión desde Python:**
```python
from supabase import create_client

supabase = create_client(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_ACCESS_TOKEN")
)

# Query ejemplo
reservas = supabase.table("reservas").select("*").eq("estado", "Confirmada").execute()
```

**Integración con Airtable:**
- Airtable es la base de datos principal operativa
- Supabase se usa para analytics y reportes históricos
- Sincronización: Pendiente de implementar

### 6. Coolify (Deployment VPS)

**Panel:** https://coolify.tu-servidor.com (configurar URL real)  
**API:** Configurada en MCP `coolify`  
**Credenciales:** Ver `.env.mcp` (COOLIFY_API_URL, COOLIFY_API_TOKEN)

**Stack Desplegado:**

1. **Aplicación Principal (FastAPI):**
   - Dockerfile multi-stage
   - Puerto: 8000
   - Health check: `/health`
   - Auto-restart en fallos

2. **Redis:**
   - Imagen oficial: `redis:7-alpine`
   - Puerto: 6379
   - Persistencia: AOF habilitado
   - Networking interno con FastAPI

3. **Variables de Entorno:**
   ```bash
   # Configuradas en Coolify UI
   AIRTABLE_API_KEY=***
   TWILIO_ACCOUNT_SID=***
   TWILIO_AUTH_TOKEN=***
   TWILIO_FROM_NUMBER=***
   OPENAI_API_KEY=***
   DEEPSEEK_API_KEY=***
   REDIS_HOST=redis  # Nombre del servicio en Docker
   REDIS_PORT=6379
   ```

4. **Dominio y SSL:**
   - Dominio: configurar en Coolify
   - SSL: Let's Encrypt automático
   - Reverse proxy: Caddy (incluido en Coolify)

**Comandos Útiles (vía MCP Coolify):**

```python
# Ver estado de servicios
mcp_coolify_get_services()

# Ver logs en tiempo real
mcp_coolify_get_logs(service_id="asistente-voz", lines=100)

# Reiniciar servicio
mcp_coolify_restart_service(service_id="asistente-voz")

# Deploy nuevo commit
mcp_coolify_deploy(service_id="asistente-voz", branch="main")
```

**CI/CD Pipeline:**
- Push a GitHub → Webhook a Coolify → Build automático → Deploy
- Health check antes de promover nueva versión
- Rollback automático si health check falla

---

## Esquema de Base de Datos

### Diagrama ER (Airtable)

```
┌──────────────────┐       ┌──────────────────┐
│    Reservas      │       │      Mesas       │
├──────────────────┤       ├──────────────────┤
│ ID (auto)        │   ┌───│ ID (auto)        │
│ Nombre           │   │   │ Nombre de Mesa   │
│ Teléfono         │   │   │ Capacidad        │
│ Fecha de Reserva │   │   │ Cap. Ampliada    │
│ Hora (DateTime)  │   │   │ Ubicación        │
│ Cant. Personas   │   │   │ Disponible       │
│ Estado           │   │   │ Notas            │
│ Mesa ───────────────┘   └──────────────────┘
│ Notas            │
│ Creado (auto)    │       ┌──────────────────┐
│ Modificado       │       │     Turnos       │
└──────────────────┘       ├──────────────────┤
                           │ Fecha            │
┌──────────────────┐       │ Hora Inicio      │
│       FAQ        │       │ Hora Fin         │
├──────────────────┤       │ Mesas Ocupadas   │
│ Pregunta         │       └──────────────────┘
│ Respuesta        │
│ Categoría        │       ┌──────────────────┐
└──────────────────┘       │    Festivos      │
                           ├──────────────────┤
                           │ Fecha            │
                           │ Nombre           │
                           │ Cierra Martes    │
                           └──────────────────┘
```

### Esquema Detallado

#### Tabla: Reservas

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| **ID** | Auto | ✅ | ID único generado por Airtable |
| **Nombre del Cliente** | Single line text | ✅ | Nombre completo |
| **Teléfono** | Phone | ✅ | Formato: +34XXXXXXXXX |
| **Fecha de Reserva** | Date | ✅ | YYYY-MM-DD |
| **Hora** | DateTime | ✅ | ISO 8601 (con timezone) |
| **Cantidad de Personas** | Number | ✅ | Min: 1, Max: 20 |
| **Estado de Reserva** | Single select | ✅ | Enum: Pendiente, Confirmada, Cancelada |
| **Mesa** | Linked record | ✅ | Referencia a tabla Mesas |
| **Notas** | Long text | ❌ | Peticiones especiales (alergias, tronas, etc) |
| **Creado** | Created time | ✅ | Auto |
| **Modificado** | Last modified | ✅ | Auto |

#### Tabla: Mesas

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| **ID** | Auto | ✅ | ID único |
| **Nombre de Mesa** | Single line text | ✅ | Formato: "Mesa 1I", "Mesa 2T" |
| **Capacidad** | Number | ✅ | Capacidad estándar |
| **Capacidad Ampliada** | Number | ❌ | Con sillas extra |
| **Ubicación** | Single select | ✅ | Enum: Interior, Terraza |
| **Disponible** | Checkbox | ✅ | false = fuera de servicio |
| **Notas** | Long text | ❌ | Características especiales |

---

## Convenciones de Código

### Estructura de Directorios

```
src/
├── application/           # Capa de aplicación
│   └── orchestrator.py   # Coordinador principal
│
├── core/                 # Núcleo del dominio
│   ├── agents/          # Agentes especializados
│   │   ├── router_agent.py
│   │   ├── logic_agent.py
│   │   └── human_agent.py
│   │
│   ├── config/          # Configuración centralizada
│   │   ├── restaurant.py
│   │   └── redis.py
│   │
│   └── entities/        # Modelos de dominio
│       ├── reservation.py
│       └── table.py
│
├── infrastructure/      # Adaptadores externos
│   ├── airtable/       # Cliente Airtable
│   ├── cache/          # Redis
│   └── llm/            # Clientes LLM (OpenAI, DeepSeek)
│
└── main.py             # Entrada FastAPI
```

### Principios Arquitectónicos

1. **Arquitectura Hexagonal (Ports & Adapters)**
   ```
   core/              (Dominio puro, sin dependencias externas)
     ├─ agents/       (Lógica de negocio)
     └─ entities/     (Modelos)
   
   infrastructure/    (Implementaciones concretas)
     ├─ airtable/     (Puerto: base de datos)
     └─ llm/          (Puerto: razonamiento)
   
   application/       (Casos de uso)
   ```

2. **Inyección de Dependencias**
   ```python
   class Orchestrator:
       def __init__(
           self,
           router: RouterAgent,
           logic: LogicAgent,
           human: HumanAgent,
           airtable: AirtableService,
           cache: RedisCache
       ):
           self.router = router
           self.logic = logic
           # ...
   ```

3. **Type Hints Estrictos (mypy)**
   ```python
   from typing import Optional
   from datetime import datetime
   
   async def create_reservation(
       self,
       customer_name: str,
       phone: str,
       date: datetime,
       num_guests: int
   ) -> Optional[Reservation]:
       # ...
   ```

### Estándares de Código

#### Naming Conventions

| Elemento | Convención | Ejemplo |
|----------|-----------|---------|
| **Clases** | PascalCase | `RouterAgent`, `ReservationService` |
| **Funciones** | snake_case | `assign_optimal_table()` |
| **Variables** | snake_case | `num_guests`, `table_id` |
| **Constantes** | UPPER_SNAKE_CASE | `MAX_GUESTS_WITHOUT_COMBO` |
| **Privadas** | _prefijo | `_validate_business_rules()` |

#### Imports Order

```python
# 1. Standard library
import json
from datetime import datetime
from typing import Optional

# 2. Third-party
from fastapi import FastAPI
from pyairtable import Api
from redis import Redis

# 3. Local
from src.core.agents import RouterAgent
from src.core.entities import Reservation
```

#### Docstrings (Google Style)

```python
async def assign_optimal_table(
    self,
    num_guests: int,
    prefer_terrace: bool = False,
    date: datetime = None
) -> Optional[Table]:
    """Asigna la mesa óptima minimizando desperdicio de capacidad.
    
    Args:
        num_guests: Número de comensales (1-20)
        prefer_terrace: Si True, prioriza mesas de terraza
        date: Fecha de la reserva (default: hoy)
    
    Returns:
        Table object si hay disponibilidad, None si no hay mesas
    
    Raises:
        ValueError: Si num_guests < 1 o > 20
        AirtableError: Si falla la consulta a Airtable
    
    Example:
        >>> table = await assign_optimal_table(4, prefer_terrace=True)
        >>> print(table.name)
        "Mesa 2T"
    """
    # ...
```

### Testing Strategy

```python
# tests/unit/agents/test_router_agent.py
import pytest
from src.core.agents.router_agent import RouterAgent

@pytest.mark.asyncio
async def test_router_classifies_reservation_intent():
    """Test: RouterAgent identifica intención de reserva correctamente"""
    router = RouterAgent()
    
    result = await router.classify("Quiero reservar para 4 personas")
    
    assert result.intent == "reservation"
    assert result.number_of_guests == 4
    assert result.needs_human is False

@pytest.mark.asyncio
async def test_router_escalates_large_groups():
    """Test: RouterAgent escala grupos >11 a humano"""
    router = RouterAgent()
    
    result = await router.classify("Somos 15 personas")
    
    assert result.intent == "human"
    assert result.reason == "group_size_exceeded"
```

---

## Troubleshooting

### Problemas Comunes

#### 1. Error: "Airtable API error: Invalid authentication token"

**Causa:** Token de Airtable expirado o revocado

**Solución:**
```bash
# 1. Regenerar token en https://airtable.com/create/tokens
# 2. Actualizar .env.mcp:
AIRTABLE_API_KEY=patNUEVO_TOKEN_AQUI

# 3. Recargar variables
. .\scripts\load_mcp_secrets.ps1

# 4. Reiniciar Verdent
```

#### 2. Error: "Redis connection refused"

**Causa:** Redis no está corriendo

**Solución:**
```bash
# Verificar estado
redis-cli ping
# Esperado: PONG

# Si no responde, iniciar Redis
redis-server --daemonize yes

# Verificar configuración en src/core/config/redis.py
```

#### 3. LogicAgent asigna mesas subóptimas

**Causa:** Algoritmo no considera capacidad ampliada

**Debug:**
```python
# Agregar logs en logic_agent.py
logger.debug(f"Available tables: {[t.name for t in tables]}")
logger.debug(f"Selected: {selected_table.name} (cap {selected_table.capacity})")

# Verificar datos en Airtable
# Tabla Mesas -> Campo "Capacidad Ampliada" debe estar rellenado
```

#### 4. HumanAgent responde en inglés

**Causa:** System prompt no está forzando español

**Solución:**
```python
# En human_agent.py, agregar al system prompt:
"""
IDIOMA: SIEMPRE español de España (castellano).
Nunca respondas en inglés, incluso si el usuario escribe en inglés.
"""
```

#### 5. Cliente no recibe WhatsApp de confirmación

**Checklist:**
- [ ] Verificar que `TWILIO_FROM_NUMBER` en `.env.mcp` tiene formato correcto (+1XXXXXXXXXX)
- [ ] Verificar que el número del cliente está en formato internacional (+34XXXXXXXXX)
- [ ] Revisar logs de Twilio: https://console.twilio.com/us1/monitor/logs/messages
- [ ] Verificar que el mensaje no supera 1600 caracteres (límite WhatsApp)

---

## Apéndices

### A. Glosario de Términos

| Término | Definición |
|---------|-----------|
| **Handoff** | Derivación de la conversación a un agente humano |
| **Intent** | Intención clasificada del mensaje del cliente (reservation, faq, etc) |
| **Session** | Contexto de conversación almacenado en Redis |
| **Turno** | Franja horaria de reserva (mediodía: 12-16h, noche: 20-23h) |

### B. Referencias Externas

- **Documentación Airtable API:** https://airtable.com/developers/web/api/introduction
- **Twilio WhatsApp Sandbox:** https://www.twilio.com/docs/whatsapp/sandbox
- **OpenAI GPT-4 Best Practices:** https://platform.openai.com/docs/guides/gpt-best-practices
- **DeepSeek API Docs:** https://platform.deepseek.com/docs

### C. Contactos y Escalamiento

| Rol | Responsable | Contacto |
|-----|-------------|----------|
| **Arquitecto del Sistema** | @ArquitectoPlan | - |
| **Responsable Negocio** | @NegocioRestobar | - |
| **DevOps** | @DBSupabase | - |

---

**Última revisión:** 2026-02-08  
**Versión:** 1.0  
**Mantenedor:** Equipo Verdent + Agentes Especializados
