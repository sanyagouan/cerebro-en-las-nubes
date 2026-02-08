# 🚀 PLAN DE CONTINUACIÓN - Próximos Pasos

> **Estado Actual:** FASE 1 completa técnicamente, pendiente de validación  
> **Fecha:** 2026-02-08  
> **Próxima Acción:** Reiniciar Verdent → Validar MCPs → Continuar FASE 2

---

## 📋 CHECKLIST DE VALIDACIÓN INMEDIATA

### ✅ Después de Reiniciar Verdent

Ejecuta estos comandos **EN ORDEN** para validar que todos los MCPs funcionan:

#### 1️⃣ **Test GitHub MCP**
```
mcp_github_list_repos_for_authenticated_user
```
**Resultado esperado:** Lista tus repositorios de GitHub  
**Si falla:** Regenera token en https://github.com/settings/tokens

---

#### 2️⃣ **Test Airtable MCP** (CRÍTICO)
```
mcp_airtable_list_bases
```
**Resultado esperado:** Lista bases de Airtable (incluyendo "appcUoRqLVqxQm7K2")  
**Si falla:** 
- Regenera token: https://airtable.com/create/tokens
- Scopes: `data.records:read`, `data.records:write`, `schema.bases:read`
- Actualiza en `.env.mcp`
- Ejecuta: `. .\scripts\load_mcp_secrets.ps1`
- Reinicia Verdent

---

#### 3️⃣ **Test Coolify MCP** (CRÍTICO)
```
(Comando de test de Coolify - verificar herramientas disponibles)
```
**Resultado esperado:** Información del sistema Coolify  
**Si falla:** Regenera token en https://coolify.generaia.site/security/api-tokens

---

#### 4️⃣ **Test Supabase MCP** (CRÍTICO)
```
(Comando de test de Supabase - verificar herramientas disponibles)
```
**Resultado esperado:** Conexión exitosa a Supabase  
**Si falla:** Verifica URL y token de acceso

---

#### 5️⃣ **Test Twilio MCP** (CRÍTICO - NO PROBAR A MENOS QUE SEA NECESARIO)
⚠️ **ADVERTENCIA:** Este MCP envía mensajes reales que cuestan dinero.  
**Solo probar si es absolutamente necesario.**

---

## 🎯 FASES PENDIENTES (ORDEN DE EJECUCIÓN)

### 🔒 FASE 1: Seguridad - Migración de Secrets ✅

**Estado:** Técnicamente completa, pendiente de validación  

**Completado:**
- ✅ Script de migración v2.0 creado
- ✅ 13 secrets extraídos (vs 9 en v1.0)
- ✅ `mcp.json` refactorizado con placeholders
- ✅ `.env.mcp` creado con todos los secrets
- ✅ Scripts de carga automatizados
- ✅ Documentación completa (REPORTE_SECRETS_MCP.md)
- ✅ Script de inicio automático (start_verdent.ps1)

**Pendiente:**
- ⏳ Validar que todos los MCPs funcionan (después de reiniciar)
- ⏳ Marcar FASE 1 como completa

**Acción Inmediata:**
```powershell
# Reiniciar Verdent
. .\scripts\start_verdent.ps1

# Validar MCPs (usar checklist arriba)
```

---

### 📚 FASE 2: Configurar NotebookLM MCP

**Objetivo:** Integrar NotebookLM como fuente de verdad de negocio

**Estado:** Pendiente (MCP ya agregado en mcp.json, requiere autenticación)

**Tareas:**
1. **Autenticar NotebookLM:**
   - Ejecutar en Verdent: "Log me in to NotebookLM"
   - Seguir flujo OAuth de autenticación
   - Verificar acceso a notebooks

2. **Identificar Notebooks Relevantes:**
   - Listar notebooks disponibles
   - Identificar el notebook del proyecto "En Las Nubes Restobar"
   - Documentar IDs de notebooks críticos

3. **Configurar AGENTS.md:**
   - Agregar sección de uso de NotebookLM
   - Definir flujos de consulta obligatorios
   - Establecer prioridad de NotebookLM sobre código

4. **Crear Guía de Uso:**
   - Documentar cuándo consultar NotebookLM
   - Ejemplos de queries típicos
   - Flujo de resolución de conflictos (NotebookLM vs código)

**Comandos MCP NotebookLM Esperados:**
- `mcp_notebooklm_list_notebooks`
- `mcp_notebooklm_query_notebook`
- `mcp_notebooklm_get_sources`

**Criterio de Completitud:**
- [ ] Autenticación exitosa
- [ ] Al menos 1 notebook identificado
- [ ] Sección en AGENTS.md actualizada
- [ ] 3 queries de prueba exitosos

**Tiempo Estimado:** 30-45 minutos

---

### 📝 FASE 3: Generar AGENTS.md Completo

**Objetivo:** Completar y actualizar AGENTS.md con información actualizada

**Estado:** Parcialmente completo (837 líneas existentes)

**Tareas:**
1. **Revisar AGENTS.md Actual:**
   - Verificar que refleje el estado real del sistema
   - Identificar secciones desactualizadas
   - Detectar información faltante

2. **Actualizar Secciones:**
   - **Integraciones MCP:** Agregar NotebookLM, actualizar credenciales
   - **Flujos de Integración:** Documentar uso de NotebookLM
   - **Troubleshooting:** Agregar problemas comunes post-migración
   - **Configuración de Seguridad:** Referenciar migración de secrets

3. **Validar Contra Código:**
   - Verificar que rutas de archivos sean correctas
   - Confirmar que nombres de funciones/clases coincidan
   - Actualizar versiones de dependencias

4. **Agregar Diagramas:**
   - Flujo completo con NotebookLM
   - Arquitectura de seguridad (secrets flow)
   - Diagrama de decisión de handoff

**Criterio de Completitud:**
- [ ] Todas las secciones actualizadas
- [ ] NotebookLM documentado
- [ ] Troubleshooting completo
- [ ] Diagramas Mermaid agregados
- [ ] Validación de código realizada

**Tiempo Estimado:** 1-1.5 horas

---

### 🏗️ FASE 4: Auditoría Arquitectónica Completa

**Objetivo:** Auditar arquitectura, flujos de negocio y código del sistema

**Estado:** Documento existente (AUDITORIA_ARQUITECTONICA.md, 588 líneas)

**Tareas:**
1. **Auditoría de Código:**
   - Revisar estructura de carpetas actual
   - Validar que siga principios arquitectónicos (Hexagonal, etc)
   - Identificar deuda técnica
   - Detectar código duplicado o innecesario

2. **Auditoría de Flujos de Negocio:**
   - Validar flujos documentados vs implementados
   - Verificar reglas de negocio en código
   - Confirmar lógica de asignación de mesas
   - Revisar manejo de estados de reserva

3. **Auditoría de Integraciones:**
   - Verificar todos los endpoints de APIs externas
   - Validar manejo de errores en integraciones
   - Revisar logs y observabilidad
   - Confirmar timeouts y reintentos

4. **Auditoría de Seguridad:**
   - Verificar que no queden secrets hardcodeados
   - Revisar validación de inputs
   - Confirmar sanitización de outputs
   - Validar autenticación/autorización

5. **Generar Reporte:**
   - Calificación por área (0-10)
   - Lista de issues priorizados (P0/P1/P2)
   - Recomendaciones de mejora
   - Plan de acción

**Criterio de Completitud:**
- [ ] 4 auditorías completadas
- [ ] Reporte con calificaciones generado
- [ ] Issues priorizados
- [ ] Plan de acción definido

**Tiempo Estimado:** 2-3 horas

---

### ⚡ FASE 5: Optimizar Configuración Redis y Airtable

**Objetivo:** Optimizar rendimiento y confiabilidad de Redis y Airtable

**Estado:** Pendiente (código existente en `redis_cache.py` y `airtable_service.py`)

**Tareas Redis:**
1. **Configuración Actual:**
   - Revisar `src/core/config/redis.py`
   - Verificar `src/infrastructure/cache/redis_cache.py`
   - Documentar patrones de uso actuales

2. **Optimizaciones:**
   - Implementar connection pooling (si no existe)
   - Agregar circuit breaker para resiliencia
   - Optimizar TTL de cachés
   - Implementar cache warming para datos críticos
   - Agregar métricas de hit/miss rate

3. **Monitoreo:**
   - Agregar logging estructurado
   - Implementar health checks
   - Configurar alertas de disponibilidad

**Tareas Airtable:**
1. **Configuración Actual:**
   - Revisar `src/infrastructure/airtable/airtable_service.py`
   - Documentar queries más frecuentes
   - Identificar cuellos de botella

2. **Optimizaciones:**
   - Implementar retry con exponential backoff
   - Agregar rate limiting (5 requests/second)
   - Optimizar queries (batching, filtering)
   - Implementar caché para datos estáticos (mesas)
   - Reducir campos solicitados (projection)

3. **Resiliencia:**
   - Implementar fallback a cache si Airtable falla
   - Agregar queue para escrituras no críticas
   - Implementar health checks
   - Configurar circuit breaker

**Criterio de Completitud:**
- [ ] Redis optimizado (connection pool, circuit breaker)
- [ ] Airtable optimizado (retry, rate limit, cache)
- [ ] Métricas implementadas
- [ ] Health checks configurados
- [ ] Documentación actualizada

**Tiempo Estimado:** 2-3 horas

---

## 📊 RESUMEN EJECUTIVO

| Fase | Estado | Prioridad | Tiempo | Bloqueador |
|------|--------|-----------|--------|------------|
| **FASE 1: Seguridad** | ⏳ 95% | 🔴 CRÍTICA | +15min | Validar MCPs después de reinicio |
| **FASE 2: NotebookLM** | ⏸️ 0% | 🟡 ALTA | 45min | FASE 1 completa |
| **FASE 3: AGENTS.md** | ⏸️ 60% | 🟢 MEDIA | 1.5h | FASE 2 completa |
| **FASE 4: Auditoría** | ⏸️ 40% | 🟡 ALTA | 2-3h | FASE 3 completa |
| **FASE 5: Optimización** | ⏸️ 0% | 🟢 MEDIA | 2-3h | FASE 4 completa |

**Tiempo Total Restante:** 6-9 horas de trabajo

---

## 🎯 PRÓXIMA ACCIÓN INMEDIATA

### ¿Qué Hacer AHORA?

1. **Reiniciar Verdent:**
   ```powershell
   cd "C:\Users\yago\Desktop\EN LAS NUBES-PROYECTOS\COPIA ASISTENTE VOZ EN LAS NUBES-VERDENT"
   .\scripts\start_verdent.ps1
   ```

2. **Validar MCPs:**
   - Ejecuta cada test del checklist arriba
   - Reporta cualquier error

3. **Marcar FASE 1 completa:**
   - Si todos los MCPs funcionan: "FASE 1 COMPLETA, continuemos con FASE 2"
   - Si algo falla: "MCP X falló con error Y"

4. **Continuar con FASE 2:**
   - "Configuremos NotebookLM"
   - O si prefieres otro orden: "Prefiero hacer FASE X primero"

---

## 📞 COMUNICACIÓN CON VERDENT

### Si Todo Funciona:
```
"Todos los MCPs funcionan correctamente. Continuemos con FASE 2: NotebookLM"
```

### Si Algo Falla:
```
"MCP de [nombre] falló con error: [mensaje de error]"
```

### Si Quieres Cambiar el Orden:
```
"Saltemos FASE 2, prefiero hacer FASE [X] primero porque [razón]"
```

### Si Necesitas un Descanso:
```
"Guardemos el estado actual, continuaremos después"
```

---

## 💾 ESTADO DEL SISTEMA

### Archivos Creados/Actualizados en FASE 1:

| Archivo | Estado | Líneas | Descripción |
|---------|--------|--------|-------------|
| `env.mcp.template` | ✅ Actualizado | 68 | Template con 13 secrets |
| `scripts/migrate_mcp_security.ps1` | ✅ Actualizado v2.0 | 346 | Migración completa automatizada |
| `scripts/load_mcp_secrets.ps1` | ✅ Actualizado | 98 | Carga de variables + validación |
| `scripts/start_verdent.ps1` | ✅ Creado | 72 | Inicio automático con secrets |
| `.env.mcp` | ✅ Creado | ~50 | Secrets reales (NO commitear) |
| `~/.verdent/mcp.json` | ✅ Refactorizado | - | Placeholders `${VARIABLE}` |
| `REPORTE_SECRETS_MCP.md` | ✅ Creado | 370 | Reporte completo de migración |
| `AGENTS.md` | ✅ Existente | 837 | Pendiente actualización FASE 3 |
| `AUDITORIA_ARQUITECTONICA.md` | ✅ Existente | 588 | Pendiente revisión FASE 4 |
| `SECURITY_MIGRATION.md` | ✅ Existente | - | Guía de seguridad |

### Backups Creados:
- `.backups/mcp_YYYYMMDD_HHMMSS.json` (backup automático de mcp.json)

---

## 🔗 REFERENCIAS ÚTILES

- **Regenerar Tokens:**
  - GitHub: https://github.com/settings/tokens
  - Airtable: https://airtable.com/create/tokens
  - Coolify: https://coolify.generaia.site/security/api-tokens

- **Documentación de Proyecto:**
  - README.md
  - AGENTS.md
  - AUDITORIA_ARQUITECTONICA.md
  - REPORTE_SECRETS_MCP.md

- **Scripts Útiles:**
  - `.\scripts\start_verdent.ps1` - Iniciar Verdent con secrets
  - `.\scripts\load_mcp_secrets.ps1` - Cargar secrets manualmente
  - `.\scripts\migrate_mcp_security.ps1` - Re-ejecutar migración

---

**¿Listo?** Ejecuta:
```powershell
.\scripts\start_verdent.ps1
```

Y luego prueba los MCPs con el checklist de arriba. 🚀
