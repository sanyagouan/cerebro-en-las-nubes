# 📱 Sistema de Confirmaciones y Recordatorios por WhatsApp

## 🎯 Visión General

**POLÍTICA OFICIAL**: Todo el sistema de notificaciones usa **exclusivamente WhatsApp**. No se envían SMS tradicionales.

### ¿Por Qué WhatsApp?

1. **Mayor tasa de lectura** - 98% vs 20% de SMS
2. **Multimedia** - Podemos enviar imágenes, ubicación, mapas
3. **Bidireccional** - Cliente puede responder para cancelar
4. **Sin costo adicional** - Twilio WhatsApp más económico que SMS
5. **Preferencia del mercado español** - WhatsApp es el estándar

---

## 📨 Tipos de Mensajes WhatsApp

### 1. Confirmación Inmediata (Post-Reserva)

**Trigger**: Inmediatamente después de crear una reserva por voz o web

**Contenido**:
```
¡Reserva Confirmada en En Las Nubes! ☁️

Hola [NOMBRE], te esperamos el [FECHA] a las [HORA] para [PAX] personas.

📍 C/ Mª Teresa Gil de Gárate 16, Logroño
🅿️ Aparcamiento en C/ Pérez Galdós o Gran Vía

⏰ Te enviaremos un recordatorio 24h antes.

Si necesitas cancelar, responde a este mensaje o llama al 941 57 84 51.

¡Gracias!
```

**Implementación**: `TwilioService.send_whatsapp()`

---

### 2. Recordatorio 24h Antes

**Trigger**: Cron job a las 10:00 AM, revisa reservas para mañana

**Contenido**:
```
🔔 Recordatorio - En Las Nubes ☁️

Hola [NOMBRE], te recordamos tu reserva:

📅 Mañana [FECHA] a las [HORA]
👥 [PAX] personas
📍 C/ Mª Teresa Gil de Gárate 16

🅿️ Recuerda: La calle es peatonal. Aparca en C/ Pérez Galdós o Gran Vía.

¿Necesitas cancelar? Responde a este mensaje o llama al 941 57 84 51.

¡Te esperamos! 🍽️
```

**Implementación**: `src/application/jobs/reminder_job.py` (Fase 1, Día 10)

---

### 3. Confirmación de Cancelación

**Trigger**: Cuando el cliente cancela por voz, web o responde al WhatsApp

**Contenido**:
```
✅ Cancelación Confirmada

Hola [NOMBRE], tu reserva para [FECHA] a las [HORA] ha sido cancelada.

Si cambias de opinión o quieres hacer otra reserva, llámanos al 941 57 84 51.

¡Hasta pronto! - En Las Nubes Resto Bar ☁️
```

---

### 4. Notificación de Mesa Disponible (Waitlist)

**Trigger**: Cuando se libera una mesa para un cliente en lista de espera

**Contenido**:
```
🎉 ¡Mesa Disponible!

Hola [NOMBRE], tenemos una mesa disponible para [PAX] personas el [FECHA] a las [HORA].

¿La quieres? Responde SÍ para confirmar o llámanos al 941 57 84 51.

⏰ Reserva disponible por 15 minutos.

- En Las Nubes Resto Bar
```

**Implementación**: `WaitlistService.notify_available()` (Fase 1, Días 8-9)

---

## 🔧 Integración Técnica

### Configuración Twilio

**Variables de Entorno** (`.env`):
```bash
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### Formato de Números

- **Entrada del cliente**: `+34666123456` (E.164)
- **Procesado interno**: `whatsapp:+34666123456` (prefijo Twilio)
- **TwilioService se encarga automáticamente** del prefijo

### Código Base

```python
# src/infrastructure/external/twilio_service.py
class TwilioService:
    def send_whatsapp(self, to_number: str, message_body: str) -> Optional[str]:
        """
        Envía WhatsApp. Añade prefijo whatsapp: automáticamente.
        
        Args:
            to_number: +34666123456
            message_body: Texto del mensaje
        
        Returns:
            SID del mensaje o None si falla
        """
```

---

## 📊 Monitoreo y Analytics

### Métricas Clave

1. **Tasa de entrega** - % de WhatsApp entregados vs enviados
2. **Tasa de lectura** - % de mensajes leídos (vía Twilio callbacks)
3. **Tasa de respuesta** - % de clientes que responden
4. **Cancelaciones vía WhatsApp** - % que cancelan respondiendo

### Logs

```python
logger.info(f"WhatsApp confirmación enviado a {telefono}: SID {message.sid}")
logger.error(f"Error enviando WhatsApp: {error}")
```

---

## 🚀 Roadmap de Mejoras

### Fase 1 (MVP)
- ✅ Confirmación inmediata post-reserva
- ⏳ Recordatorio 24h antes (Día 10)
- ⏳ Confirmación de cancelación
- ⏳ Notificación de waitlist

### Fase 2 (Avanzado)
- [ ] **Templates aprobados** - Plantillas pre-aprobadas por Meta
- [ ] **Mensajes multimedia** - Enviar mapa de ubicación, foto del restaurante
- [ ] **Respuestas automáticas** - Chatbot para preguntas frecuentes
- [ ] **Reconfirmación 2h antes** - "¿Sigues viniendo?"

### Fase 3 (Pro)
- [ ] **WhatsApp Business API** - Migrar de Twilio Sandbox a API oficial
- [ ] **Catálogo de productos** - Menú del día, carta interactiva
- [ ] **Pago por WhatsApp** - Reservas con prepago
- [ ] **Encuestas post-comida** - "¿Cómo estuvo tu experiencia?"

---

## 🔒 Seguridad y Privacidad

### RGPD / Protección de Datos

1. **Consentimiento explícito** - Cliente da su teléfono voluntariamente
2. **Opt-out fácil** - Puede responder STOP o llamar para darse de baja
3. **Uso limitado** - Solo notificaciones de reservas, no marketing masivo
4. **Almacenamiento seguro** - Números encriptados en Airtable

### Límites de Rate

- **Twilio Sandbox**: 10 mensajes/segundo
- **WhatsApp Business API**: 1000 mensajes/segundo (requiere aprobación Meta)

---

## 🧪 Testing

### Modo Mock (Sin Twilio)

Si `TWILIO_ACCOUNT_SID` no está configurado:

```python
logger.warning(f"Mocking WhatsApp to {to_number}: {message_body}")
return "MOCK_WHATSAPP_SID_12345"
```

### Testing Manual

1. Crear reserva por VAPI
2. Verificar que llega WhatsApp de confirmación
3. Responder "CANCELAR" → Verificar cancelación
4. Esperar 24h → Verificar recordatorio (o forzar cron)

### Testing Automatizado

```python
# tests/test_whatsapp_flow.py
async def test_reservation_sends_whatsapp():
    with patch('twilio_service.send_whatsapp') as mock_wa:
        mock_wa.return_value = "SID123"
        
        await create_reservation(...)
        
        mock_wa.assert_called_once()
        assert "+34666123456" in mock_wa.call_args[0][0]
```

---

## 📞 Soporte

**Problemas comunes**:

1. **"WhatsApp no llega"**
   - Verificar que número empieza con `+` (E.164)
   - Revisar logs de Twilio Console
   - Verificar que cliente tiene WhatsApp instalado

2. **"Error 63016"** - Template no aprobado
   - Usar Twilio Sandbox para testing
   - Para producción, aprobar templates con Meta

3. **"Error 21608"** - Número no opt-in
   - En Sandbox, cliente debe enviar "join [code]" primero
   - En Business API, no aplica

**Contacto Técnico**: 
- Logs: Twilio Console → Messaging → Logs
- Soporte Twilio: https://support.twilio.com

---

## 📚 Referencias

- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp/api)
- [WhatsApp Business Policy](https://www.whatsapp.com/legal/business-policy)
- [Twilio Sandbox Setup](https://www.twilio.com/console/sms/whatsapp/sandbox)
- [Meta WhatsApp Templates](https://developers.facebook.com/docs/whatsapp/message-templates)
