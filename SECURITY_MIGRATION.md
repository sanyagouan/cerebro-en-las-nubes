# 🔐 Guía de Migración de Seguridad MCP

## ⚠️ URGENTE: Secrets Expuestos Detectados

Se han identificado **8 secrets en texto plano** en el archivo `~/.verdent/mcp.json`:

1. `GITHUB_TOKEN`
2. `N8N_API_KEY`
3. `TWILIO_ACCOUNT_SID`
4. `TWILIO_AUTH_TOKEN`
5. `TWILIO_FROM_NUMBER`
6. `NOTION_TOKEN`
7. `AIRTABLE_API_KEY`
8. `COOLIFY_API_TOKEN`

---

## 📋 Plan de Migración (5 pasos)

### **Paso 1: Crear archivo de secrets local**

```powershell
# Copiar template
Copy-Item .env.mcp.example .env.mcp

# Editar con tus secrets reales
notepad .env.mcp
```

**IMPORTANTE**: Completa TODOS los valores en `.env.mcp` con los secrets actuales de tu `mcp.json`.

---

### **Paso 2: Cargar variables de entorno**

```powershell
# Ejecutar script de carga
. .\scripts\load_mcp_secrets.ps1
```

Deberías ver:
```
🔐 Cargando secrets desde .env.mcp...

  ✓ GITHUB_TOKEN = ghp_vO...nu9f
  ✓ N8N_API_KEY = eyJhbG...r8wk
  ✓ TWILIO_ACCOUNT_SID = AC2e04...3ae05
  ...

✅ Cargadas 8 variables de entorno
```

---

### **Paso 3: Actualizar mcp.json**

**ANTES** (🔴 INSEGURO):
```json
{
  "airtable": {
    "env": {
      "AIRTABLE_API_KEY": "pat**********************..."
    }
  }
}
```

**DESPUÉS** (✅ SEGURO):
```json
{
  "airtable": {
    "env": {
      "AIRTABLE_API_KEY": "${AIRTABLE_API_KEY}"
    }
  }
}
```

**Ubicación del archivo**: `C:\Users\yago\.verdent\mcp.json`

**Cambios requeridos**:
- Reemplaza todos los valores hardcoded por `${VARIABLE_NAME}`
- Aplica esto a los servidores MCP que contienen secrets

---

### **Paso 4: Regenerar tokens comprometidos**

#### 🔴 **CRÍTICO - Airtable**

El token debe regenerarse si está comprometido:

1. Ve a https://airtable.com/create/tokens
2. Crea un nuevo token con scopes:
   - ✅ `data.records:read`
   - ✅ `data.records:write`
   - ✅ `schema.bases:read`
3. Copia el nuevo token a `.env.mcp`:
   ```env
   AIRTABLE_API_KEY=patNUEVO_TOKEN_AQUI
   ```
4. Revoca el token anterior desde Airtable dashboard

#### 🟡 **RECOMENDADO - GitHub**

Si el token tiene scope `repo` (acceso completo a repositorios):

1. Ve a https://github.com/settings/tokens
2. Revoca el token antiguo/comprometido
3. Crea uno nuevo con scope mínimo necesario
4. Actualiza `.env.mcp`

#### 🟢 **OPCIONAL - Twilio/Coolify**

Si sospechas que estos tokens han sido comprometidos, regenera desde sus dashboards respectivos.

---

### **Paso 5: Validar todo funciona**

```powershell
# Test 1: Verificar que NO hay secrets hardcoded
Select-String -Path ~/.verdent/mcp.json -Pattern "ghp_|eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9|AC2e04"
# Resultado esperado: 0 matches

# Test 2: Verificar conexión Airtable
python -c "from pyairtable import Api; import os; api = Api(os.getenv('AIRTABLE_API_KEY')); print(f'✅ Bases: {len(api.bases())}')"

# Test 3: Verificar cache Redis
python -c "from src.infrastructure.cache.redis_cache import RedisCache; rc = RedisCache(); print('✅ Cache health:', rc.get_health())"
```

---

## 🚨 ¿Qué hacer si algo falla?

### Error: "AIRTABLE_API_KEY not found"

**Causa**: No se cargaron las variables de entorno.

**Solución**:
```powershell
# Re-ejecutar script de carga
. .\scripts\load_mcp_secrets.ps1

# Verificar que se cargó
$env:AIRTABLE_API_KEY
# Debe mostrar el token
```

---

### Error: "Invalid authentication token" (Airtable)

**Causa**: Token expirado o con scopes incorrectos.

**Solución**: Ve al **Paso 4** y regenera el token con los scopes correctos.

---

### Error: "mcp.json no se actualiza"

**Causa**: Verdent carga el config en startup.

**Solución**: **Reinicia Verdent** después de modificar `mcp.json`.

---

## ✅ Checklist de Validación

Antes de considerar la migración completa:

- [ ] `.env.mcp` creado y completado con todos los secrets
- [ ] `.env.mcp` está en `.gitignore` (verificar con `git status`)
- [ ] `load_mcp_secrets.ps1` ejecutado correctamente
- [ ] `~/.verdent/mcp.json` refactorizado con `${VARIABLES}`
- [ ] Test de Airtable pasó (conexión exitosa)
- [ ] Test de Redis pasó (cache funcional)
- [ ] NO hay secrets en texto plano en `mcp.json` (verificado con grep)
- [ ] Tokens antiguos revocados (GitHub, Airtable)

---

## 📚 Recursos Adicionales

- **Airtable Tokens**: https://airtable.com/create/tokens
- **GitHub Tokens**: https://github.com/settings/tokens
- **Twilio Dashboard**: https://console.twilio.com/
- **Coolify Dashboard**: https://coolify.generaia.site

---

## 🔒 Mejores Prácticas de Seguridad

### DO ✅
- Almacenar secrets en `.env.mcp` (gitignored)
- Usar referencias `${VAR}` en configs
- Regenerar tokens comprometidos inmediatamente
- Limitar scopes de tokens al mínimo necesario

### DON'T ❌
- Commitear `.env.mcp` al repositorio
- Compartir tokens en chats/emails
- Usar tokens con permisos excesivos
- Dejar tokens antiguos activos tras regenerarlos

---

**Última actualización**: 2026-02-08  
**Autor**: Equipo Verdent + Arquitecto Plan Agent
