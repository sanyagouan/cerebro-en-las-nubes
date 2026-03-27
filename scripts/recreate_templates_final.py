#!/usr/bin/env python3
"""
Script completo para recrear plantillas WhatsApp en Twilio Content API
y enviarlas a Meta para aprobacion.

Pasos:
1. Eliminar TODAS las plantillas existentes
2. Crear las 4 plantillas necesarias
3. Enviar cada plantilla a Meta para aprobacion
4. Actualizar content_sids.py con los nuevos SIDs
"""

import os
import sys
import requests
from requests.auth import HTTPBasicAuth
from pathlib import Path
from datetime import datetime

# Credenciales de Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

if not TWILIO_ACCOUNT_SID:
    print("ERROR: TWILIO_ACCOUNT_SID no esta configurado")
    print("Ejecuta: $env:TWILIO_ACCOUNT_SID='tu_account_sid'")
    sys.exit(1)

if not TWILIO_AUTH_TOKEN:
    print("ERROR: TWILIO_AUTH_TOKEN no esta configurado")
    print("Ejecuta: $env:TWILIO_AUTH_TOKEN='tu_token'")
    sys.exit(1)

# Configuracion
BASE_URL = "https://content.twilio.com/v1"
auth = HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Plantillas a crear
TEMPLATES = {
    "reserva_confirmacion_nubes": {
        "friendly_name": "reserva_confirmacion_nubes",
        "language": "es",
        "types": {
            "twilio/text": {
                "body": "Hola {{1}}, tu reserva en En Las Nubes Restobar esta confirmada!\n\nFecha: {{2}}\nHora: {{3}}\nPersonas: {{4}}\nMesa: {{5}} ({{6}})\n\nTe esperamos! Si necesitas cambios, responde a este mensaje."
            }
        },
        "variables": {
            "1": "customer_name",
            "2": "reservation_date", 
            "3": "reservation_time",
            "4": "num_guests",
            "5": "table_name",
            "6": "location"
        }
    },
    "reserva_recordatorio_nubes": {
        "friendly_name": "reserva_recordatorio_nubes",
        "language": "es",
        "types": {
            "twilio/text": {
                "body": "Hola {{1}}, te recordamos tu reserva manana en En Las Nubes Restobar.\n\nFecha: {{2}}\nHora: {{3}}\nPersonas: {{4}}\nMesa: {{5}} ({{6}})\n\nConfirmar: Responde SI\nCancelar: Responde NO\n\nTe esperamos!"
            }
        },
        "variables": {
            "1": "customer_name",
            "2": "reservation_date",
            "3": "reservation_time", 
            "4": "num_guests",
            "5": "table_name",
            "6": "location"
        }
    },
    "reserva_cancelada_nubes": {
        "friendly_name": "reserva_cancelada_nubes",
        "language": "es",
        "types": {
            "twilio/text": {
                "body": "Hola {{1}}, tu reserva en En Las Nubes Restobar ha sido cancelada.\n\nFecha: {{2}}\nHora: {{3}}\nPersonas: {{4}}\n\nSi deseas hacer una nueva reserva, contactanos al 941 123 456 o responde a este mensaje."
            }
        },
        "variables": {
            "1": "customer_name",
            "2": "reservation_date",
            "3": "reservation_time",
            "4": "num_guests"
        }
    },
    "mesa_disponible_nubes": {
        "friendly_name": "mesa_disponible_nubes",
        "language": "es",
        "types": {
            "twilio/text": {
                "body": "Hola {{1}}! Tenemos disponibilidad para ti en En Las Nubes Restobar.\n\nFecha: {{2}}\nHora: {{3}}\nMesa disponible: {{4}} ({{5}})\n\nPara reservar, responde con el numero de personas o llama al 941 123 456."
            }
        },
        "variables": {
            "1": "customer_name",
            "2": "reservation_date",
            "3": "reservation_time",
            "4": "table_name",
            "5": "location"
        }
    }
}


def get_all_templates():
    """Obtener todas las plantillas existentes."""
    print("\n" + "="*80)
    print("PASO 1: OBTENIENDO PLANTILLAS EXISTENTES")
    print("="*80)
    
    url = f"{BASE_URL}/Content"
    response = requests.get(url, auth=auth, timeout=30)
    
    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}")
        return []
    
    data = response.json()
    templates = data.get("contents", [])
    print(f"Encontradas {len(templates)} plantillas existentes")
    
    return templates


def delete_all_templates(templates):
    """Eliminar todas las plantillas."""
    print("\n" + "="*80)
    print("PASO 2: ELIMINANDO PLANTILLAS EXISTENTES")
    print("="*80)
    
    if not templates:
        print("No hay plantillas para eliminar")
        return True
    
    deleted = 0
    failed = 0
    
    for template in templates:
        sid = template.get("sid")
        name = template.get("friendly_name", "sin nombre")
        
        print(f"  Eliminando: {name} (SID: {sid})...")
        
        url = f"{BASE_URL}/Content/{sid}"
        response = requests.delete(url, auth=auth, timeout=30)
        
        if response.status_code == 204:
            print(f"    [OK] Eliminada correctamente")
            deleted += 1
        else:
            print(f"    [ERROR] {response.status_code} - {response.text}")
            failed += 1
    
    print(f"\nResumen: {deleted} eliminadas, {failed} fallos")
    return failed == 0


def create_template(name, template_data):
    """Crear una plantilla."""
    url = f"{BASE_URL}/Content"
    
    payload = {
        "friendly_name": template_data["friendly_name"],
        "language": template_data["language"],
        "types": template_data["types"],
        "variables": template_data["variables"]
    }
    
    response = requests.post(url, auth=auth, json=payload, timeout=30)
    
    if response.status_code == 201:
        data = response.json()
        return data.get("sid")
    else:
        print(f"    [ERROR] {response.status_code} - {response.text}")
        return None


def create_all_templates():
    """Crear todas las plantillas."""
    print("\n" + "="*80)
    print("PASO 3: CREANDO NUEVAS PLANTILLAS")
    print("="*80)
    
    created_sids = {}
    
    for name, template_data in TEMPLATES.items():
        print(f"\n  Creando: {name}...")
        
        sid = create_template(name, template_data)
        
        if sid:
            print(f"    [OK] Creada con SID: {sid}")
            created_sids[name] = sid
        else:
            print(f"    [ERROR] No se pudo crear")
    
    print(f"\nResumen: {len(created_sids)}/4 plantillas creadas")
    return created_sids


def submit_to_meta(sid, name):
    """Enviar plantilla a Meta para aprobacion."""
    url = f"{BASE_URL}/Content/{sid}/ApprovalRequests/whatsapp"
    
    # Categoria UTILITY para mensajes transaccionales
    payload = {
        "name": name,
        "category": "UTILITY"
    }
    
    response = requests.post(url, auth=auth, json=payload, timeout=30)
    
    return response


def submit_all_to_meta(created_sids):
    """Enviar todas las plantillas a Meta."""
    print("\n" + "="*80)
    print("PASO 4: ENVIANDO A META PARA APROBACION")
    print("="*80)
    
    results = {}
    
    for name, sid in created_sids.items():
        print(f"\n  Enviando: {name} (SID: {sid})...")
        
        response = submit_to_meta(sid, name)
        
        if response.status_code in [200, 201, 202]:
            data = response.json()
            status = data.get("status", "unknown")
            print(f"    [OK] Enviada a Meta")
            print(f"    Status: {status}")
            print(f"    Response: {data}")
            results[name] = {"sid": sid, "status": status, "success": True}
        else:
            print(f"    [ERROR] {response.status_code} - {response.text}")
            results[name] = {"sid": sid, "status": "error", "success": False}
    
    success_count = sum(1 for r in results.values() if r["success"])
    print(f"\nResumen: {success_count}/{len(created_sids)} enviadas correctamente")
    
    return results


def verify_approval_status(created_sids):
    """Verificar estado de aprobacion."""
    print("\n" + "="*80)
    print("PASO 5: VERIFICANDO ESTADO DE APROBACION")
    print("="*80)
    
    for name, sid in created_sids.items():
        print(f"\n  Verificando: {name}...")
        
        url = f"{BASE_URL}/Content/{sid}/ApprovalRequests"
        response = requests.get(url, auth=auth, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            whatsapp_data = data.get("approval_requests", {}).get("whatsapp", {})
            status = whatsapp_data.get("status", "desconocido")
            print(f"    [OK] Estado: {status}")
        elif response.status_code == 404:
            print(f"    [WARNING] Sin solicitud de aprobacion (404)")
        else:
            print(f"    [ERROR] {response.status_code}")


def update_content_sids(created_sids):
    """Actualizar archivo content_sids.py."""
    print("\n" + "="*80)
    print("PASO 6: ACTUALIZANDO content_sids.py")
    print("="*80)
    
    content_sids_path = Path("src/infrastructure/templates/content_sids.py")
    
    # Crear contenido del archivo
    content = f'''"""
Content SIDs para plantillas WhatsApp - En Las Nubes Restobar
Actualizado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Estos SIDs se generan automaticamente desde Twilio Content API.
Las plantillas fueron enviadas a Meta para aprobacion.
"""

# SIDs de plantillas WhatsApp
CONTENT_SIDS = {{
    "reserva_confirmacion": "{created_sids.get('reserva_confirmacion_nubes', 'NO_CREADO')}",
    "reserva_recordatorio": "{created_sids.get('reserva_recordatorio_nubes', 'NO_CREADO')}",
    "reserva_cancelada": "{created_sids.get('reserva_cancelada_nubes', 'NO_CREADO')}",
    "mesa_disponible": "{created_sids.get('mesa_disponible_nubes', 'NO_CREADO')}",
}}

# Alias para compatibilidad
RESERVA_CONFIRMACION_SID = CONTENT_SIDS["reserva_confirmacion"]
RESERVA_RECORDATORIO_SID = CONTENT_SIDS["reserva_recordatorio"]
RESERVA_CANCELADA_SID = CONTENT_SIDS["reserva_cancelada"]
MESA_DISPONIBLE_SID = CONTENT_SIDS["mesa_disponible"]


def get_template_sid(template_name: str) -> str:
    """
    Obtener el SID de una plantilla por su nombre.
    
    Args:
        template_name: Nombre de la plantilla (sin sufijo _nubes)
    
    Returns:
        SID de la plantilla o None si no existe
    """
    return CONTENT_SIDS.get(template_name)


def get_all_sids() -> dict:
    """Retornar todos los SIDs de plantillas."""
    return CONTENT_SIDS.copy()
'''
    
    # Crear directorio si no existe
    content_sids_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Escribir archivo
    content_sids_path.write_text(content, encoding="utf-8")
    
    print(f"  [OK] Archivo actualizado: {content_sids_path}")
    print(f"\n  Nuevos SIDs:")
    for name, sid in created_sids.items():
        print(f"    {name}: {sid}")


def main():
    """Funcion principal."""
    print("="*80)
    print("RECREACION DE PLANTILLAS WHATSAPP - EN LAS NUBES RESTOBAR")
    print("="*80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Account SID: {TWILIO_ACCOUNT_SID}")
    
    # Paso 1: Obtener plantillas existentes
    existing_templates = get_all_templates()
    
    # Paso 2: Eliminar plantillas existentes
    delete_all_templates(existing_templates)
    
    # Paso 3: Crear nuevas plantillas
    created_sids = create_all_templates()
    
    if not created_sids:
        print("\n[ERROR] No se crearon plantillas. Abortando.")
        return False
    
    # Paso 4: Enviar a Meta para aprobacion
    results = submit_all_to_meta(created_sids)
    
    # Paso 5: Verificar estado de aprobacion
    verify_approval_status(created_sids)
    
    # Paso 6: Actualizar content_sids.py
    update_content_sids(created_sids)
    
    # Resumen final
    print("\n" + "="*80)
    print("RESUMEN FINAL")
    print("="*80)
    print(f"\nPlantillas creadas: {len(created_sids)}/4")
    print(f"Enviadas a Meta: {sum(1 for r in results.values() if r['success'])}/4")
    print(f"Archivo actualizado: src/infrastructure/templates/content_sids.py")
    
    print("\nNuevos SIDs:")
    for name, sid in created_sids.items():
        print(f"  {name}: {sid}")
    
    print("\n" + "="*80)
    print("PROCESO COMPLETADO")
    print("="*80)
    print("\nNOTA: Las plantillas estan pendientes de aprobacion por Meta.")
    print("El proceso de aprobacion puede tardar entre 24-48 horas.")
    print("Puedes verificar el estado ejecutando:")
    print("  python scripts/check_template_approval_simple.py")
    
    return True


if __name__ == "__main__":
    main()
