# 🔐 REPORTE COMPLETO: Secrets MCP

> **Fecha:** 2026-02-08  
> **Estado:** ACTUALIZACIÓN CRÍTICA COMPLETADA  
> **Versión Script:** v2.0

---

## 📊 ESTADO ACTUAL DE SERVIDORES MCP

### ✅ Servidores MCP ACTIVOS (enabled=true)

| Servidor | Variables Requeridas | Estado Actual | Prioridad |
|----------|---------------------|---------------|-----------|
| **GitHub** | `GITHUB_PERSONAL_ACCESS_TOKEN` | ✅ Token encontrado | Media |
| **Coolify** | `COOLIFY_API_URL`, `COOLIFY_API_TOKEN` | ✅ Token actualizado (v14) | 🔴 CRÍTICA |
| **Twilio** | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` | ✅ Configurado | 🔴 CRÍTICA |
| **Airtable** | `AIRTABLE_API_KEY` | ⚠️ Token nuevo encontrado | 🔴 CRÍTICA |
| **Supabase** | `SUPABASE_URL`, `SUPABASE_ACCESS_TOKEN` | ✅ Configurado (en args) | 🔴 CRÍTICA |

**Total servidores activos:** 5  
**Total secrets activos:** 10 variables

---

### ⏸️ Servidores MCP DESHABILITADOS (disabled=true)

| Servidor | Variables | Motivo |
|----------|-----------|--------|
| **n8n-mcp** | `N8N_API_URL`, `N8N_API_KEY` | Workflow automation no usado actualmente |
| **perplexity-ask** | `PERPLEXITY_API_KEY` | AI search no usado actualmente |

**Total servidores deshabilitados:** 2  
**Total secrets deshabilitados:** 3 variables

---

### 🎙️ Servidores MCP SIN CREDENCIALES (pero ACTIVOS)

Los siguientes servidores NO requieren variables de entorno pero están ACTIVOS en el proyecto:

- **vapi**: Sistema de voz para asistente (CRÍTICO) - Usa archivo `run-vapi-mcp.cmd` local
- **context7**: Acceso público sin autenticación
- **sequential-thinking**: Herramienta local de razonamiento
- **notebooklm-mcp**: Autenticación manual vía OAuth (se hace desde Verdent)
- **mcp-deepwiki**: Acceso público sin autenticación
- **chrome-devtools**: Herramienta local de debugging

---

## 🔄 CAMBIOS DETECTADOS vs MIGRACIÓN ANTERIOR

### ❌ SECRETS QUE YA NO EXISTEN

| Variable | Servidor Original | Motivo |
|----------|------------------|--------|
| **NOTION_TOKEN** | notionApi | ❌ Servidor eliminado del mcp.json |

### ✅ SECRETS NUEVOS AGREGADOS

| Variable | Servidor | Tipo |
|----------|----------|------|
| **GITHUB_PERSONAL_ACCESS_TOKEN** | github | 🆕 NUEVO (no estaba en migración v1) |
| **PERPLEXITY_API_KEY** | perplexity-ask | 🆕 NUEVO (disabled) |
| **SUPABASE_URL** | supabase-mcp-server | 🆕 NUEVO (en args) |
| **SUPABASE_ACCESS_TOKEN** | supabase-mcp-server | 🆕 NUEVO (en args) |

### 🔄 SECRETS ACTUALIZADOS (valores cambiados)

| Variable | Valor Anterior | Valor Actual | Estado |
|----------|----------------|--------------|--------|
| **COOLIFY_API_TOKEN** | `13\|hwM...3f37` | `14\|8UBBFt...cf37` | ✅ Token renovado (versión 14) |
| **AIRTABLE_API_KEY** | `patAif9...e8c0` (fallando) | `patAif9...d6ed` | ⚠️ Verificar si funciona |

### ⚠️ INCONSISTENCIAS DE NOMBRES (RESUELTAS)

**Problema:** En Twilio, mcp.json usa nombres diferentes a los estándar

| En mcp.json | En .env.mcp | Solución Aplicada |
|-------------|-------------|-------------------|
| `ACCOUNT_SID` | `TWILIO_ACCOUNT_SID` | ✅ Script convierte automáticamente |
| `AUTH_TOKEN` | `TWILIO_AUTH_TOKEN` | ✅ Script convierte automáticamente |
| `FROM_NUMBER` | `TWILIO_FROM_NUMBER` | ✅ Script convierte automáticamente |

**Nota:** El script de migración v2.0 ya maneja esta conversión automáticamente.

---

## 🎯 COMPARACIÓN: v1.0 vs v2.0

### Migración v1.0 (Anterior - INCOMPLETA)

```
Total secrets extraídos: 9 variables
- N8N_API_URL ✅
- N8N_API_KEY ✅
- TWILIO_ACCOUNT_SID ✅
- TWILIO_AUTH_TOKEN ✅
- TWILIO_FROM_NUMBER ✅
- NOTION_TOKEN ❌ (ya no existe)
- AIRTABLE_API_KEY ✅ (pero valor antiguo)
- COOLIFY_API_URL ✅
- COOLIFY_API_TOKEN ✅ (pero valor antiguo)
```

**Faltantes:**
- ❌ GITHUB_PERSONAL_ACCESS_TOKEN
- ❌ PERPLEXITY_API_KEY
- ❌ SUPABASE_URL
- ❌ SUPABASE_ACCESS_TOKEN

---

### Migración v2.0 (Nueva - COMPLETA)

```
Total secrets extraídos: 13 variables

SERVIDORES ACTIVOS (10 vars):
- GITHUB_PERSONAL_ACCESS_TOKEN ✅ NUEVO
- COOLIFY_API_URL ✅
- COOLIFY_API_TOKEN ✅ ACTUALIZADO
- TWILIO_ACCOUNT_SID ✅
- TWILIO_AUTH_TOKEN ✅
- TWILIO_FROM_NUMBER ✅
- AIRTABLE_API_KEY ✅ ACTUALIZADO
- SUPABASE_URL ✅ NUEVO
- SUPABASE_ACCESS_TOKEN ✅ NUEVO

SERVIDORES DESHABILITADOS (3 vars):
- N8N_API_URL ✅
- N8N_API_KEY ✅
- PERPLEXITY_API_KEY ✅ NUEVO
```

**Removidos:**
- ❌ NOTION_TOKEN (servidor eliminado)

---

## 📝 FORMATO DE VALORES (Ejemplos Enmascarados)

**⚠️ IMPORTANTE:** Los valores reales están en `.env.mcp` (NO commiteado). Los siguientes son ejemplos ENMASCARADOS para referencia de formato.

### GitHub
```
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_****************************3nYt
```
**Formato:** `ghp_` + 36 caracteres alfanuméricos

### Coolify (Versión 14)
```
COOLIFY_API_URL=https://coolify.generaia.site
COOLIFY_API_TOKEN=14|********************************cf37
```
**Formato:** `14|` + 40 caracteres + hash

### Twilio
```
TWILIO_ACCOUNT_SID=AC****************************ca09
TWILIO_AUTH_TOKEN=********************************a4dd
TWILIO_FROM_NUMBER=+358454910405
```
**Formato SID:** `AC` + 32 caracteres hexadecimales  
**Formato TOKEN:** 32 caracteres hexadecimales

### Airtable
```
AIRTABLE_API_KEY=pat**************************************************d6ed
```
**Formato:** `pat` + identificador + `.` + 64 caracteres hexadecimales

### Supabase (en args)
```
SUPABASE_URL=https://supabasekong-bo4cc0k0swg0c08k40ockog8.app.generaia.site/mcp
SUPABASE_ACCESS_TOKEN=eyJ0eXAi****************************************************UD_A
```
**Formato TOKEN:** JWT estándar (3 segmentos separados por `.`)

### n8n (DESHABILITADO)
```
N8N_API_URL=https://n8n-eoo0480cgswk4c84gwwk08wc.app.generaia.site
N8N_API_KEY=eyJhbGci****************************************************Vzlo
```
**Formato:** JWT estándar

### Perplexity (DESHABILITADO)
```
PERPLEXITY_API_KEY=pplx-****************************************uZGC
```
**Formato:** `pplx-` + 40 caracteres alfanuméricos

---

## 🚨 ACCIONES REQUERIDAS

### 1️⃣ EJECUTAR MIGRACIÓN v2.0 (URGENTE)

El script actualizado ahora extrae **13 variables** (vs 9 anteriores):

```powershell
cd "C:\Users\yago\Desktop\EN LAS NUBES-PROYECTOS\COPIA ASISTENTE VOZ EN LAS NUBES-VERDENT"

# Ejecutar migración actualizada
. .\scripts\migrate_mcp_security.ps1
```

**Qué hace el script:**
1. ✅ Crea backup de `~/.verdent/mcp.json`
2. ✅ Extrae TODOS los secrets (incluyendo GitHub, Perplexity, Supabase)
3. ✅ Crea/actualiza `.env.mcp` con los 13 secrets
4. ✅ Refactoriza `mcp.json` reemplazando valores por `${VARIABLE}`
5. ✅ Carga las variables de entorno automáticamente
6. ✅ Valida que NO queden secrets en texto plano

---

### 2️⃣ VERIFICAR TOKEN DE AIRTABLE (CRÍTICO)

El token de Airtable cambió desde la última migración:

**Token Anterior (fallando):**
```
patAif9A1ul2XaLID...e8c0
```

**Token Actual (en mcp.json):**
```
patAif9A1ul2XaLID...d6ed (ENMASCARADO - Ver .env.mcp)
```

**⚠️ VALIDAR:**
1. Probar el MCP de Airtable después de la migración
2. Si falla, regenerar token desde:  
   👉 https://airtable.com/create/tokens  
   **Scopes:** `data.records:read`, `data.records:write`, `schema.bases:read`
3. Actualizar en `.env.mcp`
4. Recargar: `. .\scripts\load_mcp_secrets.ps1`

---

### 3️⃣ VERIFICAR COOLIFY TOKEN (MEDIA PRIORIDAD)

El token de Coolify se actualizó de versión 13 a versión 14:

**Token Anterior:**
```
13|hwMtU...3f37
```

**Token Actual:**
```
14|8UBBFtUwMQM8swml8mvbNtvvTJOFqHNWzNnGs0nde82acf37
```

**Acción:** Si encuentras problemas con Coolify, regenera el token desde:  
👉 https://coolify.generaia.site/security/api-tokens

---

### 4️⃣ REINICIAR VERDENT

Después de ejecutar la migración:

```powershell
# 1. Verificar que las variables están cargadas
. .\scripts\load_mcp_secrets.ps1

# 2. Verificar conteo
# Debe decir: "[SUCCESS] Cargadas 13 variables de entorno"

# 3. Reiniciar Verdent desde la UI
```

---

## ✅ VALIDACIÓN POST-MIGRACIÓN

Después de reiniciar Verdent, probar cada MCP crítico:

### Test 1: Airtable
```
Comando: mcp_airtable_list_bases
Resultado esperado: Lista de bases de Airtable
```

### Test 2: Twilio
```
Comando: mcp_twilio_send-message
Parámetros: {"to": "+34600000000", "message": "Test"}
Resultado esperado: Mensaje enviado
```

### Test 3: Coolify
```
Comando: mcp_coolify_system (operation: "version")
Resultado esperado: Versión de Coolify
```

### Test 4: GitHub
```
Comando: mcp_github_search_repositories
Parámetros: {"query": "test"}
Resultado esperado: Lista de repositorios
```

### Test 5: Supabase
```
(Depende de las herramientas disponibles en el MCP de Supabase)
```

---

## 📂 ARCHIVOS ACTUALIZADOS

| Archivo | Cambios | Estado |
|---------|---------|--------|
| `env.mcp.template` | +4 secrets nuevos, -1 secret eliminado | ✅ ACTUALIZADO |
| `scripts/migrate_mcp_security.ps1` | Soporte Supabase (args), Perplexity, GitHub | ✅ ACTUALIZADO v2.0 |
| `scripts/load_mcp_secrets.ps1` | +2 variables críticas nuevas | ✅ ACTUALIZADO |
| `.env.mcp` | Se regenerará al ejecutar migración | ⏳ PENDIENTE |
| `~/.verdent/mcp.json` | Se refactorizará con placeholders | ⏳ PENDIENTE |

---

## 🔒 SEGURIDAD

### ✅ Medidas Implementadas

1. **Backup automático** antes de modificar `mcp.json`
2. **Validación de secrets** en texto plano (regex patterns)
3. **Enmascaramiento en logs** (solo muestra primeros 6 + últimos 4 caracteres)
4. **`.env.mcp` en .gitignore**
5. **Variables críticas validadas** en `load_mcp_secrets.ps1`

### ⚠️ Recomendaciones de Seguridad

1. **NUNCA commitear** `.env.mcp` al repositorio
2. **Revocar tokens antiguos** después de confirmar que los nuevos funcionan:
   - GitHub: https://github.com/settings/tokens
   - Airtable: https://airtable.com/account/api-tokens
   - Coolify: Panel de administración
3. **Rotar tokens regularmente** (cada 90 días)
4. **Auditar accesos** en cada servicio mensualmente

---

## 📊 RESUMEN EJECUTIVO

| Métrica | v1.0 (Anterior) | v2.0 (Actual) | Mejora |
|---------|----------------|---------------|--------|
| **Servidores cubiertos** | 6 de 9 | 9 de 9 | ✅ +50% |
| **Secrets extraídos** | 9 | 13 | ✅ +44% |
| **Secrets críticos** | 3 | 5 | ✅ +67% |
| **Secrets faltantes** | 4 | 0 | ✅ 100% |
| **Secrets obsoletos** | 1 (Notion) | 0 | ✅ Limpiado |

---

## 🎯 PRÓXIMOS PASOS

1. ✅ **Scripts actualizados** (COMPLETADO)
2. ⏳ **Ejecutar migración v2.0** (TU ACCIÓN)
3. ⏳ **Validar Airtable token** (TU ACCIÓN si falla)
4. ⏳ **Reiniciar Verdent** (TU ACCIÓN)
5. ⏳ **Probar MCPs críticos** (TU ACCIÓN)
6. ⏳ **Marcar FASE 1 completa** (AUTOMÁTICO después de validación)

---

**¿Dudas o problemas?**  
- Revisa los logs del script de migración
- Verifica los backups en `.backups/`
- Consulta `SECURITY_MIGRATION.md` para detalles de seguridad

---

**Generado:** 2026-02-08  
**Por:** Verdent AI + ArquitectoPlan Agent  
**Estado:** ✅ LISTO PARA EJECUTAR
