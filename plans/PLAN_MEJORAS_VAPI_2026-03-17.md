# Plan de Mejoras VAPI - Respuesta a Quejas del Usuario

> **Fecha:** 2026-03-17
> **Estado:** Pendiente de aprobación
> **Prioridad:** Alta

---

## 📋 Resumen Ejecutivo

El usuario ha realizado una prueba real del sistema y ha identificado **6 problemas críticos** que deben abordarse. Este plan detalla las acciones a realizar, priorizadas por impacto en la experiencia del usuario.

---

## 🔴 PRIORIDAD 1: Validación de Horarios en `create_reservation` (Opción A)

### Problema Identificado
La función `create_reservation` NO valida internamente los horarios de apertura. Si VAPI no llama primero a `check_availability`, se podría crear una reserva en horario cerrado (ej: lunes, domingo noche).

### Análisis del Código Actual

**Ubicación:** [`src/api/vapi_tools_router.py:476-647`](src/api/vapi_tools_router.py:476)

```python
@router.post("/create_reservation")
async def tool_create_reservation(request: Request):
    # ... parsea argumentos ...
    
    # ❌ NO HAY VALIDACIÓN DE HORARIO AQUÍ
    
    # Crea la reserva directamente
    result = await reservation_service.create_reservation(reservation_data)
```

**Validación existente en `check_availability`:** [`src/api/vapi_tools_router.py:339-410`](src/api/vapi_tools_router.py:339)
- Lunes = cerrado
- Domingo noche = cerrado
- Horarios: Comida 13-17, Cena 20-23:30
- Usa `BUSINESS_HOURS` de configuración central

### Solución Propuesta

Añadir validación de horarios DESPUÉS de parsear argumentos y ANTES de crear la reserva:

```python
@router.post("/create_reservation")
async def tool_create_reservation(request: Request):
    # ... parsea argumentos ...
    
    # === NUEVA VALIDACIÓN DE HORARIOS (OPCIÓN A) ===
    try:
        fecha_clean = fecha_str[:10]
        fecha = datetime.strptime(fecha_clean, "%Y-%m-%d").date()
        
        hora_clean = hora_str.replace("Z", "").split(".")[0]
        if len(hora_clean) > 5 and ":" in hora_clean:
            parts = hora_clean.split(":")
            hora_clean = f"{parts[0]}:{parts[1]}"
        hora = datetime.strptime(hora_clean, "%H:%M").time()
    except Exception as e:
        return {
            "results": [{
                "toolCallId": tool_call_id,
                "result": "Perdona, no he podido entender la fecha u hora. ¿Me la repites?"
            }]
        }
    
    # Validar día de la semana
    weekday = fecha.weekday()
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    dia_nombre = dias[weekday]
    
    # Lunes = cerrado
    if weekday == 0:
        return {
            "results": [{
                "toolCallId": tool_call_id,
                "result": f"Los lunes estamos de descanso. ¿Te interesaría mirar mesa para otro día?"
            }]
        }
    
    # Determinar servicio
    hora_int = hora.hour
    if 13 <= hora_int < 17:
        servicio = "Comida"
    elif 20 <= hora_int <= 23:
        servicio = "Cena"
    else:
        return {
            "results": [{
                "toolCallId": tool_call_id,
                "result": f"A las {hora.strftime('%H:%M')} no servimos. Comida: 13:00-17:00, Cena: 20:00-23:30"
            }]
        }
    
    # Domingo noche = cerrado
    if weekday == 6 and servicio == "Cena":
        return {
            "results": [{
                "toolCallId": tool_call_id,
                "result": f"Los domingos no abrimos para cenar. ¿Te viene bien la comida o prefieres otro día?"
            }]
        }
    
    # Validar contra BUSINESS_HOURS central
    from src.core.config.restaurant import BUSINESS_HOURS
    dias_es = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    day_hours = BUSINESS_HOURS.get(dias_es[weekday])
    if day_hours:
        dinner_hours = day_hours.get("dinner")
        if servicio == "Cena" and not dinner_hours:
            return {
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": f"Los {dia_nombre}s no abrimos por la noche. ¿Te vendría bien la comida?"
                }]
            }
    
    # === FIN VALIDACIÓN - CONTINUAR CON CREACIÓN NORMAL ===
    # ... resto del código existente ...
```

### Archivos a Modificar
- [`src/api/vapi_tools_router.py`](src/api/vapi_tools_router.py) - Añadir validación en `tool_create_reservation()`

---

## 🟠 PRIORIDAD 2: Cambio de Voz y Fluidez de Conversación

### Problema Identificado
1. **Voz actual no gusta:** El usuario quiere voz femenina, cálida, sin acentos raros, español de España neutro
2. **Conversación no fluida:** No respeta pausas ni cortes del cliente

### Configuración Actual de VAPI

```json
{
  "voice": {
    "provider": "11labs",
    "voiceId": "cgSgspJ2msm6clMCkdW9",
    "model": "eleven_multilingual_v2"
  },
  "transcriber": {
    "provider": "deepgram",
    "model": "nova-2"
  }
}
```

### Investigación de Voces para Español de España

#### Opción A: ElevenLabs - Voz "Laura" (RECOMENDADA)
- **Voice ID:** `FnmvTQXpCsXgY92JXCLh` o similar
- **Características:** Femenina, cálida, español de España neutro
- **Modelo:** `eleven_multilingual_v2` o `eleven_turbo_v2_5` (más rápido)
- **Pros:** Mejor calidad de voz, más natural
- **Contras:** Latencia ligeramente mayor

#### Opción B: ElevenLabs - Voz "Matilda"
- **Voice ID:** `XrExE9yKIg1WjnnlVkGX` 
- **Características:** Femenina, profesional, clara
- **Modelo:** `eleven_multilingual_v2`

#### Opción C: OpenAI TTS - "Nova" o "Shimmer"
- **Voces:** `nova` (femenina, cálida) o `shimmer` (femenina, suave)
- **Pros:** Muy baja latencia, buena calidad
- **Contras:** Menos natural que ElevenLabs para español de España

### Configuración de Fluidez/Interrupciones

VAPI permite configurar el manejo de interrupciones mediante `interruptionParameters`:

```json
{
  "interruptionParameters": {
    "allowBackchannel": true,
    "backchannel": {
      "enabled": true,
      "type": "filler",
      "probability": 0.3
    },
    "timeout": {
      "endOfTurn": 500,
      "response": 1000
    }
  },
  "startSpeakingPlan": {
    "waitSeconds": 0.4
  },
  "stopSpeakingPlan": {
    "numWords": 3,
    "voiceActivityThreshold": 500
  }
}
```

**Parámetros clave para mejorar fluidez:**
- `waitSeconds: 0.4` - Espera 400ms antes de responder (evita cortar al cliente)
- `numWords: 3` - Detecta interrupción si el cliente dice 3+ palabras
- `voiceActivityThreshold: 500` - Tiempo de silencio para considerar fin de frase

### Solución Propuesta

**Actualizar configuración VAPI:**

```json
{
  "voice": {
    "provider": "11labs",
    "voiceId": "FnmvTQXpCsXgY92JXCLh",
    "model": "eleven_turbo_v2_5",
    "stability": 0.5,
    "similarity_boost": 0.75
  },
  "transcriber": {
    "provider": "deepgram",
    "model": "nova-2",
    "language": "es-ES"
  },
  "interruptionParameters": {
    "allowBackchannel": true,
    "backchannel": {
      "enabled": true,
      "type": "filler"
    }
  },
  "startSpeakingPlan": {
    "waitSeconds": 0.5
  }
}
```

### Archivos/Configuraciones a Modificar
- Actualizar asistente VAPI vía API o Dashboard
- ID del asistente: `9a1f2df2-1c2d-4061-b11c-bdde7568c85d`

---

## 🟡 PRIORIDAD 3: Formato WhatsApp y Link Google Maps

### Problema Identificado
1. **Formato:** "todos los caracteres juntos sin orden"
2. **Link Maps:** Muestra texto en lugar de preview del mapa

### Análisis del Código Actual

**Ubicación de plantilla:** [`src/infrastructure/templates/content_sids.py`](src/infrastructure/templates/content_sids.py)

La plantilla Twilio Content API actual probablemente tiene este formato:
```
Hola {{1}}, tienes una reserva en En Las Nubes para el {{2}} a las {{3}}. Confirma respondiendo SÍ o NO.
```

### Solución Propuesta

#### 1. Mejorar Formato del Mensaje

**Nueva plantilla sugerida:**
```
🍽️ *En Las Nubes Restobar*

¡Hola {{1}}! 

📅 *Tu reserva:*
• Fecha: {{2}}
• Hora: {{3}}
• Personas: {{4}}

📍 *Ubicación:*
María Teresa Gil de Gárate 16, Logroño
[Ver en Google Maps](https://maps.google.com/?q=En+Las+Nubes+Restobar+Logroño)

✅ *Para confirmar:* Responde SÍ
❌ *Para cancelar:* Responde NO

¿Necesitas cambiar algo? ¡Responde a este mensaje!
```

#### 2. Link de Google Maps con Preview

Para que WhatsApp muestre preview del mapa, el link debe:
1. Ser un enlace directo a Google Maps
2. Usar el formato correcto: `https://maps.google.com/?q=En+Las+Nubes+Restobar+Logroño`
3. O usar Google Maps Place ID si está disponible

**Opción A:** Link simple con query
```
https://maps.google.com/?q=En+Las+Nubes+Restobar+Logroño
```

**Opción B:** Link con coordenadas (más preciso)
```
https://maps.google.com/?q=42.4654,-2.4456
```

**Opción C:** Short link con preview garantizado
```
https://g.page/en-las-nubes-restobar
```

### Acciones Requeridas
1. **Modificar plantilla en Twilio Content API** - Añadir saltos de línea y formato
2. **Aprobar nueva plantilla** con Meta/Twilio (puede tardar 24-48h)
3. **Actualizar `content_sids.py`** con nuevo SID si es nueva plantilla

---

## 🟡 PRIORIDAD 4: Análisis del Fallo en Modificación por WhatsApp

### Problema Identificado
El usuario respondió al WhatsApp: *"seremos 5 personas y quiero un cachopo sin gluten"* y el sistema NO respondió ni gestionó el cambio.

### Análisis del Flujo Esperado

```
┌─────────────────────────────────────────────────────────────┐
│ FLUJO ESPERADO: MODIFICACIÓN POR WHATSAPP                  │
└─────────────────────────────────────────────────────────────┘

1. Cliente responde WhatsApp
   └─> "seremos 5 personas y quiero un cachopo sin gluten"

2. Twilio Webhook dispara
   └─> POST /twilio/webhook
       Body: {"From": "+34XXX", "Body": "seremos 5 personas..."}

3. RouterAgent clasifica
   └─> ¿intención? 
       - "SÍ"/"NO" → confirmation/cancellation
       - "5 personas" + "cachopo" → update_notes

4. LogicAgent procesa
   ├─> Busca reserva por teléfono
   ├─> Actualiza: personas=5, notas="cachopo sin gluten"
   └─> Responde confirmación

5. HumanAgent genera respuesta
   └─> "¡Apuntado! Sois 5 personas y os guardo lo del cachopo sin gluten..."
```

### Posibles Causas del Fallo

#### Causa 1: Webhook de Twilio NO configurado para mensajes entrantes
- El webhook de Twilio solo está configurado para `status_callback` (entregado/leído)
- NO está configurado para `incoming_message` webhook
- **Solución:** Configurar webhook en Twilio Console para mensajes entrantes

#### Causa 2: RouterAgent no clasificó correctamente
- El mensaje "seremos 5 personas..." no coincide con patrones de `update_notes`
- Se clasificó como `unknown` o `faq` y no se procesó
- **Solución:** Mejorar prompts del RouterAgent para detectar modificaciones

#### Causa 3: LogicAgent no encontró la reserva
- La búsqueda por teléfono falló
- El teléfono del WhatsApp no coincide con el de la reserva
- **Solución:** Mejorar lógica de matching de teléfonos

#### Causa 4: Error silencioso en el procesamiento
- Excepción no capturada que no generó respuesta
- **Solución:** Añadir más logging y manejo de errores

### Diagnóstico Requerido

Para identificar la causa exacta, necesitamos:

1. **Verificar configuración de webhook Twilio:**
   ```bash
   # Revisar si el webhook de mensajes entrantes está configurado
   twilio api:core:phone-numbers:fetch --sid=PN_XXX
   ```

2. **Revisar logs del servidor:**
   ```bash
   # Buscar logs del momento del mensaje
   grep "twilio/webhook" /var/log/verdent.log
   ```

3. **Verificar en Twilio Console:**
   - Ir a Messaging > Settings > WhatsApp sandbox settings
   - Verificar "When a message comes in" URL

### Solución Propuesta

**Paso 1:** Verificar y configurar webhook de mensajes entrantes en Twilio
**Paso 2:** Mejorar RouterAgent para detectar intenciones de modificación
**Paso 3:** Añadir logging detallado en el flujo de WhatsApp
**Paso 4:** Implementar respuesta de fallback para mensajes no clasificados

---

## 🟢 PRIORIDAD 5: Guion de Pruebas Reales

### Objetivo
Diseñar un guion de pruebas para detectar bugs mediante llamadas reales.

### Propuesta de Guion de Pruebas

```markdown
# GUION DE PRUEBAS - ASISTENTE DE VOZ EN LAS NUBES

## Test 1: Reserva Simple (Happy Path)
**Objetivo:** Verificar flujo completo de reserva
**Pasos:**
1. Llamar al número VAPI
2. Decir: "Hola, quiero reservar para 4 personas mañana a las 21:00"
3. Proporcionar nombre y teléfono cuando se solicite
4. Verificar: 
   - Respuesta natural y fluida
   - WhatsApp recibido con formato correcto
   - Reserva creada en Airtable

## Test 2: Reserva en Horario Cerrado
**Objetivo:** Verificar validación de horarios
**Pasos:**
1. Llamar y decir: "Quiero reservar para el lunes a las 14:00"
2. Verificar: Sistema indica que los lunes están cerrados

## Test 3: Modificación por WhatsApp
**Objetivo:** Verificar gestión de cambios
**Pasos:**
1. Después de Test 1, responder al WhatsApp
2. Escribir: "Seremos 5 personas y tenemos alergia al gluten"
3. Verificar: Sistema actualiza la reserva y confirma

## Test 4: Confirmación por WhatsApp
**Objetivo:** Verificar flujo de confirmación
**Pasos:**
1. Responder "SÍ" al WhatsApp de confirmación
2. Verificar: Estado cambia a "Confirmada" en Airtable

## Test 5: Grupo Grande (>11 personas)
**Objetivo:** Verificar derivación a humano
**Pasos:**
1. Llamar y decir: "Somos 15 personas para el sábado"
2. Verificar: Sistema ofrece derivar a humano

## Test 6: Interrupciones
**Objetivo:** Verificar fluidez de conversación
**Pasos:**
1. Llamar y comenzar a decir "Quiero reservar..."
2. Interrumpir a mitad de frase
3. Verificar: Sistema espera a terminar de hablar

## Test 7: Preguntas FAQ
**Objetivo:** Verificar conocimiento del restaurante
**Pasos:**
1. Preguntar: "¿Tenéis parking cerca?"
2. Preguntar: "¿Podemos ir con perro?"
3. Verificar: Respuestas correctas según FAQs

## Test 8: Voz y Tono
**Objetivo:** Verificar calidad de voz
**Pasos:**
1. Escuchar la voz del asistente
2. Verificar: 
   - Voz femenina cálida
   - Español de España neutro
   - Sin acentos extraños
```

---

## 📊 Resumen de Acciones

| # | Prioridad | Acción | Archivo/Config | Estado |
|---|-----------|--------|----------------|--------|
| 1 | 🔴 Alta | Añadir validación horarios en `create_reservation` | `src/api/vapi_tools_router.py` | Pendiente |
| 2 | 🟠 Alta | Cambiar voz a ElevenLabs "Laura" | VAPI Dashboard/API | Pendiente |
| 3 | 🟠 Alta | Configurar parámetros de interrupción | VAPI Dashboard/API | Pendiente |
| 4 | 🟡 Media | Mejorar formato WhatsApp | Twilio Content API | Pendiente |
| 5 | 🟡 Media | Configurar link Google Maps con preview | Twilio Content API | Pendiente |
| 6 | 🟡 Media | Diagnosticar fallo modificación WhatsApp | Logs/Twilio Console | Pendiente |
| 7 | 🟢 Baja | Crear guion de pruebas reales | Documentación | Pendiente |

---

## 🚀 Próximos Pasos

1. **Aprobar este plan** con el usuario
2. **Implementar Prioridad 1** (validación horarios) - Cambios de código
3. **Implementar Prioridad 2** (voz y fluidez) - Cambios en VAPI
4. **Diagnosticar Prioridad 4** (WhatsApp) - Requiere acceso a logs
5. **Ejecutar pruebas** con el guion diseñado

---

**¿Deseas que proceda con la implementación de alguna de estas acciones?**
