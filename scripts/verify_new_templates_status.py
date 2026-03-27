#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar el estado de aprobación de las 4 nuevas plantillas
de WhatsApp en Twilio Content API.

Plantillas a verificar:
- mesa_disponibilidad_enlasnubes_es: HX2bbf4bf865ac57eafe90051a41c42c3e
- reserva_cancelacion_enlasnubes_es: HXa09aef98872394b339fdb50bf8ec72e
- reserva_recordatorio_enlasnubes_es: HX2cc2087501d3f98701961631697c0b37
- reserva_confirmacion_enlasnubes_es: HXa529c4953d53a2cbb9ff5b5699ee3c3f
"""

import os
import sys
import io
import json
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth

# Forzar UTF-8 en Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Plantillas a verificar (SIDs proporcionados por el usuario)
TEMPLATES_TO_CHECK = {
    "mesa_disponibilidad_enlasnubes_es": "HX2bbf4bf865ac57eafe90051a41c42c3e",
    "reserva_cancelacion_enlasnubes_es": "HXa09aef98872394b339fdb50bf8ec72e",
    "reserva_recordatorio_enlasnubes_es": "HX2cc2087501d3f98701961631697c0b37",
    "reserva_confirmacion_enlasnubes_es": "HXa529c4953d53a2cbb9ff5b5699ee3c3f"
}

def main():
    print("=" * 70)
    print("VERIFICACIÓN DE ESTADO DE PLANTILLAS WHATSAPP - TWILIO")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Obtener credenciales
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    if not account_sid:
        print("\n❌ ERROR: TWILIO_ACCOUNT_SID no está configurado")
        print("   Ejecuta: . .\\scripts\\load_mcp_secrets.ps1")
        sys.exit(1)
    
    if not auth_token:
        print("\n❌ ERROR: TWILIO_AUTH_TOKEN no está configurado")
        print("   Ejecuta: . .\\scripts\\load_mcp_secrets.ps1")
        sys.exit(1)
    
    print(f"\n📋 Account SID: {account_sid[:8]}...{account_sid[-4:]}")
    print(f"📋 Plantillas a verificar: {len(TEMPLATES_TO_CHECK)}")
    
    auth = HTTPBasicAuth(account_sid, auth_token)
    base_url = "https://content.twilio.com/v1/Content"
    
    # Paso 1: Obtener todas las plantillas
    print("\n" + "-" * 70)
    print("1. OBTENIENDO TODAS LAS PLANTILLAS DE CONTENT API")
    print("-" * 70)
    
    try:
        response = requests.get(base_url, auth=auth, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Error {response.status_code}: {response.text}")
            sys.exit(1)
        
        data = response.json()
        all_templates = data.get('contents', [])
        print(f"   ✅ Total de plantillas en Twilio: {len(all_templates)}")
        
    except Exception as e:
        print(f"❌ Error al obtener plantillas: {e}")
        sys.exit(1)
    
    # Paso 2: Verificar cada plantilla
    print("\n" + "-" * 70)
    print("2. ESTADO DE APROBACIÓN DE LAS 4 PLANTILLAS NUEVAS")
    print("-" * 70)
    
    results = {
        "approved": [],
        "pending": [],
        "rejected": [],
        "not_submitted": [],
        "not_found": [],
        "error": []
    }
    
    for name, sid in TEMPLATES_TO_CHECK.items():
        print(f"\n📄 {name}")
        print(f"   SID: {sid}")
        
        # Buscar en la lista de plantillas
        found = None
        for template in all_templates:
            if template.get('sid') == sid:
                found = template
                break
        
        if not found:
            print(f"   ⚠️  ESTADO: NO ENCONTRADA en Content API")
            results["not_found"].append(name)
            continue
        
        # Mostrar info básica
        friendly_name = found.get('friendly_name', 'N/A')
        language = found.get('language', 'N/A')
        print(f"   Friendly Name: {friendly_name}")
        print(f"   Language: {language}")
        
        # Obtener estado de aprobación
        approval_requests = found.get('approval_requests', {})
        
        if not approval_requests:
            print(f"   ⚠️  ESTADO: SIN approval_requests")
            results["not_submitted"].append(name)
            continue
        
        whatsapp_approval = approval_requests.get('whatsapp', {})
        
        if not whatsapp_approval:
            print(f"   ⚠️  ESTADO: SIN aprobación de WhatsApp")
            results["not_submitted"].append(name)
            continue
        
        status = whatsapp_approval.get('status', 'desconocido').lower()
        category = whatsapp_approval.get('category', 'N/A')
        
        # Mostrar estado con emoji
        status_display = {
            "approved": "✅ APROBADA",
            "pending": "⏳ PENDIENTE",
            "rejected": "❌ RECHAZADA",
            "not_submitted": "⚠️ NO ENVIADA"
        }
        
        display_status = status_display.get(status, f"❓ OTRO ({status})")
        print(f"   ESTADO: {display_status}")
        print(f"   Categoría: {category}")
        
        # Si hay razón de rechazo
        if 'rejection_reason' in whatsapp_approval:
            print(f"   Razón rechazo: {whatsapp_approval['rejection_reason']}")
        
        # Clasificar
        if status == "approved":
            results["approved"].append(name)
        elif status == "pending":
            results["pending"].append(name)
        elif status == "rejected":
            results["rejected"].append(name)
        elif status == "not_submitted":
            results["not_submitted"].append(name)
        else:
            results["error"].append(name)
    
    # Paso 3: Resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE ESTADO")
    print("=" * 70)
    
    print(f"\n   ✅ Aprobadas: {len(results['approved'])}")
    for name in results["approved"]:
        print(f"      - {name}")
    
    print(f"\n   ⏳ Pendientes: {len(results['pending'])}")
    for name in results["pending"]:
        print(f"      - {name}")
    
    print(f"\n   ❌ Rechazadas: {len(results['rejected'])}")
    for name in results["rejected"]:
        print(f"      - {name}")
    
    print(f"\n   ⚠️ No enviadas: {len(results['not_submitted'])}")
    for name in results["not_submitted"]:
        print(f"      - {name}")
    
    print(f"\n   🔍 No encontradas: {len(results['not_found'])}")
    for name in results["not_found"]:
        print(f"      - {name}")
    
    if results["error"]:
        print(f"\n   ❓ Error/Desconocido: {len(results['error'])}")
        for name in results["error"]:
            print(f"      - {name}")
    
    # Conclusión
    print("\n" + "=" * 70)
    print("CONCLUSIÓN")
    print("=" * 70)
    
    total = len(TEMPLATES_TO_CHECK)
    approved = len(results["approved"])
    pending = len(results["pending"])
    not_found = len(results["not_found"])
    
    if approved == total:
        print("\n🎉 ¡TODAS LAS PLANTILLAS ESTÁN APROBADAS!")
        print("   ✅ La vinculación con Meta fue exitosa.")
        print("   ✅ Puedes proceder con el envío de mensajes WhatsApp.")
    elif approved > 0 and (approved + pending) == total:
        print(f"\n⏳ ESTADO PARCIAL: {approved} aprobadas, {pending} pendientes")
        print("   Las plantillas pendientes necesitan más tiempo para aprobación.")
        print("   Meta suele tardar 24-48 horas en aprobar plantillas.")
    elif not_found > 0:
        print(f"\n⚠️ PROBLEMA DETECTADO: {not_found} plantillas NO encontradas")
        print("   Las plantillas no existen en Twilio Content API.")
        print("   Posibles causas:")
        print("   1. Los SIDs proporcionados son incorrectos")
        print("   2. Las plantillas fueron eliminadas")
        print("   3. Las plantillas están en otra cuenta de Twilio")
    elif pending > 0:
        print(f"\n⏳ TODAS LAS PLANTILLAS ESTÁN PENDIENTES ({pending})")
        print("   La vinculación con Meta está en proceso.")
        print("   Espera 24-48 horas para que Meta apruebe las plantillas.")
    elif len(results["rejected"]) > 0:
        print(f"\n❌ ALGUNAS PLANTILLAS FUERON RECHAZADAS")
        print("   Revisa las razones de rechazo arriba.")
        print("   Necesitas corregir el contenido y reenviar.")
    else:
        print("\n❓ ESTADO INCIERTO")
        print("   No se pudo determinar el estado de aprobación.")
        print("   Revisa la configuración y los SIDs de las plantillas.")
    
    print("\n" + "=" * 70)
    
    # Retornar resultados para uso programático
    return results


if __name__ == "__main__":
    main()
