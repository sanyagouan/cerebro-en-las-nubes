# Conexión Frontend-Backend (Dashboard React)

**Fecha:** 2026-03-07  
**Estado:** ✅ CONECTADO - Usando API Real

---

## 📋 Diagnóstico del Estado Actual

### ✅ Configuración de API ([`dashboard/src/config/api.ts`](dashboard/src/config/api.ts))

El frontend **YA ESTÁ CONFIGURADO** para conectarse al backend real:

```typescript
// Desarrollo: proxy Vite → http://127.0.0.1:8000
// Producción: VITE_API_URL o fallback a Coolify
const VITE_API_URL = (import.meta as any).env?.VITE_API_URL;
const isDev = (import.meta as any).env?.DEV === true;
export const API_BASE_URL = VITE_API_URL || (isDev ? '' : 'https://go84sgscs4ckcs08wog84o0o.app.generaia.site');
```

**Características:**
- ✅ Interceptor JWT automático en cada petición
- ✅ Manejo de errores 401 (redirección a login)
- ✅ Soporte para proxy Vite en desarrollo

---

### ✅ Hooks Conectados a la API Real

| Hook | Estado | Endpoint Backend |
|------|--------|------------------|
| [`useReservations.ts`](dashboard/src/hooks/useReservations.ts) | ✅ API Real | `/api/mobile/reservations` |
| [`useTables.ts`](dashboard/src/hooks/useTables.ts) | ✅ API Real | `/api/mobile/tables` |
| [`useClientes.ts`](dashboard/src/hooks/useClientes.ts) | ✅ API Real | `/api/clients` |
| [`useWebSocket.ts`](dashboard/src/hooks/useWebSocket.ts) | ✅ WS Real | `/ws/reservations` |

**Todos los hooks usan `axios` con la instancia configurada en [`api.ts`](dashboard/src/config/api.ts).**

---

### ✅ CORS Configurado ([`src/main.py`](src/main.py:38))

```python
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
)
```

---

## 🔗 Mapeo de Endpoints Frontend ↔ Backend

### Reservas

| Frontend Hook | Endpoint | Backend Router |
|---------------|----------|----------------|
| `fetchReservations()` | `GET /api/mobile/reservations` | [`mobile_api.py:812`](src/api/mobile/mobile_api.py:812) |
| `fetchReservation(id)` | `GET /api/mobile/reservations/{id}` | [`mobile_api.py:891`](src/api/mobile/mobile_api.py:891) |
| `createReservation()` | `POST /api/mobile/reservations` | [`mobile_api.py:1095`](src/api/mobile/mobile_api.py:1095) |
| `updateReservation()` | `PUT /api/mobile/reservations/{id}` | [`mobile_api.py:936`](src/api/mobile/mobile_api.py:936) |
| `cancelReservation()` | `POST /api/mobile/reservations/{id}/cancel` | [`mobile_api.py:1158`](src/api/mobile/mobile_api.py:1158) |
| `updateReservationStatus()` | `PUT /api/mobile/reservations/{id}/status` | [`mobile_api.py:1009`](src/api/mobile/mobile_api.py:1009) |

### Mesas

| Frontend Hook | Endpoint | Backend Router |
|---------------|----------|----------------|
| `fetchTables()` | `GET /api/mobile/tables` | [`mobile_api.py:1324`](src/api/mobile/mobile_api.py:1324) |
| `createTable()` | `POST /api/mobile/tables` | [`mobile_api.py:1451`](src/api/mobile/mobile_api.py:1451) |
| `updateTable()` | `PUT /api/mobile/tables/{id}` | [`mobile_api.py:1516`](src/api/mobile/mobile_api.py:1516) |
| `deleteTable()` | `DELETE /api/mobile/tables/{id}` | [`mobile_api.py:1598`](src/api/mobile/mobile_api.py:1598) |
| `updateTableStatus()` | `PUT /api/mobile/tables/{id}/status` | [`mobile_api.py:1631`](src/api/mobile/mobile_api.py:1631) |

### Clientes (CRM)

| Frontend Hook | Endpoint | Backend Router |
|---------------|----------|----------------|
| `useCustomers()` | `GET /api/clients` | [`clients_api.py:144`](src/api/dashboard/clients_api.py:144) |
| `useCustomer()` | `GET /api/clients/{id}` | [`clients_api.py:225`](src/api/dashboard/clients_api.py:225) |
| `useCustomerStats()` | `GET /api/clients/stats` | [`clients_api.py:156`](src/api/dashboard/clients_api.py:156) |
| `useSearchCustomers()` | `GET /api/clients/search` | [`clients_api.py:197`](src/api/dashboard/clients_api.py:197) |
| `useCustomerReservations()` | `GET /api/clients/{id}/reservations` | [`clients_api.py:241`](src/api/dashboard/clients_api.py:241) |

### WebSocket

| Frontend Hook | Endpoint | Backend Router |
|---------------|----------|----------------|
| `useWebSocket()` | `WS /ws/reservations` | [`reservations_ws.py:55`](src/api/websocket/reservations_ws.py:55) |

---

## ⚙️ Variables de Entorno

### Frontend (Dashboard)

Crear archivo [`dashboard/.env.local`](dashboard/.env.local):

```bash
# Desarrollo local (proxy Vite activo)
VITE_API_URL=

# O especificar backend remoto
# VITE_API_URL=https://go84sgscs4ckcs08wog84o0o.app.generaia.site
```

### Backend (Coolify)

Configurar en Coolify:

```bash
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,https://tu-dashboard.com
```

---

## 🧪 Instrucciones de Prueba

### 1. Desarrollo Local

```bash
# Terminal 1: Iniciar backend
cd /path/to/project
python -m uvicorn src.main:app --reload --port 8000

# Terminal 2: Iniciar frontend
cd dashboard
npm install
npm run dev
```

**El frontend estará en:** http://localhost:3000  
**El backend está en:** http://localhost:8000  
**Proxy Vite:** Las peticiones `/api/*` se redirigen automáticamente al backend

### 2. Verificar Conexión

1. **Health Check:**
   ```bash
   curl http://localhost:8000/health
   # Esperado: {"status": "healthy", ...}
   ```

2. **Login:**
   - Abrir http://localhost:3000
   - Iniciar sesión con credenciales válidas
   - Verificar que el JWT se guarda en localStorage

3. **Reservas:**
   - Navegar a la pestaña "Reservas"
   - Verificar que carga datos reales (no vacío si hay reservas en Airtable)

4. **WebSocket:**
   - Abrir DevTools → Network → WS
   - Verificar conexión a `ws://localhost:8000/ws/reservations`

### 3. Producción

```bash
# Build del frontend
cd dashboard
npm run build

# Los archivos estáticos se generan en dashboard/dist/
# Configurar nginx o Coolify para servir estos archivos
```

**Variables requeridas en Coolify:**
- `VITE_API_URL` → URL del backend (ej: `https://api.tu-restaurante.com`)

---

## 🔧 Troubleshooting

### Error: CORS

**Síntoma:** `Access-Control-Allow-Origin` errors en consola

**Solución:**
1. Verificar `ALLOWED_ORIGINS` en el backend incluye la URL del frontend
2. En desarrollo, Vite proxy evita CORS (no debería pasar)

### Error: 401 Unauthorized

**Síntoma:** Peticiones API retornan 401

**Solución:**
1. Verificar que el JWT está en localStorage (`token`)
2. El interceptor de axios lo inyecta automáticamente
3. Si el token expiró, usar refresh token o re-login

### Error: WebSocket no conecta

**Síntoma:** `WebSocket connection failed`

**Solución:**
1. Verificar que el backend está corriendo
2. El WebSocket requiere JWT en query params: `?token=xxx`
3. Verificar que el token es válido (no expirado)

### Error: Datos vacíos

**Síntoma:** Las tablas muestran vacío pero hay datos en Airtable

**Solución:**
1. Verificar credenciales de Airtable en el backend
2. Revisar logs del backend para errores de Airtable API
3. El backend retorna lista vacía si Airtable no está disponible

---

## 📁 Archivos Creados/Modificados

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| [`dashboard/.env.example`](dashboard/.env.example) | Creado | Template de variables de entorno |
| [`docs/CONEXION_FRONTEND_BACKEND.md`](docs/CONEXION_FRONTEND_BACKEND.md) | Creado | Esta documentación |

---

## ✅ Conclusión

**El frontend YA ESTÁ CONECTADO al backend real.** No se requieren cambios adicionales en los hooks.

La configuración actual soporta:
- ✅ Desarrollo local con proxy Vite
- ✅ Producción con URL configurada
- ✅ Autenticación JWT automática
- ✅ WebSocket para actualizaciones en tiempo real
- ✅ Manejo de errores y re-autenticación
