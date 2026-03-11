"""
Script de prueba para verificar la autenticacion de usuarios.
"""
import asyncio
import sys
import os

# Configurar variables de entorno antes de importar
os.environ['AIRTABLE_BASE_ID'] = 'appQ2ZXAR68cqDmJt'

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from application.services.auth_service import auth_service


# Credenciales de prueba
TEST_CREDENTIALS = [
    {"usuario": "administradora", "password": "AdminNubes2026!"},
    {"usuario": "encargada", "password": "Encargada2026!"},
    {"usuario": "tecnico", "password": "Tecnico2026!"},
    # Prueba con credenciales incorrectas
    {"usuario": "administradora", "password": "PasswordIncorrecto"},
    {"usuario": "usuario_inexistente", "password": "cualquiera"},
]


async def test_authentication():
    """Prueba la autenticacion con diferentes credenciales."""
    
    print("\n" + "="*60)
    print("TEST DE AUTENTICACION")
    print("="*60 + "\n")
    
    success_count = 0
    
    for idx, creds in enumerate(TEST_CREDENTIALS, 1):
        print(f"[TEST {idx}] Probando usuario: {creds['usuario']}")
        print(f"         Password: {creds['password'][:5]}...")
        
        try:
            user = await auth_service.authenticate_user(
                usuario=creds['usuario'],
                password=creds['password']
            )
            
            if user:
                print(f"    [SUCCESS] Autenticacion exitosa")
                print(f"    Usuario ID: {user['id']}")
                print(f"    Nombre: {user['nombre']}")
                print(f"    Rol: {user['rol']}")
                
                # Crear token de acceso
                token = auth_service.create_access_token(
                    user_id=user['id'],
                    usuario=user['usuario'],
                    nombre=user['nombre'],
                    rol=user['rol']
                )
                
                print(f"    Token JWT: {token[:50]}...")
                
                # Verificar token
                payload = auth_service.verify_token(token)
                if payload:
                    print(f"    [SUCCESS] Token verificado correctamente")
                    success_count += 1
                else:
                    print(f"    [ERROR] Token no pudo ser verificado")
            else:
                print(f"    [FAILED] Autenticacion fallida")
                if idx in [1, 2, 3]:  # Solo para credenciales correctas
                    print(f"    [ERROR] Se esperaba autenticacion exitosa!")
                else:
                    print(f"    [OK] Fallo esperado (credenciales incorrectas)")
                
        except Exception as e:
            print(f"    [ERROR] Excepcion: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("="*60)
    print(f"FIN DE PRUEBAS - {success_count}/3 autenticaciones exitosas")
    print("="*60)
    
    return success_count == 3


if __name__ == "__main__":
    result = asyncio.run(test_authentication())
    sys.exit(0 if result else 1)
