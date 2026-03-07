import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.api.vapi_tools_router import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)

def test_create_reservation_success():
    """Testea el flujo feliz de crear una reserva."""
    payload = {
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
        
        # Mocks
        mock_instance = MagicMock()
        mock_airtable.return_value = mock_instance
        
        # OJO: create_record en vapi_tools_router está siendo llamado con await, por tanto mockeamos como AsyncMock
        from unittest.mock import AsyncMock
        mock_instance.create_record = AsyncMock(return_value={"id": "rec123"})
        
        mock_twilio.return_value = "MSxxxxx"

        response = client.post("/vapi/tools/create_reservation", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) > 0
        assert data["results"][0]["toolCallId"] == "call_123"
        # Comprobar que devuelve la frase hablada de confirmación (mensaje actualizado)
        assert "¡Perfecto, Juan Perez!" in data["results"][0]["result"]

def test_create_reservation_airtable_failure_graceful_recovery():
    """Testea que si Airtable explota (Exception), Vapi no recibe 500 sino un mensaje hablado pidiendo disculpas."""
    payload = {
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
        
        # Simulamos que Airtable está caído o da error 500
        mock_instance.create_record.side_effect = Exception("Airtable Connection Timeout!")

        response = client.post("/vapi/tools/create_reservation", json=payload)
        
        # Afirmamos que NUNCA devolvemos 500 al cliente de voz
        assert response.status_code == 200
        data = response.json()
        assert data["results"][0]["toolCallId"] == "call_error"
        # Comprobamos que devuelve el texto de rescate
        assert "problemita técnico" in data["results"][0]["result"] or "desastre" in data["results"][0]["result"]

def test_missing_data_returns_natural_prompt():
    """Testea que la falta de datos devuelva a Vapi instrucciones para volver a preguntar, no un error."""
    payload = {
        "message": {
            "toolCallList": [
                {
                    "id": "call_missing",
                    "function": {
                        "name": "create_reservation",
                        "arguments": '{"customer_name": "Ana Falta Datos"}' # Falta date, pax, time
                    }
                }
            ]
        }
    }
    
    response = client.post("/vapi/tools/create_reservation", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "Me faltan datos." in data["results"][0]["result"]
