#!/usr/bin/env python3
"""
Script para crear plantillas de WhatsApp usando Twilio Content API (vía REST).
"""

import os
import requests
import base64
import json

def create_content_via_rest(account_sid, auth_token, body, name, language="es", variables=None):
    """Crear contenido usando la API REST de Twilio."""
    url = f"https://content.twilio.com/v1/Content"
    
    # Variables por defecto si no se proporcionan
    if variables is None:
        # Extraer variables del cuerpo del mensaje (ej: {{1}}, {{2}})
        import re
        var_matches = re.findall(r'\{\{(\d+)\}\}', body)
        variables = {var: f"Variable {var}" for var in var_matches}
    
    # Payload corregido con el formato correcto para Twilio Content API
    payload = {
        "friendly_name": name,
        "language": language,
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
    
    auth = (account_sid, auth_token)
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, auth=auth, headers=headers)
    
    if response.status_code in (200, 201):
        return response.json()
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

def submit_for_approval(account_sid, auth_token, content_sid, name, category="UTILITY"):
    """Enviar plantilla para aprobación de Meta."""
    url = f"https://content.twilio.com/v1/Content/{content_sid}/ApprovalRequests/whatsapp"
    
    payload = {
        "name": name,
        "category": category
    }
    
    auth = (account_sid, auth_token)
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, auth=auth, headers=headers)
    
    if response.status_code in (200, 201):
        return response.json()
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

def main():
    # Obtener credenciales de Twilio desde variables de entorno
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    
    if not account_sid or not auth_token:
        raise ValueError("TWILIO_ACCOUNT_SID y TWILIO_AUTH_TOKEN deben estar definidas")
    
    # Definir las plantillas de WhatsApp (formato Meta)
    templates = [
        {
            "name": "reserva_confirmacion_nubes",
            "body": "Hola {{1}}, tienes reserva en En Las Nubes para el {{2}} a las {{3}}h. CONFIRMAS? Responde SI o NO. Gracias!",
            "variables": {
                "1": "Nombre del cliente", 
                "2": "Fecha de la reserva", 
                "3": "Hora de la reserva"
            },
            "description": "Confirmación de reserva"
        },
        {
            "name": "reserva_recordatorio_nubes",
            "body": "Hola {{1}}! Te esperamos MANANA {{2}} a las {{3}}h para {{4}} personas. Todo listo? Responde SI para confirmar.",
            "variables": {
                "1": "Nombre del cliente", 
                "2": "Fecha de la reserva", 
                "3": "Hora de la reserva", 
                "4": "Número de personas"
            },
            "description": "Recordatorio de reserva"
        },
        {
            "name": "reserva_cancelada_nubes",
            "body": "{{1}}, tu reserva del {{2}} a las {{3}}h ha sido cancelada. Quieres hacer otra? Llamanos: 941 57 84 51",
            "variables": {
                "1": "Nombre del cliente", 
                "2": "Fecha de la reserva", 
                "3": "Hora de la reserva"
            },
            "description": "Notificación de cancelación"
        },
        {
            "name": "mesa_disponible_nubes",
            "body": "{{1}}! Se ha liberado mesa para {{2}} personas el {{3}} a las {{4}}h. Te viene bien? Responde SI o NO.",
            "variables": {
                "1": "Nombre del cliente", 
                "2": "Número de personas", 
                "3": "Fecha disponible", 
                "4": "Hora disponible"
            },
            "description": "Notificación de mesa disponible"
        }
    ]
    
    content_sids = {}
    
    print("Creando plantillas de WhatsApp en Twilio...")
    
    for template in templates:
        try:
            print(f"\nProcesando plantilla: {template['name']}")
            print(f"  Body: {template['body']}")
            
            # Crear contenido
            content_result = create_content_via_rest(
                account_sid, 
                auth_token, 
                template['body'],
                template['name'],
                "es",
                template['variables']
            )
            
            content_sid = content_result['sid']
            print(f"  Contenido creado con SID: {content_sid}")
            
            # Enviar para aprobación
            try:
                approval_result = submit_for_approval(
                    account_sid,
                    auth_token,
                    content_sid,
                    template['name'],
                    "UTILITY"
                )
                print(f"  Solicitud de aprobación enviada: {approval_result.get('status', 'unknown')}")
            except Exception as e:
                print(f"  Nota: No se pudo enviar aprobación: {e}")
            
            content_sids[template['name']] = content_sid
            
        except Exception as e:
            print(f"Error al procesar {template['name']}: {e}")
            continue
    
    # Escribir los SIDs en el archivo
    output_file = 'src/infrastructure/templates/content_sids.py'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Plantillas de WhatsApp - SIDs generados automáticamente\n")
        f.write("# NO EDITAR MANUALMENTE - Actualizado por create_whatsapp_templates.py\n\n")
        f.write("WHATSAPP_TEMPLATE_SIDS = {\n")
        for name, sid in content_sids.items():
            f.write(f'    "{name}": "{sid}",\n')
        f.write("}\n\n")
        
        for name, sid in content_sids.items():
            constant_name = name.upper().replace('-', '_')
            f.write(f"{constant_name}_SID = \"{sid}\"\n")
    
    print(f"\n[OK] SIDs guardados en: {output_file}")
    
    # Generar bloque para .env
    print("\n" + "="*50)
    print("BLOQUE PARA AÑADIR AL ARCHIVO .env:")
    print("="*50)
    for name, sid in content_sids.items():
        env_var = f"WHATSAPP_TEMPLATE_{name.upper().replace('-', '_')}_SID={sid}"
        print(env_var)
    print("="*50)
    
    print(f"\n[OK] Proceso completado! Se crearon {len(content_sids)} plantillas.")

if __name__ == "__main__":
    main()
