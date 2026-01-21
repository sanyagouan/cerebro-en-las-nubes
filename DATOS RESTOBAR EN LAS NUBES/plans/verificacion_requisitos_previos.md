# 📋 Verificación de Requisitos Previos - Sistema de Recepcionista Virtual

## 📌 Introducción

Este documento proporciona un checklist completo de todos los requisitos previos necesarios para implementar el **Sistema Integral de Recepcionista Virtual** para **En Las Nubes Restobar**.

### Propósito

El objetivo de este documento es asegurar que se dispone de todas las credenciales, servicios y configuraciones necesarias antes de proceder con la implementación técnica del sistema en producción.

### Alcance

Este documento cubre:
- Credenciales de servicios externos (Airtable, OpenAI, Twilio, Slack, Telegram, VAPI, n8n)
- Servicios de infraestructura (PostgreSQL, Airtable, n8n, VAPI, Twilio)
- Configuraciones de Airtable (tablas y campos)
- Configuraciones de VAPI (webhooks y funciones)
- Configuraciones de Twilio (webhooks y número de WhatsApp)
- Configuraciones de Slack (canales y webhooks)
- Configuraciones de Telegram (grupo y webhooks)
- Configuraciones de n8n (workflows, credenciales y triggers)
- Configuraciones de base de conocimiento (FAQs)

### Instrucciones de Uso

1. **Revisar cada requisito** en el checklist
2. **Verificar el estado** de cada requisito marcando `[x]` si está completado o `[ ]` si está pendiente
3. **Añadir notas** relevantes en la columna "Notas" para documentar cualquier observación
4. **Reportar el estado final** usando el formato proporcionado al final del documento

---

## ✅ Checklist de Verificación

### 1. Credenciales de Servicios Externos

#### 1.1 Airtable

| Requisito | Estado | Notas |
|------------|---------|--------|
| API Key de Airtable | [ ] | |
| Base ID de Airtable | [ ] | |
| ID de tabla `tables` | [ ] | |
| ID de tabla `reservations` | [ ] | |
| ID de tabla `availability_slots` | [ ] | |
| ID de tabla `audit_log` | [ ] | |
| ID de tabla `customers` | [ ] | |
| ID de tabla `restaurant_info` | [ ] | |

**Instrucciones de Verificación:**
1. Iniciar sesión en [Airtable](https://airtable.com)
2. Navegar a la base de datos del proyecto
3. Ir a "Account" → "API" para obtener la API Key
4. Copiar el Base ID desde la URL de la base de datos
5. Para cada tabla, hacer clic en la tabla y copiar el ID desde la URL

---

#### 1.2 OpenAI

| Requisito | Estado | Notas |
|------------|---------|--------|
| API Key de OpenAI | [ ] | |
| Modelo configurado (gpt-4o) | [ ] | |

**Instrucciones de Verificación:**
1. Iniciar sesión en [OpenAI Platform](https://platform.openai.com)
2. Navegar a "API Keys" → "Create new secret key"
3. Copiar la API Key generada
4. Verificar que el modelo `gpt-4o` está disponible en "Models"

---

#### 1.3 Twilio

| Requisito | Estado | Notas |
|------------|---------|--------|
| Account SID de Twilio | [ ] | |
| Auth Token de Twilio | [ ] | |
| Número de WhatsApp configurado | [ ] | |

**Instrucciones de Verificación:**
1. Iniciar sesión en [Twilio Console](https://console.twilio.com)
2. Navegar a "Settings" → "General" para obtener Account SID y Auth Token
3. Navegar a "Messaging" → "Try it out" → "Send a WhatsApp message"
4. Verificar que el número de WhatsApp Business está configurado y activo

---

#### 1.4 Slack

| Requisito | Estado | Notas |
|------------|---------|--------|
| Bot Token de Slack | [ ] | |
| ID del canal de emergencias | [ ] | |
| ID del canal de operaciones | [ ] | |

**Instrucciones de Verificación:**
1. Crear una app en [Slack API](https://api.slack.com/apps)
2. Configurar un Bot User y obtener el Bot Token
3. Crear los canales `#emergencias` y `#operaciones`
4. Añadir el bot a ambos canales
5. Obtener los IDs de los canales desde la URL o usando la API de Slack

---

#### 1.5 Telegram

| Requisito | Estado | Notas |
|------------|---------|--------|
| Bot Token de Telegram | [ ] | |
| ID del grupo de emergencias | [ ] | |

**Instrucciones de Verificación:**
1. Crear un bot usando [@BotFather](https://t.me/botfather) en Telegram
2. Obtener el Bot Token
3. Crear un grupo de Telegram para emergencias
4. Añadir el bot al grupo
5. Obtener el ID del grupo usando un bot como [@userinfobot](https://t.me/userinfobot)

---

#### 1.6 VAPI

| Requisito | Estado | Notas |
|------------|---------|--------|
| API Key de VAPI | [ ] | |
| Número de teléfono del restaurante configurado | [ ] | |

**Instrucciones de Verificación:**
1. Iniciar sesión en [VAPI Dashboard](https://dashboard.vapi.ai)
2. Navegar a "Settings" → "API Keys" para obtener la API Key
3. Verificar que el número de teléfono del restaurante está configurado en "Phone Numbers"

---

### 2. Servicios de Infraestructura

#### 2.1 PostgreSQL

| Requisito | Estado | Notas |
|------------|---------|--------|
| PostgreSQL instalado y configurado en el VPS | [ ] | |
| Credenciales de acceso a la base de datos | [ ] | |
| Base de datos creada (ejecutar schema_postgresql.sql) | [ ] | |

**Instrucciones de Verificación:**
1. Conectarse al VPS via SSH
2. Verificar que PostgreSQL está instalado: `psql --version`
3. Verificar que el servicio está activo: `sudo systemctl status postgresql`
4. Conectarse a PostgreSQL: `psql -U postgres`
5. Verificar que la base de datos `restobar_nubes` existe: `\l`
6. Verificar que las tablas están creadas: `\d`
7. Ejecutar el script `schema_postgresql.sql` si las tablas no existen

---

#### 2.2 n8n

| Requisito | Estado | Notas |
|------------|---------|--------|
| n8n instalado y configurado en el VPS | [ ] | |
| URL de la instancia de n8n accesible | [ ] | |
| Credenciales de administrador configuradas | [ ] | |
| Timezone configurado (Europe/Madrid) | [ ] | |

**Instrucciones de Verificación:**
1. Verificar que n8n está instalado: `n8n --version`
2. Verificar que el servicio está activo: `sudo systemctl status n8n`
3. Acceder a la URL de n8n en el navegador
4. Verificar que se puede iniciar sesión con las credenciales de administrador
5. Navegar a "Settings" → "General" y verificar que el timezone es `Europe/Madrid`

---

### 3. Configuraciones de Airtable

#### 3.1 Tablas a Crear

| Requisito | Estado | Notas |
|------------|---------|--------|
| Tabla `tables` con 21 mesas | [ ] | |
| Tabla `reservations` | [ ] | |
| Tabla `availability_slots` | [ ] | |
| Tabla `audit_log` | [ ] | |
| Tabla `customers` | [ ] | |
| Tabla `restaurant_info` | [ ] | |

**Instrucciones de Verificación:**
1. Iniciar sesión en Airtable
2. Verificar que todas las tablas están creadas en la base de datos
3. Para la tabla `tables`, verificar que contiene 21 registros de mesas

---

#### 3.2 Campos de Tablas

| Requisito | Estado | Notas |
|------------|---------|--------|
| Todos los campos de `tables` creados | [ ] | |
| Todos los campos de `reservations` creados | [ ] | |
| Todos los campos de `availability_slots` creados | [ ] | |
| Todos los campos de `audit_log` creados | [ ] | |
| Todos los campos de `customers` creados | [ ] | |
| Todos los campos de `restaurant_info` creados | [ ] | |

**Instrucciones de Verificación:**
1. Comparar los campos de cada tabla con el esquema definido en `schema_postgresql.md`
2. Verificar que todos los campos especificados están presentes
3. Verificar que los tipos de datos son correctos

---

### 4. Configuraciones de VAPI

#### 4.1 Webhook de VAPI

| Requisito | Estado | Notas |
|------------|---------|--------|
| URL del webhook de n8n configurada en VAPI | [ ] | |
| Endpoint del webhook configurado (/vapi/voice-agent) | [ ] | |

**Instrucciones de Verificación:**
1. Iniciar sesión en VAPI Dashboard
2. Navegar a "Phone Numbers" → seleccionar el número del restaurante
3. Verificar que el webhook URL está configurado: `https://[n8n-url]/webhook/vapi/voice-agent`
4. Verificar que el método HTTP es POST

---

#### 4.2 Funciones de VAPI

| Requisito | Estado | Notas |
|------------|---------|--------|
| Función de transferencia a humano configurada (639 36 78 00) | [ ] | |
| Función de clasificación de intención configurada | [ ] | |
| Función de consulta de FAQs configurada | [ ] | |

**Instrucciones de Verificación:**
1. Navegar a "Functions" en VAPI Dashboard
2. Verificar que la función `transfer_to_human` está configurada con el número 639 36 78 00
3. Verificar que la función `classify_intent` está configurada
4. Verificar que la función `query_faqs` está configurada

---

### 5. Configuraciones de Twilio

#### 5.1 Webhook de Twilio

| Requisito | Estado | Notas |
|------------|---------|--------|
| URL del webhook de n8n configurada en Twilio | [ ] | |
| Endpoint del webhook configurado (/twilio/webhook) | [ ] | |

**Instrucciones de Verificación:**
1. Iniciar sesión en Twilio Console
2. Navegar a "Messaging" → "Settings" → "WhatsApp sandbox settings"
3. Verificar que el webhook URL está configurado: `https://[n8n-url]/webhook/twilio/webhook`
4. Verificar que el método HTTP es POST

---

#### 5.2 Número de WhatsApp

| Requisito | Estado | Notas |
|------------|---------|--------|
| Número de WhatsApp Business configurado | [ ] | |
| Número verificado y activo | [ ] | |

**Instrucciones de Verificación:**
1. Navegar a "Messaging" → "Senders" → "WhatsApp Senders" en Twilio Console
2. Verificar que el número de WhatsApp Business está configurado
3. Verificar que el estado del número es "Active"

---

### 6. Configuraciones de Slack

#### 6.1 Canales

| Requisito | Estado | Notas |
|------------|---------|--------|
| Canal de emergencias creado | [ ] | |
| Canal de operaciones creado | [ ] | |
| Bot de Slack añadido a los canales | [ ] | |

**Instrucciones de Verificación:**
1. Iniciar sesión en Slack
2. Verificar que los canales `#emergencias` y `#operaciones` existen
3. Verificar que el bot está añadido a ambos canales

---

#### 6.2 Webhooks

| Requisito | Estado | Notas |
|------------|---------|--------|
| Webhook de n8n configurado para enviar alertas a Slack | [ ] | |

**Instrucciones de Verificación:**
1. Navegar a "Incoming Webhooks" en Slack
2. Verificar que existe un webhook configurado para recibir alertas de n8n
3. Verificar que el webhook URL apunta a la instancia de n8n

---

### 7. Configuraciones de Telegram

#### 7.1 Grupo

| Requisito | Estado | Notas |
|------------|---------|--------|
| Grupo de emergencias creado | [ ] | |
| Bot de Telegram añadido al grupo | [ ] | |

**Instrucciones de Verificación:**
1. Abrir Telegram y verificar que el grupo de emergencias existe
2. Verificar que el bot está añadido al grupo

---

#### 7.2 Webhooks

| Requisito | Estado | Notas |
|------------|---------|--------|
| Webhook de n8n configurado para enviar alertas a Telegram | [ ] | |

**Instrucciones de Verificación:**
1. Verificar que el bot de Telegram tiene un webhook configurado
2. El webhook debe apuntar a la instancia de n8n

---

### 8. Configuraciones de n8n

#### 8.1 Workflows

| Requisito | Estado | Notas |
|------------|---------|--------|
| Workflow 1 (TRIG_VAPI_Voice_Agent_Reservation) importado | [ ] | |
| Workflow 2 (TRIG_Twilio_WhatsApp_Confirmation_CRM) importado | [ ] | |
| Workflow 3 (SCHED_Reminders_NoShow_Alerts) importado | [ ] | |
| Workflow 4 (ERROR_Global_Error_Handler_QA) importado | [ ] | |

**Instrucciones de Verificación:**
1. Iniciar sesión en n8n
2. Navegar a "Workflows"
3. Verificar que los 4 workflows están listados
4. Verificar que cada workflow está activo

---

#### 8.2 Credenciales

| Requisito | Estado | Notas |
|------------|---------|--------|
| Credenciales de Airtable configuradas en todos los workflows | [ ] | |
| Credenciales de OpenAI configuradas en todos los workflows | [ ] | |
| Credenciales de Twilio configuradas en todos los workflows | [ ] | |
| Credenciales de Slack configuradas en workflows 3 y 4 | [ ] | |
| Credenciales de Telegram configuradas en workflow 4 | [ ] | |

**Instrucciones de Verificación:**
1. Abrir cada workflow en n8n
2. Navegar a "Credentials"
3. Verificar que las credenciales correspondientes están configuradas
4. Verificar que las credenciales están activas y funcionales

---

#### 8.3 Triggers

| Requisito | Estado | Notas |
|------------|---------|--------|
| Webhook de VAPI activo | [ ] | |
| Webhook de Twilio activo | [ ] | |
| Schedule Trigger de Workflow 3 activo | [ ] | |
| Error Trigger global activo | [ ] | |

**Instrucciones de Verificación:**
1. Abrir cada workflow en n8n
2. Verificar que los triggers están configurados correctamente
3. Verificar que los triggers están activos

---

### 9. Configuraciones de Base de Conocimiento

#### 9.1 Tabla de FAQs en Airtable

| Requisito | Estado | Notas |
|------------|---------|--------|
| Tabla `FAQs` creada en Airtable | [ ] | |
| 28 FAQs importadas en la tabla | [ ] | |

**Instrucciones de Verificación:**
1. Iniciar sesión en Airtable
2. Verificar que la tabla `FAQs` existe
3. Verificar que contiene 28 registros de FAQs

---

#### 9.2 Integración con VAPI

| Requisito | Estado | Notas |
|------------|---------|--------|
| Endpoint de consulta de FAQs configurado en VAPI | [ ] | |
| Sistema de matching de preguntas configurado | [ ] | |

**Instrucciones de Verificación:**
1. Iniciar sesión en VAPI Dashboard
2. Navegar a "Functions"
3. Verificar que la función `query_faqs` está configurada
4. Verificar que el endpoint de n8n para consultar FAQs está configurado

---

## 📊 Resumen de Estado

### Categorías Completadas

| Categoría | Total Requisitos | Completados | Pendientes | % Completado |
|-------------|-------------------|--------------|--------------|---------------|
| 1. Credenciales de Servicios Externos | 20 | 0 | 20 | 0% |
| 2. Servicios de Infraestructura | 4 | 0 | 4 | 0% |
| 3. Configuraciones de Airtable | 12 | 0 | 12 | 0% |
| 4. Configuraciones de VAPI | 5 | 0 | 5 | 0% |
| 5. Configuraciones de Twilio | 4 | 0 | 4 | 0% |
| 6. Configuraciones de Slack | 4 | 0 | 4 | 0% |
| 7. Configuraciones de Telegram | 3 | 0 | 3 | 0% |
| 8. Configuraciones de n8n | 13 | 0 | 13 | 0% |
| 9. Configuraciones de Base de Conocimiento | 4 | 0 | 4 | 0% |
| **TOTAL** | **69** | **0** | **69** | **0%** |

---

## 📝 Formato de Reporte

### Reporte de Verificación Completado

**Fecha de Verificación:** [DD/MM/AAAA]
**Verificado por:** [Nombre]
**Rol:** [Rol]

### Resumen General

- **Total de Requisitos:** 69
- **Requisitos Completados:** [Número]
- **Requisitos Pendientes:** [Número]
- **Porcentaje de Completado:** [X]%

### Categorías Pendientes

Listar las categorías que tienen requisitos pendientes:

1. [Nombre de categoría] - [X] requisitos pendientes
2. [Nombre de categoría] - [X] requisitos pendientes
3. ...

### Observaciones y Bloqueadores

Documentar cualquier observación importante o bloqueador encontrado:

- [Observación 1]
- [Observación 2]
- ...

### Recomendaciones

Listar recomendaciones para completar los requisitos pendientes:

1. [Recomendación 1]
2. [Recomendación 2]
3. ...

### Próximos Pasos

Indicar los próximos pasos después de completar la verificación:

1. [Próximo paso 1]
2. [Próximo paso 2]
3. ...

---

## 🚀 Próximos Pasos Después de la Verificación

Una vez completada la verificación de requisitos previos, se deben seguir estos pasos:

### 1. Configuración de Credenciales en n8n

- Configurar todas las credenciales de servicios externos en n8n
- Verificar que las credenciales funcionan correctamente
- Documentar las credenciales en un lugar seguro

### 2. Importación de Workflows

- Importar los 4 workflows principales en n8n
- Configurar los triggers de cada workflow
- Activar los workflows

### 3. Configuración de Webhooks

- Configurar los webhooks de VAPI y Twilio
- Verificar que los webhooks reciben las peticiones correctamente
- Probar la comunicación entre servicios

### 4. Pruebas de Integración

- Realizar pruebas de integración entre todos los componentes
- Verificar que el flujo completo funciona correctamente
- Documentar los resultados de las pruebas

### 5. Despliegue en Producción

- Desplegar el sistema en producción
- Monitorear el funcionamiento del sistema
- Realizar ajustes según sea necesario

---

## 📞 Soporte

Si tienes alguna pregunta o necesitas ayuda con la verificación de requisitos, contacta al equipo técnico del proyecto.

---

**Documento Versión:** 1.0  
**Última Actualización:** 2025-12-25  
**Estado:** Activo
