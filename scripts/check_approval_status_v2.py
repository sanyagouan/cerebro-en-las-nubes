#!/usr/bin/env python3
"""
Script para verificar el estado de aprobación de plantillas WhatsApp en Twilio.
Usa el endpoint correcto: GET /v1/Content (lista plantillas)
El estado de aprobación está en el campo 'approval_requests' de cada plantilla.
"""
import os
import sys
import requests
from requests.auth import HTTPBasicAuth

# Forzar UTF-8 en Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Credenciales
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

if not ACCOUNT_SID:
    print("ERROR: TWILIO_ACCOUNT_SID no esta configurado")
    sys.exit(1)

if not AUTH_TOKEN:
    print("ERROR: TWILIO_AUTH_TOKEN no esta configurado")
    sys.exit(1)

# Plantillas configuradas
CONFIGURED_TEMPLATES = {
    "reserva_confirmacion_nubes": "HXd7ce27ac9661f249829fc837325e1612",
    "reserva_recordatorio_nubes": "HXb3e508a6f995764a7a7672ae82d21449",
    "reserva_cancelada_nubes": "HXeb899f313378eff3a08c182a972c5a59",
    "mesa_disponible_nubes": "HX4af239d8593e7f5d7f676c669804cf32"
}

def main():
    print("=" * 60)
    print("ESTADO DE APROBACION WHATSAPP - V2")
    print("=" * 60)
    print()
    
    auth = HTTPBasicAuth(ACCOUNT_SID, AUTH_TOKEN)
    base_url = "https://content.twilio.com/v1/Content"
    
    # Obtener todas las plantillas
    print("1. OBTENIENDO TODAS LAS PLANTILLAS DE CONTENT API")
    print("-" * 60)
    
    response = requests.get(base_url, auth=auth)
    
    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}")
        return
    
    data = response.json()
    contents = data.get('contents', [])
    
    print(f"Total plantillas: {len(contents)}")
    print()
    
    # Buscar nuestras plantillas configuradas
    print("2. ESTADO DE PLANTILLAS CONFIGURADAS")
    print("-" * 60)
    
    for name, sid in CONFIGURED_TEMPLATES.items():
        # Buscar en la lista
        found = None
        for content in contents:
            if content.get('sid') == sid:
                found = content
                break
        
        if not found:
            print(f"\n>> {name}")
            print(f"   SID: {sid}")
            print(f"   ESTADO: NO ENCONTRADA")
            continue
        
        print(f"\n>> {name}")
        print(f"   SID: {sid}")
        print(f"   Tipo: {found.get('types', {}).get('twilio/text', 'N/A')}")
        
        # Revisar approval_requests
        approval_requests = found.get('approval_requests', {})
        
        if not approval_requests:
            print(f"   ESTADO: SIN approval_requests")
            continue
        
        whatsapp_approval = approval_requests.get('whatsapp', {})
        
        if not whatsapp_approval:
            print(f"   ESTADO: SIN aprobacion de WhatsApp")
            continue
        
        status = whatsapp_approval.get('status', 'desconocido')
        category = whatsapp_approval.get('category', 'N/A')
        
        # Mostrar estado con emoji
        if status == 'approved':
            emoji = "APROBADA"
        elif status == 'pending':
            emoji = "PENDIENTE"
        elif status == 'rejected':
            emoji = "RECHAZADA"
        else:
            emoji = f"OTRO ({status})"
        
        print(f"   ESTADO: {emoji}")
        print(f"   Categoria: {category}")
        
        # Si hay más info, mostrar
        if 'rejection_reason' in whatsapp_approval:
            print(f"   Razon rechazo: {whatsapp_approval['rejection_reason']}")
    
    print()
    print("=" * 60)
    print("RESUMEN")
    print("=" * 60)
    
    # Contar estados
    approved = 0
    pending = 0
    rejected = 0
    other = 0
    
    for name, sid in CONFIGURED_TEMPLATES.items():
        for content in contents:
            if content.get('sid') == sid:
                approval_requests = content.get('approval_requests', {})
                whatsapp_approval = approval_requests.get('whatsapp', {})
                status = whatsapp_approval.get('status', '')
                
                if status == 'approved':
                    approved += 1
                elif status == 'pending':
                    pending += 1
                elif status == 'rejected':
                    rejected += 1
                else:
                    other += 1
                break
    
    print(f"Aprobadas: {approved}")
    print(f"Pendientes: {pending}")
    print(f"Rechazadas: {rejected}")
    print(f"Otro/Sin estado: {other}")
    print()
    
    if approved == len(CONFIGURED_TEMPLATES):
        print("TODO LISTO PARA ENVIAR MENSAJES WHATSAPP")
    elif pending > 0:
        print("Algunas plantillas pendientes. Esperar aprobacion de Meta.")
    elif rejected > 0:
        print("Algunas plantillas rechazadas. Revisar contenido.")
    else:
        print("No se pudo determinar el estado. Revisar configuracion.")

    
if __name__ == "__main__":
    main()
