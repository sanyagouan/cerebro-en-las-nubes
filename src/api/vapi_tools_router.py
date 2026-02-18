"""
VAPI Tools Router - Endpoints para tools de VAPI.
Apunta a /vapi/tools/* (no /vapi/webhook que es solo para Twilio)
v1.1 - Forzando rebuild
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
        tool_call = data.get("message", {}).get("toolCalls", [{}])[0]
        tool_call_id = tool_call.get("id", "unknown")

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
        return {
            "results": [
                {"toolCallId": "error", "result": "Error obteniendo información"}
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
        tool_call = data.get("message", {}).get("toolCalls", [{}])[0]
        tool_call_id = tool_call.get("id", "unknown")
        args = parse_vapi_args(tool_call)

        fecha_str = args.get("fecha")  # YYYY-MM-DD o null para hoy

        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except ValueError:
                return {
                    "results": [
                        {
                            "toolCallId": tool_call_id,
                            "result": "Formato de fecha inválido. Usa YYYY-MM-DD.",
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
        return {
            "results": [{"toolCallId": "error", "result": "Error consultando horarios"}]
        }


@router.post("/check_availability")
async def tool_check_availability(request: Request):
    """
    Tool: Verificar disponibilidad de mesas.
    Usa TableTetrisService para asignación inteligente.
    """
    try:
        data = await request.json()
        tool_call = data.get("message", {}).get("toolCalls", [{}])[0]
        tool_call_id = tool_call.get("id", "unknown")
        args = parse_vapi_args(tool_call)

        fecha_str = args.get("date") or args.get("fecha")
        hora_str = args.get("time") or args.get("hora")
        personas = args.get("pax") or args.get("personas")

        if not fecha_str or not hora_str:
            return {
                "results": [
                    {
                        "toolCallId": tool_call_id,
                        "result": "Necesito fecha y hora para comprobar disponibilidad. ¿Qué día y a qué hora?",
                    }
                ]
            }

        # Parsear
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            hora = datetime.strptime(hora_str, "%H:%M").time()
        except ValueError:
            return {
                "results": [
                    {
                        "toolCallId": tool_call_id,
                        "result": "Formato incorrecto. Fecha: YYYY-MM-DD, Hora: HH:MM",
                    }
                ]
            }

        # Validar horario con ScheduleService
        schedule_service = get_schedule_service_lazy()
        valido, mensaje = schedule_service.validar_hora_reserva(fecha, hora)

        if not valido:
            # Devolver horarios alternativos
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

            return {
                "results": [
                    {
                        "toolCallId": tool_call_id,
                        "result": f"❌ {dia_nombre} {mensaje}. ¿Te viene bien otro día u hora?",
                    }
                ]
            }

        # Determinar servicio y turno
        servicio = schedule_service.determinar_servicio(hora)
        doble = schedule_service.hay_doble_turno(fecha, servicio)
        turno = schedule_service.determinar_turno(hora, servicio, doble)

        # TODO: Integrar con TableTetrisService para disponibilidad real
        # Por ahora, simulamos disponibilidad
        disponible = True  # Placeholder

        if disponible:
            return {
                "results": [
                    {
                        "toolCallId": tool_call_id,
                        "result": f"✅ Tenemos disponibilidad para {personas or 'X'} personas el {fecha.strftime('%d/%m')} a las {hora.strftime('%H:%M')} (Turno {turno.value}). ¿Confirmamos la reserva? Necesito nombre y teléfono.",
                    }
                ]
            }
        else:
            return {
                "results": [
                    {
                        "toolCallId": tool_call_id,
                        "result": f"⚠️ No hay mesas disponibles para esa hora. ¿Te viene bien 1 hora antes o después? También puedo apuntarte en lista de espera.",
                    }
                ]
            }

    except Exception as e:
        logger.error(f"Error in check_availability: {e}")
        return {
            "results": [
                {
                    "toolCallId": "error",
                    "result": "Tuve un problema técnico. ¿Puedes repetir fecha y hora?",
                }
            ]
        }


@router.post("/create_reservation")
async def tool_create_reservation(request: Request):
    """
    Tool: Crear reserva en Airtable.
    """
    try:
        data = await request.json()
        tool_call = data.get("message", {}).get("toolCalls", [{}])[0]
        tool_call_id = tool_call.get("id", "unknown")
        args = parse_vapi_args(tool_call)

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

        # Crear en Airtable
        try:
            airtable_service = get_airtable_service_lazy()
            record = await airtable_service.create_record(
                {
                    "Nombre del Cliente": nombre,
                    "Teléfono": telefono,
                    "Fecha de Reserva": fecha_str,
                    "Hora": hora_str,
                    "Cantidad de Personas": int(personas),
                    "Notas": notas,
                    "Estado de Reserva": "Pendiente",
                    "Origen": "VAPI",
                },
                table_name="Reservas",
            )

            logger.info(f"Reserva creada en Airtable: {record}")

            return {
                "results": [
                    {
                        "toolCallId": tool_call_id,
                        "result": f"¡Perfecto, {nombre}! He reservado para {personas} personas el {fecha_str} a las {hora_str}. Te enviaré un WhatsApp de confirmación ahora mismo. ¡Nos vemos en Las Nubes!",
                    }
                ]
            }

        except Exception as e:
            logger.error(f"Error creando reserva en Airtable: {e}")
            return {
                "results": [
                    {
                        "toolCallId": tool_call_id,
                        "result": "Tuve un problema guardando la reserva. ¿Podrías llamar al 941 57 84 51 para confirmar?",
                    }
                ]
            }

    except Exception as e:
        logger.error(f"Error in create_reservation: {e}")
        return {
            "results": [
                {
                    "toolCallId": "error",
                    "result": "Error técnico. Llama al 941 57 84 51.",
                }
            ]
        }
