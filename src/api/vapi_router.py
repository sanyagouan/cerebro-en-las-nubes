from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any, Optional
import os
import logging
from datetime import datetime

from src.application.services.schedule_service import ScheduleService
from src.infrastructure.repositories.mock_reservation_repository import (
    MockReservationRepository,
)
from src.infrastructure.external.twilio_service import TwilioService
from src.infrastructure.external.airtable_service import AirtableService
from src.core.entities.booking import (
    Booking,
)  # FIXED: era src.domain.models.reservation
from src.application.services.waitlist_service import WaitlistService
# from src.api.middleware.rate_limiting import webhook_limit  # TODO: Re-enable after fixing slowapi

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
waitlist_service = WaitlistService()


@router.post("/webhook")
# @webhook_limit()  # TODO: Re-enable after fixing slowapi integration
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
            <Parameter name="assistantId" value="{os.getenv('VAPI_ASSISTANT_ID', '9a1f2df2-1c2d-4061-b11c-bdde7568c85d')}"/>
            <Parameter name="customerPhoneNumber" value="{from_number}"/>
        </Stream>
    </Connect>
    <Pause length="43200"/>
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
2. DATOS OBLIGATORIOS RESERVA: Nombre completo y Número de Teléfono (para enviar confirmación por WhatsApp). DILE AL CLIENTE que recibirá:
   - Confirmación inmediata por WhatsApp
   - Recordatorio 24h antes por WhatsApp
   - Puede cancelar respondiendo al WhatsApp o llamando
3. LISTA DE ESPERA: Si no hay mesa disponible, OFRECE apuntar al cliente en la lista de espera. Le avisaremos por WhatsApp si se libera mesa (tienen 15 min para confirmar). Usa `add_to_waitlist`.
4. CACHOPOS SIN GLUTEN: Si piden cachopo sin gluten, PREGUNTA cuál de la carta quieren (tienen que elegir uno específico). Requiere aviso 24h.
5. Para grupos de más de 10 personas, informa que necesitas consultar con el equipo y usa `transfer_to_human`.
6. Si alguien pregunta por "Susana" o dice que es "proveedor", pásale directamente con un humano.

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

        # Base URL for tools (obtenida dinámicamente)
        base_url = os.getenv("PUBLIC_URL", "https://api.cerebro.enlasnubes.restobar").rstrip("/")

        # VAPI espera la configuración DENTRO de la clave "assistant"
        return {
            "assistant": {
                "model": {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "messages": [{"role": "system", "content": SYSTEM_PROMPT_V2}],
                    "temperature": 0.7,
                    "functions": [
                        {
                            "name": "get_info",
                            "description": "Obtener información general del restaurante (dirección, teléfono, parking, especialidades, carta sin gluten, política de mascotas). Úsala cuando el cliente pregunte por información básica del restobar.",
                            "parameters": {
                                "type": "object",
                                "properties": {},
                                "required": [],
                            },
                            "server": {"url": f"{base_url}/vapi/tools/get_info"},
                        },
                        {
                            "name": "get_horarios",
                            "description": "Consultar horarios de apertura y turnos disponibles para una fecha específica. Úsala cuando el cliente pregunte qué días o horas abren, o quiera saber disponibilidad general.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "fecha": {
                                        "type": "string",
                                        "description": "Fecha en formato YYYY-MM-DD (opcional, si no se proporciona se asume hoy)",
                                    }
                                },
                                "required": [],
                            },
                            "server": {"url": f"{base_url}/vapi/tools/get_horarios"},
                        },
                        {
                            "name": "check_availability",
                            "description": "Verificar si hay mesa disponible para una fecha, hora y número de personas específicos. SIEMPRE usa esta función antes de confirmar una reserva. Si no hay disponibilidad, ofrece alternativas.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "date": {
                                        "type": "string",
                                        "description": "Fecha de la reserva en formato YYYY-MM-DD (ej: 2026-02-20)",
                                    },
                                    "time": {
                                        "type": "string",
                                        "description": "Hora de la reserva en formato HH:MM (ej: 21:00)",
                                    },
                                    "pax": {
                                        "type": "integer",
                                        "description": "Número de personas/comensales",
                                    },
                                },
                                "required": ["date", "time", "pax"],
                            },
                            "server": {
                                "url": f"{base_url}/vapi/tools/check_availability"
                            },
                        },
                        {
                            "name": "create_reservation",
                            "description": "Crear una nueva reserva en el sistema. SOLO usar después de verificar disponibilidad con check_availability. Necesita: nombre completo, teléfono, fecha, hora y número de personas.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "customer_name": {
                                        "type": "string",
                                        "description": "Nombre completo del cliente",
                                    },
                                    "phone": {
                                        "type": "string",
                                        "description": "Número de teléfono del cliente (para WhatsApp de confirmación)",
                                    },
                                    "date": {
                                        "type": "string",
                                        "description": "Fecha de la reserva en formato YYYY-MM-DD",
                                    },
                                    "time": {
                                        "type": "string",
                                        "description": "Hora de la reserva en formato HH:MM",
                                    },
                                    "pax": {
                                        "type": "integer",
                                        "description": "Número de comensales",
                                    },
                                    "notes": {
                                        "type": "string",
                                        "description": "Notas o peticiones especiales (alergias, tronas, celebraciones, etc.)",
                                    },
                                },
                                "required": [
                                    "customer_name",
                                    "phone",
                                    "date",
                                    "time",
                                    "pax",
                                ],
                            },
                            "server": {
                                "url": f"{base_url}/vapi/tools/create_reservation"
                            },
                        },
                    ],
                },
                "voice": {
                    "provider": "11labs",
                    "voiceId": "UOIqAnmS11Reiei1Ytkc",
                    "model": "eleven_multilingual_v2",
                },
                "firstMessage": "¡Hola! Soy Nube, de En Las Nubes Restobar en Logroño. ¿Quieres hacer una reserva o tienes alguna pregunta?",
                "transcriber": {
                    "provider": "deepgram",
                    "model": "nova-2",
                    "language": "es-ES",
                },
            }
        }
    except Exception as e:
        logger.error(f"Error generando configuración del asistente: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DISABLED: Duplicate tools - Better implementations in vapi_tools_router.py
# These routes are handled by vapi_tools_router with proper JSON string parsing.
# See: src/api/vapi_tools_router.py for check_availability and create_reservation
# ============================================================================

# @router.post("/tools/check_availability")
# async def tool_check_availability(request: Request):
#     """DISABLED - Use vapi_tools_router.py version instead"""
#     pass

# @router.post("/tools/create_reservation")
# async def tool_create_reservation(request: Request):
#     """DISABLED - Use vapi_tools_router.py version instead"""
#     pass


@router.post("/tools/cancel_reservation")
async def tool_cancel_reservation(request: Request):
    """
    Herramienta para CANCELAR una reserva existente por voz.

    Parámetros esperados del tool call:
    - telefono: Teléfono del cliente (para identificar la reserva)
    - motivo: Motivo de la cancelación (opcional)

    Returns:
        JSON con resultado para VAPI
    """
    try:
        body = await request.json()
        logger.info(f"Cancel Reservation Tool Call: {body}")

        message = body.get("message", {})
        tool_calls = message.get("toolCalls", [])

        if not tool_calls:
            return {
                "results": [
                    {"result": "No recibí información para cancelar. ¿Puedes repetir?"}
                ]
            }

        tool_call = tool_calls[0]
        params = tool_call.get("function", {}).get("arguments", {})

        # Obtener parámetros
        telefono = params.get("telefono", "").strip()
        motivo = params.get(
            "motivo", "Cancelación solicitada por el cliente vía telefónica"
        )

        if not telefono:
            return {
                "results": [
                    {
                        "toolCallId": tool_call["id"],
                        "result": "Necesito tu número de teléfono para buscar la reserva. ¿Cuál es tu número?",
                    }
                ]
            }

        # Importar cliente Airtable
        from src.infrastructure.mcp.airtable_client import airtable_client
        from src.api.mobile.airtable_helpers import (
            AIRTABLE_FIELD_MAP,
            build_airtable_filter,
        )
        from datetime import date

        AIRTABLE_BASE_ID = "appQ2ZXAR68cqDmJt"
        RESERVATIONS_TABLE_NAME = "Reservas"

        # Buscar reserva activa (Pendiente o Confirmada) del cliente para hoy o futuras
        filter_formula = f"AND({{{AIRTABLE_FIELD_MAP['telefono']}}}='{telefono}', IS_AFTER({{{AIRTABLE_FIELD_MAP['fecha']}}}, DATEADD(TODAY(), -1, 'days')), OR({{{AIRTABLE_FIELD_MAP['estado']}}}='Pendiente', {{{AIRTABLE_FIELD_MAP['estado']}}}='Confirmada'))"

        records_result = await airtable_client.list_records(
            base_id=AIRTABLE_BASE_ID,
            table_name=RESERVATIONS_TABLE_NAME,
            filterByFormula=filter_formula,
            max_records=5,
        )

        records = records_result.get("records", [])

        if not records:
            return {
                "results": [
                    {
                        "toolCallId": tool_call["id"],
                        "result": f"No encontré ninguna reserva activa con el teléfono {telefono}. ¿Estás seguro del número?",
                    }
                ]
            }

        # Si hay múltiples reservas, tomar la más próxima
        if len(records) > 1:
            # Ordenar por fecha (asumiendo que vienen ordenadas por Airtable)
            record_to_cancel = records[0]
            logger.warning(
                f"Multiple active reservations found for {telefono}, cancelling first one"
            )
        else:
            record_to_cancel = records[0]

        reservation_id = record_to_cancel["id"]
        fields = record_to_cancel.get("fields", {})
        nombre = fields.get(AIRTABLE_FIELD_MAP["nombre"], "Cliente")
        fecha = fields.get(AIRTABLE_FIELD_MAP["fecha"], "")
        hora = fields.get(AIRTABLE_FIELD_MAP["hora"], "")
        pax = fields.get(AIRTABLE_FIELD_MAP["pax"], "")

        # Actualizar reserva a Cancelada y liberar mesa
        update_fields = {
            AIRTABLE_FIELD_MAP["estado"]: "Cancelada",
            AIRTABLE_FIELD_MAP["mesa_asignada"]: [],  # Liberar mesa
        }

        # Agregar motivo en notas
        notas_actuales = fields.get(AIRTABLE_FIELD_MAP["notas"], "")
        motivo_completo = f"\n[CANCELACIÓN TELEFÓNICA] {motivo}"
        update_fields[AIRTABLE_FIELD_MAP["notas"]] = notas_actuales + motivo_completo

        # Actualizar en Airtable
        await airtable_client.update_record(
            base_id=AIRTABLE_BASE_ID,
            table_name=RESERVATIONS_TABLE_NAME,
            record_id=reservation_id,
            fields=update_fields,
        )

        logger.info(
            f"Reservation {reservation_id} cancelled via voice: {nombre}, {fecha} {hora}"
        )

        # Enviar confirmación por WhatsApp
        try:
            await twilio_service.send_whatsapp(
                to=telefono,
                message=f"Hola {nombre}, tu reserva para {fecha} a las {hora} ha sido cancelada. Si tienes dudas, contáctanos al 941 57 84 51. - En Las Nubes Resto Bar",
            )
        except Exception as e:
            logger.error(f"Error sending WhatsApp confirmation: {e}")

        # Broadcast WebSocket
        from src.api.websocket.connection_manager import manager

        await manager.broadcast_reservation_update(
            {
                "id": reservation_id,
                "estado": "Cancelada",
                "mesa_asignada": None,
                "cancelled_via": "voice",
                "motivo": motivo,
            },
            event_type="cancelled",
        )

        # Respuesta a VAPI para que se la diga al cliente
        respuesta_cliente = (
            f"Perfecto {nombre}, he cancelado tu reserva para el {fecha} a las {hora} "
            f"({pax} personas). Te enviaré una confirmación por WhatsApp. "
            f"Si cambias de opinión, llámanos al 941 57 84 51. ¡Hasta pronto!"
        )

        return {
            "results": [{"toolCallId": tool_call["id"], "result": respuesta_cliente}]
        }

    except Exception as e:
        logger.error(f"Error cancelling reservation: {str(e)}", exc_info=True)
        return {
            "results": [
                {
                    "toolCallId": tool_call.get("id"),
                    "result": "Lo siento, tuve un error al cancelar la reserva. ¿Podrías llamar directamente al restaurante? 941 57 84 51.",
                }
            ]
        }


@router.post("/tools/add_to_waitlist")
async def tool_add_to_waitlist(request: Request):
    """
    Herramienta para añadir un cliente a la lista de espera cuando no hay mesa disponible.

    Parámetros esperados (JSON en toolCall.function.arguments):
    - nombre: Nombre del cliente
    - telefono: Teléfono del cliente (formato E.164, ej: +34666123456)
    - fecha: Fecha deseada (YYYY-MM-DD)
    - hora: Hora deseada (HH:MM)
    - personas: Número de personas
    - zona_preferida: (Opcional) Interior/Terraza
    - notas: (Opcional) Notas adicionales
    """
    try:
        data = await request.json()
        message = data.get("message", {})
        tool_call = message.get("toolCalls", [])[0]
        args = tool_call.get("function", {}).get("arguments", {})

        logger.info(f"Adding to waitlist with args: {args}")

        # Extraer argumentos
        nombre = args.get("nombre")
        telefono = args.get("telefono")
        fecha_str = args.get("fecha")
        hora_str = args.get("hora")
        personas = args.get("personas")
        zona_preferida = args.get("zona_preferida")
        notas = args.get("notas", "")

        # Validación básica
        if not all([nombre, telefono, fecha_str, hora_str, personas]):
            return {
                "results": [
                    {
                        "toolCallId": tool_call["id"],
                        "result": "Me faltan algunos datos para apuntarte en la lista de espera. Necesito nombre, teléfono, fecha, hora y número de personas.",
                    }
                ]
            }

        # Parsear fecha y hora
        try:
            from datetime import datetime

            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            hora = datetime.strptime(hora_str, "%H:%M").time()
        except ValueError:
            return {
                "results": [
                    {
                        "toolCallId": tool_call["id"],
                        "result": "Formato de fecha u hora inválido. Usa YYYY-MM-DD y HH:MM.",
                    }
                ]
            }

        # Añadir a la waitlist
        try:
            entry = await waitlist_service.add_to_waitlist(
                nombre=nombre,
                telefono=telefono,
                fecha=fecha,
                hora=hora,
                pax=int(personas),
                zona_preferida=zona_preferida,
                notas=notas,
            )

            posicion_texto = (
                f"en la posición {entry.posicion}"
                if entry.posicion
                else "en nuestra lista"
            )

            respuesta_cliente = (
                f"¡Perfecto, {nombre}! Te he apuntado {posicion_texto} de espera para el {fecha_str} a las {hora_str} "
                f"para {personas} personas. Te avisaré por WhatsApp en cuanto se libere una mesa. "
                f"¿Hay algo más en lo que pueda ayudarte?"
            )

            logger.info(
                f"Cliente {nombre} añadido a waitlist: posición {entry.posicion}"
            )

            return {
                "results": [
                    {"toolCallId": tool_call["id"], "result": respuesta_cliente}
                ]
            }

        except Exception as e:
            logger.error(f"Error adding to waitlist: {e}", exc_info=True)
            return {
                "results": [
                    {
                        "toolCallId": tool_call["id"],
                        "result": (
                            "Lo siento, tuve un error al apuntarte en la lista de espera. "
                            "¿Podrías llamar directamente al restaurante? 941 57 84 51."
                        ),
                    }
                ]
            }

    except Exception as e:
        logger.error(f"Error in add_to_waitlist tool: {str(e)}", exc_info=True)
        return {
            "results": [
                {
                    "toolCallId": tool_call.get("id"),
                    "result": "Lo siento, tuve un error técnico. ¿Podrías llamar al restaurante? 941 57 84 51.",
                }
            ]
        }
