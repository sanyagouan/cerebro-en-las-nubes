#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar qué plantillas están rechazadas y deben eliminarse.
"""
import os
import sys
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


def get_all_content_templates(account_sid: str, auth_token: str) -> list:
    """Obtener todas las plantillas de contenido de Twilio."""
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
    """Obtener el estado de aprobación de una plantilla específica."""
    url = f"https://content.twilio.com/v1/Content/{content_sid}/ApprovalRequests/whatsapp"
    auth = (account_sid, auth_token)
    headers = {"Accept": "application/json"}
    
    response = requests.get(url, auth=auth, headers=headers, timeout=30)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        return {"status": "not_submitted", "content_sid": content_sid}
    else:
        return {"status": "error", "code": response.status_code, "message": response.text}


def main():
    print("=" * 70)
    print("VERIFICACIÓN DE PLANTILLAS PARA ELIMINACIÓN")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Obtener credenciales
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    
    if not account_sid or not auth_token:
        print("\n❌ ERROR: No se encontraron las credenciales de Twilio.")
        sys.exit(1)
    
    print(f"\n📋 Account SID: {account_sid[:8]}...{account_sid[-4:]}")
    
    # Nombres de plantillas que nos interesan
    target_templates = [
        "reserva_confirmacion_nubes",
        "reserva_recordatorio_nubes", 
        "reserva_cancelada_nubes",
        "mesa_disponible_nubes"
    ]
    
    # Obtener todas las plantillas
    print("\n" + "-" * 70)
    print("OBTENIENDO PLANTILLAS DE TWILIO CONTENT API")
    print("-" * 70)
    
    try:
        all_templates = get_all_content_templates(account_sid, auth_token)
        print(f"Total de plantillas encontradas: {len(all_templates)}")
    except Exception as e:
        print(f"❌ Error al obtener plantillas: {e}")
        sys.exit(1)
    
    # Filtrar las plantillas que nos interesan
    print("\n" + "-" * 70)
    print("VERIFICANDO ESTADO DE APROBACIÓN")
    print("-" * 70)
    
    templates_to_delete = []
    templates_ok = []
    
    for template in all_templates:
        name = template.get("friendly_name", "")
        sid = template.get("sid", "")
        
        if name in target_templates:
            print(f"\n📄 {name}")
            print(f"   SID: {sid}")
            
            # Verificar estado de aprobación
            approval = get_template_approval_status(account_sid, auth_token, sid)
            status = approval.get("status", "unknown").lower()
            
            if status == "rejected":
                print(f"   Estado: ❌ RECHAZADA - MARCAR PARA ELIMINACIÓN")
                templates_to_delete.append({"name": name, "sid": sid, "reason": approval.get("rejection_reason", "No especificada")})
            elif status == "approved":
                print(f"   Estado: ✅ APROBADA")
                templates_ok.append({"name": name, "sid": sid})
            elif status == "pending":
                print(f"   Estado: ⏳ PENDIENTE")
            else:
                print(f"   Estado: ❓ {status.upper()}")
            
            if "rejection_reason" in approval:
                print(f"   Razón: {approval['rejection_reason']}")
    
    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    
    print(f"\n🔴 Plantillas RECHAZADAS a eliminar: {len(templates_to_delete)}")
    for t in templates_to_delete:
        print(f"   - {t['name']} (SID: {t['sid']})")
        print(f"     Razón: {t['reason']}")
    
    print(f"\n🟢 Plantillas APROBADAS (no eliminar): {len(templates_ok)}")
    for t in templates_ok:
        print(f"   - {t['name']} (SID: {t['sid']})")
    
    # Guardar lista de SIDs a eliminar
    if templates_to_delete:
        print("\n" + "=" * 70)
        print("SIDs A ELIMINAR:")
        print("=" * 70)
        for t in templates_to_delete:
            print(f"   {t['sid']}  # {t['name']}")
    
    return templates_to_delete


if __name__ == "__main__":
    main()
