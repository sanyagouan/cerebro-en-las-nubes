#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear plantillas de WhatsApp en Twilio Content API.
IMPORTANTE: El contenido debe ser EXACTAMENTE igual al de Meta Business Manager
para que Twilio pueda vincular automáticamente las plantillas.

Las plantillas se crean con tipo twilio/text que incluye body y footer.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Configurar codificación para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Cargar variables de entorno
load_dotenv()

# Credenciales de Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# URL base de Twilio Content API
CONTENT_API_URL = "https://content.twilio.com/v1/Content"


def create_template(friendly_name: str, body: str, footer: str = None) -> dict:
    """
    Crea una plantilla de WhatsApp en Twilio Content API.
    
    Args:
        friendly_name: Nombre de la plantilla (debe coincidir con Meta)
        body: Texto del cuerpo del mensaje (con variables {{1}}, {{2}}, etc.)
        footer: Texto del pie de página (opcional)
    
    Returns:
        dict con la respuesta de la API o None si hay error
    """
    # Construir el contenido del mensaje
    # Para twilio/text, el contenido va en 'body'
    # El footer se incluye como parte del body para coincidir con Meta
    content_body = body
    if footer:
        content_body += f"\n\n{footer}"
    
    payload = {
        "friendly_name": friendly_name,
        "language": "es",
        "types": {
            "twilio/text": {
                "body": content_body
            }
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    try:
        print(f"\n[INFO] Creando plantilla: {friendly_name}")
        print(f"       Body: {body[:50]}...")
        if footer:
            print(f"       Footer: {footer}")
        
        response = requests.post(
            CONTENT_API_URL,
            json=payload,
            headers=headers,
            auth=auth
        )
        
        if response.status_code == 201:
            data = response.json()
            sid = data.get("sid")
            print(f"       [OK] Creada exitosamente!")
            print(f"       SID: {sid}")
            return data
        else:
            print(f"       [ERROR] Status: {response.status_code}")
            print(f"       {response.text}")
            return None
            
    except Exception as e:
        print(f"       [ERROR] Excepcion: {e}")
        return None


def main():
    """
    Crea las 4 plantillas de WhatsApp con contenido EXACTO de Meta.
    """
    print("=" * 60)
    print("CREANDO PLANTILLAS DE WHATSAPP EN TWILIO CONTENT API")
    print("=" * 60)
    
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print("\n[ERROR] Credenciales de Twilio no configuradas.")
        print("        Asegurate de que TWILIO_ACCOUNT_SID y TWILIO_AUTH_TOKEN estan en .env")
        return
    
    # Plantillas con contenido EXACTO de Meta Business Manager
    # IMPORTANTE: NO MODIFICAR NI UNA SOLA LETRA, ESPACIO O SIGNO DE PUNTUACION
    
    templates = [
        {
            "name": "mesa_disponibilidad_enlasnubes_es",
            "body": "Disponibilidad de mesa para {{1}}: tenemos mesa para {{2}} personas el {{3}} a las {{4}} en Restaurante En Las Nubes. Contacta con nosotros para confirmar.",
            "footer": "Contacta con nosotros para reservar"
        },
        {
            "name": "reserva_cancelacion_enlasnubes_es",
            "body": "Aviso para {{1}}: tu reserva del {{2}} a las {{3}} en Restaurante En Las Nubes ha sido cancelada. Para cualquier consulta contacta con nosotros.",
            "footer": "Lamentamos los inconvenientes causados"
        },
        {
            "name": "reserva_recordatorio_enlasnubes_es",
            "body": "Recordatorio de reserva para {{1}}: mesa para {{2}} personas el {{3}} a las {{4}} en Restaurante En Las Nubes. Responde SI para confirmar o NO para cancelar.",
            "footer": "Responde SI o NO para gestionar tu reserva"
        },
        {
            "name": "reserva_confirmacion_enlasnubes_es",
            "body": "Estimado/a {{1}}, confirmamos tu reserva en Restaurante En Las Nubes. Fecha: {{2}}, hora: {{3}}. Te esperamos.",
            "footer": "Gracias por confiar en nosotros"
        }
    ]
    
    # Crear cada plantilla
    results = []
    sids = {}
    
    for template in templates:
        result = create_template(
            friendly_name=template["name"],
            body=template["body"],
            footer=template["footer"]
        )
        
        if result:
            results.append({
                "name": template["name"],
                "sid": result.get("sid"),
                "status": "created"
            })
            sids[template["name"]] = result.get("sid")
        else:
            results.append({
                "name": template["name"],
                "sid": None,
                "status": "failed"
            })
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PLANTILLAS CREADAS")
    print("=" * 60)
    
    for result in results:
        status_icon = "[OK]" if result["status"] == "created" else "[FAIL]"
        print(f"\n{status_icon} {result['name']}")
        if result["sid"]:
            print(f"     SID: {result['sid']}")
    
    # Guardar SIDs en un archivo para referencia
    if sids:
        print("\n" + "=" * 60)
        print("SIDs PARA ACTUALIZAR EN content_sids.py:")
        print("=" * 60)
        for name, sid in sids.items():
            print(f'    "{name}": "{sid}",')
    
    return sids


if __name__ == "__main__":
    main()
