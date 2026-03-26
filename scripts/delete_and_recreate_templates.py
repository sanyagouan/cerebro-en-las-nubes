#!/usr/bin/env python3
"""
Script para eliminar plantillas rechazadas y recrearlas con los nombres exactos.
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Credenciales de Twilio
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# Plantillas a eliminar y recrear (con sus SIDs actuales)
TEMPLATES_TO_DELETE = [
    ("reserva_confirmacion_nubes", "HX9eabc58236ea6a1fa164bc269a5b02ec"),
    ("reserva_recordatorio_nubes", "HXdcd66832f0b0f876a3e5e35abdbadb21"),
    ("reserva_cancelada_nubes", "HX6967da785fc67facf23b52ba7f64f5cd"),
    ("mesa_disponible_nubes", "HX4c7f1da68c900f436c7099817522327a"),
]

# Contenido de las plantillas (mismo que en Meta)
TEMPLATE_CONTENT = {
    "reserva_confirmacion_nubes": {
        "body": "Hola {{1}}, tienes reserva en En Las Nubes para el {{2}} a las {{3}}h. CONFIRMAS respondiendo SÍ o NO a este mensaje.",
        "variables": {"1": "nombre", "2": "fecha", "3": "hora"}
    },
    "reserva_recordatorio_nubes": {
        "body": "Hola {{1}}! Te esperamos MAÑANA {{2}} a las {{3}}h para {{4}} personas. Todo listo para tu visita a En Las Nubes.",
        "variables": {"1": "nombre", "2": "fecha", "3": "hora", "4": "personas"}
    },
    "reserva_cancelada_nubes": {
        "body": "{{1}}, tu reserva del {{2}} a las {{3}}h ha sido cancelada. Quieres hacer otra? Llámanos al 941 123 456.",
        "variables": {"1": "nombre", "2": "fecha", "3": "hora"}
    },
    "mesa_disponible_nubes": {
        "body": "{{1}}! Se ha liberado mesa para {{2}} personas el {{3}} a las {{4}}h. Te viene bien? Responde SÍ para confirmar.",
        "variables": {"1": "nombre", "2": "personas", "3": "fecha", "4": "hora"}
    }
}


def delete_template(content_sid: str) -> bool:
    """Eliminar una plantilla de Twilio Content API."""
    url = f"https://content.twilio.com/v1/Content/{content_sid}"
    auth = (ACCOUNT_SID, AUTH_TOKEN)
    
    response = requests.delete(url, auth=auth)
    
    if response.status_code in (200, 204):
        print(f"   ✅ Eliminada: {content_sid}")
        return True
    else:
        print(f"   ❌ Error eliminando {content_sid}: {response.status_code} - {response.text}")
        return False


def create_template(name: str, body: str, variables: dict) -> dict:
    """Crear una nueva plantilla en Twilio Content API."""
    url = "https://content.twilio.com/v1/Content"
    
    payload = {
        "friendly_name": name,
        "language": "es",
        "variables": variables,
        "types": {
            "twilio/text": {
                "body": body
            },
            "whatsapp/text": {
                "body": body
            }
        }
    }
    
    auth = (ACCOUNT_SID, AUTH_TOKEN)
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, auth=auth, headers=headers)
    
    if response.status_code in (200, 201):
        result = response.json()
        print(f"   ✅ Creada: {name} -> SID: {result['sid']}")
        return {"name": name, "sid": result['sid']}
    else:
        print(f"   ❌ Error creando {name}: {response.status_code} - {response.text}")
        return None


def submit_for_approval(content_sid: str, name: str) -> bool:
    """Enviar plantilla para aprobación de Meta."""
    url = f"https://content.twilio.com/v1/Content/{content_sid}/ApprovalRequests/whatsapp"
    
    payload = {
        "name": name,
        "category": "UTILITY"
    }
    
    auth = (ACCOUNT_SID, AUTH_TOKEN)
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, auth=auth, headers=headers)
    
    if response.status_code in (200, 201):
        print(f"   ✅ Enviada para aprobación: {name}")
        return True
    else:
        print(f"   ❌ Error enviando {name}: {response.status_code} - {response.text}")
        return False


def main():
    print("=" * 70)
    print("ELIMINAR PLANTILLAS RECHAZADAS Y RECREAR")
    print("=" * 70)
    
    # Verificar credenciales
    if not ACCOUNT_SID or not AUTH_TOKEN:
        print("❌ Error: Credenciales de Twilio no configuradas")
        return
    
    print(f"\n📋 Account SID: {ACCOUNT_SID[:10]}...")
    
    # PASO 1: Eliminar plantillas existentes
    print("\n" + "-" * 70)
    print("PASO 1: ELIMINANDO PLANTILLAS RECHAZADAS")
    print("-" * 70)
    
    deleted_count = 0
    for name, sid in TEMPLATES_TO_DELETE:
        print(f"\n🗑️ Eliminando: {name} ({sid})")
        if delete_template(sid):
            deleted_count += 1
    
    print(f"\n✅ Total eliminadas: {deleted_count}/{len(TEMPLATES_TO_DELETE)}")
    
    # PASO 2: Crear nuevas plantillas
    print("\n" + "-" * 70)
    print("PASO 2: CREANDO NUEVAS PLANTILLAS")
    print("-" * 70)
    
    new_templates = []
    for name, content in TEMPLATE_CONTENT.items():
        print(f"\n📝 Creando: {name}")
        result = create_template(name, content["body"], content["variables"])
        if result:
            new_templates.append(result)
    
    print(f"\n✅ Total creadas: {len(new_templates)}/{len(TEMPLATE_CONTENT)}")
    
    # PASO 3: Enviar para aprobación
    print("\n" + "-" * 70)
    print("PASO 3: ENVIANDO PARA APROBACIÓN (VINCULACIÓN CON META)")
    print("-" * 70)
    
    approved_count = 0
    for template in new_templates:
        print(f"\n📤 Enviando: {template['name']}")
        if submit_for_approval(template['sid'], template['name']):
            approved_count += 1
    
    print(f"\n✅ Total enviadas: {approved_count}/{len(new_templates)}")
    
    # RESUMEN FINAL
    print("\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)
    print(f"\n📊 Plantillas eliminadas: {deleted_count}")
    print(f"📊 Plantillas creadas: {len(new_templates)}")
    print(f"📊 Plantillas enviadas para aprobación: {approved_count}")
    
    if new_templates:
        print("\n📋 NUEVOS SIDs:")
        for template in new_templates:
            print(f"   {template['name']}: {template['sid']}")
        
        # Generar código para actualizar content_sids.py
        print("\n📝 CÓDIGO PARA ACTUALIZAR content_sids.py:")
        print("-" * 70)
        print("CONTENT_TEMPLATE_SIDS = {")
        for template in new_templates:
            var_name = template['name'].upper()
            print(f'    "{var_name}": "{template["sid"]}",')
        print("}")


if __name__ == "__main__":
    main()
