#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para borrar TODAS las plantillas de Twilio Content API.
Esto limpia el entorno antes de sincronizar desde Meta Business Manager.

Uso:
    python delete_all_twilio_templates.py [--force]
    
    --force : Borra sin pedir confirmación (útil para automatización)
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Forzar UTF-8 en Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Cargar variables de entorno
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# Verificar flag --force
FORCE_MODE = "--force" in sys.argv or "-f" in sys.argv

def get_all_templates():
    """Lista todas las plantillas de Content API"""
    url = "https://content.twilio.com/v1/Content"
    
    response = requests.get(
        url,
        auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get("contents", [])
    else:
        print(f"Error listando plantillas: {response.status_code}")
        print(response.text)
        return []

def delete_template(content_sid):
    """Borra una plantilla especifica"""
    url = f"https://content.twilio.com/v1/Content/{content_sid}"
    
    response = requests.delete(
        url,
        auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    )
    
    return response.status_code == 204

def main():
    print("=" * 60)
    print("BORRADO DE TODAS LAS PLANTILLAS DE TWILIO CONTENT API")
    print("=" * 60)
    
    # Listar todas las plantillas
    print("\n[INFO] Listando plantillas actuales...")
    templates = get_all_templates()
    
    if not templates:
        print("[OK] No hay plantillas para borrar.")
        return
    
    print(f"\n[INFO] Encontradas {len(templates)} plantillas:")
    print("-" * 60)
    
    for t in templates:
        content_sid = t.get("sid")
        friendly_name = t.get("friendly_name", "Sin nombre")
        types_keys = list(t.get('types', {}).keys())
        print(f"  - SID: {content_sid}")
        print(f"    Nombre: {friendly_name}")
        print(f"    Tipo: {types_keys}")
        print()
    
    # Confirmar borrado
    print("-" * 60)
    
    if FORCE_MODE:
        print("[!] Modo FORCE activado - borrando sin confirmacion...")
    else:
        confirm = input(f"[!] Estas seguro de borrar TODAS las {len(templates)} plantillas? (escribe 'SI' para confirmar): ")
        
        if confirm != "SI":
            print("[CANCELADO] Operacion cancelada.")
            return
    
    # Borrar cada plantilla
    print("\n[TRABAJANDO] Borrando plantillas...")
    deleted = 0
    failed = 0
    
    for t in templates:
        content_sid = t.get("sid")
        friendly_name = t.get("friendly_name", "Sin nombre")
        
        if delete_template(content_sid):
            print(f"  [OK] Borrada: {friendly_name} ({content_sid})")
            deleted += 1
        else:
            print(f"  [ERROR] Error borrando: {friendly_name} ({content_sid})")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTADO: {deleted} borradas, {failed} fallos")
    print("=" * 60)

if __name__ == "__main__":
    main()
