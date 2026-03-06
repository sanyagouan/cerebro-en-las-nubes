import asyncio
import os
from dotenv import load_dotenv
import sys

# Añadir el directorio raíz al path para poder importar src
sys.path.append(os.getcwd())

load_dotenv()

async def test_integrations():
    print("--- Test de Integración VAPI ---")
    from src.infrastructure.external.vapi_service import vapi_service
    calls = await vapi_service.get_calls(limit=5)
    print(f"Llamadas recuperadas: {len(calls.get('calls', []))}")
    
    analytics = await vapi_service.get_analytics()
    print(f"Analíticas VAPI: {analytics.get('total_calls')} llamadas totales")
    print(f"Propiedades de analíticas presentes: {list(analytics.keys())}")

    print("\n--- Test de Integración Twilio/WhatsApp ---")
    from src.infrastructure.external.twilio_service import twilio_service
    messages = await twilio_service.get_messages(limit=5)
    print(f"Mensajes recuperados: {len(messages.get('messages', []))}")
    
    wa_analytics = await twilio_service.get_analytics()
    print(f"Analíticas WhatsApp: {wa_analytics.get('total_messages')} mensajes totales")
    print(f"Propiedades de analíticas presentes: {list(wa_analytics.keys())}")

if __name__ == "__main__":
    asyncio.run(test_integrations())
