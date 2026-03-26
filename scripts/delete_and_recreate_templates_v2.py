#!/usr/bin/env python3
"""
Script para eliminar plantillas rechazadas y recrearlas
"""
import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Twilio
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
CONTENT_API_URL = "https://content.twilio.com/v1/Content"

# SIDs de las plantillas rechazadas a eliminar
REJECTED_TEMPLATES = [
    ("reserva_confirmacion_nubes", "HX9eabc58236ea6a1fa164bc269a5b02ec"),
    ("reserva_recordatorio_nubes", "HXdcd66832f0b0f876a3e5e35abdbadb21"),
    ("reserva_cancelada_nubes", "HX6967da785fc67facf23b52ba7f64f5cd"),
    ("mesa_disponible_nubes", "HX4c7f1da68c900f436c7099817522327a"),
]

# Definición de las plantillas a recrear (formato correcto según Twilio Content API)
# Solo se requiere: friendly_name, language, types
TEMPLATES_TO_CREATE = [
    {
        "friendly_name": "reserva_confirmacion_nubes",
        "language": "es",
        "types": {
            "twilio/text": {
                "body": "Hola {{1}}, tienes reserva en En Las Nubes para el {{2}} a las {{3}}h. Confirma respondiendo SI o cancela con NO."
            }
        }
    },
    {
        "friendly_name": "reserva_recordatorio_nubes",
        "language": "es",
        "types": {
            "twilio/text": {
                "body": "Hola {{1}}! Te esperamos manana {{2}} a las {{3}}h para {{4}} personas. Todo listo? Confirma con SI."
            }
        }
    },
    {
        "friendly_name": "reserva_cancelada_nubes",
        "language": "es",
        "types": {
            "twilio/text": {
                "body": "{{1}}, tu reserva del {{2}} a las {{3}}h ha sido cancelada. Quieres hacer otra? Llamanos al 941 123 456."
            }
        }
    },
    {
        "friendly_name": "mesa_disponible_nubes",
        "language": "es",
        "types": {
            "twilio/text": {
                "body": "{{1}}! Se ha liberado mesa para {{2}} personas el {{3}} a las {{4}}h. Te viene bien? Reserva YA en 941 123 456."
            }
        }
    },
]


def delete_template(sid: str, name: str) -> bool:
    """Elimina una plantilla por su SID"""
    url = f"{CONTENT_API_URL}/{sid}"
    response = requests.delete(url, auth=(ACCOUNT_SID, AUTH_TOKEN))
    
    if response.status_code == 204:
        print(f"[OK] Eliminada: {name} (SID: {sid})")
        return True
    else:
        print(f"[ERROR] No se pudo eliminar {name}: {response.status_code} - {response.text}")
        return False


def create_template(template_data: dict) -> dict:
    """Crea una nueva plantilla con el formato correcto para Twilio Content API"""
    # Solo enviar friendly_name, language, types (sin name ni variables)
    payload = {
        "friendly_name": template_data["friendly_name"],
        "language": template_data["language"],
        "types": template_data["types"]
    }
    
    response = requests.post(
        CONTENT_API_URL,
        auth=(ACCOUNT_SID, AUTH_TOKEN),
        headers={"Content-Type": "application/json"},
        json=payload
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"[OK] Creada: {template_data['friendly_name']} (SID: {data['sid']})")
        return data
    else:
        print(f"[ERROR] No se pudo crear {template_data['friendly_name']}: {response.status_code} - {response.text}")
        return None


def submit_for_approval(sid: str, name: str) -> bool:
    """Envia plantilla para aprobacion"""
    url = f"{CONTENT_API_URL}/{sid}/ApprovalRequests/whatsapp"
    response = requests.post(url, auth=(ACCOUNT_SID, AUTH_TOKEN))
    
    if response.status_code == 202:
        print(f"[OK] Enviada para aprobacion: {name}")
        return True
    else:
        print(f"[INFO] Respuesta aprobacion {name}: {response.status_code} - {response.text}")
        return False


def main():
    print("=" * 70)
    print("ELIMINAR PLANTILLAS RECHAZADAS Y RECREAR")
    print("=" * 70)
    print()
    
    # Paso 1: Eliminar plantillas rechazadas
    print("[PASO 1] Eliminando plantillas rechazadas...")
    print("-" * 70)
    
    deleted_count = 0
    for name, sid in REJECTED_TEMPLATES:
        if delete_template(sid, name):
            deleted_count += 1
        print()
    
    print(f"Total eliminadas: {deleted_count}/4")
    print()
    
    # Paso 2: Crear nuevas plantillas
    print("[PASO 2] Creando nuevas plantillas...")
    print("-" * 70)
    
    new_sids = {}
    for template in TEMPLATES_TO_CREATE:
        result = create_template(template)
        if result:
            new_sids[template["friendly_name"]] = result["sid"]
        print()
    
    print(f"Total creadas: {len(new_sids)}/4")
    print()
    
    # Paso 3: Enviar para aprobacion
    print("[PASO 3] Enviando para aprobacion...")
    print("-" * 70)
    
    for name, sid in new_sids.items():
        submit_for_approval(sid, name)
    
    print()
    
    # Resumen final
    print("=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)
    print()
    print("Nuevos SIDs generados:")
    for name, sid in new_sids.items():
        print(f"  {name}: {sid}")
    print()
    
    if new_sids:
        print("Actualiza src/infrastructure/templates/content_sids.py con estos nuevos SIDs")
    
    return new_sids


if __name__ == "__main__":
    main()
