# Instrucciones para Iniciar Testing de Integración
**Fecha**: 2025-02-15  
**Fase**: Phase 2, Week 4 - Integration Testing  
**Estado**: Listo para ejecutar  

---

## 📋 RESUMEN EJECUTIVO

Has completado Days 16-17 (Frontend Integration) al **90%**. Ahora necesitas verificar que el frontend y backend funcionan juntos correctamente mediante pruebas de integración locales.

**Estado actual detectado**:
- ✅ Frontend dependencies instaladas (node_modules existe)
- ❌ Backend NO está corriendo (localhost:8000 no responde)
- ✅ Documentación de testing creada
- ✅ Worktree "serene-mccarthy" activo

---

## 🚀 PASO 1: INICIAR BACKEND

### Opción A: Ventana PowerShell/CMD (Recomendado)

```powershell
# 1. Abre una nueva ventana de PowerShell/CMD

# 2. Navega al proyecto principal (NO al worktree)
cd "C:\Users\yago\Desktop\EN LAS NUBES-PROYECTOS\CLAUDE-COPIA VERDENT-ASISTENTE-VOZ-EN LAS NUBES"

# 3. Activa el entorno virtual de Python
.venv\Scripts\activate

# 4. Inicia el servidor backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Salida esperada**:
```
INFO:     Will watch for changes in these directories: [...]
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXX] using WatchFiles
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Verificar que funciona:

```powershell
# En OTRA ventana PowerShell/CMD:
curl http://localhost:8000/health

# Salida esperada:
# {"status":"ok","timestamp":"2025-02-15T..."}
```

**⚠️ IMPORTANTE**: Deja esta ventana abierta ejecutándose. El backend debe estar corriendo durante todas las pruebas.

---

## 🚀 PASO 2: INICIAR FRONTEND

### Opción A: Ventana PowerShell/CMD (Recomendado)

```powershell
# 1. Abre OTRA ventana de PowerShell/CMD (el backend sigue corriendo en la primera)

# 2. Navega al dashboard en el WORKTREE
cd "C:\Users\yago\Desktop\EN LAS NUBES-PROYECTOS\CLAUDE-COPIA VERDENT-ASISTENTE-VOZ-EN LAS NUBES\.claude\worktrees\serene-mccarthy\dashboard"

# 3. Inicia el servidor de desarrollo de Vite
npm run dev
```

**Salida esperada**:
```
VITE v5.4.11  ready in XXX ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
➜  press h + enter to show help
```

**⚠️ IMPORTANTE**: Deja esta ventana abierta también. El frontend debe estar corriendo durante todas las pruebas.

---

## 🧪 PASO 3: ABRIR NAVEGADOR Y DEVTOOLS

1. Abre tu navegador (Chrome/Edge recomendado)

2. Navega a: `http://localhost:3000`

3. Abre DevTools:
   - Presiona **F12** o
   - Click derecho → "Inspect" → "Inspect Element"

4. Ve a las siguientes pestañas:
   - **Console**: Para ver errores JavaScript
   - **Network**: Para ver requests HTTP a la API

**✅ Si todo está bien**: Deberías ver la pantalla de Login del dashboard.

---

## 🧪 PASO 4: EJECUTAR TESTS MANUALMENTE

### Test 1: Authentication Flow ⏰ 2 minutos

**Objetivo**: Verificar que el login funciona y guarda el token.

**Pasos**:
1. En el navegador (`http://localhost:3000`), deberías ver el formulario de login
2. Abre DevTools → **Network tab**
3. En el login form, ingresa:
   - **Usuario**: `admin`
   - **Contraseña**: `admin123` (o revisa `dashboard/src/components/Login.tsx` para credenciales correctas)
4. Click en "Iniciar Sesión" o equivalente

**Verifica en DevTools Network**:
- ✅ Aparece request `POST /api/auth/login`
- ✅ Status code: **200** (success)
- ✅ Response body contiene: `{"access_token": "...", "token_type": "bearer"}`

**Verifica en DevTools Application**:
- Ve a: **Application** → **Local Storage** → `http://localhost:3000`
- ✅ Existe key `token` con un valor largo (JWT)

**Verifica en UI**:
- ✅ Redirige automáticamente al Dashboard
- ✅ Se ve el sidebar con navegación (Reservas, Mesas, etc.)

**Si falla**:
- **404 en /api/auth/login**: Endpoint no existe en backend → Revisar `src/api/auth_router.py`
- **401 Unauthorized**: Credenciales incorrectas → Revisar usuarios demo en backend
- **CORS error**: Backend CORS mal configurado → Revisar `src/main.py`
- **Network error**: Backend no corriendo → Volver a Paso 1

---

### Test 2: Dashboard Stats Loading ⏰ 1 minuto

**Objetivo**: Verificar que el Dashboard carga estadísticas reales.

**Pasos**:
1. Después de login exitoso, estás en Dashboard
2. En DevTools → **Network tab**, verifica requests:

**Verifica requests**:
- ✅ `GET /api/stats` (status 200)
- ✅ `GET /api/reservas` (status 200) - opcional, depende del componente

**Verifica UI**:
- ✅ Cards de estadísticas muestran números:
  - Total Reservas: X
  - Confirmadas: X
  - Mesas Disponibles: X
  - Etc.
- ✅ Si hay lista de "Reservas Recientes", se muestra data
- ✅ NO aparecen spinners de carga infinitos

**Si falla**:
- **404 en /api/stats**: Endpoint no existe → Revisar backend
- **500 error**: Backend crash → Revisar logs de backend en la ventana PowerShell
- **Stuck on loading**: Verificar que endpoint responde correctamente

---

### Test 3: Reservas List ⏰ 2 minutos

**Objetivo**: Verificar que la lista de reservas carga correctamente.

**Pasos**:
1. En el sidebar, click en "**Reservas**"
2. Espera a que cargue la vista

**Verifica en Network**:
- ✅ `GET /api/reservas` (status 200)
- ✅ Response body es array de objetos reserva

**Verifica en UI**:
- ✅ Se muestra grid/lista de reservas
- ✅ Cada card/row muestra:
  - Nombre del cliente
  - Teléfono
  - Fecha y hora
  - Número de personas
  - Mesa asignada (si existe)
  - **Estado con badge de color**:
    - Pendiente → Amarillo
    - Confirmada → Azul
    - Sentada → Púrpura
    - Completada → Verde
    - Cancelada → Rojo
- ✅ Filtros disponibles (Hoy, Semana, Mes, Por estado)

**Si falla**:
- **404 en /api/reservas**: Endpoint no implementado
- **Empty state**: Backend no tiene data → Crear reservas de prueba manualmente en Airtable
- **UI rota**: Revisar Console para errores JavaScript

---

### Test 4: Create Reservation ⏰ 3 minutos

**Objetivo**: Verificar que se puede crear una nueva reserva.

**Pasos**:
1. En vista Reservas, busca botón "**+ Nueva Reserva**" o similar
2. Click en el botón
3. Debería abrir un **modal/dialog** con formulario

**Llenar formulario**:
- **Nombre**: "Test Integration"
- **Teléfono**: "612345678"
- **Fecha**: Mañana (selecciona del date picker)
- **Hora**: "20:00"
- **Número de personas**: "4"
- **Zona**: "Interior" (o "Terraza")
- **Solicitudes especiales** (opcional): "Ventana"

4. Click en "**Crear Reserva**" o equivalente

**Verifica en Network**:
- ✅ `POST /api/reservas` con body JSON
- ✅ Status 201 (Created) o 200 (OK)
- ✅ Response body contiene la reserva creada con ID

**Verifica en UI**:
- ✅ Modal se cierra automáticamente
- ✅ **La nueva reserva aparece inmediatamente en la lista** (optimistic update)
- ✅ Toast notification verde: "Reserva creada exitosamente" (o similar)
- ✅ La lista se refresca (React Query invalidation)

**Si falla**:
- **400 Bad Request**: Validación falló → Revisar error message en response
- **Reserva no aparece**: Cache no invalidado → Revisar `useReservations.ts`
- **No toast notification**: Sistema de toast no configurado → Revisar si existe librería

---

### Test 5: Update Reservation ⏰ 2 minutos

**Objetivo**: Verificar que se puede editar una reserva existente.

**Pasos**:
1. En la lista de reservas, encuentra una reserva de test
2. Click en botón "**Editar**" (puede ser icono de lápiz)
3. Modal se abre con datos pre-llenados

**Modificar**:
- Cambia "**Número de personas**" de 4 a **6**
4. Click en "**Actualizar Reserva**"

**Verifica en Network**:
- ✅ `PUT /api/reservas/{id}` con body JSON
- ✅ Status 200 (OK)

**Verifica en UI**:
- ✅ Modal se cierra
- ✅ Card de reserva muestra nuevo valor: **6 personas**
- ✅ Toast notification: "Reserva actualizada"

---

### Test 6: Cancel Reservation ⏰ 2 minutos

**Objetivo**: Verificar cancelación de reservas.

**Pasos**:
1. Encuentra una reserva con estado "**Pendiente**" o "**Confirmada**"
2. Click en botón "**Cancelar**"
3. Confirma en dialog de confirmación

**Verifica en Network**:
- ✅ `POST /api/reservas/{id}/cancel` (status 200)

**Verifica en UI**:
- ✅ Estado cambia a "**Cancelada**"
- ✅ Badge se vuelve **rojo**
- ✅ Toast notification: "Reserva cancelada"

---

### Test 7-14: Tests Adicionales

**Por brevedad**, los tests 7-14 están documentados en detalle en:
- `INTEGRATION_TESTING_GUIDE.md` (guía completa)
- `INTEGRATION_TEST_RESULTS.md` (log de resultados)

**Tests restantes**:
- Test 7: State Transitions (Confirmar → Sentar → Completar)
- Test 8-11: CRUD de Mesas (List, Create, Toggle Status, Delete)
- Test 12: Error Handling (backend down, 401, etc.)
- Test 13: Loading States (spinners)
- Test 14: Authentication Persistence (refresh page)

**Ejecuta estos tests siguiendo la misma metodología**:
1. Sigue pasos en `INTEGRATION_TESTING_GUIDE.md`
2. Documenta resultados en `INTEGRATION_TEST_RESULTS.md`
3. Si encuentras errores, crea `INTEGRATION_ISSUES_LOG.md`

---

## 📝 PASO 5: DOCUMENTAR RESULTADOS

### Después de cada test:

1. Abre: `INTEGRATION_TEST_RESULTS.md`

2. Actualiza la sección del test:
   ```markdown
   ### 🔐 Test 1: Authentication Flow
   **Status**: ✅ PASSED (o ❌ FAILED)
   **Time Started**: 22:30
   **Time Completed**: 22:32
   
   **Results**:
   - POST /api/auth/login: ✅ 200 OK
   - Token saved: ✅ Yes
   - Redirect: ✅ Yes
   - Sidebar visible: ✅ Yes
   
   **Issues Found**: None (o describir problemas)
   ```

3. Si encuentras errores críticos, crea `INTEGRATION_ISSUES_LOG.md`:
   ```markdown
   ### Issue #1: Login endpoint returns 404
   **Date**: 2025-02-15 22:35
   **Component**: Backend
   **Severity**: Critical
   
   **Symptoms**:
   - POST /api/auth/login returns 404
   
   **Root Cause**:
   - Endpoint not registered in router
   
   **Fix Applied**:
   - Added endpoint to auth_router.py
   
   **Status**: Resolved
   ```

---

## ✅ CRITERIOS DE ÉXITO

**Integration Testing se considera PASADO cuando**:

- ✅ Todos los 14 tests ejecutados
- ✅ Al menos **12 de 14 tests pasan** (85% success rate)
- ✅ Errores críticos resueltos (login, create, read operations)
- ✅ No crashes en navegador (no console.error)
- ✅ No 500 errors en backend

**Errores aceptables** (no críticos):
- Algunos loading states no perfectos
- Algún toast notification faltante
- Pequeños bugs de UI/UX

**Errores NO aceptables** (críticos):
- Login no funciona
- No se pueden crear reservas
- No se pueden listar reservas/mesas
- Backend crashea
- Frontend crashea

---

## 🎯 SIGUIENTE PASO DESPUÉS DE TESTING

### Si todos los tests pasan ✅:

1. Actualiza todo list:
   ```markdown
   - [completed] Perform integration testing: Backend + Frontend locally
   - [in_progress] Days 18-19: Verify ReservaForm integration with check_availability
   ```

2. Crea documento final de resumen:
   - `INTEGRATION_TESTING_SUMMARY.md`
   - Incluye: tests passed, issues found, fixes applied, next steps

3. **Procede a Days 18-19**: ReservaForm refinement con `check_availability`

### Si hay fallos críticos ❌:

1. **NO avances** a Days 18-19

2. Prioriza fixes:
   - **P0 (Crítico)**: Login, CRUD básico (Create, Read)
   - **P1 (Alto)**: Update, Delete, State transitions
   - **P2 (Medio)**: Loading states, Error handling
   - **P3 (Bajo)**: UX polish, animations

3. Implementa fixes uno por uno

4. Re-ejecuta tests afectados

5. Solo avanza cuando success rate ≥85%

---

## 🛠️ TROUBLESHOOTING RÁPIDO

### Backend no inicia:
```bash
# Verificar que .venv existe
ls .venv/Scripts/activate

# Si no existe, crear:
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend no inicia:
```bash
cd dashboard
# Reinstalar dependencies
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Puerto 8000 ocupado:
```bash
# Cambiar puerto del backend
uvicorn src.main:app --reload --port 8001

# Actualizar dashboard/vite.config.ts:
# target: 'http://localhost:8001'
```

### CORS errors:
```python
# En src/main.py, verificar:
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📞 AYUDA Y RECURSOS

**Documentos de referencia**:
- `INTEGRATION_TESTING_GUIDE.md` - Guía completa de tests
- `INTEGRATION_TEST_RESULTS.md` - Log de resultados
- `DAYS_16_17_COMPLETION_REPORT.md` - Estado del frontend
- `DAYS_14_15_PROGRESS.md` - Estado del backend

**Archivos clave**:
- Backend: `src/main.py`, `src/api/auth_router.py`, `src/api/mobile/mobile_api.py`
- Frontend: `dashboard/src/App.tsx`, `dashboard/src/hooks/*.ts`, `dashboard/src/components/*.tsx`

---

**¡Buena suerte con el testing! 🚀**  
**Recuerda**: Documenta TODO en `INTEGRATION_TEST_RESULTS.md`
