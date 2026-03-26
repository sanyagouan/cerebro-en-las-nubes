#!/usr/bin/env python3
"""
Script para debuggear el estado de aprobacion de WhatsApp Business API
"""
import os
import sys
import requests
from dotenv import load_dotenv
import json

# Forzar encoding UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Cargar variables de entorno
load_dotenv()

def main():
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    if not account_sid or not auth_token:
        print("ERROR: TWILIO_ACCOUNT_SID o TWILIO_AUTH_TOKEN no estan configurados")
        sys.exit(1)
    
    print("=" * 60)
    print("DEBUG: ESTADO DE WHATSAPP BUSINESS API")
    print("=" * 60)
    print(f"\nAccount SID: {account_sid[:10]}...{account_sid[-4:]}")
    
    # Content SIDs de las plantillas configuradas
    content_sids = [
        ('reserva_confirmacion_nubes', 'HXd7ce27ac9661f249829fc837325e1612'),
        ('reserva_recordatorio_nubes', 'HXb3e508a6f995764a7a7672ae82d21449'),
        ('reserva_cancelada_nubes', 'HXeb899f313378eff3a08c182a972c5a59'),
        ('mesa_disponible_nubes', 'HX4af239d8593e7f5d7f676c669804cf32'),
    ]
    
    print("\n" + "=" * 60)
    print("1. VERIFICANDO ESTADO DE APROBACION (GET)")
    print("=" * 60)
    
    for name, sid in content_sids:
        print(f"\n>> {name}")
        print(f"   SID: {sid}")
        
        url = f'https://content.twilio.com/v1/Content/{sid}/ApprovalRequests/whatsapp'
        
        try:
            response = requests.get(url, auth=(account_sid, auth_token))
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response JSON:")
                print(f"   {json.dumps(data, indent=6)}")
            else:
                print(f"   ERROR: {response.text}")
                
        except Exception as e:
            print(f"   EXCEPCION: {e}")
    
    print("\n" + "=" * 60)
    print("2. RE-ENVIANDO A APROBACION (POST)")
    print("=" * 60)
    
    for name, sid in content_sids:
        print(f"\n>> {name}")
        url = f'https://content.twilio.com/v1/Content/{sid}/ApprovalRequests/whatsapp'
        
        try:
            response = requests.post(
                url, 
                auth=(account_sid, auth_token),
                data={'category': 'UTILITY'}
            )
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code in [200, 201, 202]:
                data = response.json()
                print(f"   Response JSON:")
                print(f"   {json.dumps(data, indent=6)}")
            else:
                print(f"   Response: {response.text[:500]}")
                
        except Exception as e:
            print(f"   EXCEPCION: {e}")
    
    print("\n" + "=" * 60)
    print("3. LISTANDO TODAS LAS PLANTILLAS")
    print("=" * 60)
    
    url = 'https://content.twilio.com/v1/Content?PageSize=50'
    
    try:
        response = requests.get(url, auth=(account_sid, auth_token))
        
        if response.status_code == 200:
            data = response.json()
            contents = data.get('contents', [])
            print(f"\nTotal plantillas en Content API: {len(contents)}")
            
            # Agrupar por nombre
            unique_names = {}
            for c in contents:
                name = c.get('friendly_name', 'Sin nombre')
                if name not in unique_names:
                    unique_names[name] = []
                unique_names[name].append(c.get('sid'))
            
            print(f"\nPlantillas unicas por nombre: {len(unique_names)}")
            for name, sids in sorted(unique_names.items()):
                print(f"   - {name}: {len(sids)} versiones")
        else:
            print(f"ERROR: {response.text}")
            
    except Exception as e:
        print(f"EXCEPCION: {e}")
    
    print("\n" + "=" * 60)
    print("DEBUG COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    main()
