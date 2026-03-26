#!/usr/bin/env python3
"""
Script para investigar la sincronización de plantillas de Meta a Twilio.
"""
import os
import sys
import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Cargar variables de entorno
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"[OK] Cargando variables desde: {env_file}")
else:
    print(f"[ERROR] No se encontro archivo .env en {project_root}")
    sys.exit(1)

# Credenciales de Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    print("[ERROR] TWILIO_ACCOUNT_SID y TWILIO_AUTH_TOKEN deben estar configurados")
    sys.exit(1)

# URLs base
BASE_URL_CONTENT = "https://content.twilio.com/v1"

print("\n" + "=" * 80)
print("INVESTIGACION DE SINCRONIZACION META -> Twilio")
print("=" * 80)
print(f"Account SID: {TWILIO_ACCOUNT_SID}")
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 1. Consultar LegacyContent (plantillas de Meta mapeadas)
print("\n" + "-" * 80)
print("1. CONSULTANDO ENDPOINT LegacyContent")
print("-" * 80)
url = f"{BASE_URL_CONTENT}/LegacyContent"
try:
    response = requests.get(url, auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN), params={"PageSize": 50})
    
    print(f"\nURL: {url}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        
        print(f"\n[OK] Respuesta exitosa!")
        print(f"   Total de plantillas mapeadas: {len(results)}")
        
        if results:
            print("\nPLANTILLAS DE META MAPEADAS:")
            print("-" * 80)
            for t in results:
                name = t.get("legacy_template_name", "N/A")
                content_sid = t.get("sid", "N/A")
                status = t.get("status", "N/A")
                legacy_id = t.get("legacy_template_id", "N/A")
                language = t.get("language", "N/A")
                variables = t.get("variables", [])
                
                print(f"\n  [*] {name}")
                print(f"     Content SID: {content_sid}")
                print(f"     Legacy ID (Meta): {legacy_id}")
                print(f"     Estado: {status}")
                print(f"     Idioma: {language}")
                print(f"     Variables: {', '.join(variables) if variables else 'Ninguna'}")
        else:
            print("\n[WARNING] No hay plantillas mapeadas en LegacyContent.")
            print("   Esto significa que:")
            print("   1. Tu WABA no ha sido migrada automaticamente")
            print("   2. Las plantillas fueron creadas despues de la migracion")
            print("   3. Necesitas contactar a soporte de Twilio")
    else:
        print(f"\n[ERROR] {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"\n[ERROR] Excepcion: {e}")

# 2. Listar todas las plantillas en Content API
print("\n" + "-" * 80)
print("2. LISTANDO PLANTILLAS EN CONTENT API")
print("-" * 80)
url = f"{BASE_URL_CONTENT}/Content"
try:
    response = requests.get(url, auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN), params={"PageSize": 50})
    
    print(f"\nURL: {url}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        contents = data.get("contents", [])
        
        print(f"\n[OK] Respuesta exitosa!")
        print(f"   Total de plantillas en Content API: {len(contents)}")
        
        if contents:
            print("\nPLANTILLAS EN CONTENT API:")
            print("-" * 80)
            for c in contents:
                sid = c.get("sid", "N/A")
                name = c.get("friendly_name", "N/A")
                status = c.get("status", "N/A")
                language = c.get("language", "N/A")
                types = c.get("types", [])
                date_created = c.get("date_created", "N/A")
                
                print(f"\n  [*] {name}")
                print(f"     Content SID: {sid}")
                print(f"     Estado: {status}")
                print(f"     Idioma: {language}")
                print(f"     Tipos: {', '.join(types) if types else 'Ninguno'}")
                print(f"     Creado: {date_created}")
        else:
            print("\n[OK] No hay plantillas en Content API.")
            print("   Entorno limpio - listo para sincronizar desde Meta.")
    else:
        print(f"\n[ERROR] {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"\n[ERROR] Excepcion: {e}")

# 3. Investigar opciones de sincronización
print("\n" + "-" * 80)
print("3. OPCIONES DE SINCRONIZACION")
print("-" * 80)
print("""
Segun la documentacion de Twilio (https://www.twilio.com/docs/content/content-api),
hay varias formas de sincronizar plantillas de Meta Business Manager a Twilio:

OPCION 1: AUTOMATICO (SI APLICA)
--------------------------------
Si creaste plantillas en Twilio con el mismo nombre y categoria que en Meta,
Twilio intenta vincularlas automaticamente.

[+] Ventaja: Sin intervencion manual
[-] Desventaja: Puede haber conflictos si los nombres no coinciden exactamente

OPCION 2: CONTENT API (RECOMENDADO)
-----------------------------------
Crear plantillas usando Content API con los mismos nombres que en Meta.
Twilio las vinculara automaticamente.

[+] Ventaja: Metodo moderno y recomendado
[+] Soporte para multiples idiomas y tipos de contenido
[-] Desventaja: Requiere recrear las plantillas

OPCION 3: CONTACTAR SOPORTE DE TWILIO
-------------------------------------
Si las opciones anteriores no funcionan, puedes contactar a soporte
tecnico de Twilio para que migren manualmente las plantillas.

Telefono: +34 91 274 5900 (Espana)
Email: help@twilio.com
""")

print("\n" + "=" * 80)
print("FIN DE LA INVESTIGACION")
print("=" * 80)
