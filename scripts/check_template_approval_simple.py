#!/usr/bin/env python3
"""
Script simplificado para verificar el estado de aprobacion de plantillas WhatsApp en Twilio.
Sin emojis para evitar errores de codificacion en Windows.
"""
import os
import requests
from requests.auth import HTTPBasicAuth

# Credenciales de Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "ACd37052c7a26448d2e12e20c68ecdca09")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")

# Plantillas a verificar (SIDs actualizados - aprobados por Meta 2026-03-26)
TEMPLATES_TO_CHECK = {
    "reserva_confirmacion": "HX501f76efa2d23dd2ccf4e86da3c01035",
    "reserva_recordatorio": "HX88be82bdddd2533f8c00fef3bf4ea410",
    "reserva_cancelada": "HX4afa946a6d0cf3a2f32f0a35cca05e47",
    "mesa_disponible": "HX2f6c7acdc8e74e47e3a4ccc887fbacfc"
}

def get_auth():
    """Obtener credenciales de autenticacion."""
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    if not auth_token:
        print("ERROR: TWILIO_AUTH_TOKEN no esta configurado")
        print("Ejecuta: $env:TWILIO_AUTH_TOKEN='tu_token'")
        return None
    return HTTPBasicAuth(TWILIO_ACCOUNT_SID, auth_token)

def check_template_approval(sid: str, auth) -> dict:
    """Consultar el estado de aprobacion de una plantilla."""
    url = f"https://content.twilio.com/v1/Content/{sid}/ApprovalRequests"
    
    try:
        response = requests.get(url, auth=auth, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status_code": 200,
                "data": data
            }
        elif response.status_code == 404:
            return {
                "status_code": 404,
                "error": "Plantilla no encontrada o sin solicitud de aprobacion"
            }
        else:
            return {
                "status_code": response.status_code,
                "error": response.text
            }
    except Exception as e:
        return {
            "status_code": 0,
            "error": str(e)
        }

def get_template_content(sid: str, auth) -> dict:
    """Obtener el contenido de una plantilla."""
    url = f"https://content.twilio.com/v1/Content/{sid}"
    
    try:
        response = requests.get(url, auth=auth, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def main():
    print("=" * 80)
    print("VERIFICACION DE ESTADO DE APROBACION DE PLANTILLAS WHATSAPP")
    print("=" * 80)
    print()
    
    # Verificar autenticacion
    auth = get_auth()
    if not auth:
        return
    
    print(f"Account SID: {TWILIO_ACCOUNT_SID}")
    print()
    
    # Resultados
    results = []
    
    for name, sid in TEMPLATES_TO_CHECK.items():
        print(f"--- Verificando: {name} ---")
        print(f"SID: {sid}")
        
        # 1. Verificar si la plantilla existe
        content = get_template_content(sid, auth)
        if "error" in content:
            print(f"  [X] Error al obtener contenido: {content['error']}")
            results.append({
                "name": name,
                "sid": sid,
                "exists": False,
                "approval_status": "N/A",
                "whatsapp_status": "N/A"
            })
            print()
            continue
        
        print(f"  [OK] Plantilla existe")
        print(f"  - Tipo: {content.get('types', {}).keys()}")
        
        # 2. Verificar estado de aprobacion
        approval = check_template_approval(sid, auth)
        
        if approval["status_code"] == 200:
            data = approval["data"]
            
            # Buscar estado de WhatsApp
            whatsapp_status = "desconocido"
            if "approval_requests" in data:
                whatsapp_data = data["approval_requests"].get("whatsapp", {})
                whatsapp_status = whatsapp_data.get("status", "no definido")
                rejection_reason = whatsapp_data.get("rejection_reason", "")
                
                print(f"  [APROBACION]")
                print(f"  - Estado WhatsApp: {whatsapp_status}")
                if rejection_reason:
                    print(f"  - Razon de rechazo: {rejection_reason}")
            else:
                print(f"  [!] Sin datos de approval_requests")
            
            results.append({
                "name": name,
                "sid": sid,
                "exists": True,
                "approval_status": "con datos",
                "whatsapp_status": whatsapp_status
            })
            
        elif approval["status_code"] == 404:
            print(f"  [!] Sin solicitud de aprobacion (404)")
            results.append({
                "name": name,
                "sid": sid,
                "exists": True,
                "approval_status": "sin solicitud",
                "whatsapp_status": "no enviado a Meta"
            })
        else:
            print(f"  [X] Error: {approval.get('error', 'Desconocido')}")
            results.append({
                "name": name,
                "sid": sid,
                "exists": True,
                "approval_status": "error",
                "whatsapp_status": "error"
            })
        
        print()
    
    # Resumen
    print("=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print()
    print(f"{'Plantilla':<45} {'Existe':<10} {'Estado WhatsApp':<20}")
    print("-" * 80)
    
    for r in results:
        existe = "SI" if r["exists"] else "NO"
        print(f"{r['name']:<45} {existe:<10} {r['whatsapp_status']:<20}")
    
    print()
    
    # Conclusion
    print("=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    
    approved = [r for r in results if r["whatsapp_status"] == "approved"]
    pending = [r for r in results if r["whatsapp_status"] == "pending"]
    rejected = [r for r in results if r["whatsapp_status"] == "rejected"]
    not_sent = [r for r in results if r["whatsapp_status"] in ["no enviado a Meta", "sin solicitud"]]
    
    if len(approved) == 4:
        print("[OK] Todas las plantillas estan APROBADAS por Meta.")
        print("     La vinculacion en segundo plano funciono correctamente.")
    elif len(not_sent) > 0:
        print("[!] PROBLEMA DETECTADO:")
        print(f"    - {len(not_sent)} plantilla(s) NO tienen solicitud de aprobacion enviada a Meta.")
        print("    - La vinculacion en segundo plano NO funciono.")
        print()
        print("SIGUIENTES PASOS:")
        print("1. Verificar que el numero de WhatsApp Business esta vinculado en Twilio")
        print("2. Esperar 24-48 horas para sincronizacion automatica")
        print("3. Si persiste, contactar soporte de Twilio")
    elif len(pending) > 0:
        print(f"[!] {len(pending)} plantilla(s) estan PENDIENTES de aprobacion por Meta.")
        print("    La vinculacion funciono, pero Meta aun no ha aprobado.")
    elif len(rejected) > 0:
        print(f"[X] {len(rejected)} plantilla(s) fueron RECHAZADAS por Meta.")
        print("    Revisar las razones de rechazo y corregir las plantillas.")
    else:
        print("[?] Estado mixto o indeterminado. Revisar detalles arriba.")

if __name__ == "__main__":
    main()
