#!/usr/bin/env python3
"""
Diagnóstico detallado del estado de aprobación de plantillas en Twilio.
Este script consulta directamente la API de Twilio Content y muestra
toda la información disponible sobre cada plantilla.
"""

import os
import sys
import requests
from requests.auth import HTTPBasicAuth
import json

# Cargar variables de entorno desde .env.mcp
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env.mcp')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Quitar comillas si las hay
                    value = value.strip('"').strip("'")
                    os.environ[key] = value

load_env()

# Configuración
ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')

if not ACCOUNT_SID or not AUTH_TOKEN:
    print("❌ Error: TWILIO_ACCOUNT_SID y TWILIO_AUTH_TOKEN deben estar configurados")
    sys.exit(1)

# Plantillas a verificar
TEMPLATES_TO_CHECK = {
    "mesa_disponibilidad_enlasnubes_es": "HX2bbf4bf865ac57eafe90051a41c42c3e",
    "reserva_cancelacion_enlasnubes_es": "HXa09aef98872394b339fdb50bf8ec72e",
    "reserva_recordatorio_enlasnubes_es": "HX2cc2087501d3f98701961631697c0b37",
    "reserva_confirmacion_enlasnubes_es": "HXa529c4953d53a2cbb9ff5b5699ee3c3f"
}

def get_all_templates():
    """Obtiene todas las plantillas de Twilio Content API"""
    url = f'https://content.twilio.com/v1/Content'
    response = requests.get(url, auth=HTTPBasicAuth(ACCOUNT_SID, AUTH_TOKEN))
    response.raise_for_status()
    return response.json().get('contents', [])

def get_template_approval_requests(sid):
    """Obtiene el estado de aprobación de una plantilla específica"""
    url = f'https://content.twilio.com/v1/Content/{sid}/ApprovalRequests'
    try:
        response = requests.get(url, auth=HTTPBasicAuth(ACCOUNT_SID, AUTH_TOKEN))
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}", "body": response.text}
    except Exception as e:
        return {"error": str(e)}

def main():
    print("=" * 80)
    print("DIAGNÓSTICO DETALLADO DE ESTADO DE APROBACIÓN DE PLANTILLAS")
    print("=" * 80)
    print()
    
    # 1. Obtener todas las plantillas
    print("📋 Obteniendo todas las plantillas de Twilio Content API...")
    all_templates = get_all_templates()
    print(f"   Total de plantillas encontradas: {len(all_templates)}")
    print()
    
    # 2. Crear un mapa de SIDs
    templates_by_sid = {t['sid']: t for t in all_templates}
    
    # 3. Verificar cada plantilla objetivo
    print("=" * 80)
    print("VERIFICACIÓN DE PLANTILLAS OBJETIVO")
    print("=" * 80)
    
    results = {
        "approved": [],
        "pending": [],
        "rejected": [],
        "not_submitted": [],
        "not_found": []
    }
    
    for name, sid in TEMPLATES_TO_CHECK.items():
        print(f"\n📄 {name}")
        print(f"   SID: {sid}")
        print("-" * 60)
        
        # Verificar si existe en Content API
        if sid not in templates_by_sid:
            print(f"   ❌ NO ENCONTRADA en Content API")
            results["not_found"].append({"name": name, "sid": sid})
            continue
        
        template = templates_by_sid[sid]
        print(f"   ✅ Encontrada en Content API")
        print(f"   Friendly Name: {template.get('friendly_name', 'N/A')}")
        print(f"   Language: {template.get('language', 'N/A')}")
        print(f"   Types: {list(template.get('types', {}).keys())}")
        print(f"   Date Created: {template.get('date_created', 'N/A')}")
        
        # Verificar approval_requests en la respuesta principal
        approval_requests = template.get('approval_requests', {})
        print(f"\n   🔍 Campo 'approval_requests' en respuesta principal:")
        if approval_requests:
            print(f"   {json.dumps(approval_requests, indent=6)}")
        else:
            print(f"   ⚠️  NO PRESENTE")
        
        # Consultar endpoint específico de aprobación
        print(f"\n   🔍 Consultando endpoint /ApprovalRequests...")
        approval_details = get_template_approval_requests(sid)
        
        if 'error' in approval_details:
            print(f"   ❌ Error: {approval_details['error']}")
            if 'body' in approval_details:
                print(f"   Response: {approval_details['body'][:200]}")
        else:
            print(f"   ✅ Respuesta recibida:")
            print(f"   {json.dumps(approval_details, indent=6)}")
            
            # Extraer estado de WhatsApp
            whatsapp_approval = approval_details.get('whatsapp', {})
            status = whatsapp_approval.get('status', 'unknown')
            
            if status == 'approved':
                results["approved"].append({"name": name, "sid": sid, "details": whatsapp_approval})
                print(f"\n   ✅ ESTADO WHATSAPP: APPROVED")
            elif status == 'pending':
                results["pending"].append({"name": name, "sid": sid, "details": whatsapp_approval})
                print(f"\n   ⏳ ESTADO WHATSAPP: PENDING")
            elif status == 'rejected':
                results["rejected"].append({"name": name, "sid": sid, "details": whatsapp_approval})
                print(f"\n   ❌ ESTADO WHATSAPP: REJECTED")
            else:
                results["not_submitted"].append({"name": name, "sid": sid, "details": whatsapp_approval})
                print(f"\n   ⚠️  ESTADO WHATSAPP: {status.upper() if status else 'NO ENVIADO'}")
    
    # 4. Resumen final
    print("\n")
    print("=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)
    print(f"✅ Approved: {len(results['approved'])}")
    for t in results['approved']:
        print(f"   - {t['name']}")
    
    print(f"\n⏳ Pending: {len(results['pending'])}")
    for t in results['pending']:
        print(f"   - {t['name']}")
    
    print(f"\n❌ Rejected: {len(results['rejected'])}")
    for t in results['rejected']:
        print(f"   - {t['name']}")
    
    print(f"\n⚠️  Not Submitted: {len(results['not_submitted'])}")
    for t in results['not_submitted']:
        print(f"   - {t['name']}")
    
    print(f"\n🔍 Not Found: {len(results['not_found'])}")
    for t in results['not_found']:
        print(f"   - {t['name']} (SID: {t['sid']})")
    
    # 5. Conclusión
    print("\n")
    print("=" * 80)
    print("CONCLUSIÓN")
    print("=" * 80)
    
    total_problems = len(results['not_submitted']) + len(results['not_found']) + len(results['rejected'])
    
    if total_problems == 0 and len(results['approved']) == 4:
        print("✅ TODAS las plantillas están APPROVED")
        print("   La vinculación con Meta fue exitosa.")
    elif total_problems > 0:
        print("❌ PROBLEMA DETECTADO:")
        if results['not_found']:
            print(f"   - {len(results['not_found'])} plantilla(s) NO EXISTEN en Content API")
            print("     Posibles causas:")
            print("     * Los SIDs proporcionados son incorrectos")
            print("     * Las plantillas fueron eliminadas")
            print("     * Error en el proceso de creación")
        
        if results['not_submitted']:
            print(f"   - {len(results['not_submitted'])} plantilla(s) SIN approval_requests")
            print("     Posibles causas:")
            print("     * Las plantillas no se enviaron a Meta para aprobación")
            print("     * Twilio no inició el proceso de vinculación automática")
            print("     * Las plantillas necesitan envío manual a Meta")
        
        print("\n   PRÓXIMOS PASOS RECOMENDADOS:")
        print("   1. Verificar que los SIDs sean correctos")
        print("   2. Si los SIDs son correctos, enviar plantillas a Meta manualmente")
        print("   3. Consultar documentación: https://www.twilio.com/docs/content/content-api-approval-requests")
    else:
        print("⏳ Las plantillas están en proceso de aprobación")
        print("   Espera 24-48 horas para que Meta complete la revisión.")

if __name__ == "__main__":
    main()
