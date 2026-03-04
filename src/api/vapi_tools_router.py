"""
VAPI Tools Router - Endpoints para tools de VAPI.
Apunta a /vapi/tools/* (no /vapi/webhook que es solo para Twilio)
v2.0 - Versión limpia y corregida
"""

from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any, Optional, List
from datetime import datetime, date, timedelta
import logging
import json

from src.application.services.schedule_service import (
    ScheduleService,
    Servicio,
    get_schedule_service,
)
from src.infrastructure.repositories.table_repository import (
    TableRepository,
    table_repository,
)
from src.infrastructure.external.airtable_service import AirtableService
from src.infrastructure.cache.redis_cache import get_cache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vapi/tools", tags=["VAPI Tools"])

# Lazy-loaded services
_schedule_service = None
_airtable_service = None
_cache = None


def get_schedule_service_lazy():
    """Lazy load schedule service."""
    global _schedule_service
    if _schedule_service is None:
        from src.application.services.schedule_service import get_schedule_service

        _schedule_service = get_schedule_service()
    return _schedule_service


def get_airtable_service_lazy():
    """Lazy load airtable service."""
    global _airtable_service
    if _airtable_service is None:
        from src.infrastructure.external.airtable_service import AirtableService

        _airtable_service = AirtableService()
    return _airtable_service


def get_cache_lazy():
    """Lazy load cache."""
    global _cache
    if _cache is None:
        from src.infrastructure.cache.redis_cache import get_cache

        _cache = get_cache()
    return _cache


def parse_vapi_request(data: dict) -> tuple:
    """
    Parsea el request completo de VAPI y extrae tool_call_id y argumentos.

    VAPI puede enviar en diferentes formatos:
    1. message.toolCalls[0].function.arguments (string JSON o dict)
    2. message.toolCallList[0].arguments (dict directo)
    3. message.toolWithToolCallList[0].toolCall.function.arguments

    Returns:
        tuple: (tool_call_id, args_dict)
    """
    message = data.get("message", {})
    tool_call_id = "unknown"
    args = {}

    # Formato 1: toolCalls con function.arguments
    tool_calls = message.get("toolCalls", [])
    if tool_calls:
        tc = tool_calls[0]
        tool_call_id = tc.get("id", "unknown")
        func = tc.get("function", {})
        args_raw = func.get("arguments", {})

        if isinstance(args_raw, str):
            try:
                args = json.loads(args_raw)
            except json.JSONDecodeError:
                args = {}
        elif isinstance(args_raw, dict):
            args = args_raw

    # Formato 2: toolCallList con arguments directo
    elif message.get("toolCallList"):
        tc = message["toolCallList"][0]
        tool_call_id = tc.get("id", "unknown")
        args_raw = tc.get("arguments", {})

        if isinstance(args_raw, str):
            try:
                args = json.loads(args_raw)
            except json.JSONDecodeError:
                args = {}
        elif isinstance(args_raw, dict):
            args = args_raw

    # Formato 3: toolWithToolCallList
    elif message.get("toolWithToolCallList"):
        twtc = message["toolWithToolCallList"][0]
        tc = twtc.get("toolCall", {})
        tool_call_id = tc.get("id", "unknown")
        func = tc.get("function", {})
        args_raw = func.get("arguments", {})

        if isinstance(args_raw, str):
            try:
                args = json.loads(args_raw)
            except json.JSONDecodeError:
                args = {}
        elif isinstance(args_raw, dict):
            args = args_raw

    logger.info(f"parse_vapi_request: tool_call_id={tool_call_id}, args={args}")
    return tool_call_id, args


def parse_vapi_args(tool_call: dict) -> dict:
    """
    Parsea los arguments de una VAPI tool call.
    VAPI puede enviar arguments como string JSON o como dict.
    """
    args = tool_call.get("function", {}).get("arguments", {})

    # Si es string, parsear como JSON
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            args = {}

    return args if isinstance(args, dict) else {}


@router.post("/get_info")
async def tool_get_info(request: Request):
    """
    Tool: Obtener información del restaurante.
    VAPI llama esto cuando necesita info dinámica.
    """
    try:
        data = await request.json()
        tool_call_id, args = parse_vapi_request(data)

        info = {
            "nombre": "En Las Nubes Restobar",
            "direccion": "María Teresa Gil de Gárate 16, Logroño",
            "telefono": "941 57 84 51",
            "parking": "Calle Pérez Galdós, República Argentina, o Parking Gran Vía",
            "nota_ubicacion": "La calle es peatonal, no se puede aparcar en la puerta",
            "especialidad": "Cachopos y cocina alemana (salchichas, codillo)",
            "sin_gluten": "Amplia carta sin gluten disponible",
            "mascotas": "Solo permitidas en terraza",
        }

        return {
            "results": [
                {
                    "toolCallId": tool_call_id,
                    "result": f"""INFORMACIÓN DEL RESTAURANTE:
- Nombre: {info["nombre"]}
- Dirección: {info["direccion"]} ({info["nota_ubicacion"]})
- Parking: {info["parking"]}
- Teléfono: {info["telefono"]}
- Especialidad: {info["especialidad"]}
- Carta sin gluten: {info["sin_gluten"]}
- Mascotas: {info["mascotas"]}""",
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error in get_info: {e}")
        tc_id = tool_call_id if 'tool_call_id' in locals() else "unknown"
        return {
            "results": [
                {"toolCallId": tc_id, "result": "Perdóname, se me ha cortado un poco el sistema. ¿Me explicabas?"}
            ]
        }


@router.post("/get_horarios")
async def tool_get_horarios(request: Request):
    """
    Tool: Obtener horarios disponibles para una fecha.
    Consulta Airtable y ScheduleService para info dinámica.
    """
    try:
        data = await request.json()
        tool_call_id, args = parse_vapi_request(data)

        # Aceptar ambos formatos de parámetro
        fecha_str = args.get("fecha")  # YYYY-MM-DD o null para hoy

        if fecha_str:
            try:
                # Relajar el formato cortando lo que pase de 10 chars (ej: 2026-03-05T00:00:00)
                fecha = datetime.strptime(fecha_str[:10], "%Y-%m-%d").date()
            except Exception:
                return {
                    "results": [
                        {
                            "toolCallId": tool_call_id,
                            "result": "Uy, no te he escuchado bien el día. ¿Para qué fecha quieres mirar?",
                        }
                    ]
                }
        else:
            fecha = date.today()

        # Día de la semana
        dias = [
            "Lunes",
            "Martes",
            "Miércoles",
            "Jueves",
            "Viernes",
            "Sábado",
            "Domingo",
        ]
        dia_nombre = dias[fecha.weekday()]

        # Verificar apertura
        schedule_service = get_schedule_service_lazy()
        abierto_comida, msg_comida = schedule_service.esta_abierto(
            fecha, Servicio.COMIDA
        )
        abierto_cena, msg_cena = schedule_service.esta_abierto(fecha, Servicio.CENA)

        # Obtener turnos
        turnos_comida = schedule_service.get_turnos_disponibles(fecha, Servicio.COMIDA)
        turnos_cena = schedule_service.get_turnos_disponibles(fecha, Servicio.CENA)

        # Construir respuesta
        respuesta_partes = [f"**{dia_nombre} {fecha.strftime('%d/%m/%Y')}:**"]

        if not abierto_comida and not abierto_cena:
            respuesta_partes.append("❌ CERRADO todo el día")
        else:
            if abierto_comida:
                turnos_text = ", ".join(
                    [
                        f"T{t.turno.value} ({t.hora_inicio.strftime('%H:%M')})"
                        for t in turnos_comida
                    ]
                )
                respuesta_partes.append(f"🍽️ Comida: {turnos_text}")

            if abierto_cena:
                turnos_text = ", ".join(
                    [
                        f"T{t.turno.value} ({t.hora_inicio.strftime('%H:%M')})"
                        for t in turnos_cena
                    ]
                )
                respuesta_partes.append(f"🌙 Cena: {turnos_text}")

            if abierto_comida and not abierto_cena:
                respuesta_partes.append("ℹ️ Este día no hay servicio de cena")

        return {
            "results": [
                {"toolCallId": tool_call_id, "result": "\n".join(respuesta_partes)}
            ]
        }

    except Exception as e:
        logger.error(f"Error in get_horarios: {e}")
        tc_id = tool_call_id if 'tool_call_id' in locals() else "unknown"
        return {
            "results": [{"toolCallId": tc_id, "result": "Uy, perdona, mi ordenador va un ratín lento hoy. ¿Me puedes repetir qué día querías mirar?"}]
        }


@router.post("/check_availability")
async def tool_check_availability(request: Request):
    """
    Tool: Verificar disponibilidad de mesas.
    Versión simplificada sin dependencias complejas.
    """
    try:
        data = await request.json()
        tool_call_id, args = parse_vapi_request(data)

        # Aceptar ambos formatos de parámetros (español e inglés)
        fecha_str = args.get("date") or args.get("fecha")
        hora_str = args.get("time") or args.get("hora")
        personas = args.get("pax") or args.get("personas")

        logger.info(
            f"check_availability: fecha={fecha_str}, hora={hora_str}, personas={personas}"
        )

        if not fecha_str or not hora_str:
            return {
                "results": [
                    {
                        "toolCallId": tool_call_id,
                        "result": "Necesito fecha y hora para comprobar disponibilidad. ¿Qué día y a qué hora?",
                    }
                ]
            }

        # Parsear con tolerancia a segundos o basuras
        try:
            fecha_clean = fecha_str[:10]
            fecha = datetime.strptime(fecha_clean, "%Y-%m-%d").date()
            
            hora_clean = hora_str.replace("Z", "").split(".")[0]
            if len(hora_clean) > 5 and ":" in hora_clean:
                parts = hora_clean.split(":")
                hora_clean = f"{parts[0]}:{parts[1]}"
            hora = datetime.strptime(hora_clean, "%H:%M").time()
        except Exception as e:
            logger.error(f"Error parseando fechas: {e} - str: {fecha_str} {hora_str}")
            return {
                "results": [
                    {
                        "toolCallId": tool_call_id,
                        "result": "Perdona, me ha fallado el sistema al anotar la fecha. ¿Me repites qué día y a qué hora?",
                    }
                ]
            }

        # Día de la semana (0=Lunes, 6=Domingo)
        weekday = fecha.weekday()
        dias = [
            "Lunes",
            "Martes",
            "Miércoles",
            "Jueves",
            "Viernes",
            "Sábado",
            "Domingo",
        ]
        dia_nombre = dias[weekday]

        # Reglas simples hardcodeadas (evita dependencias complejas)
        # Lunes = cerrado
        if weekday == 0:
            return {
                "results": [
                    {
                        "toolCallId": tool_call_id,
                        "result": f"Los lunes estamos de descanso. ¿Te interesaría mirar mesa para otro día de la semana?",
                    }
                ]
            }

        # Determinar servicio por hora
        hora_int = hora.hour
        if 13 <= hora_int < 17:
            servicio = "Comida"
            turno = "T1" if hora_int < 15 else "T2"
        elif 20 <= hora_int <= 23:
            servicio = "Cena"
            turno = "T1" if hora_int < 22 else "T2"
        else:
            return {
                "results": [
                    {
                        "toolCallId": tool_call_id,
                        "result": f"❌ A las {hora.strftime('%H:%M')} no servimos. Comida: 13:00-17:00, Cena: 20:00-23:30",
                    }
                ]
            }

        # Martes y Miércoles noche = cerrado
        if weekday in [1, 2] and servicio == "Cena":
            return {
                "results": [
                    {
                        "toolCallId": tool_call_id,
                        "result": f"Los {dia_nombre}s no abrimos por la noche. Tan solo damos servicio de comidas. ¿Te vendría bien la comida de ese día?",
                    }
                ]
            }

        # Domingo noche = cerrado
        if weekday == 6 and servicio == "Cena":
            return {
                "results": [
                    {
                        "toolCallId": tool_call_id,
                        "result": f"❌ Los domingos no abrimos para cenar. ¿Te viene bien la comida o prefieres otro día?",
                    }
                ]
            }

        # Si llegamos aquí, está disponible
        return {
            "results": [
                {
                    "toolCallId": tool_call_id,
                    "result": f"¡Qué suerte, nos queda sitio libre para {personas} personas a esa hora! Para poder dejártela totalmente confirmada a tu nombre, ¿podrías darme tu nombre completo y un número de teléfono de contacto?",
                }
            ]
        }

    except Exception as e:
        logger.error(f"Error in check_availability: {e}", exc_info=True)
        tc_id = tool_call_id if 'tool_call_id' in locals() else "unknown"
        return {
            "results": [
                {
                    "toolCallId": tc_id,
                    "result": "Perdona, se me ha quedado un poco pillado el ordenador. ¿Me puedes repetir para cuándo querías la mesa?",
                }
            ]
        }


@router.post("/create_reservation")
async def tool_create_reservation(request: Request):
    """
    Tool: Crear reserva en Airtable y enviar WhatsApp de confirmacion.
    """
    try:
        data = await request.json()
        tool_call_id, args = parse_vapi_request(data)

        # Aceptar ambos formatos de parámetros (español e inglés)
        nombre = args.get("customer_name") or args.get("nombre")
        telefono = args.get("phone") or args.get("telefono")
        fecha_str = args.get("date") or args.get("fecha")
        hora_str = args.get("time") or args.get("hora")
        personas = args.get("pax") or args.get("personas")
        notas = args.get("notes") or args.get("notas", "")

        if not all([nombre, telefono, fecha_str, hora_str, personas]):
            return {
                "results": [
                    {
                        "toolCallId": tool_call_id,
                        "result": "Me faltan datos. Necesito: nombre, teléfono, fecha, hora y número de personas.",
                    }
                ]
            }

        # Formatear teléfono si no tiene formato E.164
        if telefono and not telefono.startswith("+"):
            telefono = f"+34{telefono.lstrip('0')}"  # Añadir +34 para España

        # Formatear Hora en formato ISO 8601 para Airtable
        # Airtable espera: "2026-02-09T21:00:00.000Z"
        hora_iso = hora_str
        try:
            from datetime import datetime

            # Combinar fecha y hora
            dt = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
            hora_iso = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        except Exception as e:
            logger.warning(f"No se pudo formatear hora ISO: {e}, usando hora original")

        # Crear en Airtable
        try:
            airtable_service = get_airtable_service_lazy()
            record = await airtable_service.create_record(
                {
                    "Nombre del Cliente": nombre,
                    "Teléfono": telefono,
                    "Fecha de Reserva": fecha_str,
                    "Hora": hora_iso,
                    "Cantidad de Personas": int(personas),
                    "Notas": notas,
                    "Estado de Reserva": "Pendiente",
                },
                table_name="Reservas",
            )

            logger.info(f"Reserva creada en Airtable: {record}")

            # Enviar WhatsApp de confirmación
            try:
                from src.infrastructure.external.twilio_service import TwilioService

                twilio = TwilioService()

                # Formatear fecha para el mensaje
                fecha_formateada = fecha_str
                try:
                    from datetime import datetime

                    fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d")
                    dias = [
                        "Lunes",
                        "Martes",
                        "Miércoles",
                        "Jueves",
                        "Viernes",
                        "Sábado",
                        "Domingo",
                    ]
                    fecha_formateada = (
                        f"{dias[fecha_dt.weekday()]} {fecha_dt.strftime('%d/%m/%Y')}"
                    )
                except:
                    pass

                content_variables = {
                    "1": nombre,
                    "2": fecha_formateada,
                    "3": hora_str
                }

                sid = twilio.send_whatsapp_template(telefono, "HXdb0dca8764f0021f9ff2fd197ba22497", content_variables)
                logger.info(f"WhatsApp Template enviado con SID: {sid}")

            except Exception as e:
                logger.error(f"Error enviando WhatsApp Template: {e}")
                # No fallar la reserva si el WhatsApp falla

            return {
                "results": [
                    {
                        "toolCallId": tool_call_id,
                        "result": f"¡Perfecto, {nombre}! Acabo de anotarte la mesa y dejarla reservada. En unos segundos te va a llegar un mensaje por WhatsApp con los detalles de tu reserva para el {fecha_formateada}. ¡Qué ganas de veros por En Las Nubes!",
                    }
                ]
            }

        except Exception as e:
            logger.error(f"Error creando reserva en Airtable: {e}")
            return {
                "results": [
                    {
                        "toolCallId": tool_call_id,
                        "result": "Ay, perdona, tengo un problemita técnico guardando la reserva ahora mismo en el sistema. ¿Te importaría llamar al 941 57 84 51 para que mis compañeros te la dejen apuntada en papel?",
                    }
                ]
            }

    except Exception as e:
        logger.error(f"Error in create_reservation: {e}")
        tc_id = tool_call_id if 'tool_call_id' in locals() else "unknown"
        return {
            "results": [
                {
                    "toolCallId": tc_id,
                    "result": "Madre mía, qué desastre, el sistema de agendas no me funciona bien ahora mismo. ¿Te importa llamar a mis compañeros al 941 57 84 51 y te la apuntan ellos a mano?",
                }
            ]
        }
