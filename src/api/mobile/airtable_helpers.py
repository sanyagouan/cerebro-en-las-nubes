"""
Helper functions para convertir entre Airtable records y Pydantic models.
Maneja el mapeo de campos y transformación de datos.

NOTA DE TIMEZONE:
- El campo 'Hora' en Airtable está configurado con timeZone: "utc"
- Esto significa que Airtable interpreta cualquier valor con sufijo 'Z' como UTC
- Para España (UTC+1 en invierno, UTC+2 en verano):
  * 21:00 hora España = 20:00 UTC (invierno) / 19:00 UTC (verano)
  * Guardar 21:00Z sería interpretado como 22:00 España (invierno) - INCORRECTO
- Solución: Convertir hora local a UTC antes de guardar
"""
from typing import Dict, Any, Optional, List
from datetime import date, time, datetime, timedelta
from zoneinfo import ZoneInfo

from src.core.entities.booking import BookingStatus, ZonePreference, BookingChannel
from src.api.mobile.models import ReservationResponse


# ========== FIELD MAPPING ==========
# Mapeo entre campos de Booking entity y Airtable field IDs

AIRTABLE_FIELD_MAP = {
    "nombre": "Nombre del Cliente",           # fldSeZIwKo8yfn6YZ
    "telefono": "Teléfono",                   # fldBSYJA8AnjNrxXV
    "email": "Email",                         # fldduECur5KuqeoCp
    "fecha": "Fecha de Reserva",              # fldzFzhnO5l74XwSi
    "hora": "Hora",                           # fldjPJMo4E93Wx321
    "pax": "Cantidad de Personas",            # fld4CoP935Kpvnjgo
    "estado": "Estado",                       # flduM2hUKvl7cbqkm
    "zona_preferencia": "Zona Preferida",     # fldDpIF2630x1pCQd
    "mesa_asignada": "Mesa",                  # fldebZGXz38yLHm4E (linked record)
    "canal": "Canal",                         # fldAa1TrmCXny702z
    "vapi_call_id": "VAPI Call ID",           # fldOBkAIun1Cc4Iyy
    "notas": "Notas Especiales"               # fldLlN6Uvse34l9fB
}


# ========== CONVERSION FUNCTIONS ==========

def airtable_to_reservation_response(record: Dict[str, Any]) -> ReservationResponse:
    """
    Convierte un record de Airtable al modelo ReservationResponse.

    Args:
        record: Dict con estructura {'id': str, 'fields': {...}, 'createdTime': str}

    Returns:
        ReservationResponse con todos los campos mapeados
    """
    fields = record.get("fields", {})

    # Parsear fecha (viene como string ISO "YYYY-MM-DD")
    fecha_str = fields.get(AIRTABLE_FIELD_MAP["fecha"])
    fecha = date.fromisoformat(fecha_str) if fecha_str else date.today()

    # Parsear hora - soporta múltiples formatos:
    # 1. ISO DateTime completo: "2026-03-12T21:00:00.000Z" (nuevo formato)
    # 2. Legacy: "HH:MM" o "HH:MM:SS" (formato anterior)
    hora_str = fields.get(AIRTABLE_FIELD_MAP["hora"])
    if hora_str:
        if "T" in hora_str:
            # Formato ISO DateTime completo: "2026-03-12T21:00:00.000Z"
            # Usar fromisoformat para parsear correctamente
            try:
                dt = datetime.fromisoformat(hora_str.replace("Z", "+00:00"))
                # Convertir de UTC a hora local (Europe/Madrid) para mostrar
                madrid_tz = ZoneInfo("Europe/Madrid")
                dt_local = dt.astimezone(madrid_tz)
                hora = dt_local.time()
            except (ValueError, TypeError):
                # Fallback si el parseo falla
                hora = time(12, 0)
        else:
            # Formato legacy: "HH:MM" o "HH:MM:SS"
            parts = hora_str.split(":")
            try:
                hora = time(int(parts[0]), int(parts[1]), int(parts[2].split(".")[0]) if len(parts) > 2 else 0)
            except (ValueError, IndexError):
                hora = time(12, 0)  # Default si hay error
    else:
        hora = time(12, 0)  # Default

    # Mesa asignada (linked record, viene como array de IDs)
    mesa_ids = fields.get(AIRTABLE_FIELD_MAP["mesa_asignada"], [])
    mesa_asignada = mesa_ids[0] if mesa_ids else None

    # Estado con enum validation
    estado_str = fields.get(AIRTABLE_FIELD_MAP["estado"], "Pendiente")
    try:
        estado = BookingStatus(estado_str)
    except ValueError:
        estado = BookingStatus.PENDING

    # Zona preferencia con enum validation
    zona_str = fields.get(AIRTABLE_FIELD_MAP["zona_preferencia"], "Sin preferencia")
    try:
        zona_preferencia = ZonePreference(zona_str)
    except ValueError:
        zona_preferencia = ZonePreference.NO_PREFERENCE

    # Canal con enum validation
    canal_str = fields.get(AIRTABLE_FIELD_MAP["canal"], "VAPI")
    try:
        canal = BookingChannel(canal_str)
    except ValueError:
        canal = BookingChannel.VAPI

    # Created at (viene de Airtable como ISO string)
    created_str = record.get("createdTime", datetime.now().isoformat())
    created_at = datetime.fromisoformat(created_str.replace("Z", "+00:00"))

    return ReservationResponse(
        id=record["id"],
        nombre=fields.get(AIRTABLE_FIELD_MAP["nombre"], ""),
        telefono=fields.get(AIRTABLE_FIELD_MAP["telefono"], ""),
        email=fields.get(AIRTABLE_FIELD_MAP["email"]),
        fecha=fecha,
        hora=hora,
        pax=int(fields.get(AIRTABLE_FIELD_MAP["pax"], 2)),
        estado=estado,
        mesa_asignada=mesa_asignada,
        mesa_nombre=None,  # TODO: Resolver linked record name
        zona_preferencia=zona_preferencia,
        notas=fields.get(AIRTABLE_FIELD_MAP["notas"]),
        canal=canal,
        vapi_call_id=fields.get(AIRTABLE_FIELD_MAP["vapi_call_id"]),
        created_at=created_at,
        updated_at=None  # Airtable no tiene lastModifiedTime en list_records
    )


def reservation_request_to_airtable_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convierte datos de CreateReservationRequest o UpdateReservationRequest
    al formato de fields de Airtable.

    Args:
        data: Dict con datos del request (nombre, telefono, fecha, etc.)

    Returns:
        Dict con keys siendo nombres de campos de Airtable
    """
    fields = {}

    # Campos obligatorios en create
    if "nombre" in data and data["nombre"] is not None:
        fields[AIRTABLE_FIELD_MAP["nombre"]] = data["nombre"]

    if "telefono" in data and data["telefono"] is not None:
        fields[AIRTABLE_FIELD_MAP["telefono"]] = data["telefono"]

    if "email" in data and data["email"] is not None:
        fields[AIRTABLE_FIELD_MAP["email"]] = data["email"]

    # Fecha (convertir date a string ISO)
    if "fecha" in data and data["fecha"] is not None:
        if isinstance(data["fecha"], date):
            fields[AIRTABLE_FIELD_MAP["fecha"]] = data["fecha"].isoformat()
        else:
            fields[AIRTABLE_FIELD_MAP["fecha"]] = data["fecha"]

    # Hora (Airtable espera DateTime completo ISO 8601, no solo "HH:MM")
    #
    # CONVERSIÓN DE TIMEZONE:
    # - La hora que llega del cliente está en timezone local (Europe/Madrid)
    # - Airtable está configurado con timeZone: "utc", por lo que interpreta
    #   cualquier valor con sufijo 'Z' como UTC
    # - Para guardar correctamente, debemos convertir hora local a UTC
    # - Ejemplo: 21:00 hora España (invierno, UTC+1) = 20:00 UTC
    # - Así, Airtable mostrará 21:00 en la interfaz (porque convierte UTC a local)
    if "hora" in data and data["hora"] is not None:
        # Obtener la fecha para combinarla con la hora
        fecha_val = data.get("fecha")
        if isinstance(fecha_val, date):
            fecha_para_combinar = fecha_val
        elif fecha_val:
            fecha_para_combinar = date.fromisoformat(str(fecha_val)[:10])
        else:
            fecha_para_combinar = date.today()

        hora_val = data["hora"]
        if isinstance(hora_val, time):
            hora_local = hora_val
        else:
            # Parsear string "HH:MM" a time object
            parts = str(hora_val)[:5].split(":")
            hora_local = time(int(parts[0]), int(parts[1]))

        # Crear datetime en timezone local (Europe/Madrid)
        madrid_tz = ZoneInfo("Europe/Madrid")
        dt_local = datetime.combine(fecha_para_combinar, hora_local, tzinfo=madrid_tz)
        
        # Convertir a UTC
        utc_tz = ZoneInfo("UTC")
        dt_utc = dt_local.astimezone(utc_tz)
        
        # Formatear como ISO 8601 con sufijo Z (UTC)
        # Airtable espera: "2026-03-12T20:00:00.000Z"
        fields[AIRTABLE_FIELD_MAP["hora"]] = dt_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    if "pax" in data and data["pax"] is not None:
        fields[AIRTABLE_FIELD_MAP["pax"]] = int(data["pax"])

    # Enums (convertir a valor string)
    if "estado" in data and data["estado"] is not None:
        estado_val = data["estado"]
        fields[AIRTABLE_FIELD_MAP["estado"]] = estado_val.value if hasattr(estado_val, "value") else str(estado_val)

    if "zona_preferencia" in data and data["zona_preferencia"] is not None:
        zona_val = data["zona_preferencia"]
        fields[AIRTABLE_FIELD_MAP["zona_preferencia"]] = zona_val.value if hasattr(zona_val, "value") else str(zona_val)

    if "canal" in data and data["canal"] is not None:
        canal_val = data["canal"]
        fields[AIRTABLE_FIELD_MAP["canal"]] = canal_val.value if hasattr(canal_val, "value") else str(canal_val)

    # Mesa asignada (linked record, debe ser array de IDs)
    if "mesa_asignada" in data and data["mesa_asignada"] is not None:
        fields[AIRTABLE_FIELD_MAP["mesa_asignada"]] = [data["mesa_asignada"]]

    # Notas y VAPI call ID
    if "notas" in data and data["notas"] is not None:
        fields[AIRTABLE_FIELD_MAP["notas"]] = data["notas"]

    if "vapi_call_id" in data and data["vapi_call_id"] is not None:
        fields[AIRTABLE_FIELD_MAP["vapi_call_id"]] = data["vapi_call_id"]

    return fields


def build_airtable_filter(
    fecha: Optional[date] = None,
    estado: Optional[str] = None,
    mesa: Optional[str] = None
) -> Optional[str]:
    """
    Construye una fórmula de filtro de Airtable basada en parámetros.

    Args:
        fecha: Fecha de reserva para filtrar
        estado: Estado de reserva ("Pendiente", "Confirmada", etc.)
        mesa: ID de mesa asignada

    Returns:
        String con fórmula de Airtable o None si no hay filtros

    Examples:
        >>> build_airtable_filter(fecha=date(2024, 3, 15))
        "IS_SAME({Fecha de Reserva}, '2024-03-15', 'day')"

        >>> build_airtable_filter(fecha=date(2024, 3, 15), estado="Confirmada")
        "AND(IS_SAME({Fecha de Reserva}, '2024-03-15', 'day'), {Estado}='Confirmada')"
    """
    conditions = []

    if fecha:
        fecha_str = fecha.isoformat()
        conditions.append(f"IS_SAME({{{AIRTABLE_FIELD_MAP['fecha']}}}, '{fecha_str}', 'day')")

    if estado:
        conditions.append(f"{{{AIRTABLE_FIELD_MAP['estado']}}}='{estado}'")

    if mesa:
        # Linked records requieren búsqueda en array
        conditions.append(f"FIND('{mesa}', ARRAYJOIN({{{AIRTABLE_FIELD_MAP['mesa_asignada']}}}))>0")

    if not conditions:
        return None

    if len(conditions) == 1:
        return conditions[0]

    # AND de múltiples condiciones
    return f"AND({', '.join(conditions)})"
