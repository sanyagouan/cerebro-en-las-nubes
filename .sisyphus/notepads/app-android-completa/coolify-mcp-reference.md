# Referencia MCP Coolify

## Operaciones disponibles

### coolify_applications

| Operación | Descripción | Parámetros |
|-----------|-------------|------------|
| `list` | Lista todas las aplicaciones | - |
| `get` | Obtiene detalles de una aplicación | `id` (uuid) |
| `get_logs` | Obtiene logs del contenedor | `id` (uuid) |
| `start` | Inicia/despliega una aplicación | `id` (uuid) |
| `stop` | Detiene una aplicación | `id` (uuid) |

### Ejemplos

```
// Listar aplicaciones
coolify_applications(operation="list")

// Obtener aplicación
coolify_applications(id="go84sgscs4ckcs08wog84o0o", operation="get")

// Iniciar/desplegar
coolify_applications(id="go84sgscs4ckcs08wog84o0o", operation="start")

// Detener
coolify_applications(id="go84sgscs4ckcs08wog84o0o", operation="stop")

// Obtener logs
coolify_applications(id="go84sgscs4ckcs08wog84o0o", operation="get_logs")
```

### coolify_deployments

| Operación | Descripción | Estado |
|-----------|-------------|--------|
| `list` | Lista deployments | ❌ Devuelve vacío |
| `deploy` | Despliega | ❌ ERROR: "You must provide uuid or tag" |

**NOTA**: El MCP de `coolify_deployments` NO funciona correctamente. Usar `coolify_applications` con `operation="start"` en su lugar.

---

## Limitaciones conocidas

1. **No hay parámetro `force`**: El MCP no permite forzar rebuild sin caché
2. **No hay logs del build**: Solo se pueden ver logs del contenedor, no del proceso de build
3. **`coolify_deployments` roto**: La operación `deploy` no acepta parámetros correctamente

---

## Workaround para forzar rebuild

1. Hacer `stop` de la aplicación
2. Esperar a que se detenga
3. Hacer `start` de la aplicación
4. Si persiste caché, intervenir manualmente desde el panel de Coolify con "Force rebuild"

---

## API REST alternativa

Si el MCP falla, se puede usar la API REST directamente:

```
GET /applications/{uuid}/start?force=true&instant_deploy=true
Authorization: Bearer {token}
```

**URL base**: La URL del panel de Coolify (ej: `https://coolify.tu-dominio.com/api/v1`)

---

**Última actualización**: 2026-02-22
