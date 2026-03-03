import os
from twilio.rest import Client
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
PHONE_NUMBER = "+358454910405"
BACKEND_URL = "https://go84sgscs4ckcs08wog84o0o.app.generaia.site"

print("====================================")
print("1. VALIDANDO ERRORES RECIENTES EN TWILIO")
print("====================================")
try:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    alerts = client.monitor.alerts.list(limit=5)
    if not alerts:
        print("No hay alertas de error recientes en Twilio.")
    for record in alerts:
        print(f"[{record.date_created}] Error {record.error_code}: {record.alert_text}")
except Exception as e:
    print(f"Error consultando Twilio: {e}")

print("\n====================================")
print("2. VALIDANDO CONFIGURACIÓN DE NÚMERO EN TWILIO")
print("====================================")
try:
    incoming_phone_numbers = client.incoming_phone_numbers.list(phone_number=PHONE_NUMBER, limit=1)
    if incoming_phone_numbers:
        number = incoming_phone_numbers[0]
        print(f"Número: {number.phone_number}")
        print(f"Voice URL: {number.voice_url}")
        print(f"Voice Method: {number.voice_method}")
        if number.voice_url != "https://api.vapi.ai/twilio/inbound_call":
            print("ADVERTENCIA: La Voice URL en Twilio no apunta a VAPI.")
        else:
            print("OK: La Voice URL en Twilio está correctamente configurada hacia VAPI.")
    else:
        print("ADVERTENCIA: No se encontró el número en Twilio.")
except Exception as e:
     print(f"Error consultando Twilio: {e}")

print("\n====================================")
print("3. VALIDANDO ESTADO DEL ASSISTANT EN VAPI")
print("====================================")
vapi_headers = {
    "Authorization": f"Bearer {VAPI_API_KEY}",
    "Content-Type": "application/json"
}
try:
    resp = requests.get(f"https://api.vapi.ai/assistant/{VAPI_ASSISTANT_ID}", headers=vapi_headers)
    ast = resp.json()
    if 'id' not in ast:
        print(f"La ID del asistente no existe o hubo un error: {ast}")
    else:
        print(f"Asistente ID: {ast.get('id')}")
        server_url = ast.get('serverUrl')
        server_obj_url = ast.get('server', {}).get('url')
        print(f"serverUrl: {server_url}")
        print(f"server.url: {server_obj_url}")
except Exception as e:
    print(f"Error consultando VAPI: {e}")

print("\n====================================")
print("4. VALIDANDO NÚMERO EN VAPI")
print("====================================")
try:
    resp = requests.get(f"https://api.vapi.ai/phone-number", headers=vapi_headers)
    numbers = resp.json()
    found = False
    for num in numbers:
        if num.get('number') == PHONE_NUMBER:
            found = True
            print(f"Número importado: {num.get('number')}")
            print(f"Asistente asignado: {num.get('assistantId')}")
            if num.get('assistantId') != VAPI_ASSISTANT_ID:
                print("ADVERTENCIA: El número en VAPI no está asignado a nuestro asistente principal.")
            else:
                print("OK: El número está asignado correctamente al asistente.")
    if not found:
        print("ADVERTENCIA: El número no está importado en VAPI.")
except Exception as e:
    print(f"Error consultando VAPI: {e}")
