# Plan de Acción Inmediato - Asistente de Voz "En Las Nubes"

> **Fecha:** 17 de Marzo, 2026
> **Estado:** Pendiente de verificación Meta WhatsApp
> **Objetivo:** Avanzar en tareas críticas mientras esperamos aprobación de Meta

---

## 📋 Resumen Ejecutivo

El sistema está **95% completo y desplegado en producción**. El único bloqueador externo es la verificación de Meta para WhatsApp Business API. Este plan detalla las tareas que podemos avanzar mientras tanto.

### Estado Actual del Sistema

| Componente | Estado | URL/ID |
|------------|--------|--------|
| **Backend FastAPI** | ✅ Desplegado | `https://go84sgscs4ckcs08wog84o0o.app.generaia.site` |
| **VAPI Assistant** | ✅ Configurado | ID: `9a1f2df2-1c2d-4061-b11c-bdde7568c85d` |
| **Airtable** | ✅ Operativo | Base: `appcUoRqLVqxQm7K2` |
| **Dashboard Frontend** | ⚠️ Pendiente despliegue | Código listo en `dashboard/` |
| **WhatsApp Business** | ❌ Bloqueado | Esperando verificación Meta |

---

## 🎯 FASE 1: Integración y Pruebas del Asistente de Voz (VAPI)

**Prioridad:** 🔴 ALTA
**Duración estimada:** 2-3 horas
**Dependencias:** Ninguna

### 1.1 Verificación de Configuración VAPI ✅ (COMPLETADO)

**Estado:** Completado durante análisis

**Hallazgos:**
- ✅ Assistant ID: `9a1f2df2-1c2d-4061-b11c-bdde7568c85d`
- ✅ Nombre: "Nube - En Las Nubes"
- ✅ Server URL apunta a producción: `https://go84sgscs4ckcs08wog84o0o.app.generaia.site/vapi/webhook`
- ✅ Modelo LLM: GPT-4o (OpenAI)
- ✅ Voz: ElevenLabs con `eleven_multilingual_v2`
- ✅ Transcriptor: Deepgram `nova-2` (español)
- ✅ Herramientas configuradas: `check_availability`, `create_reservation`, `get_info`, `get_horarios`

### 1.2 Pruebas de Funcionalidad VAPI

**Tareas:**

- [ ] **Test 1: Verificar endpoint de health del backend**
  ```bash
  curl https://go84sgscs4ckcs08wog84o0o.app.generaia.site/health
  ```
  Esperado: `{"status": "healthy", ...}`

- [ ] **Test 2: Verificar webhook de VAPI responde**
  ```bash
  curl -X POST https://go84sgscs4ckcs08wog84o0o.app.generaia.site/vapi/webhook \
    -H "Content-Type: application/json" \
    -d '{"type": "test", "message": {"role": "user", "content": "Hola"}}'
  ```

- [ ] **Test 3: Llamada de prueba real (opcional)**
  - Realizar una llamada al número VAPI
  - Verificar que "Nube" responde correctamente
  - Comprobar que las herramientas se ejecutan (check_availability, etc.)

- [ ] **Test 4: Verificar logs en Coolify**
  - Revisar logs del backend durante la llamada
  - Confirmar que no hay errores 500

### 1.3 Ajustes de Prompts (si necesario)

**Tareas:**

- [ ] Revisar respuestas de Nube durante pruebas
- [ ] Ajustar prompt del sistema si hay problemas de:
  - Tono demasiado formal/informal
  - Respuestas incorrectas sobre horarios
  - Falta de empatía en situaciones de no disponibilidad

### 1.4 Documentación de Resultados

- [ ] Crear informe de pruebas VAPI
- [ ] Documentar cualquier issue encontrado
- [ ] Lista de mejoras pendientes

---

## 🎨 FASE 2: Finalización y Despliegue del Dashboard Frontend

**Prioridad:** 🟡 MEDIA
**Duración estimada:** 3-4 horas
**Dependencias:** Ninguna

### 2.1 Revisión del Código del Dashboard

**Estado actual:**
- ✅ React + TypeScript + Vite configurado
- ✅ Tailwind CSS para estilos
- ✅ Componentes principales: Dashboard, Reservas, Mesas, Clientes, Configuracion
- ✅ API configurada con fallback a producción
- ✅ Dockerfile y nginx.conf listos
- ✅ Tests con Vitest y Playwright

**Archivos clave revisados:**
- [`dashboard/src/config/api.ts`](dashboard/src/config/api.ts:8) - Configuración API con fallback
- [`dashboard/.env.example`](dashboard/.env.example:25) - Variables de entorno documentadas

### 2.2 Preparación para Despliegue en Coolify

**Tareas:**

- [ ] **Verificar Dockerfile del dashboard**
  ```bash
  cd dashboard
  docker build -t dashboard-test .
  ```

- [ ] **Configurar variables de entorno en Coolify**
  - `VITE_API_URL=https://go84sgscs4ckcs08wog84o0o.app.generaia.site`
  - Nota: Vite requiere estas variables en build-time

- [ ] **Crear aplicación en Coolify**
  - Tipo: Static Site o Node.js
  - Build command: `npm run build`
  - Output directory: `dist`

- [ ] **Configurar dominio**
  - Sugerido: `dashboard.enlasnubes.es` o similar
  - SSL automático con Let's Encrypt

### 2.3 Verificación de Conectividad Frontend-Backend

**Tareas:**

- [ ] Verificar CORS configurado en backend
- [ ] Probar endpoints desde el dashboard desplegado:
  - `/health` - Health check
  - `/api/reservas` - Lista de reservas
  - `/api/mesas` - Estado de mesas
  - `/api/stats` - Estadísticas

### 2.4 Tests de Integración del Dashboard

- [ ] Login/autenticación funciona
- [ ] CRUD de reservas operativo
- [ ] Visualización de mesas correcta
- [ ] Actualizaciones en tiempo real (WebSocket)

---

## 🔄 FASE 3: Pruebas de Integración End-to-End (E2E)

**Prioridad:** 🔴 ALTA (post-aprobación Meta)
**Duración estimada:** 4-6 horas
**Dependencias:** ❌ Aprobación de Meta WhatsApp Business

### 3.1 Flujo Completo de Reserva por Voz

```
┌─────────────────────────────────────────────────────────────┐
│ FLUJO E2E: RESERVA POR VOZ                                  │
└─────────────────────────────────────────────────────────────┘

1. Cliente llama → VAPI responde con "Nube"
2. Nube entiende intención de reserva
3. Nube llama herramienta check_availability
4. Backend consulta Airtable → Devuelve disponibilidad
5. Nube confirma datos con cliente
6. Nube llama herramienta create_reservation
7. Backend crea reserva en Airtable (Estado: Pendiente)
8. Backend envía WhatsApp de confirmación (BLOQUEADO por Meta)
9. Cliente responde "SÍ" por WhatsApp
10. Backend actualiza estado a "Confirmada"
```

### 3.2 Tests a Realizar

**Pre-Meta (podemos hacer ahora):**

- [ ] Test A: Llamada VAPI → check_availability → respuesta correcta
- [ ] Test B: Llamada VAPI → create_reservation → registro en Airtable
- [ ] Test C: Verificar que la reserva aparece en el dashboard

**Post-Meta (requiere aprobación):**

- [ ] Test D: Envío de WhatsApp de confirmación
- [ ] Test E: Recepción de respuesta "SÍ" del cliente
- [ ] Test F: Actualización de estado a "Confirmada"
- [ ] Test G: Flujo completo sin intervención humana

### 3.3 Escenarios de Error a Probar

- [ ] No hay disponibilidad → Nube ofrece alternativas
- [ ] Grupo >11 personas → Derivación a humano
- [ ] Cliente no confirma WhatsApp → Recordatorio automático
- [ ] Error en Airtable → Mensaje de error amigable

---

## 📊 Checklist de Progreso

### Fase 1: VAPI
- [x] 1.1 Verificar configuración VAPI
- [ ] 1.2 Pruebas de funcionalidad
- [ ] 1.3 Ajustes de prompts
- [ ] 1.4 Documentación

### Fase 2: Dashboard
- [ ] 2.1 Revisión de código
- [ ] 2.2 Preparación para despliegue
- [ ] 2.3 Verificación de conectividad
- [ ] 2.4 Tests de integración

### Fase 3: E2E
- [ ] 3.1 Tests pre-Meta
- [ ] 3.2 Tests post-Meta
- [ ] 3.3 Escenarios de error

---

## 🚀 Siguientes Pasos Inmediatos

1. **AHORA:** Ejecutar tests de conectividad VAPI (Fase 1.2)
2. **HOY:** Completar pruebas de funcionalidad VAPI
3. **ESTA SEMANA:** Desplegar dashboard en Coolify
4. **PENDIENTE META:** Completar tests E2E con WhatsApp real

---

## 📞 Contactos y Escalamiento

| Issue | Acción |
|-------|--------|
| VAPI no responde | Revisar logs Coolify, verificar API key |
| Dashboard no conecta | Verificar CORS, URL del backend |
| Meta no aprueba | Contactar soporte Meta Business |

---

**Documento creado por:** Arquitecto del Sistema
**Versión:** 1.0
**Última actualización:** 2026-03-17
