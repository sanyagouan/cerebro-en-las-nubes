# Plan de Rollback

> **Proyecto:** Cerebro En Las Nubes - Backend  
> **Última actualización:** 2026-03-07  
> **Estado:** Documentación Operativa

---

## 1. Resumen Ejecutivo

Este documento describe los procedimientos de rollback para el sistema **Cerebro En Las Nubes** en caso de fallos en producción.

---

## 2. Escenarios de Rollback

| Escenario | Trigger | Acción | Tiempo Máximo |
|-----------|---------|--------|---------------|
| **Deploy fallido** | Health check falla después de deploy | Rollback automático | 5 minutos |
| **Error rate alto** | >10% errores después de deploy | Rollback manual | 15 minutos |
| **Performance degradado** | Latencia >10s sostenida | Rollback manual | 30 minutos |
| **Bug crítico** | Reportado por usuario | Rollback manual + hotfix | 1 hora |

---

## 3. Procedimientos de Rollback

### Opción 1: Rollback vía Coolify UI

**Pasos:**

1. Acceder a Coolify Dashboard
2. Navegar a la aplicación `cerebro-backend`
3. Ir a la pestaña **Deployments**
4. Click en **Rollback** del deployment anterior (estado: "success")
5. Confirmar rollback
6. Verificar health check: `GET https://go84sgscs4ckcs08wog84o0o.app.generaia.site/health`

**Ventajas:**
- ✅ Más rápido (2-3 minutos)
- ✅ No requiere terminal
- ✅ Interfaz visual

**Desventajas:**
- ❌ Requiere acceso al panel de Coolify

---

### Opción 2: Rollback vía Git

**Pasos:**

```bash
# 1. Revertir el último commit
git revert HEAD

# 2. Push para disparar nuevo deploy
git push origin main
```

**Para volver a un commit específico:**

```bash
# 1. Ver historial de commits
git log --oneline -10

# 2. Resetear a commit seguro
git reset --hard <commit-sha-seguro>

# 3. Forzar push (⚠️ Usar con cuidado)
git push origin main --force
```

**Ventajas:**
- ✅ Rastro en Git
- ✅ Dispara CI/CD automáticamente

**Desventajas:**
- ❌ Más lento (esperar CI/CD)
- ❌ `--force` puede causar problemas si hay otros commits

---

### Opción 3: Rollback vía API de Coolify

**Script de PowerShell:**

```powershell
# scripts/rollback_deployment.ps1

param(
    [string]$AppUuid,
    [string]$DeploymentUuid
)

$COOLIFY_URL = "https://tu-coolify.com"
$API_TOKEN = $env:COOLIFY_API_TOKEN

# Ejecutar rollback
$rollbackBody = @{
    uuid = $DeploymentUuid
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod `
        -Method POST `
        -Uri "$COOLIFY_URL/api/v1/deployments/rollback" `
        -Body $rollbackBody `
        -Headers @{
            Authorization = "Bearer $API_TOKEN"
            "Content-Type" = "application/json"
        }
    
    Write-Host "✅ Rollback iniciado correctamente"
    Write-Host "UUID: $($response.uuid)"
    Write-Host "Status: $($response.status)"
}
catch {
    Write-Host "❌ Error en rollback: $_"
    exit 1
}
```

**Uso:**

```powershell
# Ejecutar rollback
.\scripts\rollback_deployment.ps1 -AppUuid "app-uuid" -DeploymentUuid "deployment-uuid"
```

**Ventajas:**
- ✅ Automatizable
- ✅ Rastro en logs

**Desventajas:**
- ❌ Requiere API token configurado
- ❌ Conocimiento técnico

---

## 4. Verificación Post-Rollback

### Checklist de Verificación

```markdown
## Post-Rollback Checklist

- [ ] Health check responde 200
- [ ] No hay errores 5xx en los últimos 5 minutos
- [ ] Latencia < 500ms en endpoint /health
- [ ] Redis responde correctamente
- [ ] Airtable responde correctamente
- [ ] Logs sin errores críticos
```

### Comandos de Verificación

```bash
# Health check básico
curl -f https://go84sgscs4ckcs08wog84o0o.app.generaia.site/health

# Health check profundo
curl -f https://go84sgscs4ckcs08wog84o0o.app.generaia.site/health/deep

# Verificar logs (si hay acceso SSH)
docker logs cerebro-backend --tail 100
```

---

## 5. Contactos de Emergencia

| Rol | Responsable | Contacto |
|-----|-------------|----------|
| **DevOps** | Equipo de Infraestructura | Ver configuración interna |
| **Backend Lead** | Equipo de Desarrollo | Ver configuración interna |
| **Coolify Admin** | Administrador del servidor | Ver configuración interna |

---

## 6. Lecciones Aprendidas

### Incidentes Recientes

| Fecha | Incidente | Causa | Resolución | Tiempo |
|-------|-----------|-------|------------|--------|
| - | - | - | - | - |

### Mejoras Pendientes

- [ ] Implementar rollback automático en CI/CD
- [ ] Añadir notificaciones Slack en caso de rollback
- [ ] Crear dashboard de monitoreo en tiempo real

---

## 7. Referencias

- [Plan CI/CD Completo](../plans/CI_CD_MONITOREO_PLAN.md)
- [Documentación de Coolify API](https://coolify.io/docs/api-reference)
- [Runbooks de Operaciones](./RUNBOOK.md) (si existe)

---

**Última revisión:** 2026-03-07  
**Mantenedor:** Equipo de DevOps
