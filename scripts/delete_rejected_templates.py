#!/usr/bin/env python3
"""
Script para eliminar plantillas rechazadas/duplicadas de Twilio Content API.

Este script:
1. Consulta TODAS las plantillas existentes en Twilio Content API
2. Identifica las que están en estado ERROR (rechazadas)
3. Las elimina para permitir recreación limpia
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv


def get_all_content_templates(account_sid: str, auth_token: str) -> list:
    """Obtener todas las plantillas de contenido de Twilio."""
    url = "https://content.twilio.com/v1/Content"
    auth = (account_sid, auth_token)
    headers = {"Accept": "application/json"}
    
    all_templates = []
    page_token = None
    
    while True:
        params = {"PageSize": 100}
        if page_token:
            params["PageToken"] = page_token
        
        response = requests.get(url, auth=auth, headers=headers, params=params, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Error obteniendo plantillas: {response.status_code} - {response.text}")
            break
        
        data = response.json()
        all_templates.extend(data.get("contents", []))
        
        # Verificar si hay más páginas
        meta = data.get("meta", {})
        if meta.get("next_page_url"):
            page_token = meta.get("next_page_token")
        else:
            break
    
    return all_templates


def delete_content_template(account_sid: str, auth_token: str, content_sid: str) -> dict:
    """Eliminar una plantilla de contenido de Twilio."""
    url = f"https://content.twilio.com/v1/Content/{content_sid}"
    auth = (account_sid, auth_token)
    headers = {"Accept": "application/json"}
    
    response = requests.delete(url, auth=auth, headers=headers, timeout=30)
    
    if response.status_code == 204:
        return {"success": True, "sid": content_sid}
    else:
        return {"success": False, "sid": content_sid, "code": response.status_code, "message": response.text}


def main():
    print("=" * 70)
    print("ELIMINACIÓN DE PLANTILLAS RECHAZADAS/DUPLICADAS")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Cargar variables de entorno desde .env.mcp
    load_dotenv(dotenv_path=".env.mcp")
    
    # Obtener credenciales
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    
    if not account_sid or not auth_token:
        print("\n❌ ERROR: No se encontraron las credenciales de Twilio.")
        sys.exit(1)
    
    print(f"\n📋 Account SID: {account_sid[:8]}...{account_sid[-4:]}")
    
    # Paso 1: Obtener todas las plantillas
    print("\n📥 Obteniendo plantillas actuales de Twilio Content API...")
    templates = get_all_content_templates(account_sid, auth_token)
    
    if not templates:
        print("⚠️ No se encontraron plantillas.")
        return
    
    print(f"   Encontradas {len(templates)} plantillas.")
    
    # Paso 2: Identificar plantillas en estado ERROR (rechazadas)
    rejected_templates = []
    print("\n📋 Analizando estados de plantillas:")
    print("-" * 70)
    
    for template in templates:
        sid = template.get("sid", "N/A")
        name = template.get("friendly_name", template.get("types", {}).get("twilio/text", {}).get("body", "")[:50])
        
        # Obtener el estado de aprobación
        approval_requests = template.get("approval_requests", {})
        whatsapp_status = approval_requests.get("whatsapp", {}).get("status", "unknown")
        
        status_icon = "✅" if whatsapp_status == "approved" else "⏳" if whatsapp_status == "pending" else "❌"
        print(f"   {status_icon} {sid} | {name[:40]:<40} | Estado: {whatsapp_status}")
        
        # Si está en estado error o rejected, agregar a la lista
        if whatsapp_status in ["error", "rejected", "rejected_by_provider"]:
            rejected_templates.append({
                "sid": sid,
                "name": name,
                "status": whatsapp_status
            })
    
    print("-" * 70)
    
    if not rejected_templates:
        print("\n✅ No hay plantillas rechazadas para eliminar.")
        return
    
    print(f"\n🗑️ Se encontraron {len(rejected_templates)} plantillas rechazadas para eliminar:")
    for t in rejected_templates:
        print(f"   - {t['sid']} | {t['name'][:40]}")
    
    # Paso 3: Eliminar plantillas rechazadas (sin confirmación, automático)
    print("\n🗑️ Eliminando plantillas rechazadas...")
    print("-" * 70)
    
    deleted_count = 0
    failed_count = 0
    
    for template in rejected_templates:
        sid = template["sid"]
        name = template["name"]
        print(f"\n🗑️ Eliminando {sid} ({name[:30]})...")
        
        result = delete_content_template(account_sid, auth_token, sid)
        
        if result["success"]:
            print(f"   ✅ Eliminada correctamente")
            deleted_count += 1
        else:
            print(f"   ❌ Error: {result.get('message', 'Unknown error')}")
            failed_count += 1
    
    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN DE ELIMINACIÓN")
    print("=" * 70)
    print(f"\n✅ Plantillas eliminadas: {deleted_count}")
    print(f"❌ Errores: {failed_count}")
    
    if deleted_count == len(rejected_templates):
        print("\n🎉 ¡Todas las plantillas rechazadas han sido eliminadas!")
        print("   Ahora puedes recrear las 4 plantillas limpias.")
    else:
        print("\n⚠️ Algunas plantillas no pudieron eliminarse.")
        print("   Revisa los errores arriba.")


if __name__ == "__main__":
    main()
