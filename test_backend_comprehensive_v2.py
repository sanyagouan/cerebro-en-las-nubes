"""
Test Backend Comprehensive v2 - Endpoints correctos del API
Cerebro En Las Nubes - Testing de todos los endpoints
"""
import requests
import json
from datetime import datetime, date, timedelta
import sys

# Configuración
BASE_URL = "https://go84sgscs4ckcs08wog84o0o.app.generaia.site"
USERNAME = "administradora"
PASSWORD = "AdminNubes2026!"

# Resultados
test_results = []
jwt_token = None
refresh_token = None

def log_test(endpoint, method, status, code, observation, response_data=None):
    """Registra resultado de un test"""
    result = {
        "endpoint": endpoint,
        "method": method,
        "status": status,
        "code": code,
        "observation": observation,
        "response": response_data
    }
    test_results.append(result)
    
    status_icon = "[OK]" if status == "OK" else "[ERROR]" if status == "ERROR" else "[WARN]" if status == "WARNING" else "[SKIP]"
    print(f"{status_icon} {method} {endpoint} [{code}] - {observation}")
    if response_data and status == "ERROR":
        print(f"   Response: {json.dumps(response_data, indent=2, ensure_ascii=False)[:500]}")

def make_request(method, endpoint, headers=None, data=None, params=None):
    """Helper para hacer requests HTTP"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, params=params, timeout=15)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=data, timeout=15)
        elif method == "PUT":
            resp = requests.put(url, headers=headers, json=data, timeout=15)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, timeout=15)
        else:
            return None, 0, {}
        
        try:
            return resp, resp.status_code, resp.json()
        except:
            return resp, resp.status_code, {"raw": resp.text[:200]}
    except Exception as e:
        return None, 0, {"error": str(e)}

print("=" * 60)
print("TESTING BACKEND CEREBRO EN LAS NUBES v2")
print(f"Base URL: {BASE_URL}")
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# ============================================================
# 1. TEST DE HEALTH CHECK
# ============================================================
print("\n" + "=" * 60)
print("1. TEST DE HEALTH CHECK")
print("=" * 60)

resp, code, data = make_request("GET", "/health")
if code == 200 and data.get("status") == "healthy":
    log_test("/health", "GET", "OK", code, f"Status: {data.get('status')}, Version: {data.get('version')}", data)
else:
    log_test("/health", "GET", "ERROR", code, "Health check failed", data)

# Root endpoint
resp, code, data = make_request("GET", "/")
if code == 200:
    log_test("/", "GET", "OK", code, "Root endpoint OK", data)
else:
    log_test("/", "GET", "ERROR", code, "Root endpoint failed", data)

# Cache stats
resp, code, data = make_request("GET", "/cache/stats")
if code == 200:
    log_test("/cache/stats", "GET", "OK", code, "Cache stats OK", data)
else:
    log_test("/cache/stats", "GET", "WARNING" if code in [404, 401] else "ERROR", code, f"Cache stats: {code}", data)

# ============================================================
# 2. TEST DE AUTENTICACION API
# ============================================================
print("\n" + "=" * 60)
print("2. TEST DE AUTENTICACION API")
print("=" * 60)

# Login con campo 'usuario' correcto
login_data = {
    "usuario": USERNAME,
    "password": PASSWORD
}
resp, code, data = make_request("POST", "/api/auth/login", data=login_data)

if code == 200 and "access_token" in data:
    jwt_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    user_info = data.get("user", {})
    log_test("/api/auth/login", "POST", "OK", code, 
             f"Login exitoso. User: {user_info.get('name')}, Role: {user_info.get('role')}", 
             {"access_token": jwt_token[:50] + "...", "user": user_info})
else:
    log_test("/api/auth/login", "POST", "ERROR", code, "Login fallido", data)

# Refresh token
if refresh_token:
    refresh_data = {"refresh_token": refresh_token}
    resp, code, data = make_request("POST", "/api/auth/refresh", data=refresh_data)
    if code == 200 and "access_token" in data:
        log_test("/api/auth/refresh", "POST", "OK", code, "Token refrescado OK", {"token": data.get("access_token", "")[:50] + "..."})
    else:
        log_test("/api/auth/refresh", "POST", "ERROR", code, "Refresh fallido", data)
else:
    log_test("/api/auth/refresh", "POST", "SKIP", "N/A", "No hay refresh token disponible")

# Get current user
if jwt_token:
    headers = {"Authorization": f"Bearer {jwt_token}"}
    resp, code, data = make_request("GET", "/api/auth/me", headers=headers)
    if code == 200:
        log_test("/api/auth/me", "GET", "OK", code, f"User: {data.get('name')}, Role: {data.get('role')}", data)
    else:
        log_test("/api/auth/me", "GET", "ERROR", code, "Error obteniendo usuario", data)
else:
    log_test("/api/auth/me", "GET", "SKIP", "N/A", "No hay JWT token disponible")

# Logout
resp, code, data = make_request("POST", "/api/auth/logout")
log_test("/api/auth/logout", "POST", "OK" if code == 200 else "WARNING", code, f"Logout: {data.get('message', 'OK')}", data)

# ============================================================
# 3. TEST DE GESTION DE MESAS
# ============================================================
print("\n" + "=" * 60)
print("3. TEST DE GESTION DE MESAS")
print("=" * 60)

# Health de mesas
resp, code, data = make_request("GET", "/api/mesas/health")
if code == 200:
    log_test("/api/mesas/health", "GET", "OK", code, f"Mesas service: {data.get('status')}", data)
else:
    log_test("/api/mesas/health", "GET", "ERROR", code, "Mesas health failed", data)

# Disponibilidad para hoy
today = date.today().strftime("%Y-%m-%d")
tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

# Solo probar si no es lunes (dia de cierre)
if date.today().weekday() != 0:  # 0 = lunes
    resp, code, data = make_request("GET", f"/api/mesas/disponibilidad/{today}/T1", params={"party_size": 4})
    if code == 200:
        log_test(f"/api/mesas/disponibilidad/{today}/T1", "GET", "OK", code, 
                 f"Mesas disponibles: {data.get('available_count', 0)}", data)
    else:
        log_test(f"/api/mesas/disponibilidad/{today}/T1", "GET", "ERROR", code, "Error disponibilidad", data)
else:
    log_test("/api/mesas/disponibilidad/{today}/T1", "GET", "SKIP", "N/A", "Lunes - cerrado")

# Asignar mesa de prueba
asignar_data = {
    "party_size": 4,
    "fecha": tomorrow,
    "turno": "T1",
    "zone_preference": "Sin preferencia",
    "has_pets": False,
    "terrace_closed": False
}
resp, code, data = make_request("POST", "/api/mesas/asignar", data=asignar_data)
if code == 200:
    log_test("/api/mesas/asignar", "POST", "OK", code, 
             f"Mesa asignada: {data.get('table_name')}, Zona: {data.get('zone')}", data)
else:
    log_test("/api/mesas/asignar", "POST", "ERROR", code, "Error asignando mesa", data)

# ============================================================
# 4. TEST DE VAPI TOOLS
# ============================================================
print("\n" + "=" * 60)
print("4. TEST DE VAPI TOOLS")
print("=" * 60)

# get_info
vapi_payload = {
    "message": {
        "toolCalls": [{"id": "test_001", "function": {"arguments": "{}"}}]
    }
}
resp, code, data = make_request("POST", "/vapi/tools/get_info", data=vapi_payload)
if code == 200 and "results" in data:
    log_test("/vapi/tools/get_info", "POST", "OK", code, "Info del restaurante OK", data)
else:
    log_test("/vapi/tools/get_info", "POST", "ERROR", code, "Error obteniendo info", data)

# get_horarios
vapi_payload_horarios = {
    "message": {
        "toolCalls": [{"id": "test_002", "function": {"arguments": json.dumps({"fecha": tomorrow})}}]
    }
}
resp, code, data = make_request("POST", "/vapi/tools/get_horarios", data=vapi_payload_horarios)
if code == 200 and "results" in data:
    log_test("/vapi/tools/get_horarios", "POST", "OK", code, "Horarios OK", data)
else:
    log_test("/vapi/tools/get_horarios", "POST", "ERROR", code, "Error horarios", data)

# check_availability
vapi_payload_avail = {
    "message": {
        "toolCalls": [{"id": "test_003", "function": {"arguments": json.dumps({"fecha": tomorrow, "hora": "21:00", "personas": 4})}}]
    }
}
resp, code, data = make_request("POST", "/vapi/tools/check_availability", data=vapi_payload_avail)
if code == 200 and "results" in data:
    log_test("/vapi/tools/check_availability", "POST", "OK", code, "Disponibilidad OK", data)
else:
    log_test("/vapi/tools/check_availability", "POST", "ERROR", code, "Error disponibilidad", data)

# ============================================================
# 5. TEST DE WHATSAPP
# ============================================================
print("\n" + "=" * 60)
print("5. TEST DE WHATSAPP")
print("=" * 60)

# WhatsApp status
resp, code, data = make_request("GET", "/whatsapp/status")
if code == 200:
    log_test("/whatsapp/status", "GET", "OK", code, f"WhatsApp: {data.get('status')}", data)
else:
    log_test("/whatsapp/status", "GET", "ERROR", code, "WhatsApp status failed", data)

# WhatsApp webhook (sin datos reales, solo verificar que responde)
# Nota: Este endpoint espera Form data, no JSON
try:
    url = f"{BASE_URL}/whatsapp/webhook"
    form_data = {"From": "whatsapp:+34600000000", "Body": "test", "ProfileName": "Test"}
    resp = requests.post(url, data=form_data, timeout=15)
    if resp.status_code == 200 and "<?xml" in resp.text:
        log_test("/whatsapp/webhook", "POST", "OK", resp.status_code, "Webhook responde TwiML", {"response_type": "TwiML"})
    else:
        log_test("/whatsapp/webhook", "POST", "WARNING", resp.status_code, f"Respuesta inesperada: {resp.text[:100]}", None)
except Exception as e:
    log_test("/whatsapp/webhook", "POST", "ERROR", 0, f"Error: {str(e)}", None)

# ============================================================
# 6. TEST DE ANALYTICS
# ============================================================
print("\n" + "=" * 60)
print("6. TEST DE ANALYTICS")
print("=" * 60)

if jwt_token:
    headers = {"Authorization": f"Bearer {jwt_token}"}
    
    # Analytics summary
    resp, code, data = make_request("GET", "/api/analytics/summary", headers=headers, params={"period": "day"})
    if code == 200:
        log_test("/api/analytics/summary", "GET", "OK", code, 
                 f"Reservas: {data.get('total_reservations')}, Guests: {data.get('total_guests')}", data)
    elif code == 401:
        log_test("/api/analytics/summary", "GET", "WARNING", code, "Requiere autenticacion", data)
    else:
        log_test("/api/analytics/summary", "GET", "ERROR", code, "Error analytics", data)
    
    # Dashboard metrics
    resp, code, data = make_request("GET", "/api/analytics/dashboard-metrics", headers=headers)
    if code == 200:
        log_test("/api/analytics/dashboard-metrics", "GET", "OK", code, "Dashboard metrics OK", data)
    elif code == 401:
        log_test("/api/analytics/dashboard-metrics", "GET", "WARNING", code, "Requiere autenticacion", data)
    else:
        log_test("/api/analytics/dashboard-metrics", "GET", "ERROR", code, "Error metrics", data)
    
    # Occupancy stats
    start = (date.today() - timedelta(days=7)).isoformat()
    end = date.today().isoformat()
    resp, code, data = make_request("GET", "/api/analytics/occupancy", headers=headers, 
                                    params={"start_date": start, "end_date": end})
    if code == 200:
        log_test("/api/analytics/occupancy", "GET", "OK", code, 
                 f"Avg occupancy: {data.get('avg_occupancy')}%", data)
    elif code == 401:
        log_test("/api/analytics/occupancy", "GET", "WARNING", code, "Requiere autenticacion", data)
    else:
        log_test("/api/analytics/occupancy", "GET", "ERROR", code, "Error occupancy", data)
else:
    log_test("/api/analytics/summary", "GET", "SKIP", "N/A", "No hay JWT token")
    log_test("/api/analytics/dashboard-metrics", "GET", "SKIP", "N/A", "No hay JWT token")
    log_test("/api/analytics/occupancy", "GET", "SKIP", "N/A", "No hay JWT token")

# ============================================================
# 7. TEST DE WEBSOCKET
# ============================================================
print("\n" + "=" * 60)
print("7. TEST DE WEBSOCKET")
print("=" * 60)

# Verificar que el endpoint existe (no podemos probar WS directamente sin libreria)
try:
    import websocket
    
    ws_url = BASE_URL.replace("https://", "wss://") + "/ws/reservations"
    print(f"   Intentando conectar a: {ws_url}")
    
    # Intentar conexion rapida
    try:
        ws = websocket.create_connection(ws_url, timeout=5)
        ws.close()
        log_test("/ws/reservations", "WS", "OK", 101, "WebSocket conectado OK")
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "Forbidden" in error_msg:
            log_test("/ws/reservations", "WS", "ERROR", 403, "WebSocket rechazado (403 Forbidden) - Requiere token JWT", {"error": error_msg})
        elif "404" in error_msg or "Not Found" in error_msg:
            log_test("/ws/reservations", "WS", "ERROR", 404, "WebSocket endpoint no encontrado", {"error": error_msg})
        else:
            log_test("/ws/reservations", "WS", "WARNING", 0, f"Error de conexion: {error_msg}", {"error": error_msg})
except ImportError:
    # Sin libreria websocket, probar con HTTP
    resp, code, data = make_request("GET", "/ws/reservations")
    if code == 426:  # Upgrade Required - normal para WS
        log_test("/ws/reservations", "WS", "OK", 426, "Endpoint existe (requiere upgrade a WebSocket)")
    elif code == 404:
        log_test("/ws/reservations", "WS", "ERROR", 404, "Endpoint no encontrado", data)
    else:
        log_test("/ws/reservations", "WS", "WARNING", code, f"Respuesta inesperada: {code}", data)

# ============================================================
# 8. TEST DE RATE LIMITING
# ============================================================
print("\n" + "=" * 60)
print("8. TEST DE RATE LIMITING")
print("=" * 60)

print("   Ejecutando 20 requests rapidos para probar rate limiting...")
rate_limited = False
for i in range(20):
    resp, code, data = make_request("GET", "/health")
    if code == 429:
        rate_limited = True
        log_test("/health (rate limit)", "GET", "OK", 429, f"Rate limiting activo en request #{i+1}", data)
        break

if not rate_limited:
    log_test("/health (rate limit)", "GET", "WARNING", "N/A", "Rate limiting NO detectado en 20 requests")

# ============================================================
# 9. TEST DE VAPI WEBHOOK
# ============================================================
print("\n" + "=" * 60)
print("9. TEST DE VAPI WEBHOOK")
print("=" * 60)

# VAPI webhook principal
vapi_webhook_payload = {
    "message": {
        "type": "transcript",
        "content": "Hola, quiero reservar una mesa"
    },
    "session_id": "test_session_123"
}
resp, code, data = make_request("POST", "/vapi/webhook", data=vapi_webhook_payload)
if code == 200:
    log_test("/vapi/webhook", "POST", "OK", code, "VAPI webhook OK", data)
elif code == 422:
    log_test("/vapi/webhook", "POST", "WARNING", code, "VAPI webhook requiere formato especifico", data)
else:
    log_test("/vapi/webhook", "POST", "ERROR", code, "Error VAPI webhook", data)

# ============================================================
# 10. TEST DE TWILIO WEBHOOK
# ============================================================
print("\n" + "=" * 60)
print("10. TEST DE TWILIO WEBHOOK")
print("=" * 60)

# Twilio webhook (WhatsApp incoming)
try:
    url = f"{BASE_URL}/twilio/whatsapp/incoming"
    form_data = {"From": "whatsapp:+34600000000", "Body": "Hola", "ProfileName": "Test"}
    resp = requests.post(url, data=form_data, timeout=15)
    if resp.status_code == 200:
        log_test("/twilio/whatsapp/incoming", "POST", "OK", resp.status_code, "Twilio webhook OK")
    else:
        log_test("/twilio/whatsapp/incoming", "POST", "WARNING", resp.status_code, f"Status: {resp.status_code}")
except Exception as e:
    log_test("/twilio/whatsapp/incoming", "POST", "ERROR", 0, f"Error: {str(e)}")

# ============================================================
# RESUMEN FINAL
# ============================================================
print("\n" + "=" * 60)
print("RESUMEN FINAL")
print("=" * 60)

ok_count = len([r for r in test_results if r["status"] == "OK"])
error_count = len([r for r in test_results if r["status"] == "ERROR"])
skip_count = len([r for r in test_results if r["status"] == "SKIP"])
warning_count = len([r for r in test_results if r["status"] == "WARNING"])

print(f"\n[ESTADISTICAS]:")
print(f"   [OK] Exitosos: {ok_count}")
print(f"   [ERROR] Errores: {error_count}")
print(f"   [SKIP] Saltados: {skip_count}")
print(f"   [WARN] Warnings: {warning_count}")
print(f"   [TOTAL] Total tests: {len(test_results)}")

# Guardar resultados
with open("test_results_v2.json", "w", encoding="utf-8") as f:
    json.dump(test_results, f, indent=2, ensure_ascii=False)
print(f"\n[SAVED] Resultados guardados en: test_results_v2.json")

# Tabla resumen
print("\n[TABLA RESUMEN]:")
print("-" * 100)
print(f"{'Endpoint':<45} {'Metodo':<8} {'Status':<10} {'Codigo':<8} {'Observaciones'}")
print("-" * 100)

for r in test_results:
    status_icon = "[OK]" if r["status"] == "OK" else "[ERROR]" if r["status"] == "ERROR" else "[WARN]" if r["status"] == "WARNING" else "[SKIP]"
    code_str = str(r["code"]) if r["code"] else "N/A"
    obs = r["observation"][:40] + "..." if len(r["observation"]) > 40 else r["observation"]
    print(f"{r['endpoint']:<45} {r['method']:<8} {status_icon:<10} {code_str:<8} {obs}")

print("-" * 100)

# Errores encontrados
errors = [r for r in test_results if r["status"] == "ERROR"]
if errors:
    print("\n[ERRORS] ERRORES ENCONTRADOS:")
    for e in errors:
        print(f"\n   {e['method']} {e['endpoint']}:")
        print(f"   Codigo: {e['code']}")
        print(f"   Observacion: {e['observation']}")
        if e.get("response"):
            resp_str = json.dumps(e["response"], indent=4, ensure_ascii=False)[:300]
            print(f"   Response: {resp_str}")

print("\n" + "=" * 60)
print("TEST COMPLETADO")
print("=" * 60)
