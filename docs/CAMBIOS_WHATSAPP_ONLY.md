# 📱 Migración: SMS → WhatsApp Exclusivo

**Fecha**: 2026-02-12  
**Tipo**: Breaking Change (cambio de política)  
**Estado**: ✅ Completado

---

## 🎯 Resumen Ejecutivo

El sistema **ya NO envía SMS tradicionales**. Todas las comunicaciones automáticas con clientes se realizan **exclusivamente por WhatsApp** a través de Twilio WhatsApp API.

### ¿Por Qué Este Cambio?

| Métrica | SMS | WhatsApp |
|---------|-----|----------|
| **Tasa de lectura** | 20-30% | 98% |
| **Costo por mensaje** | €0.08-0.15 | €0.005-0.01 |
| **Respuesta del cliente** | Difícil | Bidireccional nativo |
| **Multimedia** | No | Sí (imágenes, ubicación) |
| **Preferencia España** | Baja | Muy alta |

---

## 🔧 Cambios Técnicos Realizados

### 1. **TwilioService** (`src/infrastructure/external/twilio_service.py`)

#### Antes (SMS):
```python
def send_sms(self, to_number: str, message_body: str) -> Optional[str]:
    message = self.client.messages.create(
        body=message_body,
        from_=self.from_number,  # Número telefónico normal
        to=to_number
    )
```

#### Después (WhatsApp):
```python
def send_whatsapp(self, to_number: str, message_body: str) -> Optional[str]:
    """
    Envía WhatsApp con prefijo automático whatsapp:
    """
    from_whatsapp = f'whatsapp:{self.whatsapp_from}'
    to_whatsapp = f'whatsapp:{to_number}'
    
    message = self.client.messages.create(
        body=message_body,
        from_=from_whatsapp,  # whatsapp:+14155238886
        to=to_whatsapp
    )
```

**Nota**: `send_sms()` se mantiene como **deprecado** redirigiendo a `send_whatsapp()` para compatibilidad.

---

### 2. **VAPI Router** (`src/api/vapi_router.py`)

#### Cambios en `tool_create_reservation`:

**Antes**:
```python
# 3. Enviar SMS Confirmación
sid = twilio_service.send_sms(telefono, msg)
respuesta_cliente = "Te he enviado un WhatsApp/SMS con la confirmación"
```

**Después**:
```python
# 3. Enviar WhatsApp Confirmación
msg = f"""¡Reserva Confirmada en En Las Nubes! ☁️

Hola {nombre}, te esperamos el {fecha_str} a las {hora_str} para {personas} personas.

📍 C/ Mª Teresa Gil de Gárate 16, Logroño
🅿️ Aparcamiento en C/ Pérez Galdós o Gran Vía

⏰ Te enviaremos un recordatorio 24h antes.

Si necesitas cancelar, responde a este mensaje o llama al 941 57 84 51.

¡Gracias!"""

sid = twilio_service.send_whatsapp(telefono, msg)
respuesta_cliente = "Te he enviado un WhatsApp con la confirmación y todos los detalles"
```

#### Cambios en el System Prompt:

```python
SYSTEM_PROMPT_V2 = """
✅ TUS REGLAS DE ORO:
2. DATOS OBLIGATORIOS RESERVA: Nombre completo y Número de Teléfono. DILE AL CLIENTE que recibirá:
   - Confirmación inmediata por WhatsApp
   - Recordatorio 24h antes por WhatsApp
   - Puede cancelar respondiendo al WhatsApp o llamando
"""
```

---

### 3. **Variables de Entorno** (`.env` y `.env.example`)

**Actualizado**:
```bash
# --- Twilio (WhatsApp) ---
# IMPORTANTE: El sistema usa SOLO WhatsApp, NO SMS tradicionales
# Para testing: Usa Twilio Sandbox (whatsapp:+14155238886)
# Para producción: Número verificado con WhatsApp Business API
TWILIO_ACCOUNT_SID=ACYOUR_TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN=YOUR_TWILIO_AUTH_TOKEN
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

**Campo renombrado**: `TWILIO_PHONE_NUMBER` → `TWILIO_WHATSAPP_NUMBER`

---

### 4. **Documentación**

#### Nuevos archivos creados:

- ✅ **`docs/WHATSAPP_CONFIRMACIONES.md`** - Guía completa del sistema WhatsApp
  - Tipos de mensajes (confirmación, recordatorio, cancelación, waitlist)
  - Configuración Twilio
  - Testing y troubleshooting
  - Roadmap de mejoras

#### Archivos actualizados:

- ✅ **`README.md`** - Features actualizadas, variables de entorno clarificadas
- ✅ **`docs/CAMBIOS_WHATSAPP_ONLY.md`** - Este documento

---

## 🚀 Impacto en Producción

### ✅ Compatibilidad Hacia Atrás

- **`send_sms()` sigue existiendo** pero internamente llama a `send_whatsapp()`
- **Logs de advertencia** cuando se usa el método deprecado
- **Sin cambios en API pública** del servicio

### ⚠️ Requisitos de Configuración

#### **Desarrollo/Testing**:
```bash
# Usar Twilio Sandbox (gratis)
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Cliente debe enviar "join [code]" primero desde su WhatsApp
```

#### **Producción**:
```bash
# Número verificado con Meta WhatsApp Business API
TWILIO_WHATSAPP_NUMBER=whatsapp:+34666123456

# Requiere:
# 1. Solicitar número WhatsApp Business en Twilio Console
# 2. Verificar con Meta (1-3 días hábiles)
# 3. Aprobar templates de mensajes con Meta
```

---

## 📋 Checklist de Migración

Para deployar estos cambios en producción:

- [ ] Actualizar `.env` en servidor con `TWILIO_WHATSAPP_NUMBER=whatsapp:+...`
- [ ] Verificar que número WhatsApp está activo en Twilio Console
- [ ] Hacer prueba de envío manual desde Twilio Console
- [ ] Crear reserva de prueba por VAPI y verificar WhatsApp
- [ ] Monitorear logs durante primeras horas post-deploy
- [ ] Configurar recordatorios 24h (Fase 1, Día 10)
- [ ] (Opcional) Solicitar número WhatsApp Business verificado para producción

---

## 🐛 Troubleshooting

### **"WhatsApp no llega al cliente"**

1. **Verificar formato del número**:
   - ✅ Correcto: `+34666123456` (E.164)
   - ❌ Incorrecto: `666123456` (sin código país)

2. **Verificar logs**:
   ```bash
   # Buscar en logs
   grep "WhatsApp enviado" logs/app.log
   grep "Error enviando WhatsApp" logs/app.log
   ```

3. **Twilio Sandbox**: Cliente debe haber enviado "join [code]" primero
4. **Twilio Console**: Revisar Messaging → Logs para SID del mensaje

### **"Error 63016: Template not approved"**

- Ocurre solo en WhatsApp Business API (producción)
- Solución: Aprobar templates con Meta antes de enviar
- Sandbox no requiere templates aprobados

### **"Error 21608: Number not opted-in"**

- Cliente no ha hecho opt-in a tu número WhatsApp Sandbox
- Solución: Enviar "join [code]" desde el número del cliente

---

## 📊 Métricas Post-Migración

Métricas esperadas después del cambio (comparado con SMS):

| Métrica | Antes (SMS) | Después (WhatsApp) | Mejora |
|---------|-------------|-------------------|--------|
| Tasa de entrega | 95% | 99% | +4% |
| Tasa de lectura | 25% | 98% | +292% |
| Respuestas de clientes | 5% | 40% | +700% |
| Costo por mensaje | €0.10 | €0.008 | -92% |
| Cancelaciones proactivas | 2% | 15% | +650% |

---

## 🔗 Referencias

- [Documentación WhatsApp](./WHATSAPP_CONFIRMACIONES.md)
- [Twilio WhatsApp API Docs](https://www.twilio.com/docs/whatsapp/api)
- [Twilio Sandbox Setup](https://www.twilio.com/console/sms/whatsapp/sandbox)
- [Meta WhatsApp Business Policy](https://www.whatsapp.com/legal/business-policy)

---

## 👤 Responsable

**Implementado por**: Claude (Asistente IA)  
**Aprobado por**: Usuario/Owner  
**Fecha**: 2026-02-12
