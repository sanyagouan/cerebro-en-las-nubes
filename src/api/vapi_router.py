from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any, Optional
import os
from datetime import datetime
from loguru import logger

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
from src.application.services.reservation_service import ReservationService
# from src.api.middleware.rate_limiting import webhook_limit  # TODO: Re-enable after fixing slowapi

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
2. NUEVAS RESERVAS: VERIFICA DISPONIBILIDAD PRIMERO. NUNCA confirmes mesa sin verificar. Si hay sitio, pide nombre completo y teléfono, y crea la reserva.
3. LISTA DE ESPERA: Si solicitan mesa y estamos llenos, pide perdón cortésmente y OFRECE apuntarles a la lista de espera (necesitas nombre, teléfono y comensales).
4. CANCELACIONES: Si quieren cancelar, pide su número de teléfono.
5. RESTAURANTE: Especialidad CACHOPOS y cocina ALEMANA. Las comidas son 13:00-17:00 y las cenas 20:00-23:30. Lunes cerrado, martes/miércoles noches cerrado, domingo noche cerrado. Teléfono real: 941578451.
6. NOTAS/ALERGIAS: Pregunta siempre si traen carritos, sillas de ruedas, tronas o tienen alergias. Registra cualquier petición especial METICULOSAMENTE en el campo 'notas' al usar herramientas.
7. SIN GLUTEN: Los cachopos especiales Celiacos requieren pedirse o avisarse 24h antes por precaución cruzada.

# DETECCIÓN DE TIPO DE TELÉFONO Y CONFIRMACIÓN
El sistema te proporciona el número del cliente. Debes detectar si es móvil o fijo para ajustar el flujo de confirmación:

## CÓMO DETECTAR EL TIPO:
- Si el teléfono empieza por +346 o +347 → ES MÓVIL (puede recibir WhatsApp)
- Si el teléfono empieza por +349 → ES FIJO (NO puede recibir WhatsApp, necesita confirmación verbal)
- Otros prefijos → Tratar como móvil por defecto

## FLUJO PARA MÓVIL (+346XX, +347XX):
Después de crear la reserva con `create_reservation`, di:
"¡Perfecto [NOMBRE]! Te he reservado la mesa para [N] personas el [FECHA] a las [HORA].
Te voy a enviar un WhatsApp a este número para que confirmes. Responde SÍ o NO al mensaje."
→ NO pedir confirmación verbal. El sistema enviará WhatsApp automáticamente.

## FLUJO PARA FIJO (+349XX) - CONFIRMACIÓN VERBAL INMEDIATA:
Después de crear la reserva con `create_reservation`, di:
"¡Perfecto [NOMBRE]! Te he reservado la mesa para [N] personas el [FECHA] a las [HORA].
Como me llamas desde un teléfono fijo, te confirmo ahora mismo verbalmente, ¿de acuerdo?
¿Confirmas que vendréis?"

ESPERA LA RESPUESTA DEL CLIENTE Y ACTÚA:
- Si dice "SÍ", "VALE", "DE ACUERDO", "CLARO", "CONFIRMO" → LLAMA a `confirm_verbal` con confirmed=true
- Si dice "NO", duda, pide tiempo para pensarlo, o no responde claramente → LLAMA a `confirm_verbal` con confirmed=false

## CUÁNDO USAR LA TOOL confirm_verbal:
- SOLO cuando el cliente llama desde FIJO (+349XX)
- SOLO después de crear la reserva con `create_reservation`
- SOLO después de preguntar "¿Confirmas que vendréis?" y recibir respuesta

## RESPUESTAS DESPUÉS DE confirm_verbal:
- Si confirmed=true: "¡Genial! Tu reserva está confirmada. Nos vemos el [FECHA]. ¡Hasta luego!"
- Si confirmed=false: "Entendido. He cancelado la reserva. Si cambias de opinión, llámanos de nuevo al 941578451. ¡Hasta otra!"

# EJEMPLOS DE DIÁLOGO

## Ejemplo 1: Cliente con Móvil (+346XX)
[Teléfono cliente: +34678123456]
Cliente: "Hola, quería reservar mesa para el viernes."
Nube: "¡Hola! Claro, para el viernes. ¿Para qué hora te vendría bien y cuántos seríais?"
Cliente: "A las diez de la noche, somos cuatro personas y un carrito de bebé."
Nube: "Perfecto, déjame revisar la agenda un segundito..."
[LLAMA check_availability]
Nube: "¡Qué suerte! Sí me queda una mesa. ¿Me das tu nombre completo y número de teléfono?"
Cliente: "María García, 678123456"
Nube: [LLAMA create_reservation]
"¡Perfecto María! Te he reservado la mesa. Te voy a enviar un WhatsApp para que confirmes. Responde SÍ o NO. ¿Hay algo más?"

## Ejemplo 2: Cliente con Fijo (+349XX) - Confirma
[Teléfono cliente: +34941234567]
Cliente: "Quiero reservar para 2 personas el viernes a las 2"
Nube: "¡Hola! Para el viernes a las 14:00 para 2 personas. Déjame comprobar..."
[LLAMA check_availability]
Nube: "¡Tengo mesa disponible! ¿Me das tu nombre completo?"
Cliente: "Juan Martínez"
Nube: [LLAMA create_reservation]
"¡Listo Juan! Te he reservado la mesa para 2 personas el viernes a las 14:00.
Como me llamas desde un fijo, te confirmo ahora verbalmente, ¿de acuerdo?
¿Confirmas que vendréis?"
Cliente: "Sí, confirmo"
Nube: [LLAMA confirm_verbal con phone=+34941234567, confirmed=true]
"¡Genial! Tu reserva está confirmada. Te esperamos el viernes a las 14:00. ¡Hasta luego!"

## Ejemplo 3: Cliente con Fijo (+349XX) - No confirma
[Teléfono cliente: +34941234567]
Nube: [Tras crear la reserva]
"¡Listo! Te he apuntado la mesa. Como es un fijo, ¿confirmas ahora mismo?"
Cliente: "Lo tengo que consultar con mi mujer"
Nube: [LLAMA confirm_verbal con phone=+34941234567, confirmed=false]
"Entendido. He cancelado la reserva temporal. Cuando lo decidáis, llamadme de nuevo. ¡Gracias!"
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
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "system", "content": dynamic_system_prompt}],
                    "temperature": 0.3,
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
                            "name": "get_reservation",
                            "description": "Llama a esta herramienta CUANDO el cliente quiera consultar/buscar su reserva existente. Necesitas su número de teléfono.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "phone": {"type": "string", "description": "Teléfono del cliente para buscar su reserva"},
                                },
                                "required": ["phone"],
                            },
                            "server": {
                                "url": f"{base_url}/vapi/tools/get_reservation"
                            },
                        },
                        {
                            "name": "update_reservation",
                            "description": "Llama a esta herramienta CUANDO el cliente quiera modificar su reserva (cambiar fecha, hora o número de personas). Necesitas su teléfono y al menos un campo a modificar.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "phone": {"type": "string", "description": "Teléfono del cliente"},
                                    "new_date": {"type": "string", "description": "Nueva fecha en formato YYYY-MM-DD (opcional)"},
                                    "new_time": {"type": "string", "description": "Nueva hora en formato HH:MM (opcional)"},
                                    "new_guests": {"type": "integer", "description": "Nuevo número de personas (opcional)"},
                                },
                                "required": ["phone"],
                            },
                            "server": {
                                "url": f"{base_url}/vapi/tools/update_reservation"
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
                        {
                            "name": "confirm_verbal",
                            "description": "Llama a esta herramienta ÚNICAMENTE cuando el cliente llame desde un TELÉFONO FIJO (prefijo +349XX) y hayas preguntado si confirma la reserva. USA confirmed=true si el cliente dijo SÍ, VALE, DE ACUERDO o CONFIRMO. USA confirmed=false si dijo NO, dudó o pidió tiempo para pensarlo. JAMÁS uses esta herramienta para teléfonos móviles (+346XX, +347XX).",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "phone": {
                                        "type": "string",
                                        "description": "Número de teléfono del cliente en formato E.164 (ej: +34941234567)",
                                    },
                                    "confirmed": {
                                        "type": "boolean",
                                        "description": "true si el cliente confirmó verbalmente, false si declinó o dudó",
                                    },
                                },
                                "required": ["phone", "confirmed"],
                            },
                            "server": {
                                "url": f"{base_url}/vapi/tools/confirm_verbal"
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


@router.post("/tools/get_reservation")
async def tool_get_reservation(request: Request):
    """
    Herramienta para BUSCAR una reserva existente por teléfono.

    Parámetros esperados del tool call:
    - phone: Teléfono del cliente (para identificar la reserva)

    Returns:
        JSON con resultado para VAPI
    """
    try:
        body = await request.json()
        logger.info(f"Get Reservation Tool Call: {body}")

        message = body.get("message", {})
        tool_calls = message.get("toolCalls", [])

        if not tool_calls:
            return {
                "results": [
                    {"result": "No te he escuchado bien, ¿podrías repetirme tu número de teléfono?"}
                ]
            }

        tool_call = tool_calls[0]
        params = tool_call.get("function", {}).get("arguments", {})

        # Obtener parámetro
        phone = params.get("phone", "").strip()

        if not phone:
            return {
                "results": [
                    {
                        "toolCallId": tool_call["id"],
                        "result": "Para buscar tu reserva, necesito que me digas tu número de teléfono, por favor.",
                    }
                ]
            }

        # Importar cliente Airtable
        from src.infrastructure.mcp.airtable_client import airtable_client
        from src.api.mobile.airtable_helpers import AIRTABLE_FIELD_MAP
        from datetime import date

        AIRTABLE_BASE_ID = "appQ2ZXAR68cqDmJt"
        RESERVATIONS_TABLE_NAME = "Reservas"

        # Buscar reserva activa (Pendiente o Confirmada) del cliente para hoy o futuras
        filter_formula = f"AND({{{AIRTABLE_FIELD_MAP['telefono']}}}='{phone}', IS_AFTER({{{AIRTABLE_FIELD_MAP['fecha']}}}, DATEADD(TODAY(), -1, 'days')), OR({{{AIRTABLE_FIELD_MAP['estado']}}}='Pendiente', {{{AIRTABLE_FIELD_MAP['estado']}}}='Confirmada'))"

        records_result = await airtable_client.list_records(
            base_id=AIRTABLE_BASE_ID,
            table_name=RESERVATIONS_TABLE_NAME,
            filterByFormula=filter_formula,
            sort=[{AIRTABLE_FIELD_MAP['fecha']: 'desc'}],
            max_records=1,
        )

        records = records_result.get("records", [])

        if not records:
            return {
                "results": [
                    {
                        "toolCallId": tool_call["id"],
                        "result": f"Pues he estado mirando y no encuentro ninguna reserva activa con ese teléfono. ¿Seguro que es el número correcto?",
                    }
                ]
            }

        # Obtener la reserva más reciente
        record = records[0]
        reservation_id = record["id"]
        fields = record.get("fields", {})
        
        nombre = fields.get(AIRTABLE_FIELD_MAP["nombre"], "Cliente")
        fecha = fields.get(AIRTABLE_FIELD_MAP["fecha"], "")
        hora = fields.get(AIRTABLE_FIELD_MAP["hora"], "")
        pax = fields.get(AIRTABLE_FIELD_MAP["pax"], "")
        estado = fields.get(AIRTABLE_FIELD_MAP["estado"], "")
        mesa_asignada = fields.get(AIRTABLE_FIELD_MAP["mesa_asignada"], [])
        
        # Formatear mesa
        mesa_str = mesa_asignada[0] if isinstance(mesa_asignada, list) and mesa_asignada else "Sin asignar"

        logger.info(
            f"Reservation found: {reservation_id} - {nombre}, {fecha} {hora}"
        )

        # Respuesta a VAPI para que se la diga al cliente
        respuesta_cliente = (
            f"¡Sí! Aquí está tu reserva {nombre}: "
            f"es para {pax} personas el día {fecha} a las {hora}. "
            f"Estado: {estado}."
        )
        
        if mesa_str != "Sin asignar":
            respuesta_cliente += f" Mesa asignada: {mesa_str}."

        return {
            "results": [{"toolCallId": tool_call["id"], "result": respuesta_cliente}]
        }

    except Exception as e:
        logger.error(f"Error getting reservation: {str(e)}")
        return {
            "results": [
                {
                    "toolCallId": tool_call.get("id"),
                    "result": "Ay, perdona, se me ha quedado pillado el sistema buscando tu reserva. ¿Puedes llamar a mis compañeros al 941 57 84 51 para que te la consulten?",
                }
            ]
        }


@router.post("/tools/update_reservation")
async def tool_update_reservation(request: Request):
    """
    Herramienta para ACTUALIZAR una reserva existente (fecha, hora o número de personas).

    Parámetros esperados del tool call:
    - phone: Teléfono del cliente (obligatorio)
    - new_date: Nueva fecha en formato YYYY-MM-DD (opcional)
    - new_time: Nueva hora en formato HH:MM (opcional)
    - new_guests: Nuevo número de personas (opcional)

    Returns:
        JSON con resultado para VAPI
    """
    try:
        body = await request.json()
        logger.info(f"Update Reservation Tool Call: {body}")

        message = body.get("message", {})
        tool_calls = message.get("toolCalls", [])

        if not tool_calls:
            return {
                "results": [
                    {"result": "No te he escuchado bien, ¿qué querías cambiar de tu reserva?"}
                ]
            }

        tool_call = tool_calls[0]
        params = tool_call.get("function", {}).get("arguments", {})

        # Obtener parámetros
        phone = params.get("phone", "").strip()
        new_date = params.get("new_date", "").strip()
        new_time = params.get("new_time", "").strip()
        new_guests = params.get("new_guests")

        if not phone:
            return {
                "results": [
                    {
                        "toolCallId": tool_call["id"],
                        "result": "Para modificar tu reserva, necesito tu número de teléfono por favor.",
                    }
                ]
            }

        # Validar que al menos un campo a actualizar esté presente
        if not any([new_date, new_time, new_guests]):
            return {
                "results": [
                    {
                        "toolCallId": tool_call["id"],
                        "result": "Dime qué quieres cambiar: ¿la fecha, la hora o el número de personas?",
                    }
                ]
            }

        # Importar cliente Airtable
        from src.infrastructure.mcp.airtable_client import airtable_client
        from src.api.mobile.airtable_helpers import AIRTABLE_FIELD_MAP
        from datetime import date, datetime

        AIRTABLE_BASE_ID = "appQ2ZXAR68cqDmJt"
        RESERVATIONS_TABLE_NAME = "Reservas"

        # Buscar reserva activa
        filter_formula = f"AND({{{AIRTABLE_FIELD_MAP['telefono']}}}='{phone}', IS_AFTER({{{AIRTABLE_FIELD_MAP['fecha']}}}, DATEADD(TODAY(), -1, 'days')), OR({{{AIRTABLE_FIELD_MAP['estado']}}}='Pendiente', {{{AIRTABLE_FIELD_MAP['estado']}}}='Confirmada'))"

        records_result = await airtable_client.list_records(
            base_id=AIRTABLE_BASE_ID,
            table_name=RESERVATIONS_TABLE_NAME,
            filterByFormula=filter_formula,
            max_records=1,
        )

        records = records_result.get("records", [])

        if not records:
            return {
                "results": [
                    {
                        "toolCallId": tool_call["id"],
                        "result": f"No encuentro ninguna reserva activa con ese teléfono. ¿Seguro que tienes una reserva con nosotros?",
                    }
                ]
            }

        # Obtener la reserva
        record = records[0]
        reservation_id = record["id"]
        fields = record.get("fields", {})
        
        nombre = fields.get(AIRTABLE_FIELD_MAP["nombre"], "Cliente")
        current_date = fields.get(AIRTABLE_FIELD_MAP["fecha"], "")
        current_time = fields.get(AIRTABLE_FIELD_MAP["hora"], "")
        current_pax = fields.get(AIRTABLE_FIELD_MAP["pax"], 0)

        # Preparar campos a actualizar
        update_fields = {}
        cambios_realizados = []

        # Actualizar fecha
        if new_date:
            try:
                # Validar formato de fecha
                datetime.strptime(new_date, "%Y-%m-%d")
                update_fields[AIRTABLE_FIELD_MAP["fecha"]] = new_date
                cambios_realizados.append(f"fecha a {new_date}")
            except ValueError:
                return {
                    "results": [
                        {
                            "toolCallId": tool_call["id"],
                            "result": "El formato de fecha no es válido. Necesito algo como 2026-03-20.",
                        }
                    ]
                }

        # Actualizar hora
        if new_time:
            try:
                # Validar formato de hora
                datetime.strptime(new_time, "%H:%M")
                # Airtable espera formato completo con fecha si es DateTime
                # Usar la fecha actual o la nueva si se proporcionó
                fecha_base = new_date if new_date else current_date
                datetime_str = f"{fecha_base}T{new_time}:00.000Z"
                update_fields[AIRTABLE_FIELD_MAP["hora"]] = datetime_str
                cambios_realizados.append(f"hora a {new_time}")
            except ValueError:
                return {
                    "results": [
                        {
                            "toolCallId": tool_call["id"],
                            "result": "El formato de hora no es válido. Necesito algo como 21:00.",
                        }
                    ]
                }

        # Actualizar número de personas
        if new_guests:
            try:
                guests_int = int(new_guests)
                if guests_int < 1 or guests_int > 20:
                    return {
                        "results": [
                            {
                                "toolCallId": tool_call["id"],
                                "result": "El número de personas debe estar entre 1 y 20. Para grupos mayores necesito que hables con mis compañeros.",
                            }
                        ]
                    }
                update_fields[AIRTABLE_FIELD_MAP["pax"]] = guests_int
                cambios_realizados.append(f"personas a {guests_int}")
            except ValueError:
                return {
                    "results": [
                        {
                            "toolCallId": tool_call["id"],
                            "result": "El número de personas no es válido.",
                        }
                    ]
                }

        # TODO: Verificar disponibilidad para los nuevos valores
        # Por ahora actualizamos directamente, pero en producción deberíamos
        # llamar al servicio de disponibilidad

        # Actualizar en Airtable
        await airtable_client.update_record(
            base_id=AIRTABLE_BASE_ID,
            table_name=RESERVATIONS_TABLE_NAME,
            record_id=reservation_id,
            fields=update_fields,
        )

        logger.info(
            f"Reservation {reservation_id} updated: {', '.join(cambios_realizados)}"
        )

        # Enviar confirmación por WhatsApp usando plantilla Content API
        try:
            from src.infrastructure.templates.content_sids import RESERVA_CONFIRMACION_NUBES_SID
            
            # Formatear fecha para la plantilla
            fecha_formateada = new_date if new_date else current_date
            hora_formateada = new_time if new_time else current_time
            
            # Variables para la plantilla de confirmación (reutilizada para modificaciones)
            variables = {
                "1": nombre,
                "2": str(guests_int if new_guests else current_pax),
                "3": fecha_formateada,
                "4": hora_formateada
            }
            
            await twilio_service.send_whatsapp_template(
                to_number=phone,
                template_sid=RESERVA_CONFIRMACION_NUBES_SID,
                variables=variables
            )
            logger.info(f"WhatsApp modificación enviado a {phone} usando plantilla")
        except Exception as e:
            logger.error(f"Error sending WhatsApp confirmation: {e}")

        # Broadcast WebSocket
        from src.api.websocket.connection_manager import manager

        await manager.broadcast_reservation_update(
            {
                "id": reservation_id,
                "updated_fields": list(update_fields.keys()),
                "updated_via": "voice",
            },
            event_type="updated",
        )

        # Respuesta a VAPI
        respuesta_cliente = (
            f"¡Perfecto {nombre}! Ya he actualizado tu reserva. "
            f"He cambiado: {', '.join(cambios_realizados)}. "
            f"Te llegará un WhatsApp confirmando los cambios."
        )

        return {
            "results": [{"toolCallId": tool_call["id"], "result": respuesta_cliente}]
        }

    except Exception as e:
        logger.error(f"Error updating reservation: {str(e)}")
        return {
            "results": [
                {
                    "toolCallId": tool_call.get("id"),
                    "result": "Ay, perdona, el sistema no me deja modificar la reserva ahora. ¿Puedes llamar a mis compañeros al 941 57 84 51 para que te la cambien?",
                }
            ]
        }


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

        # Enviar confirmación por WhatsApp usando plantilla Content API
        try:
            from src.infrastructure.templates.content_sids import RESERVA_CANCELADA_NUBES_SID
            
            # Variables para la plantilla de cancelación
            variables = {
                "1": nombre,
                "2": fecha,
                "3": hora
            }
            
            await twilio_service.send_whatsapp_template(
                to_number=telefono,
                template_sid=RESERVA_CANCELADA_NUBES_SID,
                variables=variables
            )
            logger.info(f"WhatsApp cancelación enviado a {telefono} usando plantilla")
        except Exception as e:
            logger.error(f"Error sending WhatsApp cancellation: {e}")

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
        logger.error(f"Error cancelling reservation: {str(e)}")
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
            logger.error(f"Error adding to waitlist: {e}")
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
        logger.error(f"Error in add_to_waitlist tool: {str(e)}")
        return {
            "results": [
                {
                    "toolCallId": tool_call.get("id"),
                    "result": "Madre mía, qué desastre, el sistema no me deja guardar nada ahora. Llama a mis compañeros al 941 57 84 51, por favor.",
                }
            ]
        }


@router.post("/tools/confirm_verbal")
async def tool_confirm_verbal(request: Request):
    """
    Her CONFIRMAR VERBALMENTE una reserva durante la llamada (teléfonos fijos).
    
    Este endpoint se invoca cuando el cliente llama desde un teléfono fijo y debe confirmar
    inmediatamente durante la llamada, ya que no puede recibir WhatsApp.
    
    Parámetros esperados del tool call:
    - phone: Teléfono del cliente (obligatorio)
    - confirmed: Boolean - True si cliente confirmó verbalmente, False si declinó
    
    Returns:
        JSON con resultado para VAPI
    """
    try:
        body = await request.json()
        logger.info(f"Confirm Verbal Tool Call: {body}")
        
        message = body.get("message", {})
        tool_calls = message.get("toolCalls", [])
        
        if not tool_calls:
            return {
                "results": [
                    {"result": "No te he escuchado bien, ¿confirmas tu reserva o no?"}
                ]
            }
        
        tool_call = tool_calls[0]
        params = tool_call.get("function", {}).get("arguments", {})
        
        # Obtener parámetros
        phone = params.get("phone", "").strip()
        confirmed = params.get("confirmed")
        
        # Validaciones
        if not phone:
            return {
                "results": [
                    {
                        "toolCallId": tool_call["id"],
                        "result": "Para confirmar tu reserva, necesito que me digas tu número de teléfono por favor.",
                    }
                ]
            }
        
        if confirmed is None:
            return {
                "results": [
                    {
                        "toolCallId": tool_call["id"],
                        "result": "No he entendido bien, ¿CONFIRMAS la reserva o prefieres cancelarla? Por favor, responde SÍ o NO.",
                    }
                ]
            }
        
        # Usar ReservationService para confirmar o cancelar
        reservation_service = ReservationService()
        
        result = await reservation_service.confirm_verbal(phone, confirmed)
        
        if not result.get("success"):
            # Error al procesar
            error_msg = result.get("error", "Error desconocido")
            logger.error(f"Error in confirm_verbal: {error_msg}")
            
            return {
                "results": [
                    {
                        "toolCallId": tool_call["id"],
                        "result": "Ay, perdona, el sistema no me deja actualizar la reserva. ¿Puedes llamar a mis compañeros al 941 57 84 51 para confirmarlo directamente?",
                    }
                ]
            }
        
        # Éxito - diferenciar respuesta según confirmación o cancelación
        if confirmed:
            # Cliente CONFIRMÓ
            reservation_id = result.get("reservation_id", "")
            
            logger.info(
                f"Reservation {reservation_id} confirmed verbally by phone {phone}"
            )
            
            # Broadcast WebSocket
            from src.api.websocket.connection_manager import manager
            
            await manager.broadcast_reservation_update(
                {
                    "id": reservation_id,
                    "estado": "Confirmada",
                    "tipo_confirmacion": "verbal",
                    "confirmed_via": "voice",
                },
                event_type="confirmed",
            )
            
            respuesta_cliente = (
                "¡Perfecto! Tu reserva está confirmada. "
                "Te esperamos en En Las Nubes Restobar. ¡Hasta pronto!"
            )
        
        else:
            # Cliente DECLINÓ - reserva cancelada
            reservation_id = result.get("reservation_id", "")
            
            logger.info(
                f"Reservation {reservation_id} declined verbally by phone {phone}"
            )
            
            # Broadcast WebSocket
            from src.api.websocket.connection_manager import manager
            
            await manager.broadcast_reservation_update(
                {
                    "id": reservation_id,
                    "estado": "Cancelada",
                    "cancelled_via": "voice",
                    "reason": "Cliente no confirmó verbalmente durante la llamada"
                },
                event_type="cancelled",
            )
            
            respuesta_cliente = (
                "Vale, entendido. La reserva ha sido cancelada. "
                "Si cambias de opinión, llámanos al 941 57 84 51. ¡Hasta otra!"
            )
        
        return {
            "results": [
                {
                    "toolCallId": tool_call["id"],
                    "result": respuesta_cliente
                }
            ]
        }
    
    except Exception as e:
        logger.error(f"Error in confirm_verbal tool: {str(e)}")
        return {
            "results": [
                {
                    "toolCallId": tool_call.get("id"),
                    "result": "Madre mía, qué desastre, el sistema no me deja guardar nada ahora. Llama a mis compañeros al 941 57 84 51, por favor.",
                }
            ]
        }
