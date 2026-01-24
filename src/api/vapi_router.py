import os
import logging
from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from datetime import datetime, date

from src.core.config.airtable_ids import BASE_ID, TABLES
from src.application.services.schedule_service import get_schedule_service, Servicio, Turno
from src.application.services.table_assignment_service import get_table_assignment_service, ZonePreference
from src.application.services.orchestrator import get_orchestrator
from src.application.services.escalation_service import get_escalation_service, EscalationReason

router = APIRouter(prefix="/vapi", tags=["vapi"])

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
        logger.info(f"DEBUG: Body type: {type(body)}")
        logger.info(f"DEBUG: Body content: {body}")
        
        message_data = body.get("message", {})
        logger.info(f"DEBUG: Message type: {type(message_data)}")
        
        message_type = message_data.get("type", "unknown") if isinstance(message_data, dict) else "unknown"
        
        logger.info(f"📞 VAPI Event: {message_type}")
        
        if message_type == "assistant-request":
            return await handle_assistant_request(body)
            
        elif message_type == "function-call":
            return await handle_function_call(body)
            
        elif message_type == "transcript":
            return {"status": "received"}
            
        elif message_type == "end-of-call-report":
            return await handle_call_end(body)
            
        else:
            return {"status": "ok", "message_type": message_type}
            
    except Exception as e:
        logger.error(f"❌ VAPI Webhook Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_assistant_request(body: dict) -> dict:
    """
    Returns assistant configuration when VAPI initiates a call.
    Updated with V2 prompt and escalation functions.
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
                "voiceId": "UOIqAnmS11Reiei1Ytkc",  # Carolina (Spanish Spain)
                "model": "eleven_multilingual_v2"
            },
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "es"
            },
            "silenceTimeoutSeconds": 20,
            "backgroundSound": None,
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
                                "enum": ["Interior", "Terraza", "Sin preferencia"],
                                "description": "Preferencia de mesa (interior o terraza)"
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
                            "motivo": {"type": "string", "description": "Razón corta de la transferencia"}
                        },
                        "required": ["motivo"]
                    }
                }
            ]
        }
    }


async def handle_function_call(body: dict) -> dict:
    """
    Process function calls from VAPI with V2 logic.
    """
    message = body.get("message", {})
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
    
    # ========== CHECK AVAILABILITY ==========
    if function_name == "check_availability":
        date_str = parameters.get("date", "")
        time_str = parameters.get("time", "")
        pax = parameters.get("pax", 2)
        zona_pref = parameters.get("zona_preferencia", "Sin preferencia")
        
        # Graceful handling of missing parameters
        if not date_str:
            return {"result": "¿Para qué día te gustaría reservar?"}
        if not time_str:
            return {"result": "¿A qué hora querríais venir?"}

        try:
            from datetime import date as dt_date, time as dt_time
            fecha = dt_date.fromisoformat(date_str)
            hora = dt_time.fromisoformat(time_str)
        except ValueError:
            return {"result": "No he entendido bien la fecha u hora. ¿ Puedes repetirlo? Por ejemplo: 'El sábado a las 2 de la tarde'."}
        
        # Check if restaurant is open
        servicio = schedule_service.determinar_servicio(hora)
        abierto, motivo = schedule_service.esta_abierto(fecha, servicio)
        
        if not abierto:
            return {"result": f"Lo siento, ese día {motivo}. ¿Quieres probar otro día?"}
        
        # Check if we need to escalate
        escalation = escalation_service.evaluar_escalado(pax, fecha)
        if escalation.debe_escalar:
            return {"result": escalation.mensaje_cliente}
        
        # Try to assign a table
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
            avisos = " ".join(resultado.avisos) if resultado.avisos else ""
            return {
                "result": f"Sí, tengo disponibilidad para {pax} personas el {fecha.strftime('%d/%m')} a las {time_str} en {resultado.zona.lower()}. {avisos} ¿Confirmamos la reserva?"
            }
        else:
            return {
                "result": f"Lo siento, {resultado.motivo_fallo}. ¿Quieres que pruebe otra hora o día?"
            }
    
    # ========== MAKE RESERVATION ==========
    elif function_name == "make_reservation":
        date_str = parameters.get("date", "")
        time_str = parameters.get("time", "")
        pax = parameters.get("pax", 2)
        client_name = parameters.get("client_name", "")
        phone = parameters.get("client_phone", caller_number)
        zona_pref = parameters.get("zona_preferencia", "Sin preferencia")
        solicitudes = parameters.get("solicitudes_especiales", [])
        
        # Validate essential data
        if not date_str or not time_str:
            return {"result": "Para confirmar la reserva necesito saber el día y la hora. ¿Para cuándo sería?"}
        
        try:
            fecha = date.fromisoformat(date_str)
        except ValueError:
            return {"result": "La fecha no parece válida. ¿Puedes decirme el día de nuevo?"}

        # Final table assignment attempt
        zona_enum = ZonePreference.TERRAZA if zona_pref == "Terraza" else \
                    ZonePreference.INTERIOR if zona_pref == "Interior" else \
                    ZonePreference.NO_PREFERENCE
        
        # Re-check escalation (just in case)
        escalation = escalation_service.evaluar_escalado(pax, fecha, solicitudes)
        if escalation.debe_escalar:
            return {"result": escalation.mensaje_cliente}
            
        # Create booking in Orchestrator
        exito, msg = await orchestrator.procesar_reserva(
            nombre=client_name,
            telefono=phone,
            pax=pax,
            fecha=fecha,
            hora=time_str,
            zona_preferida=zona_enum,
            notas=", ".join(solicitudes) if solicitudes else ""
        )
        
        if exito:
            return {"result": f"¡Perfecto! Ya tienes tu mesa para {pax} personas el día {fecha.strftime('%d/%m')} a las {time_str}. Te acabo de enviar un WhatsApp con la confirmación. ¡Te esperamos!"}
        else:
            return {"result": f"Vaya, ha habido un problemilla al guardar la reserva: {msg}. ¿Quieres que lo intente de nuevo o prefieres hablar con un compañero?"}

    # ========== TRANSFER TO HUMAN ==========
    elif function_name == "transfer_to_human":
        motivo = parameters.get("motivo", "Solicitud del cliente")
        logger.info(f"🔄 Transferring to human. Reason: {motivo}")
        
        mensaje = "Te paso con un compañero para que te ayude mejor con eso. Un momento, por favor."
        
        return {
            "result": mensaje,
            "transferDestination": {
                "type": "number",
                "number": os.getenv("RESTAURANT_PHONE", "+34941578451"),
                "message": mensaje
            }
        }
    
    return {"result": "No sé cómo hacer eso todavía, pero puedo ayudarte con reservas."}


async def handle_call_end(body: dict) -> dict:
    """Handles logic after a call ends (not used for logic, just logging/reporting)."""
    logger.info("📞 Call ended. Processing report...")
    return {"status": "success"}


async def handle_call_transcript(body: dict) -> dict:
    """Optionally process Real-time Transcript if needed."""
    return {"status": "success"}
