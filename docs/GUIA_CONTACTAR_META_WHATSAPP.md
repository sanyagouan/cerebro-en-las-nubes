# Guía para Contactar Meta y Levantar Restricción WhatsApp Business

## Situación Actual

**Cuenta WhatsApp Business:** RESTRINGIDA  
**Business Account ID:** `1437289745941886`  
**Número afectado:** +358454910405 (Finlandia, temporal)  
**Fecha detección:** 10 de marzo de 2026

### Evidencia del Problema

- 100% de mensajes WhatsApp fallidos (error 63016)
- Estado en Meta Business Suite: "RESTRICTED"
- Causa probable: Tests técnicos durante desarrollo detectados como actividad sospechosa

### Causa Probable

Tests técnicos realizados durante el desarrollo del sistema de reservas fueron detectados como actividad sospechosa por los sistemas automatizados de Meta.

---

## Opción A: Meta Business Suite (Recomendada)

### Paso 1: Acceder a Meta Business Suite

1. Ir a: https://business.facebook.com
2. Iniciar sesión con las credenciales del negocio
3. Seleccionar **"En Las Nubes Restobar"**

### Paso 2: Buscar Notificaciones

1. Click en el icono de campana (🔔 notificaciones) en la esquina superior derecha
2. Buscar alertas relacionadas con **WhatsApp Business Account**
3. Si hay una notificación de restricción, click en **"Review"** o **"Revisar"**

### Paso 3: Seguir el Proceso de Apelación

Si aparece opción de apelación:

1. Click en **"Appeal"** o **"Apelar"**
2. Completar el formulario con:
   - **Tipo de negocio:** Restaurante
   - **Descripción:** "Restaurante legítimo en Logroño, España. Sistema de reservas automatizado en desarrollo."
   - **Documentación adjunta (si se solicita):** licencia comercial, carta del menú, página web
3. Enviar y esperar respuesta (**24-72 horas**)

---

## Opción B: Soporte Directo (Si Opción A no funciona)

### Paso 1: Acceder al Portal de Soporte

1. Ir a: https://business.facebook.com/direct-support
2. Click en **"Contact Support"** o **"Contactar Soporte"**

### Paso 2: Seleccionar Tipo de Problema

1. **Categoría:** "WhatsApp Business"
2. **Subcategoría:** "Account Restriction" o "Restricción de Cuenta"
3. **Prioridad:** "High" o "Alta"

### Paso 3: Completar el Formulario

**Asunto:** Request to Review WhatsApp Business Account Restriction - Legitimate Restaurant

**Descripción sugerida (copiar y pegar tal cual):**

```
Dear Meta Business Support Team,

I am writing to request a review of the restriction placed on our WhatsApp Business Account (ID: 1437289745941886).

BUSINESS INFORMATION:
- Business Name: En Las Nubes Restobar
- Business Type: Restaurant (Restobar)
- Location: Logroño, La Rioja, Spain
- Contact: +34 941 123 456 (restaurant phone)

REASON FOR RESTRICTION APPEAL:
We believe the restriction was triggered by automated testing of our new reservation system. We are a legitimate restaurant implementing a voice assistant for table reservations, and the test messages sent during development were flagged as suspicious activity.

WHAT WE ARE DOING:
1. We have stopped all automated testing
2. We are using a temporary Finnish number (+358454910405) for development
3. We plan to purchase a Spanish number once the system is stable
4. Our system will only send confirmation messages to real customers who make reservations

REQUEST:
We kindly ask you to review our account and lift the restriction. We are happy to provide any documentation needed to verify our legitimacy as a business (business license, menu, photos of the establishment, etc.).

We are committed to following all WhatsApp Business policies and will ensure our messaging practices comply with your guidelines.

Thank you for your time and assistance.

Best regards,
[Tu Nombre]
Owner/Manager, En Las Nubes Restobar
[Tu Email]
[Tu Teléfono]
```

### Paso 4: Adjuntar Documentación (Opcional pero Recomendado)

Si tienes estos documentos, adjúntalos para acelerar el proceso:

- [ ] Licencia comercial o CIF/NIF
- [ ] Carta del menú (PDF)
- [ ] Fotos del local
- [ ] Captura de pantalla de Google Maps del negocio
- [ ] Cualquier otra prueba de actividad comercial legítima

### Paso 5: Enviar y Esperar

- **Tiempo de respuesta típico:** 24-72 horas
- Recibirás una notificación por **email** cuando Meta responda
- Revisa también la sección "Support" en Meta Business Suite

---

## Opción C: WhatsApp Manager Directo

### Paso 1: Acceder a WhatsApp Manager

1. Ir a: https://business.facebook.com/wa/manage/phones/
2. Seleccionar el número afectado: **+358454910405**

### Paso 2: Revisar Estado del Número

1. Buscar sección **"Quality Rating"** o **"Calidad"**
2. Si muestra **"Restricted"** o **"Restringido"**:
3. Click en **"Learn More"** o **"Más información"**
4. Seguir instrucciones para apelación

### Paso 3: Verificar Templates

1. Ir a: https://business.facebook.com/wa/manage/message-templates/
2. Buscar template `reserva_confirmacion_nubes`
3. Verificar estado:
   - ✅ **APPROVED:** Template está bien, el problema es solo la cuenta
   - ⏳ **PENDING:** Esperar aprobación antes de contactar soporte
   - ❌ **REJECTED:** Crear nuevo template sin URLs externas

---

## Qué Hacer Mientras Esperas

### 1. No Envíes Más Mensajes de Prueba

Mientras la cuenta está restringida, cualquier intento de enviar mensajes fallará y podría **empeorar la situación** (más señales de spam).

### 2. Prepara Documentación

Ten a mano:
- Licencia comercial
- CIF/NIF
- Fotos del local
- Carta del menú
- Google Maps listing del restaurante

### 3. El Sistema Funciona Sin WhatsApp

El sistema está diseñado para funcionar incluso si WhatsApp falla:
- **Móviles:** Confirmación verbal durante la llamada (igual que fijos)
- **Fijos:** Confirmación verbal (ya implementado con `confirm_verbal`)
- **Dashboard:** El staff puede ver todas las reservas y confirmar manualmente

### 4. Alternativas si Meta Tarda Más de 1 Semana

- Usar **SMS** (Twilio) como backup para confirmaciones
- Ver [`docs/INVESTIGACION_NUMEROS_ESPANOLES_TWILIO.md`](docs/INVESTIGACION_NUMEROS_ESPANOLES_TWILIO.md) para proveedores alternativos
- Contactar a Twilio para obtener un número español con WhatsApp Business habilitado

---

## Después de que Meta Levante la Restricción

### 1. Verificar Estado

1. Ir a Meta Business Suite
2. Verificar que el estado cambió a **"Active"** o **"Activo"**
3. Probar enviando **1 mensaje de prueba** a tu propio móvil

### 2. Usar el Template Optimizado

Ver detalles completos en [`docs/WHATSAPP_TEMPLATE_OPTIMIZADO.md`](docs/WHATSAPP_TEMPLATE_OPTIMIZADO.md).

Template recomendado:
```
Hola {{1}}! Reserva confirmada en En Las Nubes para {{2}} personas el {{3}} a las {{4}}. ¿Necesitas cambiar algo? Llámanos al 941 123 456.
```

### 3. Testing Gradual (IMPORTANTE)

Para no volver a activar los filtros de spam de Meta:

| Día | Máximo mensajes | Notas |
|-----|----------------|-------|
| Día 1 | 5 mensajes | Solo a amigos/familia |
| Día 2 | 10 mensajes | Mezcla de conocidos y clientes reales |
| Día 3+ | Normal | Uso con clientes reales |

### 4. Monitorear Quality Rating

En **WhatsApp Manager**, verificar que el rating no baje de **"High"** o **"Alto"**. Si baja, reducir volumen de envíos.

---

## Checklist Antes de Contactar a Meta

Antes de abrir el ticket de soporte, verifica:

- [ ] Tienes acceso a Meta Business Suite como **administrador**
- [ ] Tienes la documentación del negocio lista
- [ ] Has dejado de enviar mensajes de prueba
- [ ] Has leído esta guía completa
- [ ] Tienes disponibilidad para esperar respuesta (24-72h)
- [ ] Tienes el **Business Account ID** a mano: `1437289745941886`

---

## Contactos y Recursos Útiles

| Recurso | URL |
|---------|-----|
| **Meta Business Help** | https://www.facebook.com/business/help |
| **WhatsApp Business API Docs** | https://developers.facebook.com/docs/whatsapp |
| **Meta Direct Support** | https://business.facebook.com/direct-support |
| **WhatsApp Manager** | https://business.facebook.com/wa/manage/phones/ |
| **Twilio Support** | https://support.twilio.com |

---

**¡Buena suerte!** Siguiendo estos pasos, es muy probable que Meta levante la restricción en **2-3 días hábiles**.

---

*Documento creado: 11 de marzo de 2026*  
*Relacionado con: Business Account ID `1437289745941886`*
