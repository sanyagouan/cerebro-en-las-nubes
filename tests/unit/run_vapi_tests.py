import asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.api.vapi_tools_router import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)

def run_tests():
    print("Iniciando pruebas unitarias de Vapi Tools...")
    
    # TEST 1: Éxito
    print("--- TEST 1: Flujo de reserva exitoso ---")
    payload_success = {
        "message": {
            "toolCalls": [
                {
                    "id": "call_123",
                    "function": {
                        "name": "create_reservation",
                        "arguments": '{"customer_name": "Juan Perez", "phone": "600123456", "date": "2026-05-10", "time": "21:00", "pax": 4}'
                    }
                }
            ]
        }
    }
    
    with patch('src.api.vapi_tools_router.get_airtable_service_lazy') as mock_airtable, \
         patch('src.infrastructure.external.twilio_service.TwilioService.send_whatsapp_template') as mock_twilio:
        
        mock_instance = MagicMock()
        mock_airtable.return_value = mock_instance
        
        future = asyncio.Future()
        future.set_result({"id": "rec123"})
        mock_instance.create_record.return_value = future
        mock_twilio.return_value = "MSxxxxx"

        response = client.post("/vapi/tools/create_reservation", json=payload_success)
        assert response.status_code == 200, f"Error: {response.status_code}"
        data = response.json()
        print("DATOS RECIBIDOS DEL BACKEND:", data)
        assert data["results"][0]["toolCallId"] == "call_123", "Fallo en ID de tool call"
        print("OK - TEST 1 PASADO: Reserva atómica creada con éxito.")

    # TEST 2: Fallo en BD -> Rescate Semántico
    print("--- TEST 2: Recuperación ante caída de Base de Datos ---")
    payload_error = {
        "message": {
            "toolCalls": [
                {
                    "id": "call_error",
                    "function": {
                        "name": "create_reservation",
                        "arguments": '{"customer_name": "Ana Error", "phone": "600000000", "date": "2026-05-10", "time": "21:00", "pax": 2}'
                    }
                }
            ]
        }
    }
    
    with patch('src.api.vapi_tools_router.get_airtable_service_lazy') as mock_airtable:
        mock_instance = MagicMock()
        mock_airtable.return_value = mock_instance
        mock_instance.create_record.side_effect = Exception("Airtable Connection Timeout!")

        response = client.post("/vapi/tools/create_reservation", json=payload_error)
        assert response.status_code == 200, f"Error: El backend devolvió HTTP {response.status_code} en vez de 200 con respuesta hablada de fallo"
        data = response.json()
        assert data["results"][0]["toolCallId"] == "call_error", "No se devolvió el toolCallId correcto"
        
        result_text = data["results"][0]["result"]
        assert "problemita técnico" in result_text or "desastre" in result_text, f"No se deolvió el texto de rescate: {result_text}"
        print(f"OK - TEST 2 PASADO: Sistema protegido contra caídas (500). Devuelve a Vapi: '{result_text}'")

    print("\nTODOS LOS TESTS COMPLETADOS Y PASADOS CORRECTAMENTE.")

if __name__ == "__main__":
    run_tests()
