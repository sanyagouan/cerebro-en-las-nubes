#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para comprobar el estado de aprobación de las plantillas de WhatsApp
en Twilio Content API.

Basado en scripts/create_whatsapp_templates.py
"""

import io
import os
import sys
import requests
from datetime import datetime
from pathlib import Path

# Añadir el directorio raíz al path para importar content_sids
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from src.infrastructure.templates.content_sids import whatsapp_template_sids

# Cargar variables de entorno desde .env si existe
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


def get_all_content_templates(account_sid: str, auth_token: str) -> list:
    """
    Obtener todas las plantillas de contenido de Twilio.
    
    Endpoint: GET https://content.twilio.com/v1/Content
    """
    url = "https://content.twilio.com/v1/Content"
    
    auth = (account_sid, auth_token)
    headers = {"Accept": "application/json"}
    
    response = requests.get(url, auth=auth, headers=headers, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("contents", [])
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")


def get_template_approval_status(account_sid: str, auth_token: str, content_sid: str) -> dict:
    """
    Obtener el estado de aprobación de una plantilla específica.
    
    Endpoint: GET https://content.twilio.com/v1/Content/{sid}/ApprovalRequests/whatsapp
    """
    url = f"https://content.twilio.com/v1/Content/{content_sid}/ApprovalRequests/whatsapp"
    
    auth = (account_sid, auth_token)
    headers = {"Accept": "application/json"}
    
    response = requests.get(url, auth=auth, headers=headers, timeout=30)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        # No se ha enviado para aprobación todavía
        return {"status": "not_submitted", "content_sid": content_sid}
    else:
        return {"status": "error", "code": response.status_code, "message": response.text}


def get_template_details(account_sid: str, auth_token: str, content_sid: str) -> dict:
    """
    Obtener detalles de una plantilla específica.
    
    Endpoint: GET https://content.twilio.com/v1/Content/{sid}
    """
    url = f"https://content.twilio.com/v1/Content/{content_sid}"
    
    auth = (account_sid, auth_token)
    headers = {"Accept": "application/json"}
    
    response = requests.get(url, auth=auth, headers=headers, timeout=30)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Error {response.status_code}: {response.text}"}


def main():
    # Configurar codificación UTF-8 para Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    print("=" * 70)
    print("ESTADO DE PLANTILLAS DE WHATSAPP EN TWILIO")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Obtener credenciales de Twilio desde variables de entorno
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    
    if not account_sid or not auth_token:
        print("\n❌ ERROR: No se encontraron las credenciales de Twilio.")
        print("Asegúrate de tener configuradas las variables de entorno:")
        print("  - TWILIO_ACCOUNT_SID")
        print("  - TWILIO_AUTH_TOKEN")
        sys.exit(1)
    
    print(f"\n📋 Account SID: {account_sid[:8]}...{account_sid[-4:]}")
    
    # Primero, obtener todas las plantillas de Content API
    print("\n" + "-" * 70)
    print("1. OBTENIENDO TODAS LAS PLANTILLAS DE CONTENT API")
    print("-" * 70)
    
    try:
        all_templates = get_all_content_templates(account_sid, auth_token)
        print(f"   Total de plantillas encontradas: {len(all_templates)}")
    except Exception as e:
        print(f"   ❌ Error al obtener plantillas: {e}")
        all_templates = []
    
    # Mostrar todas las plantillas encontradas
    if all_templates:
        print("\n   Plantillas en Content API:")
        for template in all_templates:
            sid = template.get("sid", "N/A")
            name = template.get("friendly_name", "Sin nombre")
            language = template.get("language", "N/A")
            print(f"   - {name}")
            print(f"     SID: {sid}")
            print(f"     Idioma: {language}")
    
    # Ahora verificar el estado de aprobación de nuestras plantillas
    print("\n" + "-" * 70)
    print("2. VERIFICANDO ESTADO DE APROBACIÓN DE NUESTRAS PLANTILLAS")
    print("-" * 70)
    
    # Mapeo de nombres a SIDs desde content_sids.py
    template_sids = whatsapp_template_sids
    
    if not template_sids:
        print("   ⚠️ No hay SIDs de plantillas configurados en content_sids.py")
        sys.exit(0)
    
    print(f"   Plantillas configuradas: {len(template_sids)}")
    
    approval_summary = {
        "approved": [],
        "pending": [],
        "rejected": [],
        "not_submitted": [],
        "error": []
    }
    
    for name, sid in template_sids.items():
        print(f"\n   📄 {name}")
        print(f"      SID: {sid}")
        
        # Obtener detalles de la plantilla
        details = get_template_details(account_sid, auth_token, sid)
        if "error" not in details:
            print(f"      Friendly Name: {details.get('friendly_name', 'N/A')}")
            print(f"      Language: {details.get('language', 'N/A')}")
            # Mostrar el cuerpo del mensaje si está disponible
            types = details.get("types", {})
            if "twilio/text" in types:
                body = types["twilio/text"].get("body", "")
                if body:
                    print(f"      Body: {body[:80]}..." if len(body) > 80 else f"      Body: {body}")
        
        # Obtener estado de aprobación
        approval = get_template_approval_status(account_sid, auth_token, sid)
        status = approval.get("status", "unknown").lower()
        
        # Mapear estados comunes
        status_display = {
            "approved": "✅ APROBADA",
            "pending": "⏳ PENDIENTE",
            "rejected": "❌ RECHAZADA",
            "not_submitted": "⚠️ NO ENVIADA",
            "unknown": "❓ DESCONOCIDO"
        }
        
        display_status = status_display.get(status, f"❓ {status.upper()}")
        print(f"      Estado: {display_status}")
        
        # Si hay información adicional de aprobación
        if "rejection_reason" in approval:
            print(f"      Razón rechazo: {approval['rejection_reason']}")
        if "category" in approval:
            print(f"      Categoría: {approval['category']}")
        
        # Clasificar en el resumen
        if status == "approved":
            approval_summary["approved"].append(name)
        elif status == "pending":
            approval_summary["pending"].append(name)
        elif status == "rejected":
            approval_summary["rejected"].append(name)
        elif status == "not_submitted":
            approval_summary["not_submitted"].append(name)
        else:
            approval_summary["error"].append(name)
    
    # Mostrar resumen final
    print("\n" + "=" * 70)
    print("RESUMEN DE ESTADO")
    print("=" * 70)
    
    print(f"\n   ✅ Aprobadas: {len(approval_summary['approved'])}")
    for name in approval_summary["approved"]:
        print(f"      - {name}")
    
    print(f"\n   ⏳ Pendientes: {len(approval_summary['pending'])}")
    for name in approval_summary["pending"]:
        print(f"      - {name}")
    
    print(f"\n   ❌ Rechazadas: {len(approval_summary['rejected'])}")
    for name in approval_summary["rejected"]:
        print(f"      - {name}")
    
    print(f"\n   ⚠️ No enviadas: {len(approval_summary['not_submitted'])}")
    for name in approval_summary["not_submitted"]:
        print(f"      - {name}")
    
    if approval_summary["error"]:
        print(f"\n   ❓ Error/Desconocido: {len(approval_summary['error'])}")
        for name in approval_summary["error"]:
            print(f"      - {name}")
    
    # Conclusión
    print("\n" + "=" * 70)
    total = len(template_sids)
    approved = len(approval_summary["approved"])
    
    if approved == total:
        print("🎉 ¡TODAS LAS PLANTILLAS ESTÁN APROBADAS!")
        print("   Puedes proceder con las pruebas de envío.")
    elif approved > 0:
        print(f"⚠️ {approved} de {total} plantillas aprobadas.")
        print("   Espera a que las pendientes sean aprobadas o revisa las rechazadas.")
    else:
        print("❌ Ninguna plantilla está aprobada todavía.")
        print("   Verifica que las plantillas fueron enviadas para aprobación.")
    
    print("=" * 70)
    
    return approval_summary


if __name__ == "__main__":
    main()
