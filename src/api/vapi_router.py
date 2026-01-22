"""
VAPI Webhook Router: Handles incoming voice calls from VAPI.
VAPI sends events like assistant-request, function-call, end-of-call-report.
"""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from src.application.orchestrator import Orchestrator

router = APIRouter(prefix="/vapi", tags=["VAPI"])
logger = logging.getLogger(__name__)

# Lazy-loaded orchestrator
_orchestrator: Optional[Orchestrator] = None

def get_orchestrator() -> Orchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator


class VAPIMessage(BaseModel):
    """VAPI webhook message structure."""
    message: Dict[str, Any]


@router.post("/webhook")
async def vapi_webhook(request: Request):
    """
    Main VAPI webhook endpoint.
    Handles different message types from VAPI.
    """
    try:
        body = await request.json()
        message_type = body.get("message", {}).get("type", "unknown")
        
        logger.info(f"📞 VAPI Event: {message_type}")
        
        if message_type == "assistant-request":
            # VAPI asks for assistant configuration
            return await handle_assistant_request(body)
            
        elif message_type == "function-call":
            # VAPI wants to execute a function
            return await handle_function_call(body)
            
        elif message_type == "transcript":
            # Real-time transcript (useful for logging)
            return {"status": "received"}
            
        elif message_type == "end-of-call-report":
            # Call ended, get summary
            return await handle_call_end(body)
            
        else:
            return {"status": "ok", "message_type": message_type}
            
    except Exception as e:
        logger.error(f"❌ VAPI Webhook Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_assistant_request(body: dict) -> dict:
    """
    Returns assistant configuration when VAPI initiates a call.
    This defines the AI's behavior for the call.
    """
    return {
        "assistant": {
            "name": "Nube",
            "firstMessage": "¡Hola! Soy Nube, de En Las Nubes Restobar. ¿En qué puedo ayudarte?",
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "temperature": 0.7,
                "systemPrompt": """Eres Nube, la recepcionista virtual de En Las Nubes Restobar en Logroño.
                
SOLO HABLAS ESPAÑOL DE ESPAÑA.
Si el usuario habla en otro idioma, responde amablemente en español.

INFORMACIÓN DEL RESTAURANTE:
- Dirección: María Teresa Gil de Gárate 16, Logroño.
- Horario: X-D 13-16h y 20:30-23:30h. L-M Cerrado.

TU OBJETIVO:
1. Gestionar reservas (fecha, hora, pax, nombre).
2. El número de teléfono YA LO TIENES (no lo preguntes).
3. Ser breve, cálida y eficaz.
"""
            },
            "voice": {
                "provider": "11labs",
                "voiceId": "UOIqAnmS11Reiei1Ytkc",  # Carolina (Spanish Spain)
                "model": "eleven_multilingual_v2"
            },
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "es"
            },
            "functions": [
                {
                    "name": "make_reservation",
                    "description": "Crear una reserva en el restaurante",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string", "description": "Fecha de la reserva (YYYY-MM-DD)"},
                            "time": {"type": "string", "description": "Hora de la reserva (HH:MM)"},
                            "pax": {"type": "integer", "description": "Número de personas"},
                            "client_name": {"type": "string", "description": "Nombre del cliente"},
                            "client_phone": {"type": "string", "description": "Teléfono del cliente (opcional, si el usuario lo dicta)"}
                        },
                        "required": ["date", "time", "pax", "client_name"]
                    }
                },
                {
                    "name": "check_availability",
                     "description": "Verificar si hay mesa disponible",
                     "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string"},
                            "time": {"type": "string"},
                            "pax": {"type": "integer"}
                        },
                        "required": ["date", "time", "pax"]
                     }
                }
            ]
        }
    }


async def handle_function_call(body: dict) -> dict:
    """
    Process function calls from VAPI (check_availability, create_reservation).
    """
    message = body.get("message", {})
    function_call = message.get("functionCall", {})
    function_name = function_call.get("name", "")
    parameters = function_call.get("parameters", {})
    
    logger.info(f"🔧 Function Call: {function_name} with {parameters}")
    
    orchestrator = get_orchestrator()
    
    if function_name == "check_availability":
        # Check availability for date/time/pax
        date = parameters.get("date", "")
        time = parameters.get("time", "")
        pax = parameters.get("pax", 2)
        
        result = await orchestrator.process_message(
            f"Verificar disponibilidad para {pax} personas el {date} a las {time}",
            metadata={"date": date, "time": time, "pax": pax, "action": "check_availability"}
        )
        
        if result.get("booking_result", {}).get("available"):
            return {
                "result": f"Sí, hay disponibilidad para {pax} personas el {date} a las {time}. ¿Quieres que haga la reserva?"
            }
        else:
            return {
                "result": f"Lo siento, no hay disponibilidad para ese horario. ¿Quieres que pruebe otra hora?"
            }
    
    elif function_name == "create_reservation" or function_name == "make_reservation":
        # Create a reservation
        date = parameters.get("date", "")
        time = parameters.get("time", "")
        pax = parameters.get("pax", 2)
        customer_name = parameters.get("customer_name", parameters.get("client_name", ""))
        phone = parameters.get("phone", parameters.get("client_phone", ""))
        
        # Extract caller's phone number from VAPI payload
        call_info = message.get("call", {})
        customer_info = call_info.get("customer", {})
        caller_number = customer_info.get("number", "")
        
        # Use extracted caller number if parameter is missing/empty, otherwise use parameter
        # Priority: Parameter (if user explicitly gave a different one) > Caller ID
        final_phone = phone if phone else caller_number

        result = await orchestrator.process_message(
            f"Crear reserva para {pax} personas el {date} a las {time}",
            metadata={
                "date": date,
                "time": time,
                "pax": pax,
                "client_name": customer_name,
                "client_phone": final_phone, # Use the robust phone number
                "action": "create_reservation"
            }
        )
        
        if result.get("booking_result", {}).get("available"):
            table = result.get("booking_result", {}).get("assigned_table", "una mesa")
            return {
                "result": f"¡Perfecto! Reserva confirmada para {customer_name}: {pax} personas el {date} a las {time} en {table}. ¡Os esperamos!"
            }
        else:
            return {
                "result": "Lo siento, no hay disponibilidad en ese horario. ¿Quieres que te ofrezca alternativas?"
            }
    
    return {"result": "Función no reconocida."}


async def handle_call_end(body: dict) -> dict:
    """
    Process end-of-call report for logging/analytics.
    """
    message = body.get("message", {})
    summary = message.get("summary", "Sin resumen")
    duration = message.get("durationSeconds", 0)
    
    logger.info(f"📊 Call ended. Duration: {duration}s. Summary: {summary}")
    
    return {"status": "logged"}
