import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
PHONE_NUMBER = "+358454910405"

# La URL de Webhook por defecto de VAPI para llamadas entrantes en números importados.
VAPI_INBOUND_WEBHOOK = "https://api.vapi.ai/twilio/inbound_call"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

try:
    print(f"Buscando número {PHONE_NUMBER} en Twilio...")
    incoming_phone_numbers = client.incoming_phone_numbers.list(phone_number=PHONE_NUMBER, limit=1)
    
    if not incoming_phone_numbers:
        print(f"No se encontró el número {PHONE_NUMBER} en la cuenta de Twilio proporcionada.")
    else:
        number = incoming_phone_numbers[0]
        print(f"Encontrado: {number.friendly_name} (SID: {number.sid})")
        print(f"URL de Voice actual: {number.voice_url}")
        
        print(f"Actualizando Voice URL a {VAPI_INBOUND_WEBHOOK}...")
        updated_number = client.incoming_phone_numbers(number.sid).update(
            voice_url=VAPI_INBOUND_WEBHOOK,
            voice_method="POST"
        )
        print(f"¡Actualizado con éxito! Nueva URL: {updated_number.voice_url}")

except Exception as e:
    print(f"Error al actualizar en Twilio: {e}")
