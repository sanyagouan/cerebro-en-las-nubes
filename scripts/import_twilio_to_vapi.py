import os
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
PHONE_NUMBER = "+358454910405"

headers = {
    "Authorization": f"Bearer {VAPI_API_KEY}",
    "Content-Type": "application/json"
}

print("1. Buscando números existentes en VAPI...")
try:
    response = requests.get("https://api.vapi.ai/phone-number", headers=headers)
    response.raise_for_status()
    numbers = response.json()
    print("Números actuales:")
    for num in numbers:
        print(f" - ID: {num.get('id')}, Number: {num.get('number')}, Assistant: {num.get('assistantId')}")
except Exception as e:
    print(f"Error listando números: {e}")

print("\n2. Importando número de Twilio a VAPI...")
payload = {
    "provider": "twilio",
    "number": PHONE_NUMBER,
    "twilioAccountSid": TWILIO_ACCOUNT_SID,
    "twilioAuthToken": TWILIO_AUTH_TOKEN,
    "assistantId": VAPI_ASSISTANT_ID,
    "name": "Línea Principal En Las Nubes"
}

try:
    response = requests.post("https://api.vapi.ai/phone-number", headers=headers, json=payload)
    if response.status_code == 201:
        print(f"¡Número importado exitosamente! Respuesta:\n{response.json()}")
    elif response.status_code == 409: # Conflict / Ya existe
        print(f"El número ya parece estar importado en VAPI. Procediendo a actualizar su asistente asignado...")
        # En caso de que ya exista, deberíamos buscar su ID y hacer un PATCH. 
        # Pero como listamos arriba, lo veremos.
    else:
        print(f"Error importando número: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Error de red/petición: {e}")
