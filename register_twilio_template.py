import os
import requests
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

# Endpoint for Twilio Content API
url = "https://content.twilio.com/v1/Content"

headers = {
    "Content-Type": "application/json"
}

payload = {
    "friendly_name": "reserva_confirmacion_nubes",
    "language": "es",
    "variables": {
        "1": "Nombre del cliente",
        "2": "Fecha de la reserva",
        "3": "Hora de la reserva"
    },
    "types": {
        "twilio/text": {
            "body": "¡Hola {{1}}! Tienes una solicitud de reserva en En Las Nubes para el {{2}} a las {{3}}h. Por favor, responde \"SÍ\" para confirmarla o \"NO\" para cancelarla. Ubicación: https://maps.app.goo.gl/QzCwv2ZfKjG6LpZc8 . Puedes usar este chat para enviarnos modificaciones o informar sobre alérgenos. ¡Te esperamos!"
        },
        "whatsapp/card": {
             "body": "¡Hola {{1}}! Tienes una solicitud de reserva en En Las Nubes para el {{2}} a las {{3}}h. Por favor, responde \"SÍ\" para confirmarla o \"NO\" para cancelarla. Ubicación: https://maps.app.goo.gl/QzCwv2ZfKjG6LpZc8 . Puedes usar este chat para enviarnos modificaciones o informar sobre alérgenos. ¡Te esperamos!",
             "actions": [
                 {
                     "type": "QUICK_REPLY",
                     "title": "SÍ",
                     "id": "confirm_yes"
                 },
                 {
                     "type": "QUICK_REPLY",
                     "title": "NO",
                     "id": "confirm_no"
                 }
             ]
        }
    }
}

try:
    response = requests.post(url, json=payload, auth=(account_sid, auth_token), headers=headers)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
    
    if response.status_code == 201:
        content_sid = response.json().get('sid')
        
        # Now submit it for WhatsApp approval
        approval_url = f"https://content.twilio.com/v1/Content/{content_sid}/ApprovalRequests/whatsapp"
        approval_payload = {
            "name": "reserva_confirmacion_nubes",
            "category": "UTILITY"
        }
        
        approval_res = requests.post(approval_url, json=approval_payload, auth=(account_sid, auth_token), headers=headers)
        print("Approval Status Code:", approval_res.status_code)
        print("Approval Response:", approval_res.json())
        
except Exception as e:
    print(f"Error: {e}")
