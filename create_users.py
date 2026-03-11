"""
Script para crear usuarios iniciales en Airtable con contrasenias hasheadas.
"""
import bcrypt
import asyncio
from pyairtable import Api
import os

# Configuracion
BASE_ID = "appQ2ZXAR68cqDmJt"
TABLE_NAME = "Usuarios"
BCRYPT_ROUNDS = 12

# Usuarios a crear
USERS = [
    {
        "usuario": "administradora",
        "nombre": "Alba",
        "password": "AdminNubes2026!",
        "rol": "administradora",
        "telefono": None
    },
    {
        "usuario": "encargada",
        "nombre": "Maria",
        "password": "Encargada2026!",
        "rol": "encargada",
        "telefono": None
    },
    {
        "usuario": "tecnico",
        "nombre": "Soporte",
        "password": "Tecnico2026!",
        "rol": "camarero",  # Temporal: usamos camarero ya que "tecnico" no esta en las opciones
        "telefono": None
    }
]


def hash_password(password: str) -> str:
    """Hashea una contrasenia con bcrypt."""
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hash: str) -> bool:
    """Verifica una contrasenia contra su hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hash.encode("utf-8"))


def create_users():
    """Crea los usuarios en Airtable."""
    
    # Obtener API key desde variables de entorno
    api_key = os.getenv("AIRTABLE_API_KEY")
    if not api_key:
        print("[ERROR] AIRTABLE_API_KEY no esta configurada")
        print("   Ejecuta: $env:AIRTABLE_API_KEY='tu_api_key'")
        return False
    
    try:
        # Conectar con Airtable
        api = Api(api_key)
        table = api.table(BASE_ID, TABLE_NAME)
        
        print("\n[*] Generando hashes de contrasenias con bcrypt (12 rounds)...\n")
        
        created_users = []
        
        for user_data in USERS:
            print(f"[+] Procesando usuario: {user_data['usuario']}")
            
            # Generar hash
            password_hash = hash_password(user_data['password'])
            print(f"    Hash generado: {password_hash[:30]}...")
            
            # Verificar que el hash funciona
            if verify_password(user_data['password'], password_hash):
                print(f"    Hash verificado correctamente")
            else:
                print(f"    [ERROR] Hash no verifica")
                continue
            
            # Preparar campos para Airtable
            fields = {
                "Usuario": user_data['usuario'],
                "Nombre": user_data['nombre'],
                "Password_Hash": password_hash,
                "Rol": user_data['rol'],
                "Activo": True
            }
            
            if user_data['telefono']:
                fields["Telefono"] = user_data['telefono']
            
            # Crear registro en Airtable
            try:
                record = table.create(fields)
                print(f"    Usuario creado en Airtable (ID: {record['id']})")
                
                created_users.append({
                    "usuario": user_data['usuario'],
                    "nombre": user_data['nombre'],
                    "rol": user_data['rol'],
                    "password": user_data['password'],  # Solo para documentacion inicial
                    "airtable_id": record['id']
                })
                
            except Exception as e:
                print(f"    [ERROR] creando usuario en Airtable: {e}")
                continue
            
            print()
        
        # Resumen
        print("\n" + "="*60)
        print("[SUCCESS] USUARIOS CREADOS EXITOSAMENTE")
        print("="*60)
        
        for user in created_users:
            print(f"\n[USER] {user['nombre']} ({user['rol']})")
            print(f"   Usuario: {user['usuario']}")
            print(f"   Password: {user['password']}")
            print(f"   Airtable ID: {user['airtable_id']}")
        
        print("\n" + "="*60)
        print("[!] IMPORTANTE: Guarda estas credenciales de forma segura")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR]: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    create_users()
