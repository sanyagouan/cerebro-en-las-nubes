#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para eliminar 22 plantillas WhatsApp obsoletas de Twilio Content API.
Solo conserva las 4 plantillas correctas.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Forzar codificacion UTF-8 en Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Cargar credenciales de .env
load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

if not account_sid or not auth_token:
    print("[ERROR] Credenciales TWILIO no encontradas en .env")
    sys.exit(1)

# Plantillas a eliminar (22 SIDs)
templates_to_delete = [
    # Confirmacion (7 obsoletas)
    "HXd7ce27ac9661f249829fc837325e1612",
    "HXe179c437fce3cbf0c325edd43389d930",
    "HX23b0e71dd0324315a64427e44679d6a3",
    "HXa0915cf5109e2e5062fa195a6ab3c3a4",
    "HX5352b9aa7f916c818e2407dccb671a74",
    "HX7175f69e6fcd551065df13962b6d96c6",
    "HXdb0dca8764f0021f9ff2fd197ba22497",
    # Recordatorio (5 obsoletas)
    "HXb3e508a6f995764a7a7672ae82d21449",
    "HXf4773e8889a00b6bd89bc6315753299a",
    "HX1b13d76cadb3c3d1b83ca7a156e8a2c4",
    "HX9f412c66c3b020f33263a7c427fb4f8a",
    "HXfd2da5b5d0be89ee94da39c32087c2dd",
    # Cancelacion (5 obsoletas)
    "HXeb899f313378eff3a08c182a972c5a59",
    "HX2e728719e799d43062bed2cc1c5f32e3",
    "HXf61a6c6d4f4f8db797a000cae0e2b9a0",
    "HX11653feaa8033ec23d509bc175b45499",
    "HX00f05a592e1cc7d1236fddd557483131",
    # Mesa disponible (5 obsoletas)
    "HX4af239d8593e7f5d7f676c669804cf32",
    "HXe8f9d9f9b332f8471df617c76923df19",
    "HX70e954af8fa6b908b09d9ef46ae86c46",
    "HX290ecdc892f4cac5f856c7a103b1e016",
    "HX59e92f47f2a3fa3d81f472eac4092737",
]

# Ejecutar la eliminacion
success_count = 0
failed_count = 0
failed_sids = []

print(f"[INFO] Iniciando eliminacion de {len(templates_to_delete)} plantillas obsoletas...")
print("=" * 60)

for sid in templates_to_delete:
    print(f"\n[DELETE] Eliminando {sid}...")
    url = f"https://content.twilio.com/v1/Content/{sid}"
    
    try:
        response = requests.delete(
            url,
            auth=(account_sid, auth_token),
            timeout=30
        )
        
        if response.status_code == 204:
            success_count += 1
            print(f"  [OK] Eliminado: {sid}")
        else:
            failed_count += 1
            failed_sids.append(sid)
            print(f"  [ERROR] HTTP {response.status_code} eliminando {sid}")
            if response.text:
                print(f"         Detalle: {response.text[:200]}")
    except requests.exceptions.Timeout:
        failed_count += 1
        failed_sids.append(sid)
        print(f"  [TIMEOUT] Timeout eliminando {sid}")
    except Exception as e:
        failed_count += 1
        failed_sids.append(sid)
        print(f"  [ERROR] Error inesperado: {str(e)}")

# Verificar resultado final
print(f"\n{'=' * 60}")
print(f"[RESUMEN] Resumen de eliminacion:")
print(f"  - Plantillas procesadas: {len(templates_to_delete)}")
print(f"  - Eliminadas exitosamente: {success_count}")
print(f"  - Errores: {failed_count}")
if failed_sids:
    print(f"\n[ERRORES] SIDs con errores:")
    for sid in failed_sids:
        print(f"    - {sid}")

if success_count > 0:
    print(f"\n[SUCCESS] Limpieza completada. Se eliminaron {success_count} plantillas.")
