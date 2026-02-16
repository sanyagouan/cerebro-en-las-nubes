# 🎯 PLAN DE COORDINACIÓN: Deploy + Testing Integrado

**Fecha**: 2025-02-15  
**Objetivo**: Coordinar deploy a Coolify + testing automatizado sin errores  
**Estado**: ⏳ PROPUESTA PARA APROBACIÓN

---

## 📋 RESUMEN EJECUTIVO

### ¿Qué vamos a hacer?
1. **Merge PR** #1 en GitHub (claude/serene-mccarthy → dashboard-production)
2. **Coolify auto-deploya** backend + frontend desde GitHub
3. **Testing automatizado** con Playwright (9 tests)
4. **Documentar resultados** con screenshots

### Tiempo estimado: **25-35 minutos**

### Herramientas MCP usadas:
- ✅ **Playwright MCP** - Browser automation + screenshots
- ✅ **Chrome DevTools MCP** - Network monitoring + console errors
- ✅ **Coolify MCP** - Deploy monitoring + logs
- ✅ **GitHub MCP** - Merge PR

---

## 🚀 FASE 1: PRE-DEPLOY (5 min)

### 1.1 Verificar Coolify Status
```
MCP: coolify.applications.list()
Verificar: cerebro-backend (running:healthy) ✅
Verificar: cerebro-dashboard-nix (running) ✅
```

### 1.2 Health Check Backend PRE-deploy
```
MCP: playwright.navigate("https://go84sgscs4ckcs08wog84o0o.app.generaia.site/health")
Esperar: Status 200 + JSON response
```

### 1.3 Frontend Screenshot PRE-deploy
```
MCP: playwright.navigate("https://y08s40o0sgco88g0ook4gk48.app.generaia.site")
MCP: playwright.screenshot("frontend-pre-deploy.png")
```

---

## 🔄 FASE 2: MERGE PR (2 min)

### 2.1 Merge PR #1
```
MCP: github.merge_pull_request(
  owner: "sanyagouan",
  repo: "cerebro-en-las-nubes",
  pullNumber: 1,
  merge_method: "squash"
)
```

### 2.2 Esperar Coolify Webhook
```
Esperar: 30 segundos
Coolify detecta push a dashboard-production y inicia deploy
```

---

## 📦 FASE 3: MONITOREAR DEPLOY (5-10 min)

### 3.1 Loop: Verificar Backend Deploy
```
LOOP (cada 30s, máx 10 intentos):
  MCP: coolify.applications.get(id: "go84sgscs4ckcs08wog84o0o")
  
  SI status = "running:healthy":
    ✅ Continuar
  SI status = "starting":
    ⏳ Esperar 30s más
  SI status = "exited:unhealthy":
    ❌ STOP - Obtener logs y reportar error
```

### 3.2 Loop: Verificar Frontend Deploy
```
LOOP (cada 30s, máx 10 intentos):
  MCP: coolify.applications.get(id: "y08s40o0sgco88g0ook4gk48")
  
  SI status contiene "running":
    ✅ Continuar
  SI status = "starting":
    ⏳ Esperar 30s más
  SI status = "exited":
    ❌ STOP - Obtener logs y reportar error
```

### 3.3 Health Check Backend POST-deploy
```
MCP: playwright.navigate("/health")
Verificar: Status 200 + nuevos endpoints visibles
```

### 3.4 Health Check Frontend POST-deploy
```
MCP: playwright.navigate(frontend_url)
MCP: playwright.screenshot("frontend-post-deploy.png")
Verificar: Login visible + no console errors
```

---

## 🧪 FASE 4: TESTING AUTOMATIZADO (10 min)

### Test 1: Backend Health ✅
```
playwright.navigate("/health")
PASS: Status 200
```

### Test 2: Authentication Login 🔐
```
1. playwright.navigate(frontend)
2. playwright.fill_form([
     {ref: "username", value: "waiter"},
     {ref: "password", value: "waiter123"}
   ])
3. playwright.click("login_button")
4. playwright.wait_for(text: "Dashboard")
5. playwright.screenshot("test-login-success.png")
PASS: Dashboard visible
```

### Test 3: List Reservations 📋
```
1. devtools.click("reservas_tab")
2. devtools.list_network_requests(type: "fetch")
3. Verificar: GET /api/mobile/reservations → 200
4. devtools.screenshot()
PASS: API call OK + tabla visible
```

### Test 4: Create Reservation ➕
```
1. playwright.click("nueva_reserva_btn")
2. playwright.wait_for(text: "Nueva Reserva")
3. playwright.fill_form([
     {ref: "customer_name", value: "Test Playwright"},
     {ref: "customer_phone", value: "+1234567890"},
     {ref: "date", value: "2025-02-16"},
     {ref: "time", value: "19:00"},
     {ref: "party_size", value: "4"},
     {ref: "zone", value: "Interior"}
   ])
4. playwright.click("guardar_btn")
5. playwright.wait_for(text: "Reserva creada")
6. playwright.screenshot("test-create-reservation.png")
PASS: Toast de éxito + nueva reserva en tabla
```

### Test 5: List Tables 🪑
```
1. playwright.click("mesas_tab")
2. playwright.wait_for(text: "Mesas")
3. playwright.screenshot("test-list-tables.png")
PASS: Tabla de mesas con datos de Airtable
```

### Test 6: Create Table ➕🪑
```
Similar a Test 4, pero para mesas
PASS: Nueva mesa creada en Airtable
```

### Test 7: Update Reservation ✏️
```
1. playwright.click("editar_reserva_btn")
2. playwright.fill_form(cambios)
3. playwright.click("guardar_btn")
4. playwright.wait_for(text: "Reserva actualizada")
PASS: Cambios guardados
```

### Test 8: Cancel Reservation ❌
```
1. playwright.click("cancelar_reserva_btn")
2. playwright.click("confirmar_btn")
3. playwright.wait_for(text: "Reserva cancelada")
PASS: Estado = "Cancelada"
```

### Test 9: Error Handling 🚨
```
1. devtools.emulate({networkConditions: "Offline"})
2. Intentar crear reserva
3. playwright.wait_for(text: "Error")
4. devtools.emulate({networkConditions: "No emulation"})
PASS: Error toast visible con mensaje claro
```

---

## 📊 FASE 5: DOCUMENTAR (5 min)

### 5.1 Actualizar INTEGRATION_TEST_RESULTS.md
```
Crear archivo con:
- Resultados de 9 tests (PASS/FAIL)
- Screenshots embebidos
- Observaciones
```

### 5.2 Actualizar TODO list
```
TodoWrite({
  todos: [
    {content: "Deploy + Testing Automatizado", status: "completed"},
    {content: "Manual integration testing", status: "pending"},
    ...
  ]
})
```

---

## 🚨 MANEJO DE ERRORES

### Error 1: Deploy Falla ❌
**Acción**:
1. Obtener logs: `coolify.applications.get_logs(id)`
2. Analizar error
3. Reportar al usuario
4. NO continuar con testing

### Error 2: Health Check Falla después de Deploy 🏥
**Acción**:
1. Esperar 60 segundos (startup lento)
2. Reintentar
3. Si persiste → obtener logs
4. Reportar al usuario

### Error 3: Test Automatizado Falla 🧪
**Acción**:
1. Capturar screenshot
2. Capturar console errors
3. Documentar error
4. CONTINUAR con siguiente test (no detener todo)
5. Reportar todos los failures al final

---

## ✅ CRITERIOS DE ÉXITO

### Deploy Exitoso 🚀
- [x] Backend: `running:healthy`
- [x] Frontend: `running:*`
- [x] Health checks: 200 OK

### Testing Exitoso 🧪
- [x] Mínimo 7/9 tests PASS (78%)
- [x] Tests críticos (Login, Health) PASS obligatorio
- [x] Screenshots capturados

### Documentación Completa 📝
- [x] INTEGRATION_TEST_RESULTS.md actualizado
- [x] Screenshots organizados
- [x] TODO list actualizado

---

## 🎯 COMANDO PARA EJECUTAR

**Para aprobar y ejecutar este plan automáticamente**:
```
"Ejecuta el plan de coordinación"
```

**Para modificar el plan**:
```
"Modifica el plan: [cambios específicos]"
```

---

## 📋 CHECKLIST PRE-FLIGHT

Antes de ejecutar, verificar:
- [ ] PR #1 está listo para merge
- [ ] Coolify webhook está configurado en GitHub
- [ ] Credenciales de Coolify funcionando
- [ ] Playwright MCP disponible
- [ ] Chrome DevTools MCP disponible
- [ ] Usuario aprobó este plan ⭐

---

**Creado por**: Claude Sonnet 4.5  
**Fecha**: 2025-02-15  
**Timing**: 25-35 minutos total  
**Basado en**: Plan maestro `drifting-hopping-fairy.md`
