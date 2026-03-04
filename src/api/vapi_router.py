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
        content_type = request.headers.get("Content-Type", "")
        if "application/json" in content_type:
            data = await request.json()
            message = data.get("message", {})
            logger.info(f"Recibido evento JSON en webhook (VAPI). Tipo: {message.get('type')}")
            return {"status": "ok"}
            
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

SYSTEM_PROMPT_V3 = """
# CONTEXTO (IDENTITY)
Eres Nube, la recepcionista principal de 'En Las Nubes Restobar' en Logroño (España). 
Eres humana, cálida, empática y resolutiva. NUNCA menciones que eres una Inteligencia Artificial ni que usas herramientas, funciones o sistemas.

# ACCIÓN (GOALS & TONE)
Tu misión es gestionar las mesas del restaurante por teléfono con naturalidad humana ("¡Claro que sí!", "Déjame mirar...").
- Ritmo: Respuestas muy breves, directas y conversacionales para no saturar la llamada de voz.

# FORMATO (RULES & CONSTRAINTS)
1. HABLA Y ESCUCHA: Si el cliente te interrumpe, cállate e interrumpe tu habla inmediatamente.
2. NUEVAS RESERVAS: VERIFICA DISPONIBILIDAD PRIMERO. NUNCA confirmes mesa sin verificar. Si hay sitio, pide nombre completo y teléfono móvil, y crea la reserva advirtiendo que recibirán un WhatsApp en segundos.
3. LISTA DE ESPERA: Si solicitan mesa y estamos llenos, pide perdón cortésmente y OFRECE apuntarles a la lista de espera (necesitas nombre, teléfono y comensales).
4. CANCELACIONES: Si quieren cancelar, pide su número de teléfono.
5. RESTAURANTE: Especialidad CACHOPOS y cocina ALEMANA. Las comidas son 13:00-17:00 y las cenas 20:00-23:30. Lunes cerrado, martes/miércoles noches cerrado, domingo noche cerrado. Teléfono real: 941578451.
6. NOTAS/ALERGIAS: Pregunta siempre si traen carritos, sillas de ruedas, tronas o tienen alergias. Registra cualquier petición especial METICULOSAMENTE en el campo 'notas' al usar herramientas.
7. SIN GLUTEN: Los cachopos especiales Celiacos requieren pedirse o avisarse 24h antes por precaución cruzada.

# EJEMPLOS (FLUJO ESPERADO)
[Cliente]: Hola, quería reservar mesa para el viernes.
[Nube]: ¡Hola! Claro, para el viernes. ¿Para qué hora te vendría bien y cuántos seríais?
[Cliente]: A las diez de la noche, somos cuatro personas y un carrito de bebé.
[Nube]: Perfecto, déjame revisar la agenda un segundito...
(AQUÍ LLAMAS A LA HERRAMIENTA CHECK_AVAILABILITY)
[Nube]: ¡Qué suerte! Sí me queda una mesa. Para dejártela confirmada a tu nombre y que la tengan lista con hueco para el carrito, ¿me puedes dar tu nombre y un número de móvil?
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
        try:
            from datetime import datetime
            import pytz
            madrid_tz = pytz.timezone('Europe/Madrid')
            now_dt = datetime.now(madrid_tz)
        except:
            from datetime import datetime
            now_dt = datetime.now()
            
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        dia_semana = dias[now_dt.weekday()]
        mes = meses[now_dt.month - 1]
        fecha_str = f"{dia_semana}, {now_dt.day} de {mes} de {now_dt.year}"
        hora_str = now_dt.strftime("%H:%M")
        
        dynamic_system_prompt = f"[INFORMACIÓN DEL SISTEMA]\nLa fecha actual exacta es: {fecha_str}. La hora actual es: {hora_str}.\nUsa esta fecha como referencia MANDATORIA para calcular 'hoy', 'mañana' o los días de la semana de las reservas.\nBajo ningún concepto inventes fechas pasadas ni uses el año 2023, estamos en {now_dt.year}.\n\n" + SYSTEM_PROMPT_V3

        return {
            "assistant": {
                "model": {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "messages": [{"role": "system", "content": dynamic_system_prompt}],
                    "temperature": 0.7,
                    "functions": [
                        {
                            "name": "get_info",
                            "description": "Llama a esta herramienta SOLAMENTE CUANDO el cliente haga una pregunta explícita sobre información estática del restaurante (dirección, parking, tipo de comida, mascotas). NO la uses para ver disponibilidad.",
                            "parameters": {
                                "type": "object",
                                "properties": {},
                                "required": [],
                            },
                            "server": {"url": f"{base_url}/vapi/tools/get_info"},
                        },
                        {
                            "name": "get_horarios",
                            "description": "Llama a esta herramienta ÚNICAMENTE CUANDO el cliente quiera saber en qué horarios abrimos un día concreto, o pregunte genéricamente qué días cerramos.",
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
                            "description": "Llama a esta herramienta OBLIGATORIAMENTE CUANDO quieras comprobar si hay sitio para una nueva reserva. Ejecútala EXCLUSIVAMENTE DESPUÉS de haber obtenido la fecha, hora exacta y número de personas. JAMÁS CREES UNA RESERVA SIN LLAMAR PREVIAMENTE A ESTA HERRAMIENTA.",
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
                            "description": "Llama a esta herramienta ESTRICTAMENTE DESPUÉS de haber comprobado sitio con 'check_availability' Y ÚNICAMENTE DESPUÉS de haber recabado el nombre completo y teléfono del cliente. Confirma siempre sus alergias/notas.",
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
                        {
                            "name": "add_to_waitlist",
                            "description": "Llama a esta herramienta CUANDO el restaurante esté lleno (te lo dirá un check previo) Y el cliente ACEPTE explícitamente ser apuntado a la lista de reserva/espera. Necesitarás su teléfono.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "nombre": {"type": "string"},
                                    "telefono": {"type": "string"},
                                    "fecha": {"type": "string", "description": "YYYY-MM-DD"},
                                    "hora": {"type": "string", "description": "HH:MM"},
                                    "personas": {"type": "integer"},
                                    "notas": {"type": "string", "description": "Alergias o requerimientos (opcional)"},
                                },
                                "required": ["nombre", "telefono", "fecha", "hora", "personas"],
                            },
                            "server": {
                                "url": f"{base_url}/vapi/tools/add_to_waitlist"
                            },
                        },
                        {
                            "name": "cancel_reservation",
                            "description": "Llama a esta herramienta SOLAMENTE CUANDO el cliente pida firmemente cancelar su reserva DEBES HABERLE PEDIDO SU NÚMERO DE TELÉFONO ANTES de invocarla.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "telefono": {"type": "string", "description": "Teléfono del cliente"},
                                    "motivo": {"type": "string", "description": "Razón de cancelación por parte del cliente (opcional)"},
                                },
                                "required": ["telefono"],
                            },
                            "server": {
                                "url": f"{base_url}/vapi/tools/cancel_reservation"
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
                "silenceTimeoutSeconds": 30,
                "maxDurationSeconds": 600,
                "voicemailDetection": {
                    "provider": "twilio",
                },
                "backgroundSound": "office"
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
                    {"result": "No te he escuchado bien, ¿podrías repetirme qué querías cancelar?"}
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
                        "result": "Para poder cancelarla, necesito buscar tu reserva. ¿Me dices tu número de teléfono por favor?",
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
                        "result": f"Pues he estado mirando y no encuentro ninguna reserva activa a nombre de ese teléfono. ¿Seguro que es con el que reservaste?",
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
            f"Listo {nombre}, acabo de cancelar tu reserva. "
            f"Te llegará un mensaje por WhatsApp ahora mismo confirmando la anulación. "
            f"¡Esperamos verte en En Las Nubes en otra ocasión!"
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
                    "result": "Madre mía, qué desastre, se me ha quedado pillado el sistema y no puedo cancelarla. ¿Te importa aguantar un segundo en línea o llamar a mis compañeros al 941 57 84 51 para que te la borren a mano?",
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
                f"¡Estupendo, {nombre}! Ya te he apuntado {posicion_texto} de espera. "
                f"En cuanto se quede una mesa libre te avisaremos volando por WhatsApp. ¡Muchas gracias por tu paciencia!"
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
                            "Ay, perdona, está el ordenador un poco tonto hoy y no me deja guardarte en la lista. "
                            "¿Te importaría llamar en cinco minutitos para que te apunten mis compañeros a mano en el 941 57 84 51?"
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
                    "result": "Madre mía, qué desastre, el sistema no me deja guardar nada ahora. Llama a mis compañeros al 941 57 84 51, por favor.",
                }
            ]
        }
