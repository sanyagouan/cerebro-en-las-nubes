#!/usr/bin/env python3
"""
Script para eliminar plantillas duplicadas de Twilio Content API.

Este script elimina los duplicados extra, dejando solo las 4 plantillas correctas.
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Credenciales de Twilio
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# Plantillas a CONSERVAR (las correctas)
KEEP_TEMPLATES = {
    "HX9eabc58236ea6a1fa164bc269a5b02ec": "reserva_confirmacion_nubes",
    "HXdcd66832f0b0f876a3e5b35abdbadb21": "reserva_recordatorio_nubes",
    "HX6967da785fc67facf23b52ba7f64f5cd": "reserva_cancelada_nubes",
    "HX4c7f1da68c900f436c7099817522327a": "mesa_disponible_nubes",
}

# Plantillas duplicadas a ELIMINAR
DELETE_TEMPLATES = [
    "HXac7ce43a992ad569970aedfc62268634",  # mesa_disponible_nubes (duplicado)
    "HX4aa053a5af88f5b45fe08828c4c604bb",  # reserva_cancelada_nubes (duplicado)
    "HXeea08fc6bd52c6f18afb8bf5c793746b",  # reserva_confirmacion_nubes (duplicado)
    "HX123ebd02fc4a286200d9dc9ee090657f",  # reserva_recordatorio_nubes (duplicado)
]


def delete_template(sid: str) -> tuple[bool, str]:
    """
    Elimina una plantilla de Twilio Content API.
    
    Returns:
        tuple: (success, message)
    """
    url = f"https://content.twilio.com/v1/Content/{sid}"
    
    try:
        response = requests.delete(
            url,
            auth=(ACCOUNT_SID, AUTH_TOKEN),
            timeout=30
        )
        
        if response.status_code == 204:
            return True, "Eliminada exitosamente"
        elif response.status_code == 404:
            return True, "Ya no existe (previamente eliminada)"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
            
    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    print("[INFO] Eliminando plantillas duplicadas...")
    print("=" * 60)
    print()
    
    # Verificar credenciales
    if not ACCOUNT_SID or not AUTH_TOKEN:
        print("[ERROR] Faltan credenciales de Twilio")
        return
    
    print(f"[INFO] Account SID: {ACCOUNT_SID[:10]}...{ACCOUNT_SID[-4:]}")
    print(f"[INFO] Plantillas a eliminar: {len(DELETE_TEMPLATES)}")
    print()
    
    # Eliminar cada plantilla
    deleted = []
    already_gone = []
    errors = []
    
    for sid in DELETE_TEMPLATES:
        print(f"[DELETE] Eliminando {sid}...")
        success, message = delete_template(sid)
        
        if success:
            if "previamente" in message.lower():
                already_gone.append(sid)
                print(f"  [INFO] {message}")
            else:
                deleted.append(sid)
                print(f"  [OK] {message}")
        else:
            errors.append((sid, message))
            print(f"  [ERROR] {message}")
    
    # Resumen
    print()
    print("=" * 60)
    print("[RESUMEN] Resumen de eliminación:")
    print(f"  - Eliminadas en esta ejecución: {len(deleted)}")
    print(f"  - Ya no existían: {len(already_gone)}")
    print(f"  - Errores: {len(errors)}")
    
    if deleted:
        print()
        print("[ELIMINADAS] SIDs eliminados exitosamente:")
        for sid in deleted:
            print(f"    - {sid}")
    
    if already_gone:
        print()
        print("[PREVIAMENTE] SIDs que ya no existían:")
        for sid in already_gone:
            print(f"    - {sid}")
    
    if errors:
        print()
        print("[ERRORES] SIDs con errores:")
        for sid, msg in errors:
            print(f"    - {sid}: {msg}")
    
    # Verificar estado final
    print()
    print("=" * 60)
    print("[VERIFICACIÓN] Consultando plantillas restantes...")
    
    url = "https://content.twilio.com/v1/Content"
    response = requests.get(url, auth=(ACCOUNT_SID, AUTH_TOKEN), timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        contents = data.get("contents", [])
        print(f"  Total de plantillas restantes: {len(contents)}")
        print()
        
        for content in contents:
            sid = content.get("sid")
            name = content.get("friendly_name", "N/A")
            expected = KEEP_TEMPLATES.get(sid, "⚠️ NO ESPERADA")
            status = "✅ CORRECTA" if sid in KEEP_TEMPLATES else "⚠️ DUPLICADO EXTRA"
            print(f"  {status} - {name}")
            print(f"    SID: {sid}")
    else:
        print(f"  [ERROR] No se pudo verificar: HTTP {response.status_code}")


if __name__ == "__main__":
    main()
