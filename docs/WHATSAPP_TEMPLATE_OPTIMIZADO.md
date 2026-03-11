# WhatsApp Template Optimizado - En Las Nubes Restobar

> **Creado:** 2026-03-10  
> **Estado:** Pendiente de envío a Meta (cuando se levante restricción)  
> **Objetivo:** Template corto y compatible con políticas Meta para confirmaciones de reserva

---

## 📋 Especificaciones del Template

### Identificación

| Campo | Valor |
|-------|-------|
| **Nombre** | `reserva_confirmacion_nubes_v2` |
| **Categoría** | `UTILITY` |
| **Idioma** | Spanish (es) |
| **Total caracteres** | < 160 (optimizado para aprobación rápida) |

---

## 📝 Contenido del Template

```
Hola {{1}}, tienes reserva en En Las Nubes para el {{2}} a las {{3}}h.

¿CONFIRMAS?

Responde SÍ o NO.

Gracias!
```

---

## 🔧 Variables Dinámicas

| Variable | Nombre | Formato | Ejemplo |
|----------|--------|---------|---------|
| **{{1}}** | Nombre del cliente | Texto (capitalizado) | `Juan`, `María` |
| **{{2}}** | Fecha de reserva | Texto largo español | `viernes 12 de marzo`, `sábado 20 de mayo` |
| **{{3}}** | Hora de reserva | HH:MM formato 24h | `21:00`, `14:30` |

---

## ✅ Características Optimizadas

### Cumplimiento de Políticas Meta

- ✅ **Longitud:** < 160 caracteres (mejora tasa de aprobación)
- ✅ **Sin URLs:** No incluye links externos (reducen aprobación)
- ✅ **Call-to-Action claro:** "¿CONFIRMAS? Responde SÍ o NO"
- ✅ **Categoría UTILITY:** Uso transaccional (no marketing)
- ✅ **Tono profesional pero cercano:** Marca del restobar

### Ventajas vs Template Anterior

| Aspecto | Template Anterior | Template Nuevo |
|---------|-------------------|----------------|
| **Longitud** | ~200 caracteres | < 160 caracteres |
| **URLs** | Incluía link confirmación | Sin URLs |
| **Call-to-Action** | Poco claro | Explícito "SÍ o NO" |
| **Aprobación estimada** | 3-5 días | 1-2 días |

---

## 🔄 Mapeo de Variables en Código Python

### Implementación en [`twilio_service.py`](../src/infrastructure/external/twilio_service.py)

```python
def send_whatsapp_confirmation(
    self,
    to_number: str,
    customer_name: str,
    date_str: str,  # Formato: "viernes 12 de marzo"
    time_str: str   # Formato: "21:00"
) -> Optional[str]:
    """
    Envía template de confirmación optimizado.
    
    Args:
        to_number: Número WhatsApp del cliente (formato: +34XXXXXXXXX)
        customer_name: Nombre del cliente (ejemplo: "Juan")
        date_str: Fecha en formato largo español (ejemplo: "viernes 12 de marzo")
        time_str: Hora en formato 24h (ejemplo: "21:00")
    
    Returns:
        Message SID si éxito, None si falla
    """
    variables = {
        "1": customer_name,
        "2": date_str,
        "3": time_str
    }
    
    return self.send_whatsapp_template(
        to_number=to_number,
        template_sid="reserva_confirmacion_nubes_v2",
        variables=variables
    )
```

### Ejemplo de Uso Real

```python
# Caso 1: Reserva para 4 personas el viernes 14 de marzo a las 21:00
twilio_service.send_whatsapp_confirmation(
    to_number="+34600123456",
    customer_name="Juan",
    date_str="viernes 14 de marzo",
    time_str="21:00"
)

# Mensaje enviado:
# "Hola Juan, tienes reserva en En Las Nubes para el viernes 14 de marzo a las 21:00h.
#  
#  ¿CONFIRMAS?
#  
#  Responde SÍ o NO.
#  
#  Gracias!"
```

---

## 📤 Proceso de Envío a Meta

### Pasos para Registrar el Template

1. **Acceder a Meta Business Suite**
   - URL: https://business.facebook.com/
   - Login con cuenta business vinculada a WhatsApp

2. **Navegar a WhatsApp Manager**
   - Menú lateral → WhatsApp Business
   - Seleccionar cuenta de "En Las Nubes Restobar"

3. **Crear Nuevo Template**
   - Botón: "Crear plantilla de mensaje"
   - Categoría: **UTILITY** (no MARKETING)
   - Nombre: `reserva_confirmacion_nubes_v2`

4. **Configurar Contenido**
   - Copiar el contenido exacto de arriba
   - Configurar 3 variables:
     - {{1}} → Nombre del cliente (TEXT)
     - {{2}} → Fecha de reserva (TEXT)
     - {{3}} → Hora de reserva (TEXT)

5. **Enviar a Revisión**
   - Esperar aprobación (1-2 días estimado)
   - Meta notificará vía email cuando esté aprobado

6. **Configurar en Código**
   - Una vez aprobado, actualizar [`_format_template_body()`](../src/infrastructure/external/twilio_service.py:78) con el template nuevo
   - Probar con número de prueba antes de producción

---

## ⚠️ Notas Importantes

### Requisitos Previos

- [ ] **Cuenta WhatsApp Business aprobada** (actualmente restringida por Meta)
- [ ] **Número WhatsApp activo** (actualmente usando +358 finlandés temporalmente)
- [ ] **Business Verification completada** (verificar estado en Meta Business Suite)

### Restricciones Actuales

> **BLOQUEADOR CRÍTICO:** La cuenta WhatsApp Business de "En Las Nubes" está **RESTRINGIDA por Meta**. 
> 
> **Causa raíz:** Posible violación de políticas o actividad sospechosa reportada.
> 
> **Acción requerida:** Contactar soporte de Meta Business para levantar restricción ANTES de enviar este template.

### Testing Post-Aprobación

```python
# Script de testing (ejecutar SOLO después de aprobación)
import os
from src.infrastructure.external.twilio_service import twilio_service

# Número de prueba (personal del equipo técnico)
TEST_NUMBER = "+34XXXXXXXXX"  # Reemplazar con número real

# Enviar mensaje de prueba
sid = twilio_service.send_whatsapp_confirmation(
    to_number=TEST_NUMBER,
    customer_name="Equipo Pruebas",
    date_str="lunes 15 de marzo",
    time_str="20:00"
)

if sid:
    print(f"✅ Template enviado correctamente. SID: {sid}")
else:
    print("❌ Error enviando template. Revisar logs.")
```

---

## 📊 Métricas Esperadas

### KPIs Post-Implementación

| Métrica | Objetivo | Tracking |
|---------|----------|----------|
| **Tasa de entrega** | > 95% | Dashboard WhatsApp |
| **Tasa de lectura** | > 80% | Dashboard WhatsApp |
| **Tasa de respuesta** | > 70% | Dashboard interno |
| **Tiempo de respuesta** | < 2 horas | Dashboard interno |
| **Costo por mensaje** | < €0.05 | Factura Twilio |

---

## 🔗 Referencias

- **Políticas Meta WhatsApp:** https://www.whatsapp.com/legal/business-policy/
- **Guía Templates UTILITY:** https://developers.facebook.com/docs/whatsapp/message-templates/guidelines
- **Twilio Content API:** https://www.twilio.com/docs/content/content-api-resources
- **Documentación interna:** [WHATSAPP_CONFIRMACIONES.md](./WHATSAPP_CONFIRMACIONES.md)

---

**Última actualización:** 2026-03-10  
**Responsable:** Equipo Técnico En Las Nubes  
**Estado:** ⏸️ Pendiente de levantamiento de restricción Meta
