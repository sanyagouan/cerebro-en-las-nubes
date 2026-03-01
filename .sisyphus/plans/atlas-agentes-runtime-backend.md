# Plan de Implementación: Agentes OpenCode + Runtime Backend

**Fecha**: 2026-02-26  
**Prioridad**: P0 (Agentes) → P1 (Runtime) → P2 (Encoding)  
**Estado**: Planificación (listo para Atlas)  
**Autor**: Prometheus (Plan Builder) con consulta de Metis

---

## 1. Contexto y Objetivo

### Problema Actual
1. **Agentes OpenCode (explore, librarian, quick, hephaestus)** lanzan sesiones pero devuelven contenido vacío (assistant content = "").
2. **Runtime Backend**: Airtable y Redis no configurados (env vars faltantes).
3. **Scheduler**: Unicode encoding error en Windows cp1252 al imprimir emojis ✅/❌.

### Restricciones del Usuario
- **Modelos preferidos**: deepseek, z.ai (GLM-5), antigravity (si viable), Google Vertex (si posible).
- **Evitar GPT-5 Codex** por costo excesivo de tokens.
- **Antropic limitado** a Claude Code/Desktop.
- **Configuraciones JSON** ya modificadas manualmente.
- **Funciona**: deepseek, openai, z.ai.
- **No funciona**: antigravity (probablemente configuración incorrecta).

### Meta Final
Sistema 100% funcional con:
- Agentes respondiendo texto no vacío.
- Backend conectado a Airtable y Redis.
- Scheduler estable en Windows/Linux.
- Configuración óptima de modelos según coste/rendimiento.

---

## 2. Análisis de Gaps (Metis)

### Gap 1: Agentes Vacíos (CRÍTICO)
**Preguntas clave**:
- ¿Vacío en todas las vías (CLI, API, UI) o solo una?
- ¿Hay tool results pero no assistant content?
- ¿Streaming vs non-streaming?
- ¿Solo con ciertos proveedores/modelos?
- ¿Post-procesado descarta contenido "falsy"?

**Suposiciones a validar**:
- No es causado por UnicodeEncodeError interrumpiendo stream.
- El vacío no es por tool calls que UI no renderiza.

### Gap 2: Configuración Runtime (CRÍTICO)
**Decisiones necesarias**:
1. **Fuente de verdad env**: ¿`.env` vs `.env.mcp` vs OS env?
2. **Airtable base_id**: ¿Bug (ignora argumento) o diseño?
3. **Redis**: ¿Obligatorio o degradable?

### Gap 3: Encoding Windows (MENOR)
**Opciones**:
- Eliminar emojis de stdout.
- Forzar UTF-8 en entrypoint.
- Configurar logging handler con UTF-8.

---

## 3. Decisiones Explícitas (Pre-Plan)

### Decisión 1: Fuente de Verdad Environment
**Opción elegida**: `.env` (ya usado por `load_dotenv()`) + variables OS.
- **Razón**: `main.py` ya carga `.env`; `.env.mcp` es para MCP local.
- **Acción**: Mover `AIRTABLE_BASE_ID` y `REDIS_URL` a `.env`.
- **Compatibilidad**: Mantener `.env.mcp` para MCP, ignorar en runtime.

### Decisión 2: Comportamiento Airtable/Redis
**Airtable**:
- Si falta `AIRTABLE_BASE_ID` → `RuntimeError` al inicio (fail-fast).
- **Fix bug**: `AirtableMCPClient` debe usar `base_id` argument si se pasa.

**Redis**:
- Si falta `REDIS_URL` → cache disabled (warning, no error).
- Endpoints críticos deben funcionar sin cache (degradación controlada).

### Decisión 3: Estrategia Encoding
**Opción elegida**: Eliminar emojis de stdout + forzar UTF-8 en scheduler.
- Reemplazar `print("✅")` por `logger.info("OK")`.
- En `scheduler_service.py`, configurar encoding UTF-8.
- **No** cambiar logging global (scope creep).

### Decisión 4: Modelos por Agente (Optimizado Coste/Rendimiento)
Basado en preferencias usuario y funcionalidad actual:

| Agente | Modelo Preferido | Fallback 1 | Fallback 2 | Razón |
|--------|------------------|------------|------------|-------|
| **Sisyphus** | z.ai/glm-5 | deepseek/deepseek-chat | antigravity-claude-opus-4-5-thinking | Orquestador principal, necesita razonamiento |
| **Hephaestus** | deepseek/deepseek-chat | z.ai/glm-5 | openai/gpt-4o-mini | Trabajo autónomo, bajo costo |
| **Explore** | z.ai/glm-5 | deepseek/deepseek-chat | google/gemini-3.0 | Búsqueda contextual, rápido |
| **Librarian** | google/gemini-3.0 | z.ai/glm-5 | deepseek/deepseek-chat | Búsqueda externa, buena con documentos |
| **Oracle** | antigravity-claude-opus-4-5-thinking | z.ai/glm-5 | google/gemini-3.0 | Consulta read-only, alta calidad |
| **Metis** | z.ai/glm-5 | deepseek/deepseek-chat | antigravity-claude-opus-4-5-thinking | Pre-planning, razonamiento |
| **Momus** | deepseek/deepseek-chat | z.ai/glm-5 | google/gemini-3.0 | Revisión de planes, bajo costo |
| **Atlas** | z.ai/glm-5 | deepseek/deepseek-chat | antigravity-claude-opus-4-5-thinking | Orquestador todo-list |
| **Prometheus** | antigravity-claude-opus-4-5-thinking | z.ai/glm-5 | deepseek/deepseek-chat | Planificación estratégica |

**Nota**: Verificar configuración antigravity (¿API key correcta? ¿Endpoint?).

---

## 4. Plan de Implementación por Fases

### Fase 0: Validación Configuración Actual (Día 0)
**Objetivo**: Confirmar estado actual y detectar configuraciones incorrectas.

**Tareas**:
1. **Revisar todos los JSON de configuración**:
   - `~/.config/opencode/oh-my-opencode.json`
   - `opencode.json` 
   - `antigravity-accounts.json`
   - Verificar: activeIndex, enabled, API keys, endpoints.

2. **Probar conectividad por proveedor**:
   - deepseek: smoke test simple.
   - z.ai (GLM-5): smoke test.
   - antigravity: diagnosticar por qué falla.
   - google/gemini: verificar credenciales Vertex.

3. **Documentar hallazgos** en `.sisyphus/logs/config-audit-YYYYMMDD.md`.

**Criterio de éxito**: Lista clara de qué proveedores funcionan y cuáles no.

### Fase 1: Fix Agentes Vacíos (P0 - Día 1)
**Objetivo**: Agentes devuelven texto no vacío.

**Tareas**:
1. **Diagnóstico profundo del vacío**:
   - Instrumentar puente de agentes para loguear payload completo.
   - Verificar si hay tool results vs assistant content.
   - Probar con/sin streaming.

2. **Fix según causa raíz**:
   - **Caso A**: Serialización incorrecta → arreglar parser.
   - **Caso B**: Streaming interrumpido → fix stream handler.
   - **Caso C**: Post-procesado descarta contenido → ajustar lógica.
   - **Caso D**: Modelo/proveedor específico → cambiar modelo de prueba.

3. **Validación cruzada**:
   - Probar con deepseek (funciona) como baseline.
   - Probar con z.ai/glm-5.
   - Probar con antigravity (si se arregla).

4. **Tests de aceptación**:
   - `task(explore, "buscar X")` → respuesta no vacía.
   - `task(librarian, "buscar docs")` → respuesta no vacía.
   - `task(quick, "smoke test")` → respuesta no vacía.

**Rollback**: Revertir cambios en puente de agentes si empeora.

### Fase 2: Configuración Runtime Backend (P1 - Día 2)
**Objetivo**: Airtable y Redis funcionando.

**Tareas**:
1. **Environment variables**:
   - Agregar `AIRTABLE_BASE_ID` y `REDIS_URL` a `.env`.
   - Actualizar `main.py` para cargar `.env` explícitamente.
   - Documentar variables requeridas.

2. **Fix AirtableMCPClient**:
   - Arreglar bug "ignora base_id argument".
   - Validar que usa `AIRTABLE_BASE_ID` de env.
   - Test: lectura simple de tabla Mesas.

3. **RedisCache**:
   - Implementar degradación elegante si `REDIS_URL` falta.
   - Test: conexión y operación básica (set/get).

4. **Health endpoint**:
   - Extender `/health` para reportar estado de Airtable/Redis.
   - Degradado claro si servicios faltan.

**Rollback**: Remover variables env, restaurar comportamiento original.

### Fase 3: Fix Encoding Scheduler (P2 - Día 3)
**Objetivo**: Scheduler estable en Windows.

**Tareas**:
1. **Eliminar emojis de stdout**:
   - Reemplazar `print("✅")`/`print("❌")` en `booking_repo.py`.
   - Usar `logger.info("OK")`/`logger.error("FAIL")`.

2. **Forzar UTF-8 en scheduler**:
   - En `scheduler_service.py`, configurar encoding.
   - Opción: `sys.stdout.reconfigure(encoding="utf-8")` en entrypoint.

3. **Test Windows**:
   - Ejecutar job manualmente (no excepción).
   - Ejecutar vía scheduler (background).

**Rollback**: Revertir cambios de logging.

### Fase 4: Optimización Modelos (Día 4)
**Objetivo**: Configuración óptima de modelos según coste/rendimiento.

**Tareas**:
1. **Diagnóstico antigravity**:
   - Verificar API key, endpoint, configuración.
   - Probar modelo claude-opus-4-5-thinking.
   - Si no viable, usar fallback (z.ai/glm-5).

2. **Configurar Vertex (Google)**:
   - Verificar credenciales de facturación.
   - Probar gemini-3.0.
   - Configurar en `opencode.json`.

3. **Actualizar asignaciones**:
   - Aplicar tabla de decisiones (sección 3.4).
   - Validar cada agente con su modelo asignado.

4. **Benchmark costo**:
   - Estimar tokens/mes por agente.
   - Ajustar si algún modelo es muy caro.

### Fase 5: Validación Integral (Día 5)
**Objetivo**: Todo el sistema funciona correctamente.

**Tareas**:
1. **End-to-end test agents**:
   - Explore: búsqueda en código.
   - Librarian: búsqueda externa.
   - Quick: tarea simple.
   - Hephaestus: trabajo autónomo.

2. **Backend integration test**:
   - Reservas: crear, confirmar, cancelar (con Airtable).
   - Cache: operaciones Redis.
   - Scheduler: ejecución estable.

3. **Windows compatibility**:
   - Ejecutar todo en Windows (encoding OK).
   - Verificar logs sin errores.

4. **Documentación**:
   - Actualizar `AGENTS.md` con nuevas asignaciones.
   - Actualizar `README.md` con setup instructions.

### Fase 6: Preparación Producción (Día 6)
**Objetivo**: Listo para despliegue.

**Tareas**:
1. **Environment producción**:
   - Crear `.env.production` template.
   - Configurar Coolify/Docker variables.

2. **Monitoring**:
   - Health checks extendidos.
   - Logs estructurados (JSON).

3. **Rollback plan**:
   - Documentar pasos para revertir cada fase.
   - Puntos de restauración claros.

4. **Handoff a equipo**:
   - Documentación completa.
   - Session de conocimiento.

---

## 5. Criterios de Aceptación por Fase

### Fase 0 (Configuración)
- [ ] JSON de configuración auditados y documentados.
- [ ] Estado claro de cada proveedor (funciona/no funciona).
- [ ] Issues específicos identificados (ej: antigravity).

### Fase 1 (Agentes)
- [ ] `task(explore, "X")` devuelve texto no vacío (≥1 línea).
- [ ] `task(librarian, "docs")` devuelve texto no vacío.
- [ ] `task(quick, "test")` devuelve texto no vacío.
- [ ] Logs muestran payload completo (no vacío).

### Fase 2 (Runtime)
- [ ] `/health` reporta "Airtable: OK", "Redis: OK|DISABLED".
- [ ] Operación lectura Airtable funciona (no RuntimeError).
- [ ] Redis conecta si `REDIS_URL` presente.
- [ ] Cache disabled si `REDIS_URL` ausente (no error).

### Fase 3 (Encoding)
- [ ] Scheduler ejecuta en Windows sin `UnicodeEncodeError`.
- [ ] Logs no contienen emojis que rompan encoding.
- [ ] Output legible en consola cp1252.

### Fase 4 (Modelos)
- [ ] Cada agente usa modelo asignado (tabla 3.4).
- [ ] Antigravity funciona o tiene fallback viable.
- [ ] Vertex (Google) configurado si posible.
- [ ] Coste estimado documentado.

### Fase 5 (Validación)
- [ ] Todos los agentes responden no vacío.
- [ ] Backend completo opera con Airtable/Redis.
- [ ] Windows compatibility verificada.
- [ ] No regresiones introducidas.

### Fase 6 (Producción)
- [ ] Environment templates creados.
- [ ] Rollback plan documentado.
- [ ] Handoff material listo.

---

## 6. Riesgos y Mitigación

| Riesgo | Impacto | Probabilidad | Mitigación |
|--------|---------|--------------|------------|
| **Agentes vacíos es bug complejo** | Alto | Media | Diagnóstico incremental; fallback a proveedor que funciona (deepseek). |
| **Antigravity no viable** | Medio | Alta | Usar fallbacks (z.ai/glm-5, deepseek). |
| **Vertex Google no accesible** | Bajo | Media | Usar gemini vía otro proveedor o fallback a z.ai. |
| **Encoding fix rompe Linux** | Medio | Baja | Test cross-platform; solución específica Windows. |
| **Airtable schema changes** | Alto | Baja | Validar con operaciones de lectura primero. |
| **Redis required for sessions** | Alto | Media | Implementar session store alternativo (memory) si Redis falta. |

---

## 7. Recursos Necesarios

### Configuración
- Acceso a `.env` y `.env.mcp` (solo lectura inicial).
- Credenciales: Airtable API key, Redis URL, keys de proveedores LLM.
- Permisos para modificar `src/` (agentes, runtime, scheduler).

### Herramientas
- Terminal Windows (testing encoding).
- Python 3.11+ environment.
- Acceso a logs del servidor OpenCode.

### Tiempo Estimado
- **Total**: 6 días (fases 0-6).
- **Crítico**: Día 1-2 (agentes + runtime).
- **Buffer**: +2 días para imprevistos.

---

## 8. Notas para Atlas

### Prioridades Estrictas
1. **Agentes no vacíos** (P0) - bloquea todo lo demás.
2. **Runtime funcional** (P1) - necesario para backend.
3. **Encoding** (P2) - mejora estabilidad Windows.

### Decisiones Pendientes (consultar si duda)
1. **Fuente de verdad env**: Seguir con `.env` (ya decidido).
2. **Comportamiento Redis**: Degradación controlada (ya decidido).
3. **Estrategia encoding**: Eliminar emojis + UTF-8 (ya decidido).

### Puntos de Validación
- Después de Fase 1: ¿Agentes responden?
- Después de Fase 2: ¿/health reporta OK?
- Después de Fase 3: ¿Scheduler Windows sin error?

### Comunicación
- Documentar progreso en `.sisyphus/logs/`.
- Reportar bloqueos inmediatamente.
- Confirmar con usuario antes de cambios de modelo costosos.

---

**Fin del Plan** - Listo para implementación por Atlas.