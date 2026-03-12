# Plan Completo: Plantillas WhatsApp Meta-Compliant

> **Fecha:** 2026-03-12  
> **Estado:** Pendiente de aprobación  
> **Problema:** Error 63016 - Outside Allowed Window and Missing Pre-Registered Template

---

## 📋 Resumen Ejecutivo

### Problema Identificado

Los mensajes de WhatsApp están fallando con **Error 63016** porque:

1. **No hay plantillas aprobadas** en Meta Business Suite (o las existentes son incorrectas)
2. **El código NO usa Content API correctamente** - usa `body=` en lugar de `content_sid=`
3. **Las plantillas locales son demasiado largas** y contienen URLs (no permitidas en UTILITY)

### Solución Propuesta

1. ✅ Diseñar **4 plantillas Meta-compliant** (cortas, sin URLs, variables `{{1}}`)
2. ✅ Registrarlas en **Meta Business Suite** → Twilio Content Library
3. ✅ Actualizar código para usar **`content_sid`** y **`content_variables`**
4. ✅ Eliminar plantillas antiguas ineficientes

---

## 🎯 Plantillas Necesarias

### Análisis de Casos de Uso

| # | Caso de Uso | Cuándo se Envía | Template Actual | Problema |
|---|-------------|-----------------|-----------------|----------|
| 1 | **Confirmación Inmediata** | Al crear reserva | `confirmacion_reserva_template()` | Muy largo, con URL |
| 2 | **Recordatorio 24h** | 24h antes | `recordatorio_24h_template()` | Muy largo, con URL |
| 3 | **Cancelación** | Al cancelar reserva | `cancelacion_reserva_template()` | Aceptable |
| 4 | **Mesa Disponible** | Cuando hay cancelación | No existe | Falta crear |
| 5 | **Reconfirmación Éxito** | Cliente confirma | Mensaje simple inline | OK |
| 6 | **Feedback Post-Visita** | Después de visita | `post_visit_feedback_template()` | MARKETING (no UTILITY) |

### Plantillas a Crear

#### 1. `reserva_confirmacion` (UTILITY)

**Propósito:** Solicitar confirmación inmediata tras crear reserva

```
Nombre: reserva_confirmacion
Categoría: UTILITY
Idioma: Spanish (es)
```

**Contenido:**
```
Hola {{1}}, tienes reserva en En Las Nubes para el {{2}} a las {{3}}h. ¿CONFIRMAS? Responde SÍ o NO. Gracias!
```

**Variables:**
| Variable | Contenido | Ejemplo |
|----------|-----------|---------|
| `{{1}}` | Nombre cliente | "Juan" |
| `{{2}}` | Fecha formateada | "miércoles 12" |
| `{{3}}` | Hora | "21:00" |

**Longitud:** 108 caracteres ✅ (óptimo <160)

---

#### 2. `reserva_recordatorio` (UTILITY)

**Propósito:** Recordar 24 horas antes

```
Nombre: reserva_recordatorio
Categoría: UTILITY
Idioma: Spanish (es)
```

**Contenido:**
```
¡Hola {{1}}! Te esperamos MAÑANA {{2}} a las {{3}}h para {{4}} personas. ¿Todo listo? Responde SÍ para confirmar.
```

**Variables:**
| Variable | Contenido | Ejemplo |
|----------|-----------|---------|
| `{{1}}` | Nombre cliente | "Juan" |
| `{{2}}` | Fecha | "miércoles 12" |
| `{{3}}` | Hora | "21:00" |
| `{{4}}` | Número personas | "4" |

**Longitud:** 115 caracteres ✅

---

#### 3. `reserva_cancelada` (UTILITY)

**Propósito:** Confirmar cancelación de reserva

```
Nombre: reserva_cancelada
Categoría: UTILITY
Idioma: Spanish (es)
```

**Contenido:**
```
{{1}}, tu reserva del {{2}} a las {{3}}h ha sido cancelada. ¿Quieres hacer otra? Llámanos: 941 57 84 51
```

**Variables:**
| Variable | Contenido | Ejemplo |
|----------|-----------|---------|
| `{{1}}` | Nombre cliente | "Juan" |
| `{{2}}` | Fecha | "miércoles 12" |
| `{{3}}` | Hora | "21:00" |

**Longitud:** 106 caracteres ✅

---

#### 4. `mesa_disponible` (UTILITY)

**Propósito:** Notificar a clientes en lista de espera cuando hay mesa libre

```
Nombre: mesa_disponible
Categoría: UTILITY
Idioma: Spanish (es)
```

**Contenido:**
```
¡{{1}}! Se ha liberado mesa para {{2}} personas el {{3}} a las {{4}}h. ¿Te viene bien? Responde SÍ o NO.
```

**Variables:**
| Variable | Contenido | Ejemplo |
|----------|-----------|---------|
| `{{1}}` | Nombre cliente | "Juan" |
| `{{2}}` | Número personas | "4" |
| `{{3}}` | Fecha | "miércoles 12" |
| `{{4}}` | Hora | "21:00" |

**Longitud:** 110 caracteres ✅

---

## 🔧 Cambios de Código Necesarios

### 1. Actualizar `twilio_service.py`

**Ubicación:** `src/infrastructure/external/twilio_service.py`

**Cambio Crítico en `send_whatsapp_template()` (líneas 55-85):**

```python
# ❌ ANTES (INCORRECTO - No usa Content API)
def send_whatsapp_template(
    self, to_number: str, template_sid: str, variables: Dict[str, str]
) -> Optional[str]:
    message = self.client.messages.create(
        from_=self.whatsapp_from,
        body=self._format_template_body(template_sid, variables),  # WRONG!
        to=to_formatted
    )

# ✅ DESPUÉS (CORRECTO - Usa Content API)
def send_whatsapp_template(
    self, to_number: str, content_sid: str, variables: Dict[str, str]
) -> Optional[str]:
    """
    Envía mensaje usando plantilla aprobada de Twilio Content API.
    
    Args:
        to_number: Número del cliente (formato +34XXXXXXXXX)
        content_sid: SID de la plantilla en Twilio Content Library (HX...)
        variables: Diccionario de variables {"1": "Juan", "2": "miércoles 12"}
    
    Returns:
        Message SID si éxito, None si error
    """
    import json
    
    if not self.client:
        logger.error("Twilio client not initialized")
        return None
    
    try:
        to_formatted = self._format_phone_number(to_number)
        
        message = self.client.messages.create(
            from_=self.whatsapp_from,
            content_sid=content_sid,  # ✅ CORRECTO - ID de la plantilla aprobada
            content_variables=json.dumps(variables),  # ✅ CORRECTO - Variables como JSON string
            to=to_formatted
        )
        
        logger.info(f"✅ Template message sent: {message.sid}")
        return message.sid
        
    except Exception as e:
        logger.error(f"❌ Error sending template: {e}")
        return None
```

### 2. Crear Mapeo de Content SIDs

**Nuevo archivo:** `src/infrastructure/templates/content_sids.py`

```python
"""
Mapeo de Content SIDs de Twilio para plantillas WhatsApp.
Estos SIDs se obtienen del Twilio Console > Content Library después de aprobar las plantillas.
"""

import os

# Content SIDs para plantillas aprobadas
# Reemplazar con los SIDs reales después de aprobación en Twilio

CONTENT_SIDS = {
    "confirmacion": os.getenv("TWILIO_CONTENT_SID_CONFIRMACION", "HXxxxxxxxx"),  # Pendiente
    "recordatorio": os.getenv("TWILIO_CONTENT_SID_RECORDATORIO", "HXxxxxxxxx"),  # Pendiente
    "cancelacion": os.getenv("TWILIO_CONTENT_SID_CANCELACION", "HXxxxxxxxx"),    # Pendiente
    "mesa_disponible": os.getenv("TWILIO_CONTENT_SID_MESA_DISPONIBLE", "HXxxxxxxxx"),  # Pendiente
}

def get_content_sid(template_name: str) -> str:
    """Obtiene el Content SID para una plantilla."""
    sid = CONTENT_SIDS.get(template_name)
    if not sid or sid.startswith("HXxx"):
        raise ValueError(f"Content SID no configurado para: {template_name}")
    return sid
```

### 3. Actualizar `whatsapp_service.py`

**Ubicación:** `src/infrastructure/services/whatsapp_service.py`

```python
from src.infrastructure.templates.content_sids import get_content_sid

class WhatsAppService:
    
    def send_confirmation_request(
        self, 
        to_number: str, 
        nombre: str, 
        fecha_str: str, 
        hora_str: str
    ) -> bool:
        """
        Envía solicitud de confirmación usando plantilla aprobada.
        
        Args:
            to_number: Teléfono del cliente
            nombre: Nombre del cliente
            fecha_str: Fecha formateada (ej: "miércoles 12")
            hora_str: Hora formateada (ej: "21:00")
        """
        try:
            content_sid = get_content_sid("confirmacion")
            variables = {
                "1": nombre,
                "2": fecha_str,
                "3": hora_str
            }
            
            # Usar twilio_service.send_whatsapp_template()
            result = self.twilio_service.send_whatsapp_template(
                to_number=to_number,
                content_sid=content_sid,
                variables=variables
            )
            
            return result is not None
            
        except Exception as e:
            logger.error(f"Error sending confirmation: {e}")
            return False
```

### 4. Variables de Entorno Requeridas

**Agregar a `.env` y Coolify:**

```bash
# Twilio Content SIDs (obtener de Twilio Console > Content Library)
TWILIO_CONTENT_SID_CONFIRMACION=HXxxxxxxxxxxxxxxxx
TWILIO_CONTENT_SID_RECORDATORIO=HXxxxxxxxxxxxxxxxx
TWILIO_CONTENT_SID_CANCELACION=HXxxxxxxxxxxxxxxxx
TWILIO_CONTENT_SID_MESA_DISPONIBLE=HXxxxxxxxxxxxxxxxx
```

---

## 📝 Guía Paso a Paso para el Usuario

### Paso 1: Acceder a Meta Business Suite

1. Ir a [Meta Business Suite](https://business.facebook.com/)
2. Seleccionar el negocio correcto (En Las Nubes Restobar)
3. Navegar a: **Configuración** → **Cuentas de WhatsApp** → **Plantillas de mensajes**

### Paso 2: Eliminar Plantillas Antiguas

1. Revisar plantillas existentes
2. Eliminar cualquier plantilla que:
   - Tenga URLs
   - Sea muy larga (>200 caracteres)
   - Sea categoría MARKETING (necesitamos UTILITY)
   - No siga el formato de variables `{{1}}`

### Paso 3: Crear Nueva Plantilla de Confirmación

1. Clic en **Crear plantilla**
2. Configurar:
   - **Nombre:** `reserva_confirmacion`
   - **Categoría:** UTILITY (¡importante!)
   - **Idioma:** Spanish (es)
3. Contenido del cuerpo:
   ```
   Hola {{1}}, tienes reserva en En Las Nubes para el {{2}} a las {{3}}h. ¿CONFIRMAS? Responde SÍ o NO. Gracias!
   ```
4. **NO agregar botones** (por ahora, para simplificar aprobación)
5. Clic en **Enviar para revisión**

### Paso 4: Crear Resto de Plantillas

Repetir el proceso para:

| Plantilla | Contenido |
|-----------|-----------|
| `reserva_recordatorio` | `¡Hola {{1}}! Te esperamos MAÑANA {{2}} a las {{3}}h para {{4}} personas. ¿Todo listo? Responde SÍ para confirmar.` |
| `reserva_cancelada` | `{{1}}, tu reserva del {{2}} a las {{3}}h ha sido cancelada. ¿Quieres hacer otra? Llámanos: 941 57 84 51` |
| `mesa_disponible` | `¡{{1}}! Se ha liberado mesa para {{2}} personas el {{3}} a las {{4}}h. ¿Te viene bien? Responde SÍ o NO.` |

### Paso 5: Esperar Aprobación

- Meta suele aprobar plantillas UTILITY en **24-48 horas**
- Recibirás notificación por email cuando estén aprobadas

### Paso 6: Obtener Content SIDs de Twilio

1. Ir a [Twilio Console](https://console.twilio.com/)
2. Navegar a: **Content** → **Content Library**
3. Las plantillas aprobadas aparecerán automáticamente
4. Copiar el **Content SID** de cada plantilla (formato: `HXxxxxxxxx`)
5. Actualizar variables de entorno con los SIDs

### Paso 7: Verificar en Twilio Console

```bash
# Test rápido via Twilio CLI
twilio api:core:messages:create \
  --from whatsapp:+14155238886 \
  --to whatsapp:+34XXXXXXXXX \
  --content-sid HXxxxxxxxx \
  --content-variables '{"1":"Juan","2":"miércoles 12","3":"21:00"}'
```

---

## 📊 Comparativa: Antes vs Después

| Aspecto | Antes | Después |
|---------|-------|---------|
| **Longitud mensaje** | 500+ caracteres | 100-115 caracteres |
| **URLs** | Incluía Google Maps | Sin URLs |
| **Formato variables** | `{nombre}` | `{{1}}` (Meta-compliant) |
| **API usada** | `body=` (regular message) | `content_sid=` (Content API) |
| **Categoría** | Sin categoría | UTILITY |
| **Aprobación Meta** | No aprobadas | Aprobadas |
| **Error 63016** | ❌ Sí | ✅ No |

---

## ✅ Checklist de Implementación

### Fase 1: Crear Plantillas (Usuario)
- [ ] Acceder a Meta Business Suite
- [ ] Eliminar plantillas antiguas ineficientes
- [ ] Crear `reserva_confirmacion`
- [ ] Crear `reserva_recordatorio`
- [ ] Crear `reserva_cancelada`
- [ ] Crear `mesa_disponible`
- [ ] Esperar aprobación (24-48h)

### Fase 2: Obtener SIDs (Usuario)
- [ ] Ir a Twilio Console → Content Library
- [ ] Copiar Content SID de cada plantilla
- [ ] Proporcionar SIDs al equipo de desarrollo

### Fase 3: Actualizar Código (Desarrollo)
- [ ] Actualizar `twilio_service.py` - usar `content_sid`
- [ ] Crear `content_sids.py` con mapeo
- [ ] Actualizar `whatsapp_service.py`
- [ ] Actualizar `scheduler_service.py`
- [ ] Actualizar `vapi_tools_router.py`
- [ ] Agregar variables de entorno a Coolify

### Fase 4: Testing
- [ ] Test unitario de `send_whatsapp_template()`
- [ ] Test de integración con número real
- [ ] Verificar que no hay Error 63016
- [ ] Deploy a producción

---

## 🚨 Notas Importantes

1. **NO usar URLs en plantillas UTILITY** - Meta las rechaza
2. **Mantener mensajes cortos** - <160 caracteres ideal
3. **Variables numéricas** - Usar `{{1}}`, `{{2}}`, NO `{{nombre}}`
4. **Categoría correcta** - UTILITY para mensajes transaccionales
5. **Esperar aprobación** - No intentar enviar hasta que Meta apruebe

---

## 📞 Contacto y Soporte

Si tienes dudas durante el proceso de creación de plantillas:
- **Meta Business Help:** https://www.facebook.com/business/help
- **Twilio Docs:** https://www.twilio.com/docs/whatsapp

---

**Próximo paso:** El usuario debe crear las plantillas en Meta Business Suite y proporcionar los Content SIDs cuando estén aprobados.
