from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any, Optional
import os
import logging
from datetime import datetime

from src.application.services.schedule_service import ScheduleService
from src.infrastructure.repositories.mock_reservation_repository import MockReservationRepository
from src.infrastructure.external.twilio_service import TwilioService
from src.infrastructure.external.airtable_service import AirtableService
from src.core.entities.booking import Booking  # FIXED: era src.domain.models.reservation

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vapi", tags=["VAPI"])

# Instanciar servicios
# En un entorno real, esto se inyectaría mediante dependencias
# Se asume que estos servicios existen o se inyectan correctamente.
# Para simplificar y mantener compatibilidad con lo que hay en el repo remoto:
reservation_repository = MockReservationRepository()
schedule_service = ScheduleService()
twilio_service = TwilioService()
airtable_service = AirtableService()


@router.post("/webhook")
async def vapi_voice_webhook(request: Request):
    """
    Webhook para llamadas entrantes de Twilio.
    Devuelve TwiML para conectar la llamada con VAPI.
    """
    try:
        form_data = await request.form()
        from_number = form_data.get("From", "unknown")
        to_number = form_data.get("To", "unknown")
        call_sid = form_data.get("CallSid", "unknown")
        
        logger.info(f"Incoming call from {from_number} to {to_number}, SID: {call_sid}")
        
        from fastapi import Response
        
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="wss://api.vapi.ai/twilio/stream">
            <Parameter name="assistantId" value="9a1f2df2-1c2d-4061-b11c-bdde7568c85d"/>
            <Parameter name="customerPhoneNumber" value="{from_number}"/>
        </Stream>
    </Connect>
</Response>"""
        
        return Response(content=twiml_response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling voice webhook: {str(e)}")
        from fastapi import Response
        error_twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-ES">
        Lo sentimos, ha ocurrido un error técnico. Por favor, llame al restaurante directamente al 941 57 84 51.
    </Say>
    <Hangup/>
</Response>"""
        return Response(content=error_twiml, media_type="application/xml")


# --- CONSTANTES Y PROMPTS ---

SYSTEM_PROMPT_V2 = """Eres Nube, la recepcionista virtual COMPATIBLE y ENCANTADORA de En Las Nubes Restobar en Logroño.

🗣️ TU PERSONALIDAD (ESENCIAL):
- Tu rasgo principal es la EMPATÍA. No eres un robot, eres una anfitriona cálida.
- Hablas con soltura, usas expresiones naturales ("¡Claro que sí!", "¡Qué bien!", "No te preocupes por eso").
- Si el cliente duda, ayúdale proactivamente.
- Eres capaz de mantener una pequeña charla si el cliente lo inicia, sin perder el foco.
- Tono: Profesional pero muy cercano (tuteas con respeto).

📍 INFORMACIÓN DEL RESTAURANTE:
- Dirección: María Teresa Gil de Gárate 16, Logroño.
- NOTA UBICACIÓN: La calle es PEATONAL (no se puede aparcar en la puerta).
- 🅿️ APARCAMIENTO RECOMENDADO: Calle Pérez Galdós, Calle República Argentina, Calle Huesca y el Parking de Gran Vía.
- Teléfono: 941 57 84 51.
- Cocina: Especialidad en CACHOPOS y cocina de inspiración ALEMANA (salchichas, codillo). También tenemos entrantes, hamburguesas y postres caseros.
- Carta Sin Gluten: Tenemos variedad de entrantes, hamburguesas y platos alemanes aptos.

🕒 HORARIOS Y TURNOS:
- Comidas (Martes a Domingo): 13:00 - 17:00 (Cocina cierra antes).
- Cenas (Jueves): 20:00 - 24:00.
- Cenas (Viernes/Sábado): 20:00 - 00:30 (Viernes) / 01:00 (Sábado).
- Lunes: CERRADO (salvo festivos).
- Domingo noche, Martes noche, Miércoles noche: CERRADO habitual.
- IMPORTANTE: SÍ existen turnos en días concurridos (fines de semana). El sistema te dirá la disponibilidad.

✅ TUS REGLAS DE ORO:
1. SIEMPRE verifica disponibilidad antes de confirmar una reserva usando `check_availability`.
2. DATOS OBLIGATORIOS RESERVA: Nombre completo y Número de Teléfono (para enviar confirmación por WhatsApp). DILE AL CLIENTE que recibirá confirmación por WhatsApp.
3. CACHOPOS SIN GLUTEN: Si piden cachopo sin gluten, PREGUNTA cuál de la carta quieren (tienen que elegir uno específico). Requiere aviso 24h.
4. Para grupos de más de 10 personas, informa que necesitas consultar con el equipo y usa `transfer_to_human`.
5. Si alguien pregunta por "Susana" o dice que es "proveedor", pásale directamente con un humano.

SI NO SABES ALGO:
"Oye, pues esa pregunta es muy buena y no quiero meter la pata. ¿Te importa si te llama mi compañero en un ratito y te lo confirma?"

NOTA IMPORTANTE: Siempre responde en español de España. Sé breve y clara.
"""

# --- ENDPOINTS ---

@router.post("/assistant")
async def get_assistant_config(request: Request):
    """
    Endpoint que VAPI llama para obtener la configuración del asistente.
    Devuelve el system prompt, la voz, y las herramientas disponibles.
    """
    try:
        data = await request.json()
        logger.info(f"Recibida petición de configuración de asistente: {data}")
        
        # Aquí podrías personalizar la respuesta según el caller_id, etc.
        
        return {
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "systemPrompt": SYSTEM_PROMPT_V2,
                "temperature": 0.7,
                # Force Spanish
                "language": "es" 
            },
            "voice": {
                "provider": "11labs",
                "voiceId": "sarah", # ID generico, validar
                "stability": 0.5,
                "similarityBoost": 0.75
            },
            "firstMessage": "¡Hola! Bienvenido a En Las Nubes Restobar. Soy Nube. ¿En qué puedo ayudarte hoy?",
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "es-ES"
            }
        }
    except Exception as e:
        logger.error(f"Error generando configuración del asistente: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/check_availability")
async def tool_check_availability(request: Request):
    """
    Herramienta para verificar disponibilidad.
    """
    try:
        data = await request.json()
        message = data.get("message", {})
        tool_call = message.get("toolCalls", [])[0]
        args = tool_call.get("function", {}).get("arguments", {})
        
        logger.info(f"Checking availability with args: {args}")
        
        fecha_str = args.get("fecha") # YYYY-MM-DD
        hora_str = args.get("hora")   # HH:MM
        personas = args.get("personas")
        
        if not fecha_str or not hora_str or not personas:
            return {"results": [{"toolCallId": tool_call["id"], "result": "Faltan datos para comprobar la disponibilidad. Por favor, pide fecha, hora y número de personas."}]}

        # Parsear fecha y hora
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            hora = datetime.strptime(hora_str, "%H:%M").time()
        except ValueError:
             return {"results": [{"toolCallId": tool_call["id"], "result": "Formato de fecha u hora inválido. Usa YYYY-MM-DD y HH:MM."}]}

        is_open, msg_open = schedule_service.es_horario_apertura(fecha, hora)
        if not is_open:
             return {"results": [{"toolCallId": tool_call["id"], "result": f"El restaurante está cerrado en ese horario. {msg_open}"}]}

        disponible = reservation_repository.check_availability(fecha, hora, int(personas))
        
        if disponible:
            resultado = "¡Sí! Tenemos mesa disponible para esa hora. ¿Quieres que te la reserve?"
        else:
            # Sugerir alternativas (simple implementación)
            resultado = "Vaya, lo siento mucho, pero para esa hora exacta no me queda nada. ¿Te vendría bien un poco antes o después? Podría mirar a las..."
            
        return {
            "results": [
                {
                    "toolCallId": tool_call["id"],
                    "result": resultado
                }
            ]
        }

    except Exception as e:
        logger.error(f"Error checking availability: {str(e)}")
        return {
            "results": [
                {
                    "toolCallId": tool_call.get("id"),
                    "result": "Tuve un pequeño problema técnico comprobando la agenda. ¿Te importa repetirme la fecha y hora?"
                }
            ]
        }

@router.post("/tools/create_reservation")
async def tool_create_reservation(request: Request):
    """
    Herramienta para crear la reserva FINAL.
    """
    try:
        data = await request.json()
        message = data.get("message", {})
        tool_call = message.get("toolCalls", [])[0]
        args = tool_call.get("function", {}).get("arguments", {})
        
        logger.info(f"Creating reservation with args: {args}")

        nombre = args.get("nombre")
        telefono = args.get("telefono")
        fecha_str = args.get("fecha")
        hora_str = args.get("hora")
        personas = args.get("personas")
        notas = args.get("notas", "")
        
        if not all([nombre, telefono, fecha_str, hora_str, personas]):
             return {"results": [{"toolCallId": tool_call["id"], "result": "Me faltan algunos datos para confirmar. Necesito nombre, teléfono, fecha, hora y personas."}]}

        # Crear objeto Reserva
        reserva = Booking(  # FIXED: era Reservation
            nombre_cliente=nombre,
            telefono_cliente=telefono,
            fecha=fecha_str,
            hora=hora_str,
            num_personas=int(personas),
            notas=notas,
            origen="VAPI_VOICE"
        )
        
        # 1. Guardar en BD (Mock)
        res_id = reservation_repository.create_reservation(reserva)
        
        # 2. Guardar en Airtable
        try:
             airtable_record = await airtable_service.create_record({
                "Nombre": nombre,
                "Teléfono": telefono,
                "Fecha": fecha_str,
                "Hora": hora_str,
                "Personas": int(personas),
                "Notas": notas,
                "Estado": "Confirmada",
                "Origen": "VAPI"
             })
             logger.info(f"Reserva guardada en Airtable: {airtable_record}")
        except Exception as e:
            logger.error(f"Error guardando en Airtable: {e}")
            # No fallamos la reserva si falla Airtable, pero logueamos
        
        # 3. Enviar SMS Confirmación (Twilio)
        sms_enviado = False
        try:
            msg = f"¡Reserva Confirmada en En Las Nubes! ☁️\nHola {nombre}, te esperamos el {fecha_str} a las {hora_str} ({personas} pax).\n📍 C/ Mª Teresa Gil de Gárate 16.\nSi necesitas cancelar, avísanos por aquí. ¡Gracias!"
            sid = twilio_service.send_sms(telefono, msg)
            if sid:
                sms_enviado = True
                logger.info(f"SMS enviado: {sid}")
        except Exception as e:
            logger.error(f"Error enviando SMS: {e}")

        respuesta_cliente = f"¡Perfecto, {nombre}! Ya está hecha la reserva. Te he enviado un WhatsApp/SMS con la confirmación. ¡Nos vemos en Las Nubes!"
        if not sms_enviado:
            respuesta_cliente = f"¡Perfecto, {nombre}! Reserva confirmada. No he podido enviarte el SMS de confirmación por un error técnico, pero tu mesa está guardada. ¡Nos vemos!"

        return {
            "results": [
                {
                    "toolCallId": tool_call["id"],
                    "result": respuesta_cliente
                }
            ]
        }

    except Exception as e:
        logger.error(f"Error creating reservation: {str(e)}")
        return {
            "results": [
                {
                    "toolCallId": tool_call.get("id"), # Safe get
                    "result": "Lo siento, tuve un error al guardar la reserva. ¿Podrías intentar llamar al restaurante directamente? 941 57 84 51."
                }
            ]
        }
