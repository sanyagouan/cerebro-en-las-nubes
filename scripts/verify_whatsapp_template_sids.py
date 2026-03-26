#!/usr/bin/env python3
"""
Script para verificar directamente los SIDs de las plantillas de WhatsApp en Twilio.
Este script compara los SIDs definidos en ambos archivos:
1. scripts/test_whatsapp_live.py (PLANTILLAS_WHATSAPP)
2. src/infrastructure/templates/content_sids.py (WHATSAPP_TEMPLATE_SIDS)
"""

import os
import requests
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_template_details(account_sid: str, auth_token: str, content_sid: str) -> dict:
    """
    Obtener detalles de una plantilla específica.
    
    Endpoint: GET https://content.twilio.com/v1/Content/{sid}
    """
    url = f"https://content.twilio.com/v1/Content/{content_sid}"
    
    auth = (account_sid, auth_token)
    headers = {"Accept": "application/json"}
    
    try:
        response = requests.get(url, auth=auth, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"Error {response.status_code}: {response.text}", "status_code": response.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_template_approval_status(account_sid: str, auth_token: str, content_sid: str) -> dict:
    """
    Obtener el estado de aprobación de una plantilla específica.
    
    Endpoint: GET https://content.twilio.com/v1/Content/{sid}/ApprovalRequests/whatsapp
    """
    url = f"https://content.twilio.com/v1/Content/{content_sid}/ApprovalRequests/whatsapp"
    
    auth = (account_sid, auth_token)
    headers = {"Accept": "application/json"}
    
    try:
        response = requests.get(url, auth=auth, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        elif response.status_code == 404:
            # No se ha enviado para aprobación todavía
            return {"success": True, "data": {"status": "not_submitted", "content_sid": content_sid}}
        else:
            return {"success": False, "error": f"Error {response.status_code}: {response.text}", "status_code": response.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    # Obtener credenciales de Twilio
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    if not account_sid or not auth_token:
        print("X ERROR: No se encontraron las credenciales de Twilio.")
        print("Asegurate de tener configuradas las variables de entorno:")
        print("  - TWILIO_ACCOUNT_SID")
        print("  - TWILIO_AUTH_TOKEN")
        sys.exit(1)
    
    print("[INFO] VERIFICACION DE SIDS DE PLANTILLAS WHATSAPP")
    print("="*70)
    
    # SIDs del archivo test_whatsapp_live.py (archivo 1)
    PLANTILLAS_WHATSAPP = {
        "recordatorio": "HXf4773e8889a00b6bd89bc6315753299a",
        "confirmacion": "HXe179c437fce3cbf0c325edd43389d930",
        "cancelacion": "HX2e728719e799d43062bed2cc1c5f32e3",
        "mesa_disponible": "HXe8f9d9f9b332f8471df617c76923df19",
    }
    
    # SIDs del archivo content_sids.py (archivo 2)
    WHATSAPP_TEMPLATE_SIDS = {
        "reserva_confirmacion_nubes": "HXd7ce27ac9661f249829fc837325e1612",
        "reserva_recordatorio_nubes": "HXb3e508a6f995764a7a7672ae82d21449",
        "reserva_cancelada_nubes": "HXeb899f313378eff3a08c182a972c5a59",
        "mesa_disponible_nubes": "HX4af239d8593e7f5d7f676c669804cf32",
    }
    
    print("Archivo 1: scripts/test_whatsapp_live.py")
    print("   PLANTILLAS_WHATSAPP = {")
    for key, value in PLANTILLAS_WHATSAPP.items():
        print(f"       '{key}': '{value}',")
    print("   }")
    print()
    
    print("Archivo 2: src/infrastructure/templates/content_sids.py")
    print("   WHATSAPP_TEMPLATE_SIDS = {")
    for key, value in WHATSAPP_TEMPLATE_SIDS.items():
        print(f"       '{key}': '{value}',")
    print("   }")
    print()
    
    print("RESULTADOS DE VERIFICACION:")
    print("-"*70)
    
    all_results = {}
    
    # Verificar SIDs del primer archivo
    print("Verificando SIDs del archivo 1 (test_whatsapp_live.py):")
    for name, sid in PLANTILLAS_WHATSAPP.items():
        print(f"\n   Document: {name}: {sid}")
        
        # Obtener detalles de la plantilla
        details = get_template_details(account_sid, auth_token, sid)
        if details["success"]:
            data = details["data"]
            friendly_name = data.get("friendly_name", "N/A")
            language = data.get("language", "N/A")
            print(f"      OK Nombre: {friendly_name}")
            print(f"      OK Idioma: {language}")
            
            # Verificar estado de aprobación
            approval = get_template_approval_status(account_sid, auth_token, sid)
            if approval["success"]:
                approval_data = approval["data"]
                approval_status = approval_data.get("status", "unknown")
                print(f"      OK Estado aprobacion: {approval_status}")
                
                # Guardar resultado
                all_results[sid] = {
                    "name": name,
                    "file": "test_whatsapp_live.py",
                    "friendly_name": friendly_name,
                    "language": language,
                    "approval_status": approval_status,
                    "exists": True
                }
            else:
                print(f"      X Error estado aprobacion: {approval['error']}")
                all_results[sid] = {
                    "name": name,
                    "file": "test_whatsapp_live.py",
                    "friendly_name": friendly_name,
                    "language": language,
                    "approval_status": "error",
                    "exists": True,
                    "approval_error": approval['error']
                }
        else:
            print(f"      X Error: {details['error']}")
            all_results[sid] = {
                "name": name,
                "file": "test_whatsapp_live.py",
                "approval_status": "not_found",
                "exists": False,
                "error": details['error']
            }
    
    # Verificar SIDs del segundo archivo
    print("\nVerificando SIDs del archivo 2 (content_sids.py):")
    for name, sid in WHATSAPP_TEMPLATE_SIDS.items():
        print(f"\n   Document: {name}: {sid}")
        
        # Obtener detalles de la plantilla
        details = get_template_details(account_sid, auth_token, sid)
        if details["success"]:
            data = details["data"]
            friendly_name = data.get("friendly_name", "N/A")
            language = data.get("language", "N/A")
            print(f"      OK Nombre: {friendly_name}")
            print(f"      OK Idioma: {language}")
            
            # Verificar estado de aprobación
            approval = get_template_approval_status(account_sid, auth_token, sid)
            if approval["success"]:
                approval_data = approval["data"]
                approval_status = approval_data.get("status", "unknown")
                print(f"      OK Estado aprobacion: {approval_status}")
                
                # Guardar resultado
                all_results[sid] = {
                    "name": name,
                    "file": "content_sids.py",
                    "friendly_name": friendly_name,
                    "language": language,
                    "approval_status": approval_status,
                    "exists": True
                }
            else:
                print(f"      X Error estado aprobacion: {approval['error']}")
                all_results[sid] = {
                    "name": name,
                    "file": "content_sids.py",
                    "friendly_name": friendly_name,
                    "language": language,
                    "approval_status": "error",
                    "exists": True,
                    "approval_error": approval['error']
                }
        else:
            print(f"      X Error: {details['error']}")
            all_results[sid] = {
                "name": name,
                "file": "content_sids.py",
                "approval_status": "not_found",
                "exists": False,
                "error": details['error']
            }
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE VERIFICACION")
    print("="*70)
    
    approved_sids = []
    not_approved_sids = []
    invalid_sids = []
    
    for sid, info in all_results.items():
        if info["exists"]:
            if info["approval_status"] == "approved":
                approved_sids.append((sid, info["name"], info["file"]))
            elif info["approval_status"] in ["pending", "submitted"]:
                not_approved_sids.append((sid, info["name"], info["file"]))
            else:
                not_approved_sids.append((sid, info["name"], info["file"]))
        else:
            invalid_sids.append((sid, info["name"], info["file"]))
    
    print(f"\nAPROBADAS POR META: {len(approved_sids)}")
    for sid, name, file in approved_sids:
        print(f"   - {name} ({sid}) - {file}")
    
    print(f"\nNO APROBADAS (pendientes/rechazadas/no enviadas): {len(not_approved_sids)}")
    for sid, name, file in not_approved_sids:
        info = all_results[sid]
        status = info.get("approval_status", "unknown")
        print(f"   - {name} ({sid}) - {file} [{status}]")
    
    if invalid_sids:
        print(f"\nNO VALIDAS (no existen en Twilio): {len(invalid_sids)}")
        for sid, name, file in invalid_sids:
            info = all_results[sid]
            error = info.get("error", "unknown error")
            print(f"   - {name} ({sid}) - {file} [ERROR: {error}]")
    
    print("\n" + "="*70)
    print("CONCLUSIONES:")
    print("="*70)
    
    # Determinar cuál archivo tiene los SIDs válidos
    valid_sids_from_file1 = [(sid, name) for sid, name, file in approved_sids + not_approved_sids if file == "test_whatsapp_live.py"]
    valid_sids_from_file2 = [(sid, name) for sid, name, file in approved_sids + not_approved_sids if file == "content_sids.py"]
    
    if len(valid_sids_from_file2) > len(valid_sids_from_file1):
        print("CONCLUSION: El archivo src/infrastructure/templates/content_sids.py")
        print("   parece contener los SIDs correctos y actualizados.")
    elif len(valid_sids_from_file1) > len(valid_sids_from_file2):
        print("CONCLUSION: El archivo scripts/test_whatsapp_live.py")
        print("   parece contener los SIDs correctos y actualizados.")
    else:
        print("CONCLUSION: Ambos archivos tienen la misma cantidad de SIDs válidos.")
        print("   Se requiere analisis adicional para determinar cual es el correcto.")
    
    if approved_sids:
        print(f"\nHay {len(approved_sids)} plantillas APROBADAS por Meta:")
        for sid, name, file in approved_sids:
            print(f"   - {name}: {sid} (desde {file})")
        print("\n   Estos son los SIDs que deben usarse en produccion.")
    else:
        print("\nNO hay plantillas aprobadas por Meta aun.")
        print("   Debes asegurarte de que las plantillas hayan sido enviadas")
        print("   para aprobacion en Meta Business Suite.")
    
    return all_results

if __name__ == "__main__":
    main()