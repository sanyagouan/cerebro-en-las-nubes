"""
Content SIDs para plantillas WhatsApp - En Las Nubes Restobar
Actualizado: 2026-03-26 06:00:54

Estos SIDs se generan automaticamente desde Twilio Content API.
Las plantillas fueron enviadas a Meta para aprobacion.
"""

# SIDs de plantillas WhatsApp
CONTENT_SIDS = {
    "reserva_confirmacion": "HX501f76efa2d23dd2ccf4e86da3c01035",
    "reserva_recordatorio": "HX88be82bdddd2533f8c00fef3bf4ea410",
    "reserva_cancelada": "HX4afa946a6d0cf3a2f32f0a35cca05e47",
    "mesa_disponible": "HX2f6c7acdc8e74e47e3a4ccc887fbacfc",
}

# Alias para compatibilidad con nombres legacy
RESERVA_CONFIRMACION_SID = CONTENT_SIDS["reserva_confirmacion"]
RESERVA_RECORDATORIO_SID = CONTENT_SIDS["reserva_recordatorio"]
RESERVA_CANCELADA_SID = CONTENT_SIDS["reserva_cancelada"]
MESA_DISPONIBLE_SID = CONTENT_SIDS["mesa_disponible"]
MESA_DISPONIBLE_NUBES_SID = CONTENT_SIDS["mesa_disponible"]
RESERVA_CONFIRMACION_NUBES_SID = CONTENT_SIDS["reserva_confirmacion"]
RESERVA_RECORDATORIO_NUBES_SID = CONTENT_SIDS["reserva_recordatorio"]
RESERVA_CANCELADA_NUBES_SID = CONTENT_SIDS["reserva_cancelada"]

# Alias para compatibilidad con scripts que usan nombres con sufijo _nubes
WHATSAPP_TEMPLATE_SIDS = {
    "reserva_recordatorio_nubes": CONTENT_SIDS["reserva_recordatorio"],
    "reserva_confirmacion_nubes": CONTENT_SIDS["reserva_confirmacion"],
    "reserva_cancelada_nubes": CONTENT_SIDS["reserva_cancelada"],
    "mesa_disponible_nubes": CONTENT_SIDS["mesa_disponible"],
}


def get_template_sid(template_name: str) -> str:
    """
    Obtener el SID de una plantilla por su nombre.
    
    Args:
        template_name: Nombre de la plantilla (sin sufijo _nubes)
    
    Returns:
        SID de la plantilla o None si no existe
    """
    return CONTENT_SIDS.get(template_name)


def get_all_sids() -> dict:
    """Retornar todos los SIDs de plantillas."""
    return CONTENT_SIDS.copy()
