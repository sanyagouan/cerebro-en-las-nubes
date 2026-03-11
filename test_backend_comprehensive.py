#!/usr/bin/env python3
"""
Test comprehensivo del Backend API de "Cerebro En Las Nubes"
Ejecuta todas las pruebas definidas y genera un reporte detallado.
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

# Configuración
BASE_URL = "https://go84sgscs4ckcs08wog84o0o.app.generaia.site"
USERNAME = "administradora"
PASSWORD = "AdminNubes2026!"

# Resultados de tests
test_results: List[Dict[str, Any]] = []

def log_test(endpoint: str, method: str, status: str, status_code: Optional[int] = None, 
             observations: str = "", response_data: Any = None):
    """Registra el resultado de un test"""
    result = {
        "endpoint": endpoint,
        "method": method,
        "status": status,
        "status_code": status_code,
        "observations": observations,
        "response_data": response_data,
        "timestamp": datetime.now().isoformat()
    }
    test_results.append(result)
    
    # Print en tiempo real
    status_icon = "[OK]" if status == "OK" else "[ERROR]" if status == "ERROR" else "[WARN]"
    code_str = f" [{status_code}]" if status_code else ""
    print(f"{status_icon} {method} {endpoint}{code_str} - {observations}")
    if response_data and status == "ERROR":
        print(f"   Response: {json.dumps(response_data, indent=2, ensure_ascii=False)[:500]}")

def make_request(method: str, endpoint: str, headers: Dict = None, 
                 data: Dict = None, params: Dict = None, timeout: int = 15) -> tuple:
    """Helper para hacer requests HTTP"""
    url = f"{BASE_URL}{endpoint}"
    default_headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if headers:
        default_headers.update(headers)
    
    try:
        if method == "GET":
            response = requests.get(url, headers=default_headers, params=params, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, headers=default_headers, json=data, timeout=timeout)
        elif method == "PUT":
            response = requests.put(url, headers=default_headers, json=data, timeout=timeout)
        elif method == "DELETE":
            response = requests.delete(url, headers=default_headers, timeout=timeout)
        else:
            return None, 0, f"Método no soportado: {method}"
        
        try:
            response_data = response.json()
        except:
            response_data = response.text
        
        return response_data, response.status_code, None
    except requests.exceptions.Timeout:
        return None, 0, "Timeout - servidor no responde"
    except requests.exceptions.ConnectionError as e:
        return None, 0, f"Error de conexión: {str(e)}"
    except Exception as e:
        return None, 0, f"Error: {str(e)}"

# ============================================
# 1. TEST DE HEALTH CHECK
# ============================================
print("\n" + "="*60)
print("1. TEST DE HEALTH CHECK")
print("="*60)

data, code, error = make_request("GET", "/health")
if error:
    log_test("/health", "GET", "ERROR", None, error)
elif code == 200:
    log_test("/health", "GET", "OK", code, f"Status: {data.get('status', 'unknown') if isinstance(data, dict) else 'unknown'}", data)
else:
    log_test("/health", "GET", "ERROR", code, f"Respuesta inesperada", data)

# ============================================
# 2. TEST DE AUTENTICACIÓN API
# ============================================
print("\n" + "="*60)
print("2. TEST DE AUTENTICACIÓN API")
print("="*60)

# 2.1 Login
login_data = {"username": USERNAME, "password": PASSWORD}
data, code, error = make_request("POST", "/api/auth/login", data=login_data)

jwt_token = None
refresh_token = None

if error:
    log_test("/api/auth/login", "POST", "ERROR", None, error)
elif code == 200 and data:
    jwt_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    log_test("/api/auth/login", "POST", "OK", code, "Login exitoso, JWT obtenido", {
        "has_access_token": bool(jwt_token),
        "has_refresh_token": bool(refresh_token),
        "token_type": data.get("token_type"),
        "user": data.get("user", {}).get("username") if data.get("user") else None
    })
else:
    log_test("/api/auth/login", "POST", "ERROR", code, "Credenciales inválidas o error", data)

# 2.2 Verificar estructura del JWT
if jwt_token:
    try:
        parts = jwt_token.split(".")
        if len(parts) == 3:
            log_test("/api/auth/login", "POST", "OK", None, "JWT tiene estructura válida (3 partes)", None)
        else:
            log_test("/api/auth/login", "POST", "ERROR", None, f"JWT estructura inválida ({len(parts)} partes)", None)
    except:
        log_test("/api/auth/login", "POST", "ERROR", None, "Error analizando JWT", None)

# 2.3 Refresh token
if refresh_token:
    refresh_data = {"refresh_token": refresh_token}
    data, code, error = make_request("POST", "/api/auth/refresh", data=refresh_data)
    if error:
        log_test("/api/auth/refresh", "POST", "ERROR", None, error)
    elif code == 200:
        log_test("/api/auth/refresh", "POST", "OK", code, "Token refrescado exitosamente", data)
    else:
        log_test("/api/auth/refresh", "POST", "ERROR", code, "Error refrescando token", data)
else:
    log_test("/api/auth/refresh", "POST", "SKIP", None, "No hay refresh token disponible")

# 2.4 Get current user
if jwt_token:
    headers = {"Authorization": f"Bearer {jwt_token}"}
    data, code, error = make_request("GET", "/api/auth/me", headers=headers)
    if error:
        log_test("/api/auth/me", "GET", "ERROR", None, error)
    elif code == 200:
        log_test("/api/auth/me", "GET", "OK", code, f"Usuario: {data.get('username', 'N/A')}", data)
    else:
        log_test("/api/auth/me", "GET", "ERROR", code, "Error obteniendo usuario", data)
else:
    log_test("/api/auth/me", "GET", "SKIP", None, "No hay JWT token disponible")

# ============================================
# 3. TEST DE GESTIÓN DE RESERVAS (CRUD)
# ============================================
print("\n" + "="*60)
print("3. TEST DE GESTIÓN DE RESERVAS (CRUD)")
print("="*60)

auth_headers = {"Authorization": f"Bearer {jwt_token}"} if jwt_token else {}

# 3.1 Listar reservas
data, code, error = make_request("GET", "/api/reservas", headers=auth_headers)
reserva_id = None

if error:
    log_test("/api/reservas", "GET", "ERROR", None, error)
elif code == 200:
    reservas = data if isinstance(data, list) else data.get("reservas", [])
    log_test("/api/reservas", "GET", "OK", code, f"Total reservas: {len(reservas)}", 
             {"count": len(reservas), "sample": reservas[0] if reservas else None})
else:
    log_test("/api/reservas", "GET", "ERROR", code, "Error listando reservas", data)

# 3.2 Crear reserva de prueba
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
nueva_reserva = {
    "nombre_cliente": "TEST - Usuario de Prueba",
    "telefono": "+34600000000",
    "fecha": tomorrow,
    "hora": "21:00",
    "num_personas": 4,
    "notas": "RESERVA DE PRUEBA - ELIMINAR DESPUÉS DE TEST"
}

data, code, error = make_request("POST", "/api/reservas", headers=auth_headers, data=nueva_reserva)

if error:
    log_test("/api/reservas", "POST", "ERROR", None, error)
elif code in [200, 201]:
    reserva_id = data.get("id") if isinstance(data, dict) else None
    log_test("/api/reservas", "POST", "OK", code, f"Reserva creada, ID: {reserva_id}", data)
else:
    log_test("/api/reservas", "POST", "ERROR", code, "Error creando reserva", data)

# 3.3 Obtener reserva específica
if reserva_id:
    data, code, error = make_request("GET", f"/api/reservas/{reserva_id}", headers=auth_headers)
    if error:
        log_test(f"/api/reservas/{reserva_id}", "GET", "ERROR", None, error)
    elif code == 200:
        log_test(f"/api/reservas/{reserva_id}", "GET", "OK", code, "Reserva obtenida", data)
    else:
        log_test(f"/api/reservas/{reserva_id}", "GET", "ERROR", code, "Error obteniendo reserva", data)
else:
    log_test("/api/reservas/{id}", "GET", "SKIP", None, "No hay ID de reserva disponible")

# 3.4 Actualizar reserva
if reserva_id:
    update_data = {"notas": "ACTUALIZADO - Test comprehensivo"}
    data, code, error = make_request("PUT", f"/api/reservas/{reserva_id}", headers=auth_headers, data=update_data)
    if error:
        log_test(f"/api/reservas/{reserva_id}", "PUT", "ERROR", None, error)
    elif code == 200:
        log_test(f"/api/reservas/{reserva_id}", "PUT", "OK", code, "Reserva actualizada", data)
    else:
        log_test(f"/api/reservas/{reserva_id}", "PUT", "ERROR", code, "Error actualizando reserva", data)
else:
    log_test("/api/reservas/{id}", "PUT", "SKIP", None, "No hay ID de reserva disponible")

# 3.5 Eliminar reserva
if reserva_id:
    data, code, error = make_request("DELETE", f"/api/reservas/{reserva_id}", headers=auth_headers)
    if error:
        log_test(f"/api/reservas/{reserva_id}", "DELETE", "ERROR", None, error)
    elif code in [200, 204]:
        log_test(f"/api/reservas/{reserva_id}", "DELETE", "OK", code, "Reserva eliminada", data)
    else:
        log_test(f"/api/reservas/{reserva_id}", "DELETE", "ERROR", code, "Error eliminando reserva", data)
else:
    log_test("/api/reservas/{id}", "DELETE", "SKIP", None, "No hay ID de reserva disponible")

# ============================================
# 4. TEST DE GESTIÓN DE MESAS
# ============================================
print("\n" + "="*60)
print("4. TEST DE GESTIÓN DE MESAS")
print("="*60)

# 4.1 Listar mesas
data, code, error = make_request("GET", "/api/mesas", headers=auth_headers)

if error:
    log_test("/api/mesas", "GET", "ERROR", None, error)
elif code == 200:
    mesas = data if isinstance(data, list) else data.get("mesas", [])
    log_test("/api/mesas", "GET", "OK", code, f"Total mesas: {len(mesas)}", 
             {"count": len(mesas), "sample": mesas[0] if mesas else None})
else:
    log_test("/api/mesas", "GET", "ERROR", code, "Error listando mesas", data)

# 4.2 Mesas disponibles
data, code, error = make_request("GET", "/api/mesas/disponibles", headers=auth_headers, 
                                  params={"fecha": tomorrow, "hora": "21:00"})

if error:
    log_test("/api/mesas/disponibles", "GET", "ERROR", None, error)
elif code == 200:
    disponibles = data if isinstance(data, list) else data.get("mesas", [])
    log_test("/api/mesas/disponibles", "GET", "OK", code, f"Mesas disponibles: {len(disponibles)}", 
             {"count": len(disponibles), "sample": disponibles[0] if disponibles else None})
else:
    log_test("/api/mesas/disponibles", "GET", "ERROR", code, "Error obteniendo mesas disponibles", data)

# ============================================
# 5. TEST DE DISPONIBILIDAD
# ============================================
print("\n" + "="*60)
print("5. TEST DE DISPONIBILIDAD")
print("="*60)

# 5.1 Verificar disponibilidad
disponibilidad_data = {
    "fecha": tomorrow,
    "hora": "21:00",
    "num_personas": 4
}

data, code, error = make_request("POST", "/api/disponibilidad/verificar", 
                                  headers=auth_headers, data=disponibilidad_data)

if error:
    log_test("/api/disponibilidad/verificar", "POST", "ERROR", None, error)
elif code == 200:
    log_test("/api/disponibilidad/verificar", "POST", "OK", code, 
             f"Disponible: {data.get('disponible', 'N/A')}", data)
else:
    log_test("/api/disponibilidad/verificar", "POST", "ERROR", code, "Error verificando disponibilidad", data)

# 5.2 Probar con diferentes horarios
horarios = ["13:00", "14:00", "20:00", "22:00"]
for hora in horarios:
    disp_data = {"fecha": tomorrow, "hora": hora, "num_personas": 2}
    data, code, error = make_request("POST", "/api/disponibilidad/verificar", 
                                      headers=auth_headers, data=disp_data)
    if code == 200:
        log_test("/api/disponibilidad/verificar", "POST", "OK", code, 
                 f"Hora {hora}: Disponible={data.get('disponible', 'N/A')}", None)
    else:
        log_test("/api/disponibilidad/verificar", "POST", "ERROR", code, f"Error hora {hora}", data)

# ============================================
# 6. TEST DE VAPI TOOLS
# ============================================
print("\n" + "="*60)
print("6. TEST DE VAPI TOOLS")
print("="*60)

data, code, error = make_request("GET", "/api/vapi/tools", headers=auth_headers)

if error:
    log_test("/api/vapi/tools", "GET", "ERROR", None, error)
elif code == 200:
    tools = data if isinstance(data, list) else data.get("tools", [])
    log_test("/api/vapi/tools", "GET", "OK", code, f"Total tools: {len(tools)}", 
             {"count": len(tools), "tools": tools if isinstance(tools, list) else list(tools)[:5] if tools else None})
else:
    log_test("/api/vapi/tools", "GET", "ERROR", code, "Error listando tools VAPI", data)

# ============================================
# 7. TEST DE WHATSAPP
# ============================================
print("\n" + "="*60)
print("7. TEST DE WHATSAPP")
print("="*60)

data, code, error = make_request("GET", "/api/whatsapp/messages", headers=auth_headers)

if error:
    log_test("/api/whatsapp/messages", "GET", "ERROR", None, error)
elif code == 200:
    messages = data if isinstance(data, list) else data.get("messages", [])
    log_test("/api/whatsapp/messages", "GET", "OK", code, f"Total mensajes: {len(messages)}", 
             {"count": len(messages), "sample": messages[0] if messages else None})
else:
    log_test("/api/whatsapp/messages", "GET", "ERROR", code, "Error listando mensajes WhatsApp", data)

# ============================================
# 8. TEST DE ANALYTICS
# ============================================
print("\n" + "="*60)
print("8. TEST DE ANALYTICS")
print("="*60)

data, code, error = make_request("GET", "/api/analytics/resumen", headers=auth_headers)

if error:
    log_test("/api/analytics/resumen", "GET", "ERROR", None, error)
elif code == 200:
    log_test("/api/analytics/resumen", "GET", "OK", code, "Analytics obtenido", data)
else:
    log_test("/api/analytics/resumen", "GET", "ERROR", code, "Error obteniendo analytics", data)

# ============================================
# 9. TEST DE WEBSOCKET
# ============================================
print("\n" + "="*60)
print("9. TEST DE WEBSOCKET")
print("="*60)

# Nota: WebSocket requiere conexión persistente, aquí solo verificamos el endpoint
# Intentamos GET para ver si responde (normalmente WebSocket usa WS://)
data, code, error = make_request("GET", "/ws", headers=auth_headers, timeout=5)

if error:
    log_test("/ws", "WS", "ERROR", None, f"WebSocket no accesible via HTTP: {error}")
elif code == 403:
    log_test("/ws", "WS", "ERROR", 403, "Error 403 Forbidden - Token JWT posiblemente inválido para WS", data)
elif code == 426:
    log_test("/ws", "WS", "OK", 426, "Endpoint WebSocket existe (426 Upgrade Required es esperado)", None)
elif code in [200, 101]:
    log_test("/ws", "WS", "OK", code, "WebSocket accesible", data)
else:
    log_test("/ws", "WS", "ERROR", code, f"Respuesta inesperada del endpoint WebSocket", data)

# ============================================
# 10. TEST DE RATE LIMITING
# ============================================
print("\n" + "="*60)
print("10. TEST DE RATE LIMITING")
print("="*60)

print("   Ejecutando 15 requests rápidos para probar rate limiting...")
rate_limited = False
for i in range(15):
    data, code, error = make_request("GET", "/health", timeout=5)
    if code == 429:
        rate_limited = True
        log_test("/health", "GET", "OK", 429, f"Rate limiting activo (request #{i+1})", 
                 {"retry_after": data.get("retry_after") if data else None})
        break
    time.sleep(0.1)  # Pequeña pausa entre requests

if not rate_limited:
    log_test("/health", "GET", "WARNING", None, "Rate limiting NO detectado en 15 requests", None)

# ============================================
# RESUMEN FINAL
# ============================================
print("\n" + "="*60)
print("RESUMEN FINAL")
print("="*60)

# Contar resultados
ok_count = sum(1 for r in test_results if r["status"] == "OK")
error_count = sum(1 for r in test_results if r["status"] == "ERROR")
skip_count = sum(1 for r in test_results if r["status"] == "SKIP")
warning_count = sum(1 for r in test_results if r["status"] == "WARNING")

print(f"\n[ESTADISTICAS]:")
print(f"   [OK] Exitosos: {ok_count}")
print(f"   [ERROR] Errores: {error_count}")
print(f"   [SKIP] Saltados: {skip_count}")
print(f"   [WARN] Warnings: {warning_count}")
print(f"   [TOTAL] Total tests: {len(test_results)}")

# Guardar resultados en JSON
with open("test_results.json", "w", encoding="utf-8") as f:
    json.dump(test_results, f, indent=2, ensure_ascii=False)

print(f"\n[SAVED] Resultados guardados en: test_results.json")

# Mostrar tabla resumen
print("\n[TABLA RESUMEN]:")
print("-" * 100)
print(f"{'Endpoint':<40} {'Método':<8} {'Status':<8} {'Código':<8} {'Observaciones'}")
print("-" * 100)
for r in test_results:
    status_icon = "[OK]" if r["status"] == "OK" else "[ERROR]" if r["status"] == "ERROR" else "[WARN]" if r["status"] == "WARNING" else "[SKIP]"
    code_str = str(r["status_code"]) if r["status_code"] else "N/A"
    print(f"{r['endpoint']:<40} {r['method']:<8} {status_icon} {r['status']:<6} {code_str:<8} {r['observations'][:50]}")
print("-" * 100)

# Errores encontrados
errors = [r for r in test_results if r["status"] == "ERROR"]
if errors:
    print("\n[ERRORS] ERRORES ENCONTRADOS:")
    for e in errors:
        print(f"\n   {e['method']} {e['endpoint']}:")
        print(f"   Código: {e['status_code']}")
        print(f"   Observación: {e['observations']}")
        if e.get("response_data"):
            print(f"   Response: {json.dumps(e['response_data'], indent=4, ensure_ascii=False)[:300]}")

print("\n" + "="*60)
print("TEST COMPLETADO")
print("="*60)
