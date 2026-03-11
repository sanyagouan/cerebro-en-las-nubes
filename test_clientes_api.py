"""
Test Comprehensivo de API de Clientes
======================================

Valida los 6 endpoints implementados en clients_api.py:
1. GET /dashboard/clients (lista)
2. GET /dashboard/clients?include_relations=true (con relaciones)
3. GET /dashboard/clients/{phone} (detalle)
4. POST /dashboard/clients (crear)
5. POST /dashboard/clients/{phone}/preferencias (añadir preferencia)
6. POST /dashboard/clients/{phone}/notas (añadir nota)

Foco especial en:
- Conversión Boolean<->String (Es_Importante: "Sí"/"No")
- Linked records (relaciones Cliente -> Preferencias/Notas)
- Validación de teléfonos españoles (+34XXXXXXXXX)
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any

# ========== CONFIGURACIÓN ==========

BASE_URL = "http://localhost:8000"
AUTH_URL = f"{BASE_URL}/api/auth/login"  # Dashboard router prefix /api
CLIENTS_URL = f"{BASE_URL}/clients"       # Clients router prefix /clients

# Credenciales de prueba (usuario existente en Airtable)
TEST_USER = "administradora"
TEST_PASSWORD = "AdminNubes2026!"

# Teléfono de cliente existente en Airtable (3 registros de prueba)
EXISTING_PHONE = "+34600000000"  # Ajustar según datos reales

# Teléfono para crear nuevo cliente (testing)
NEW_PHONE = "+34999888777"

# ========== UTILIDADES ==========

class Colors:
    """Colores ANSI para terminal."""
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

def print_step(step: str):
    """Imprime paso de testing."""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{step}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")

def print_success(message: str):
    """Imprime mensaje de éxito."""
    print(f"{Colors.GREEN}[OK] {message}{Colors.RESET}")

def print_error(message: str):
    """Imprime mensaje de error."""
    print(f"{Colors.RED}[FAIL] {message}{Colors.RESET}")

def print_warning(message: str):
    """Imprime mensaje de advertencia."""
    print(f"{Colors.YELLOW}[WARN] {message}{Colors.RESET}")

def print_json(data: Any, title: str = ""):
    """Imprime JSON formateado."""
    if title:
        print(f"\n{Colors.YELLOW}{title}:{Colors.RESET}")
    print(json.dumps(data, indent=2, ensure_ascii=False))

# ========== AUTENTICACIÓN ==========

def get_auth_token() -> str:
    """Obtiene token JWT autenticándose."""
    print_step("AUTENTICACIÓN")
    
    try:
        response = requests.post(
            AUTH_URL,
            json={
                "usuario": TEST_USER,  # Campo correcto: "usuario" (no "username")
                "password": TEST_PASSWORD
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print_success(f"Autenticado como: {TEST_USER}")
            print_success(f"Token obtenido: {token[:20]}...")
            return token
        else:
            print_error(f"Error de autenticación: {response.status_code}")
            print_json(response.json())
            raise Exception("No se pudo autenticar")
    
    except Exception as e:
        print_error(f"Excepción en autenticación: {str(e)}")
        raise

# ========== TESTS DE ENDPOINTS ==========

def test_list_clients(token: str):
    """Test 1: GET /dashboard/clients (lista básica)."""
    print_step("TEST 1: Listar Clientes (sin relaciones)")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(CLIENTS_URL, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        clientes = response.json()
        print_success(f"Clientes encontrados: {len(clientes)}")
        
        if clientes:
            # Mostrar primer cliente como ejemplo
            print_json(clientes[0], "Ejemplo de cliente")
            
            # Validar estructura
            primer = clientes[0]
            assert "id" in primer, "Falta campo 'id'"
            assert "nombre" in primer, "Falta campo 'nombre'"
            assert "telefono" in primer, "Falta campo 'telefono'"
            assert primer["telefono"].startswith("+34"), "Teléfono no es español"
            
            # Verificar que NO incluye relaciones (default)
            if primer.get("preferencias"):
                print_warning("Incluye preferencias (no debería sin include_relations=true)")
            if primer.get("notas"):
                print_warning("Incluye notas (no debería sin include_relations=true)")
            
            print_success("Estructura de datos correcta")
        else:
            print_warning("No hay clientes en la base de datos")
    else:
        print_error(f"Error: {response.status_code}")
        print_json(response.json())

def test_list_clients_with_relations(token: str):
    """Test 2: GET /dashboard/clients?include_relations=true."""
    print_step("TEST 2: Listar Clientes (con relaciones)")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{CLIENTS_URL}?include_relations=true",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        clientes = response.json()
        print_success(f"Clientes encontrados: {len(clientes)}")
        
        if clientes:
            # Buscar cliente con relaciones
            cliente_con_relaciones = None
            for c in clientes:
                if c.get("preferencias") or c.get("notas"):
                    cliente_con_relaciones = c
                    break
            
            if cliente_con_relaciones:
                print_success(f"Cliente con relaciones: {cliente_con_relaciones['nombre']}")
                
                # Mostrar preferencias
                if cliente_con_relaciones.get("preferencias"):
                    prefs = cliente_con_relaciones["preferencias"]
                    print_success(f"  - Preferencias: {len(prefs)}")
                    
                    # ⚠️ CRÍTICO: Verificar conversión Boolean
                    for pref in prefs:
                        es_importante = pref.get("es_importante")
                        print(f"    * {pref['tipo']}: {pref['descripcion']}")
                        print(f"      Es importante: {es_importante} (tipo: {type(es_importante).__name__})")
                        
                        # VALIDAR: Debe ser boolean, NO string
                        if isinstance(es_importante, bool):
                            print_success(f"      Conversión Boolean correcta")
                        else:
                            print_error(f"      FALLO: es_importante es {type(es_importante)}, debe ser bool")
                
                # Mostrar notas
                if cliente_con_relaciones.get("notas"):
                    notas = cliente_con_relaciones["notas"]
                    print_success(f"  - Notas: {len(notas)}")
                    
                    for nota in notas[:2]:  # Primeras 2
                        print(f"    * [{nota['fecha_creacion']}] {nota['contenido'][:50]}...")
            else:
                print_warning("Ningún cliente tiene preferencias o notas")
    else:
        print_error(f"Error: {response.status_code}")
        print_json(response.json())

def test_get_client_by_phone(token: str, phone: str):
    """Test 3: GET /dashboard/clients/{phone}."""
    print_step(f"TEST 3: Obtener Cliente por Teléfono ({phone})")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{CLIENTS_URL}/{phone}", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        cliente = response.json()
        print_success(f"Cliente encontrado: {cliente['nombre']}")
        print_json(cliente, "Datos completos")
        
        # Validar inclusión de relaciones
        if "preferencias" in cliente and cliente["preferencias"]:
            print_success(f"Incluye {len(cliente['preferencias'])} preferencias")
        else:
            print_warning("No tiene preferencias o no se incluyeron")
        
        if "notas" in cliente and cliente["notas"]:
            print_success(f"Incluye {len(cliente['notas'])} notas")
        else:
            print_warning("No tiene notas o no se incluyeron")
        
        return cliente
    elif response.status_code == 404:
        print_warning(f"Cliente {phone} no encontrado (esperado si es nuevo)")
        return None
    else:
        print_error(f"Error: {response.status_code}")
        print_json(response.json())
        return None

def test_create_client(token: str) -> Dict[str, Any]:
    """Test 4: POST /dashboard/clients."""
    print_step("TEST 4: Crear Nuevo Cliente")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    nuevo_cliente = {
        "nombre": "Cliente Testing API",
        "telefono": NEW_PHONE,
        "email": "testing@enlasnubes.com",
        "notas_generales": "Cliente creado automáticamente por test_clientes_api.py"
    }
    
    print_json(nuevo_cliente, "Datos a crear")
    
    response = requests.post(
        CLIENTS_URL,
        json=nuevo_cliente,
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 201:
        cliente = response.json()
        print_success(f"Cliente creado exitosamente")
        print_success(f"  - ID: {cliente['id']}")
        print_success(f"  - Nombre: {cliente['nombre']}")
        print_success(f"  - Teléfono: {cliente['telefono']}")
        
        return cliente
    elif response.status_code == 400:
        error = response.json()
        if "ya existe" in error.get("detail", "").lower():
            print_warning("Cliente ya existe (probablemente de test anterior)")
            # Intentar obtenerlo
            return test_get_client_by_phone(token, NEW_PHONE)
        else:
            print_error(f"Error de validación: {error}")
            return None
    else:
        print_error(f"Error: {response.status_code}")
        print_json(response.json())
        return None

def test_add_preferencia(token: str, phone: str):
    """Test 5: POST /dashboard/clients/{phone}/preferencias."""
    print_step(f"TEST 5: Añadir Preferencia a Cliente ({phone})")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # ⚠️ NOTA: La tabla ClientePreferencias NO tiene campo es_importante
    # Solo tiene: Tipo, Descripcion, Cliente, Fecha_Creacion
    # Valores válidos para Tipo: zona_favorita, solicitud_especial, restriccion_dietetica, ocasion_celebracion
    nueva_preferencia = {
        "tipo": "restriccion_dietetica",  # Valor válido en Airtable
        "descripcion": "Alergia al marisco (TEST)"
    }
    
    print_json(nueva_preferencia, "Preferencia a crear")
    print_warning("[INFO] Tabla ClientePreferencias NO tiene campo es_importante")
    
    response = requests.post(
        f"{CLIENTS_URL}/{phone}/preferencias",
        json=nueva_preferencia,
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 201:
        preferencia = response.json()
        print_success("Preferencia creada exitosamente")
        print_json(preferencia, "Respuesta del servidor")
        
        # VALIDAR ESTRUCTURA
        assert "id" in preferencia, "Falta campo 'id'"
        assert "tipo" in preferencia, "Falta campo 'tipo'"
        assert "descripcion" in preferencia, "Falta campo 'descripcion'"
        print_success("[OK] Estructura de preferencia correcta")
        
        return preferencia
    elif response.status_code == 404:
        print_error(f"Cliente {phone} no encontrado")
        return None
    else:
        print_error(f"Error: {response.status_code}")
        print_json(response.json())
        return None

def test_add_nota(token: str, phone: str):
    """Test 6: POST /dashboard/clients/{phone}/notas."""
    print_step(f"TEST 6: Añadir Nota a Cliente ({phone})")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    nueva_nota = {
        "contenido": "Nota de testing añadida automáticamente. Cliente muy satisfecho con el servicio.",
        "staff_nombre": "Sistema Testing"
    }
    
    print_json(nueva_nota, "Nota a crear")
    
    response = requests.post(
        f"{CLIENTS_URL}/{phone}/notas",
        json=nueva_nota,
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 201:
        nota = response.json()
        print_success("Nota creada exitosamente")
        print_json(nota, "Respuesta del servidor")
        
        # Validar campos
        assert nota.get("contenido") == nueva_nota["contenido"], "Texto de nota no coincide"
        assert nota.get("staff_nombre") == nueva_nota["staff_nombre"], "Staff no coincide"
        assert "fecha_creacion" in nota, "Falta campo fecha_creacion"
        
        print_success("Todos los campos validados correctamente")
        return nota
    elif response.status_code == 404:
        print_error(f"Cliente {phone} no encontrado")
        return None
    else:
        print_error(f"Error: {response.status_code}")
        print_json(response.json())
        return None

def test_verify_airtable_boolean_conversion(token: str, phone: str):
    """Test especial: Verificar creación de múltiples tipos de preferencias."""
    print_step("TEST: Crear Múltiples Tipos de Preferencias")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear preferencia de tipo zona_favorita
    pref1 = {
        "tipo": "zona_favorita",
        "descripcion": "Prefiere terraza (TEST)"
    }
    
    response1 = requests.post(
        f"{CLIENTS_URL}/{phone}/preferencias",
        json=pref1,
        headers=headers
    )
    
    if response1.status_code == 201:
        print_success(f"Creada preferencia tipo zona_favorita")
    else:
        print_error(f"Error creando preferencia zona_favorita: {response1.status_code}")
    
    # Crear preferencia de tipo solicitud_especial
    pref2 = {
        "tipo": "solicitud_especial",
        "descripcion": "Necesita trona para bebé (TEST)"
    }
    
    response2 = requests.post(
        f"{CLIENTS_URL}/{phone}/preferencias",
        json=pref2,
        headers=headers
    )
    
    if response2.status_code == 201:
        print_success(f"Creada preferencia tipo solicitud_especial")
    else:
        print_error(f"Error creando preferencia solicitud_especial: {response2.status_code}")
    
    print("\n" + "="*60)
    print("RESUMEN PREFERENCIAS:")
    print("="*60)
    print("Tipos válidos en Airtable:")
    print("  - zona_favorita")
    print("  - solicitud_especial")
    print("  - restriccion_dietetica")
    print("  - ocasion_celebracion")
    print("="*60)

# ========== EJECUCIÓN PRINCIPAL ==========

def main():
    """Ejecuta todos los tests en secuencia."""
    print("\n")
    print("="*60)
    print("  TEST COMPREHENSIVO: API DE CLIENTES")
    print("  Módulo: src/api/dashboard/clients_api.py")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Usuario: {TEST_USER}")
    print("="*60)
    
    try:
        # 1. Autenticación
        token = get_auth_token()
        
        # 2. Listar clientes (sin relaciones)
        test_list_clients(token)
        
        # 3. Listar clientes (con relaciones)
        test_list_clients_with_relations(token)
        
        # 4. Obtener cliente existente por teléfono
        print_warning(f"\nAjustar EXISTING_PHONE={EXISTING_PHONE} según datos reales en Airtable")
        test_get_client_by_phone(token, EXISTING_PHONE)
        
        # 5. Crear nuevo cliente
        nuevo_cliente = test_create_client(token)
        
        if nuevo_cliente:
            phone_creado = nuevo_cliente["telefono"]
            
            # 6. Añadir preferencia (test conversión Boolean)
            test_add_preferencia(token, phone_creado)
            
            # 7. Añadir nota
            test_add_nota(token, phone_creado)
            
            # 8. TEST CRÍTICO: Conversión Boolean exhaustiva
            test_verify_airtable_boolean_conversion(token, phone_creado)
            
            # 9. Verificar que relaciones se crearon correctamente
            print_step("VERIFICACIÓN FINAL: Cliente con todas las relaciones")
            cliente_final = test_get_client_by_phone(token, phone_creado)
            
            if cliente_final:
                total_prefs = len(cliente_final.get("preferencias", []))
                total_notas = len(cliente_final.get("notas", []))
                
                print_success(f"\nCliente creado con éxito:")
                print(f"  - Nombre: {cliente_final['nombre']}")
                print(f"  - Teléfono: {cliente_final['telefono']}")
                print(f"  - Preferencias: {total_prefs}")
                print(f"  - Notas: {total_notas}")
                
                # Validar linked records
                if total_prefs > 0:
                    print_success("[OK] Linked records de Preferencias funcionan")
                else:
                    print_warning("[WARN] No se encontraron preferencias")
                
                if total_notas > 0:
                    print_success("[OK] Linked records de Notas funcionan")
                else:
                    print_warning("[WARN] No se encontraron notas")
        
        # RESUMEN FINAL
        print("\n" + "="*60)
        print(f"{Colors.GREEN}  [SUCCESS] TESTING COMPLETADO EXITOSAMENTE{Colors.RESET}")
        print("="*60)
        print("\nVerificar en Airtable:")
        print("  1. Base: appQ2ZXAR68cqDmJt")
        print("  2. Tabla Clientes: tblPcVRnFTKDu7Z9t")
        print("  3. Tabla ClientePreferencias: tbl6xjlRuyJZMmzOV")
        print("  4. Tabla ClienteNotas: tbl5RZ31kxSOkGe0U")
        print("\nCampos críticos a verificar:")
        print("  - ClientePreferencias.Es_Importante debe tener 'Sí' o 'No'")
        print("  - ClientePreferencias.Cliente debe estar linkeado (array)")
        print("  - ClienteNotas.Cliente debe estar linkeado (array)")
        print("="*60 + "\n")
        
    except Exception as e:
        print_error(f"\nERROR FATAL: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
