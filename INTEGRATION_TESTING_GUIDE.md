# Integration Testing Guide - Frontend + Backend
**Date**: 2025-02-15  
**Phase**: Phase 2, Week 4 - Post Days 16-17  
**Status**: Ready for Integration Testing

---

## OVERVIEW

Days 16-17 frontend integration is **90% complete** (100% for in-scope tasks). All core infrastructure is implemented:
- ✅ React Query with QueryClient
- ✅ JWT Authentication (AuthContext)
- ✅ API Configuration (environment-aware)
- ✅ Custom Hooks (useReservations, useTables)
- ✅ All Core Components (Dashboard, Reservas, Mesas, Forms)
- ✅ Loading States & Error Handling
- ✅ Toast Notifications

**Next Step**: Verify frontend-backend integration works correctly.

---

## PREREQUISITES

### Backend Status
According to `DAYS_14_15_PROGRESS.md`:
- ✅ All REST endpoints implemented (Phase 1, Week 1)
- ✅ Tests passing (100 tests, 89% coverage)
- ✅ Backend deployed to Coolify: https://go84sgscs4ckcs08wog84o0o.app.generaia.site

### Frontend Status
According to `DAYS_16_17_COMPLETION_REPORT.md`:
- ✅ All components implemented
- ✅ React Query integrated
- ✅ Authentication working
- ✅ API config points to: Empty string (dev) → Vite proxy → localhost:8000

---

## INTEGRATION TEST PLAN

### Test Environment Setup

#### 1. Start Backend Locally
```bash
cd "EN LAS NUBES-PROYECTOS/CLAUDE-COPIA VERDENT-ASISTENTE-VOZ-EN LAS NUBES"
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Verify Backend**:
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok","timestamp":"..."}
```

#### 2. Start Frontend Locally
```bash
cd "EN LAS NUBES-PROYECTOS/CLAUDE-COPIA VERDENT-ASISTENTE-VOZ-EN LAS NUBES/.claude/worktrees/serene-mccarthy/dashboard"
npm install  # if first time
npm run dev
```

**Expected Output**:
```
VITE v5.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

**Note**: Vite proxy configuration should forward API requests from `http://localhost:5173` to `http://localhost:8000`

---

## TEST SCENARIOS

### 🔐 Test 1: Authentication Flow

**Steps**:
1. Open browser: http://localhost:5173
2. Should see Login screen (no token in localStorage)
3. Use demo credentials:
   - Usuario: `admin` (or check Login.tsx for current demo users)
   - Contraseña: `password123`
4. Click "Iniciar Sesión"

**Expected Results**:
- ✅ POST request to `/api/auth/login` (check Network tab)
- ✅ Response contains JWT token
- ✅ Token saved to localStorage (`token` key)
- ✅ Redirected to Dashboard view
- ✅ Sidebar visible with navigation

**Debugging**:
- If 404: Backend `/api/auth/login` endpoint missing
- If 401: Wrong credentials
- If CORS error: Backend CORS configuration issue
- Check browser Console for errors

---

### 📊 Test 2: Dashboard Stats Loading

**Steps**:
1. After successful login, verify Dashboard loads
2. Check Network tab for API calls

**Expected Results**:
- ✅ GET `/api/stats` called automatically
- ✅ GET `/api/reservas` called (for recent reservations)
- ✅ Stats cards show real data (Total Reservas, Confirmadas, etc.)
- ✅ Recent reservations list populated
- ✅ Loading spinner appears briefly, then data

**Debugging**:
- If stuck on loading: Check `/api/stats` response status
- If "Error": Check error message in red banner
- If empty: Backend may have no data yet

---

### 📅 Test 3: Reservas CRUD - List

**Steps**:
1. Click "Reservas" in sidebar
2. Observe list of reservations

**Expected Results**:
- ✅ GET `/api/reservas` called
- ✅ Reservations displayed in grid
- ✅ Each card shows: nombre, teléfono, fecha, hora, personas, mesa, estado
- ✅ Estado badges color-coded:
  - Pendiente: Yellow
  - Confirmada: Blue
  - Sentada: Purple
  - Completada: Green
  - Cancelada: Red
- ✅ Filter chips work (Hoy, Semana, Mes, Todas, Por estado)

**Debugging**:
- If empty: Check if backend has reservations in DB (Airtable)
- If 401: Token expired, try re-login
- If 500: Backend error, check backend logs

---

### ➕ Test 4: Reservas CRUD - Create

**Steps**:
1. In Reservas view, click "+ Nueva Reserva" button
2. Modal should open (ReservaForm)
3. Fill form:
   - Nombre: "Juan Pérez"
   - Teléfono: "612345678"
   - Fecha: Tomorrow's date
   - Hora: "20:00"
   - Número de personas: "4"
   - Zona: "Interior" or "Terraza"
4. Click "Crear Reserva"

**Expected Results**:
- ✅ Form validation passes
- ✅ POST `/api/reservas` with JSON body
- ✅ Backend responds with created reservation (201 status)
- ✅ Modal closes
- ✅ New reservation appears in list immediately (optimistic update)
- ✅ Toast notification: "Reserva creada exitosamente" (success, green)
- ✅ Lista refreshes from backend (React Query invalidation)

**Debugging**:
- If validation error: Check form fields (phone format, time range)
- If 400: Backend validation failed, check error message
- If reservation not visible: Check React Query cache invalidation

---

### ✏️ Test 5: Reservas CRUD - Update

**Steps**:
1. Click "Editar" button on any reservation card
2. ReservaForm opens in edit mode (pre-filled)
3. Change "Número de personas" from 4 to 6
4. Click "Actualizar Reserva"

**Expected Results**:
- ✅ PUT `/api/reservas/{id}` called
- ✅ Modal closes
- ✅ Card updates with new data (6 personas)
- ✅ Toast notification: "Reserva actualizada"

**Debugging**:
- If 404: Reservation ID not found in backend
- If data doesn't update: Check query invalidation

---

### ❌ Test 6: Reservas CRUD - Cancel

**Steps**:
1. Click "Cancelar" button on a Pendiente or Confirmada reservation
2. Confirm cancellation in dialog

**Expected Results**:
- ✅ POST `/api/reservas/{id}/cancel` called
- ✅ Estado changes to "Cancelada"
- ✅ Badge turns red
- ✅ Toast notification: "Reserva cancelada"
- ✅ Mesa liberada (if assigned)

**Debugging**:
- If cancel fails: Check backend `cancel` endpoint exists
- If estado doesn't change: Check backend response

---

### ✅ Test 7: Reservas State Transitions

**Test Pendiente → Confirmada**:
1. Find a "Pendiente" reservation
2. Click "Confirmar" button
3. Expected: POST `/api/reservas/{id}/confirm`, estado → Confirmada, badge blue

**Test Confirmada → Sentada**:
1. Find a "Confirmada" reservation
2. Click "Sentar" button
3. Expected: POST `/api/reservas/{id}/seat`, estado → Sentada, badge purple

**Test Sentada → Completada**:
1. Find a "Sentada" reservation
2. Click "Completar" button
3. Expected: POST `/api/reservas/{id}/complete`, estado → Completada, badge green

**Expected**: All transitions work smoothly with optimistic updates

---

### 🪑 Test 8: Mesas CRUD - List

**Steps**:
1. Click "Mesas" in sidebar
2. Verify grid layout

**Expected Results**:
- ✅ GET `/api/mesas` called
- ✅ Stats cards show: Total Mesas, Disponibles, Ocupadas, Reservadas
- ✅ Tables separated by location (Interior / Terraza)
- ✅ Each card shows: número, capacidad, ubicación, estado
- ✅ Estado color-coded:
  - Libre: Green border
  - Ocupada: Red border
  - Reservada: Blue border
  - Bloqueada: Gray border

---

### ➕ Test 9: Mesas CRUD - Create

**Steps**:
1. Click "+ Nueva Mesa" button
2. Modal opens (MesaForm)
3. Fill form:
   - Número: "15"
   - Capacidad: "6"
   - Ubicación: "Interior"
   - Estado: "Libre"
4. Click "Crear Mesa"

**Expected Results**:
- ✅ POST `/api/mesas` with JSON body
- ✅ Modal closes
- ✅ New mesa appears in grid
- ✅ Toast notification: "Mesa creada exitosamente"
- ✅ Stats update (Total Mesas +1)

---

### 🔄 Test 10: Mesas - Toggle Status

**Steps**:
1. Find a "Libre" mesa
2. Click the toggle button (Estado: ...)
3. Should change to "Ocupada"
4. Click again
5. Should change back to "Libre"

**Expected Results**:
- ✅ PUT `/api/mesas/{id}/status` called
- ✅ Card border color changes instantly (optimistic)
- ✅ Stats update (Disponibles ↔ Ocupadas)
- ✅ No full page reload

---

### 🗑️ Test 11: Mesas CRUD - Delete

**Steps**:
1. Click "Eliminar" button on any mesa
2. Confirm deletion in ConfirmDialog

**Expected Results**:
- ✅ DELETE `/api/mesas/{id}` called
- ✅ Mesa disappears from grid
- ✅ Toast notification: "Mesa eliminada"
- ✅ Stats update (Total Mesas -1)

**Debugging**:
- If 409: Mesa in use (has active reservation)
- If deletion doesn't reflect: Check query invalidation

---

### 🚨 Test 12: Error Handling

**Simulate Backend Down**:
1. Stop backend server (Ctrl+C)
2. Try creating a reservation in frontend
3. Expected:
   - ✅ Error banner appears: "Error: Failed to fetch" or similar
   - ✅ Toast notification: "Error al crear reserva" (red)
   - ✅ No crash, UI remains responsive

**Simulate 401 Unauthorized**:
1. Delete token from localStorage (DevTools → Application → Local Storage → remove `token`)
2. Refresh page
3. Expected:
   - ✅ Redirected to Login screen
   - ✅ No infinite loading

---

### ⚡ Test 13: Loading States

**Steps**:
1. Throttle network (DevTools → Network → Slow 3G)
2. Navigate to Reservas
3. Observe loading spinner appears
4. Wait for data to load
5. Spinner disappears, data appears

**Expected Results**:
- ✅ All views show loading spinner during fetch
- ✅ No "flash of empty content"
- ✅ Smooth transition from loading → data

---

### 🔐 Test 14: Authentication Persistence

**Steps**:
1. Login successfully
2. Navigate to Mesas
3. Refresh page (F5)
4. Should stay logged in (Dashboard visible)
5. Manually delete token from localStorage
6. Refresh page
7. Should redirect to Login

**Expected Results**:
- ✅ Token persists across refreshes
- ✅ Token removal triggers logout flow

---

## API ENDPOINTS VERIFICATION CHECKLIST

### Reservations Endpoints
- [ ] `GET /api/reservas` - List reservations
- [ ] `POST /api/reservas` - Create reservation
- [ ] `PUT /api/reservas/{id}` - Update reservation
- [ ] `POST /api/reservas/{id}/cancel` - Cancel reservation
- [ ] `POST /api/reservas/{id}/confirm` - Confirm reservation
- [ ] `POST /api/reservas/{id}/seat` - Mark as seated
- [ ] `POST /api/reservas/{id}/complete` - Mark as completed

### Tables Endpoints
- [ ] `GET /api/mesas` - List tables
- [ ] `POST /api/mesas` - Create table
- [ ] `PUT /api/mesas/{id}` - Update table
- [ ] `DELETE /api/mesas/{id}` - Delete table
- [ ] `PUT /api/mesas/{id}/status` - Update status

### Stats Endpoints
- [ ] `GET /api/stats` - Get dashboard stats

### Auth Endpoints
- [ ] `POST /api/auth/login` - Login
- [ ] `POST /api/auth/refresh` - Refresh token (if implemented)

---

## INTEGRATION ISSUES LOG

### Issue Template
```markdown
### Issue #X: [Short Description]
**Date**: YYYY-MM-DD  
**Component**: Frontend/Backend/Both  
**Severity**: Critical/High/Medium/Low  

**Symptoms**:
- What happened

**Expected Behavior**:
- What should happen

**Steps to Reproduce**:
1. Step 1
2. Step 2

**Root Cause**:
- Analysis

**Fix Applied**:
- Solution

**Status**: Open/In Progress/Resolved
```

---

## SUCCESS CRITERIA

Integration testing is considered **PASSED** when:

- ✅ All 14 test scenarios pass
- ✅ All API endpoints return expected responses
- ✅ No console errors in browser
- ✅ No 500 errors from backend
- ✅ Loading states work correctly
- ✅ Error handling graceful
- ✅ Toast notifications appear
- ✅ Optimistic updates work
- ✅ Query cache invalidation works
- ✅ Authentication persists across refreshes

---

## NEXT STEPS AFTER INTEGRATION TESTING

### If All Tests Pass ✅
1. Mark "Integration Testing" task as complete
2. Update DAYS_16_17_PROGRESS.md to 100% complete
3. Proceed to Days 18-19: ReservaForm refinement and `check_availability` integration

### If Tests Fail ❌
1. Document all issues in INTEGRATION_ISSUES_LOG.md
2. Prioritize critical issues (blocking CRUD operations)
3. Fix backend issues first (API contracts)
4. Fix frontend issues second (error handling, UI bugs)
5. Re-test until all scenarios pass

---

## PRODUCTION READINESS CHECKLIST

Before deploying to production:

- [ ] All integration tests pass locally
- [ ] All integration tests pass with production backend URL
- [ ] CORS configured correctly for production domain
- [ ] Environment variables configured in Coolify
- [ ] SSL/HTTPS working
- [ ] Authentication tested on production
- [ ] Mobile responsive verified
- [ ] Dark mode (if implemented)
- [ ] Performance tested (Lighthouse score >90)

---

**Testing Guide Generated**: 2025-02-15  
**For**: Phase 2, Week 4 - Frontend Integration  
**Status**: Ready for Execution
