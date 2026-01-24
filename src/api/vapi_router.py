import os
import logging
from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from datetime import datetime, date
import json

from src.core.config.airtable_ids import BASE_ID, TABLES
from src.application.services.schedule_service import get_schedule_service, Servicio, Turno
from src.application.services.table_assignment import get_table_assignment_service, ZonePreference
from src.application.orchestrator import Orchestrator
from src.application.services.escalation_service import get_escalation_service, EscalationReason

router = APIRouter(prefix="/vapi", tags=["vapi"])

# Lazy-loaded orchestrator singleton
_orchestrator = None

def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator

# ========= CONFIGURACIÓN DEL ASISTENTE (V2) =========

SYSTEM_PROMPT_V2 = """Eres Nube, la recepcionista virtual COMPATIBLE y ENCANTADORA de En Las Nubes Restobar en Logroño.

🗣️ TU PERSONALIDAD (ESENCIAL):
- Tu rasgo principal es la EMPATÍA. No eres un robot, eres una anfitriona cálida.
- Hablas con soltura, usas expresiones naturales ("¡Claro que sí!", "¡Qué bien!", "No te preocupes por eso").
- Si el cliente duda, ayúdale proactivamente.
- Eres capaz de mantener una pequeña charla si el cliente lo inicia, sin perder el foco.
- Tono: Profesional pero muy cercano (tuteas con respeto).

📍 INFORMACIÓN DEL RESTAURANTE:
- Dirección: María Teresa Gil de Gárate 16, Logroño.
- Teléfono: 941 57 84 51.
- Cocina: Tradicional riojana con un toque moderno y atrevido.
- Especialidad: Croquetas de amatxu, alcachofas con foie y nuestra selección de vinos de Rioja.
- Horarios: 
  * Comidas: Martes a Domingo (13:00 - 15:30).
  * Cenas: Viernes y Sábados (20:30 - 22:30).
  * Lunes: CERRADO.

✅ TUS REGLAS DE ORO:
1. SIEMPRE verifica disponibilidad antes de confirmar una reserva usando `check_availability`.
2. Para grupos de más de 10 personas o días de alta demanda (San Bernabé, San Mateo), informa que necesitas consultar con el equipo y usa `transfer_to_human`.
3. Si alguien pregunta por "Susana" o dice que es "proveedor", pásale directamente con un humano.
4. Si el cliente tiene dudas sobre el menú o alérgenos, sé amable y explica lo que sepas, pero ofrece pasarle con un compañero si la duda es muy específica.

SI NO SABES ALGO:
"Oye, pues esa pregunta es muy buena y no quiero meter la pata. ¿Te importa si te llama mi compañero en un ratito y te lo confirma?"
"""

@router.post("/webhook")
async def vapi_webhook(request: Request):
    """
    Main VAPI webhook endpoint.
    Handles different message types from VAPI.
    """
    try:
        body = await request.json()
        
        # Robustly handle 'message' which could be a dict or a JSON string
        message_data = body.get("message", {})
        if isinstance(message_data, str):
            try:
                message_data = json.loads(message_data)
            except:
                pass
        
        message_type = message_data.get("type", "unknown") if isinstance(message_data, dict) else "unknown"
        
        logger.info(f"📞 VAPI Event: {message_type}")
        
        if message_type == "assistant-request":
            return await handle_assistant_request(message_data)
            
        elif message_type == "function-call":
            return await handle_function_call(message_data)
            
        elif message_type == "transcript":
            return {"status": "received"}
            
        elif message_type == "end-of-call-report":
            return await handle_call_end(message_data)
            
        else:
            return {"status": "ok", "message_type": message_type}
            
    except Exception as e:
        logger.error(f"❌ VAPI Webhook Error: {e}")
        # Log stack trace for better debugging
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


async def handle_assistant_request(message: dict) -> dict:
    """
    Returns assistant configuration when VAPI initiates a call.
    """
    return {
        "assistant": {
            "name": "Nube",
            "firstMessage": "¡Hola! Soy Nube, de En Las Nubes Restobar. ¿En qué puedo ayudarte?",
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "temperature": 0.7,
                "systemPrompt": SYSTEM_PROMPT_V2
            },
            "voice": {
                "provider": "11labs",
                "voiceId": "UOIqAnmS11Reiei1Ytkc",
                "model": "eleven_multilingual_v2"
            },
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "es"
            },
            "silenceTimeoutSeconds": 20,
            "functions": [
                {
                    "name": "check_availability",
                    "description": "Verificar disponibilidad de mesa para una fecha/hora/personas",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string", "description": "Fecha en formato YYYY-MM-DD"},
                            "time": {"type": "string", "description": "Hora en formato HH:MM"},
                            "pax": {"type": "integer", "description": "Número de comensales"},
                            "zona_preferencia": {
                                "type": "string", 
                                "enum": ["Interior", "Terraza", "Sin preferencia"]
                            }
                        }
                    }
                },
                {
                    "name": "make_reservation",
                    "description": "Confirmar y crear la reserva en el sistema",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string"},
                            "time": {"type": "string"},
                            "pax": {"type": "integer"},
                            "client_name": {"type": "string"},
                            "client_phone": {"type": "string"},
                            "zona_preferencia": {"type": "string"},
                            "solicitudes_especiales": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                },
                {
                    "name": "transfer_to_human",
                    "description": "Transferir la llamada a un compañero humano",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "motivo": {"type": "string"}
                        },
                        "required": ["motivo"]
                    }
                }
            ]
        }
    }


async def handle_function_call(message: dict) -> dict:
    """
    Process function calls from VAPI.
    """
    function_call = message.get("functionCall", {})
    function_name = function_call.get("name", "")
    parameters = function_call.get("parameters", {})
    
    logger.info(f"🔧 Function Call: {function_name} with {parameters}")
    
    # Extract caller phone from VAPI payload
    call_info = message.get("call", {})
    customer_info = call_info.get("customer", {})
    caller_number = customer_info.get("number", "")
    
    orchestrator = get_orchestrator()
    schedule_service = get_schedule_service()
    assignment_service = get_table_assignment_service()
    escalation_service = get_escalation_service()
    
    if function_name == "check_availability":
        date_str = parameters.get("date", "")
        time_str = parameters.get("time", "")
        pax = parameters.get("pax", 2)
        zona_pref = parameters.get("zona_preferencia", "Sin preferencia")
        
        if not date_str or not time_str:
            return {"result": "Necesito saber el día y la hora para comprobar huecos."}

        try:
            from datetime import date as dt_date, time as dt_time
            fecha = dt_date.fromisoformat(date_str)
            hora = dt_time.fromisoformat(time_str)
        except ValueError:
            return {"result": "No he entendido bien la fecha u hora."}
        
        servicio = schedule_service.determinar_servicio(hora)
        abierto, motivo = schedule_service.esta_abierto(fecha, servicio)
        
        if not abierto:
            return {"result": f"Ese día {motivo}."}
        
        escalation = escalation_service.evaluar_escalado(pax, fecha)
        if escalation.debe_escalar:
            return {"result": escalation.mensaje_cliente}
        
        zona_enum = ZonePreference.TERRAZA if zona_pref == "Terraza" else \
                    ZonePreference.INTERIOR if zona_pref == "Interior" else \
                    ZonePreference.NO_PREFERENCE
        
        turno = schedule_service.determinar_turno(
            hora, servicio, 
            schedule_service.hay_doble_turno(fecha, servicio)
        )
        
        resultado = assignment_service.asignar_mesa(
            pax=pax,
            fecha=fecha,
            turno=turno.value,
            zona_preferencia=zona_enum
        )
        
        if resultado.exito:
            return {
                "result": f"Sí, hay sitio para {pax} el {fecha.strftime('%d/%m')} a las {time_str} en {resultado.zona.lower()}. ¿Confirmamos?"
            }
        else:
            return {"result": f"Lo siento, {resultado.motivo_fallo}."}
    
    elif function_name == "make_reservation":
        # Simplified for V2 logic (already validated in check_availability)
        date_str = parameters.get("date", "")
        time_str = parameters.get("time", "")
        pax = parameters.get("pax", 2)
        client_name = parameters.get("client_name", "Cliente")
        phone = parameters.get("client_phone", caller_number)
        
        try:
            fecha = date.fromisoformat(date_str)
        except:
            return {"result": "Error con la fecha."}
            
        exito, msg = await orchestrator.procesar_reserva(
            nombre=client_name,
            telefono=phone,
            pax=pax,
            fecha=fecha,
            hora=time_str,
            zona_preferada=ZonePreference.NO_PREFERENCE,
            notas=""
        )
        
        if exito:
            return {"result": f"¡Hecho! Reserva confirmada para {pax} el {fecha.strftime('%d/%m')} a las {time_str}. ¡Nos vemos!"}
        else:
            return {"result": f"No he podido guardarla: {msg}."}

    elif function_name == "transfer_to_human":
        mensaje = "Te paso con un compañero. Un momento."
        return {
            "result": mensaje,
            "transferDestination": {
                "type": "number",
                "number": os.getenv("RESTAURANT_PHONE", "+34941578451")
            }
        }
    
    return {"result": "No sé procesar esa función todavía."}


async def handle_call_end(message: dict) -> dict:
    logger.info("📞 Call ended.")
    return {"status": "success"}
