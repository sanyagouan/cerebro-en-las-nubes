# 🔐 INSTRUCCIONES IMPORTANTES - MIGRACIÓN DE SEGURIDAD

## ⚠️ ACCIÓN INMEDIATA REQUERIDA

Antes de continuar con el proyecto, **DEBES completar la migración de seguridad** para proteger los secrets expuestos en `mcp.json`.

---

## 🚀 Inicio Rápido (3 comandos)

```powershell
# 1. Crear archivo de secrets desde template
Copy-Item env.mcp.template .env.mcp

# 2. EDITAR .env.mcp y completar con tus secrets reales
#    (Ver sección "Secrets Actuales" abajo)
notepad .env.mcp

# 3. Cargar variables de entorno
. .\scripts\load_mcp_secrets.ps1
```

---

## 📝 Secrets Actuales que Debes Migrar

**Tu `~/.verdent/mcp.json` contiene secrets en texto plano que deben migrarse:**

### 🔴 CRÍTICOS (producción)

1. **AIRTABLE_API_KEY**: `pat**********************D...` 
   - ⚠️ **Regenerar desde** https://airtable.com/create/tokens

2. **TWILIO_ACCOUNT_SID**: `AC********************************05`

3. **TWILIO_AUTH_TOKEN**: `********************************aa0`

4. **COOLIFY_API_TOKEN**: `14|**************************************4a`

### 🟡 OPCIONALES (desarrollo)

5. **GITHUB_TOKEN**: `ghp_************************************9f`

6. **N8N_API_KEY**: `eyJ****************************************************8wk`

7. **NOTION_TOKEN**: `ntn_******************************************7sH`

---

## 📋 Documentación Completa

Lee el archivo `SECURITY_MIGRATION.md` para la guía completa con:
- Pasos detallados de migración
- Regeneración de tokens
- Validación y troubleshooting
- Mejores prácticas de seguridad

---

## ✅ Checklist de Verificación

Antes de continuar con desarrollo:

- [ ] `.env.mcp` creado con TODOS los secrets actuales
- [ ] `load_mcp_secrets.ps1` ejecutado sin errores
- [ ] Nuevo token Airtable generado y probado
- [ ] `mcp.json` actualizado con referencias `${VAR}` (próximo paso)
- [ ] Tokens antiguos revocados

---

**SIGUIENTE PASO**: Después de completar esta migración, continuaremos con:
- FASE 2: Configuración NotebookLM
- FASE 3: Generación AGENTS.md
- FASE 4: Auditoría Arquitectónica
- FASE 5: Optimización Redis/Airtable

**¿Dudas?** Revisa `SECURITY_MIGRATION.md` o pregunta al equipo.
