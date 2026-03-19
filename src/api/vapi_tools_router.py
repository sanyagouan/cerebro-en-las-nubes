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
from src.application.services.table_assignment import get_table_assignment_service
from src.application.services.reservation_service import ReservationService
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

        # Determinar servicio por hora usando configuración central
        hora_int = hora.hour
        
        # Importar configuración de horarios
        from src.core.config.restaurant import BUSINESS_HOURS
        # BUSINESS_HOURS usa claves en inglés
        dias_en = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        dia_actual = dias_en[weekday]
        day_hours = BUSINESS_HOURS.get(dia_actual, {})
        
        # Determinar si es hora de comida o cena
        if 13 <= hora_int < 17:
            servicio = "Comida"
            turno = "T1" if hora_int < 15 else "T2"
            lunch_hours = day_hours.get("lunch") if day_hours else None
            if not lunch_hours:
                return {
                    "results": [
                        {
                            "toolCallId": tool_call_id,
                            "result": f"Lo siento, el {dia_nombre} no abrimos para comer. ¿Te interesa otro día?",
                        }
                    ]
                }
        elif hora_int >= 20 or hora_int == 0:
            # Incluir hora 0 (medianoche) para cenas que cierran tarde
            servicio = "Cena"
            turno = "T1" if hora_int < 22 else "T2"
            dinner_hours = day_hours.get("dinner") if day_hours else None
            
            if not dinner_hours:
                return {
                    "results": [
                        {
                            "toolCallId": tool_call_id,
                            "result": f"Los {dia_nombre}s no abrimos para cenar. ¿Te viene bien la comida o prefieres otro día?",
                        }
                    ]
                }
            
            # Verificar que la hora esté dentro del horario de cierre real
            if dinner_hours:
                close_str = dinner_hours.get("close", "23:30")
                close_parts = close_str.split(":")
                close_hour = int(close_parts[0])
                close_min = int(close_parts[1]) if len(close_parts) > 1 else 0
                
                # Convertir hora de cierre a entero para comparación (minutos desde medianoche)
                close_minutes = close_hour * 60 + close_min
                request_minutes = hora_int * 60 + hora.minute
                
                # Para horas después de medianoche (00:XX), sumar 24*60
                if hora_int == 0:
                    request_minutes = 24 * 60 + hora.minute
                
                if request_minutes > close_minutes:
                    return {
                        "results": [
                            {
                                "toolCallId": tool_call_id,
                                "result": f"Lo siento, el {dia_nombre} cerramos la cocina a las {close_str}. ¿Te viene bien algo más temprano?",
                            }
                        ]
                    }
        else:
            # Hora fuera de los rangos permitidos
            return {
                "results": [
                    {
                        "toolCallId": tool_call_id,
                        "result": f"A las {hora.strftime('%H:%M')} no servimos. Nuestros horarios son: Comida de 13:00 a 17:00 y Cena de 20:00 hasta el cierre según día. ¿Te viene bien alguno de estos horarios?",
                    }
                ]
            }

        # Validación de horarios basada en la configuración central
        from src.core.config.restaurant import BUSINESS_HOURS
        dia_nombre_lower = dia_nombre.lower()
        dias_es = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        dia_actual = dias_es[weekday]
        
        day_hours = BUSINESS_HOURS.get(dia_actual)
        if day_hours:
            dinner_hours = day_hours.get("dinner")
            if servicio == "Cena" and not dinner_hours:
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

        # === VERIFICAR DISPONIBILIDAD REAL DE MESAS ===
        try:
            assignment_service = get_table_assignment_service()
            
            # Asignar mesa (verifica disponibilidad real)
            resultado = await assignment_service.asignar_mesa(
                pax=int(personas) if personas else 2,
                fecha=fecha,
                turno=turno
            )
            
            if not resultado.exito:
                # Si requiere escalado (grupos >10), derivar a humano
                if resultado.requiere_escalado:
                    return {
                        "results": [
                            {
                                "toolCallId": tool_call_id,
                                "result": f"Para grupos de {personas} personas necesitamos que hables con el encargado para confirmar la disponibilidad. ¿Puedes llamar al 941 57 84 51?",
                            }
                        ]
                    }
                
                # No hay mesas disponibles
                return {
                    "results": [
                        {
                            "toolCallId": tool_call_id,
                            "result": f"Vaya, lo siento mucho, pero no nos queda sitio para {personas} personas el {dia_nombre} a esa hora. ¿Te vendría bien una hora antes o después? También puedo mirar otro día si lo prefieres.",
                        }
                    ]
                }
            
            # Hay disponibilidad confirmada
            logger.info(f"Mesa asignada: {resultado.mesa_nombre} en {resultado.zona}")
            
        except Exception as e:
            logger.error(f"Error verificando disponibilidad real de mesas: {e}")
            # Continuar con respuesta optimista si hay error en el servicio
            logger.warning("Continuando sin verificación real de mesas por error en servicio")

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
    Tool: Crear reserva con detección automática de tipo de teléfono.
    
    Flujos diferenciados:
    - Móviles: Estado=Pre-reserva, se envía WhatsApp de confirmación
    - Fijos: Estado=Pre-reserva, requiere confirmación verbal inmediata en llamada
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

        # === OPCIÓN A: VALIDACIÓN DE HORARIOS (SEGURIDAD) ===
        # Esta validación es una medida de seguridad para evitar reservas en horarios no permitidos
        # incluso si el LLM de VAPI no la validó correctamente antes de llamar a esta tool.
        try:
            # Parsear fecha y hora con tolerancia
            fecha_clean = fecha_str[:10] if fecha_str else ""
            fecha = datetime.strptime(fecha_clean, "%Y-%m-%d").date()
            
            hora_clean = hora_str.replace("Z", "").split(".")[0] if hora_str else ""
            if len(hora_clean) > 5 and ":" in hora_clean:
                parts = hora_clean.split(":")
                hora_clean = f"{parts[0]}:{parts[1]}"
            hora = datetime.strptime(hora_clean, "%H:%M").time()
            
            # Día de la semana (0=Lunes, 6=Domingo)
            weekday = fecha.weekday()
            dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            dia_nombre = dias[weekday]
            
            # VALIDACIÓN 1: Lunes = cerrado
            if weekday == 0:
                logger.warning(f"Reserva rechazada: Lunes cerrado - {fecha_str}")
                return {
                    "results": [
                        {
                            "toolCallId": tool_call_id,
                            "result": f"Lo siento {nombre}, los lunes estamos de descanso y no podemos hacer reservas. ¿Te interesaría mirar mesa para otro día de la semana?",
                        }
                    ]
                }
            
            # VALIDACIÓN 2: Determinar servicio por hora usando configuración central
            hora_int = hora.hour
            
            # Importar configuración de horarios
            from src.core.config.restaurant import BUSINESS_HOURS
            dias_es = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
            dia_actual = dias_es[weekday]
            day_hours = BUSINESS_HOURS.get(dia_actual, {})
            
            # Determinar si es hora de comida o cena
            if 13 <= hora_int < 17:
                servicio = "Comida"
                lunch_hours = day_hours.get("lunch") if day_hours else None
                if not lunch_hours:
                    logger.warning(f"Reserva rechazada: {dia_nombre} sin servicio de comida - {fecha_str}")
                    return {
                        "results": [
                            {
                                "toolCallId": tool_call_id,
                                "result": f"Lo siento {nombre}, el {dia_nombre} no abrimos para comer. ¿Te interesa otro día?",
                            }
                        ]
                    }
            elif hora_int >= 20 or hora_int == 0:
                # Incluir hora 0 (medianoche) para cenas que cierran tarde
                servicio = "Cena"
                dinner_hours = day_hours.get("dinner") if day_hours else None
                
                if not dinner_hours:
                    logger.warning(f"Reserva rechazada: {dia_nombre} sin servicio de cena - {fecha_str}")
                    return {
                        "results": [
                            {
                                "toolCallId": tool_call_id,
                                "result": f"Lo siento {nombre}, los {dia_nombre}s no abrimos para cenar. ¿Te viene bien la comida o prefieres otro día?",
                            }
                        ]
                    }
                
                # Verificar que la hora esté dentro del horario de cierre real
                if dinner_hours:
                    close_str = dinner_hours.get("close", "23:30")
                    close_parts = close_str.split(":")
                    close_hour = int(close_parts[0])
                    close_min = int(close_parts[1]) if len(close_parts) > 1 else 0
                    
                    # Convertir hora de cierre a entero para comparación (minutos desde medianoche)
                    close_minutes = close_hour * 60 + close_min
                    request_minutes = hora_int * 60 + hora.minute
                    
                    # Para horas después de medianoche (00:XX), sumar 24*60
                    if hora_int == 0:
                        request_minutes = 24 * 60 + hora.minute
                    
                    if request_minutes > close_minutes:
                        logger.warning(f"Reserva rechazada: Hora {hora_str} posterior al cierre {close_str} - {fecha_str}")
                        return {
                            "results": [
                                {
                                    "toolCallId": tool_call_id,
                                    "result": f"Lo siento {nombre}, el {dia_nombre} cerramos la cocina a las {close_str}. ¿Te viene bien algo más temprano?",
                                }
                            ]
                        }
            else:
                # Hora fuera de los rangos permitidos
                logger.warning(f"Reserva rechazada: Fuera de horario - {hora_str}")
                return {
                    "results": [
                        {
                            "toolCallId": tool_call_id,
                            "result": f"Lo siento {nombre}, a las {hora.strftime('%H:%M')} no servimos. Nuestros horarios son: Comida de 13:00 a 17:00 y Cena de 20:00 hasta el cierre según día. ¿Te viene bien alguno de estos horarios?",
                        }
                    ]
                }
            
            # VALIDACIÓN 3: Domingo noche = cerrado
            if weekday == 6 and servicio == "Cena":
                logger.warning(f"Reserva rechazada: Domingo noche cerrado - {fecha_str}")
                return {
                    "results": [
                        {
                            "toolCallId": tool_call_id,
                            "result": f"Lo siento {nombre}, los domingos no abrimos para cenar, solo damos servicio de comidas. ¿Te viene bien la comida del domingo o prefieres otro día?",
                        }
                    ]
                }
            
            # VALIDACIÓN 4: Verificar horarios según configuración central (días sin cena)
            from src.core.config.restaurant import BUSINESS_HOURS
            dias_es = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
            dia_actual = dias_es[weekday]
            
            day_hours = BUSINESS_HOURS.get(dia_actual)
            if day_hours:
                dinner_hours = day_hours.get("dinner")
                if servicio == "Cena" and not dinner_hours:
                    logger.warning(f"Reserva rechazada: {dia_nombre} sin servicio de cena - {fecha_str}")
                    return {
                        "results": [
                            {
                                "toolCallId": tool_call_id,
                                "result": f"Lo siento {nombre}, los {dia_nombre}s no abrimos por la noche, solo damos servicio de comidas. ¿Te vendría bien la comida de ese día?",
                            }
                        ]
                    }
            
            logger.info(f"Validación de horarios OK: {fecha_str} {hora_str} - {servicio}")
            
        except Exception as e:
            logger.error(f"Error en validación de horarios: {e}")
            # Si hay error en la validación, continuar con precaución (no bloquear la reserva)
            # pero registrar el error para revisión
            logger.warning("Continuando con la reserva a pesar del error de validación")
        # === FIN VALIDACIÓN DE HORARIOS ===

        # Formatear teléfono si no tiene formato E.164
        if telefono and not telefono.startswith("+"):
            # Quitar SOLO un cero inicial si existe (lstrip elimina TODOS los ceros)
            if telefono.startswith("0"):
                telefono = telefono[1:]
            telefono = f"+34{telefono}"  # Añadir +34 para España

        # Formatear Hora en formato ISO 8601 para Airtable
        hora_iso = hora_str
        try:
            # Combinar fecha y hora
            dt = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
            hora_iso = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        except Exception as e:
            logger.warning(f"No se pudo formatear hora ISO: {e}, usando hora original")

        # === USO DEL NUEVO ReservationService ===
        try:
            reservation_service = ReservationService()
            
            # Preparar datos para el servicio
            reservation_data = {
                "nombre": nombre,
                "telefono": telefono,
                "fecha": fecha_str,
                "hora": hora_iso,
                "personas": int(personas),
                "notas": notas
            }
            
            # Crear reserva (el servicio detecta automáticamente tipo de teléfono)
            result = await reservation_service.create_reservation(reservation_data)
            
            if not result.get("success"):
                return {
                    "results": [
                        {
                            "toolCallId": tool_call_id,
                            "result": "Ay, perdona, tengo un problemita técnico guardando la reserva. ¿Te importaría llamar al 941 57 84 51?",
                        }
                    ]
                }
            
            logger.info(f"Reserva creada exitosamente: {result}")
            
            tipo_telefono = result.get("tipo_telefono")
            reservation_id = result.get("reservation_id")
            
            # Formatear fecha para el mensaje
            fecha_formateada = fecha_str
            try:
                fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d")
                dias = [
                    "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"
                ]
                fecha_formateada = f"{dias[fecha_dt.weekday()]} {fecha_dt.strftime('%d/%m/%Y')}"
            except:
                pass
            
            # === FLUJOS DIFERENCIADOS SEGÚN TIPO DE TELÉFONO ===
            
            # CASO 1: Teléfono FIJO -> Requiere confirmación verbal INMEDIATA
            if result.get("requires_verbal_confirmation"):
                logger.info(f"Reserva {reservation_id}: Requiere confirmación verbal (teléfono fijo)")
                return {
                    "results": [
                        {
                            "toolCallId": tool_call_id,
                            "result": f"¡Perfecto, {nombre}! Te he anotado una mesa para {personas} personas el {fecha_formateada} a las {hora_str}. Como veo que me estás llamando desde un fijo, ¿confirmas que te viene bien esta reserva? (Responde SÍ o NO)",
                        }
                    ]
                }
            
            # CASO 2: Teléfono MÓVIL -> Enviar WhatsApp de confirmación
            elif result.get("requires_whatsapp_confirmation"):
                logger.info(f"Reserva {reservation_id}: Enviando WhatsApp de confirmación (teléfono móvil)")
                
                # Enviar WhatsApp de confirmación usando la nueva plantilla Content API
                try:
                    from src.infrastructure.external.twilio_service import TwilioService
                    from src.infrastructure.templates.content_sids import RESERVA_CONFIRMACION_NUBES_SID
                    
                    twilio = TwilioService()
                    content_variables = {
                        "1": nombre,
                        "2": fecha_formateada,
                        "3": hora_str
                    }
                    
                    # Usar el método existente que ya implementa Content API correctamente
                    sid = twilio.send_whatsapp_template(
                        to_number=telefono,
                        template_sid=RESERVA_CONFIRMACION_NUBES_SID,  # Usar el SID de la plantilla Content API
                        variables=content_variables
                    )
                    logger.info(f"WhatsApp Template enviado con SID: {sid}")
                    
                except Exception as e:
                    logger.error(f"Error enviando WhatsApp Template: {e}")
                    # No fallar la reserva si el WhatsApp falla
                
                return {
                    "results": [
                        {
                            "toolCallId": tool_call_id,
                            "result": f"¡Perfecto, {nombre}! Acabo de anotarte la mesa y dejarla reservada. En unos segundos te va a llegar un mensaje por WhatsApp con los detalles de tu reserva para el {fecha_formateada}. ¡Qué ganas de veros en En Las Nubes!",
                        }
                    ]
                }
            
            # CASO 3: Tipo desconocido -> Asumir flujo WhatsApp por defecto
            else:
                logger.warning(f"Reserva {reservation_id}: Tipo de teléfono desconocido, asumiendo flujo WhatsApp")
                return {
                    "results": [
                        {
                            "toolCallId": tool_call_id,
                            "result": f"¡Perfecto, {nombre}! Acabo de anotarte la mesa para el {fecha_formateada}. Si el número es un móvil, te llegará un WhatsApp con los detalles.",
                        }
                    ]
                }

        except Exception as e:
            logger.error(f"Error creando reserva con ReservationService: {e}", exc_info=True)
            return {
                "results": [
                    {
                        "toolCallId": tool_call_id,
                        "result": "Ay, perdona, tengo un problemita técnico guardando la reserva ahora mismo en el sistema. ¿Te importaría llamar al 941 57 84 51 para que mis compañeros te la dejen apuntada en papel?",
                    }
                ]
            }

    except Exception as e:
        logger.error(f"Error in create_reservation: {e}", exc_info=True)
        tc_id = tool_call_id if 'tool_call_id' in locals() else "unknown"
        return {
            "results": [
                {
                    "toolCallId": tc_id,
                    "result": "Madre mía, qué desastre, el sistema de agendas no me funciona bien ahora mismo. ¿Te importa llamar a mis compañeros al 941 57 84 51 y te la apuntan ellos a mano?",
                }
            ]
        }
