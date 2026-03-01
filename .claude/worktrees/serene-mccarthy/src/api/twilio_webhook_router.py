"""
Router para webhooks de Twilio (mensajes WhatsApp entrantes).
Procesa respuestas de clientes a notificaciones de waitlist.
"""
from fastapi import APIRouter, Request, Response, HTTPException
from typing import Dict, Any
import logging
from datetime import datetime

from src.application.services.waitlist_service import WaitlistService
from src.core.entities.waitlist import WaitlistStatus
from src.api.middleware.rate_limiting import webhook_limit

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/twilio", tags=["twilio"])

# Instanciar servicio
waitlist_service = WaitlistService()


@router.post("/whatsapp/incoming")
@webhook_limit()
async def handle_incoming_whatsapp(request: Request):
    """
    Webhook para mensajes WhatsApp entrantes de Twilio.
    Procesa respuestas SÍ/NO de clientes en waitlist.

    Twilio envía:
    - From: whatsapp:+34666123456
    - To: whatsapp:+14155238886 (tu número Twilio)
    - Body: Mensaje del cliente
    - MessageSid: Identificador único
    """
    try:
        form_data = await request.form()
        from_number = form_data.get("From", "").replace("whatsapp:", "")
        body = form_data.get("Body", "").strip().lower()
        message_sid = form_data.get("MessageSid", "")

        logger.info(f"Incoming WhatsApp from {from_number}: '{body}' (SID: {message_sid})")

        # Normalizar respuesta
        respuesta_positiva = body in ["si", "sí", "yes", "vale", "ok", "okay", "confirmo", "confirmado", "acepto"]
        respuesta_negativa = body in ["no", "nope", "cancelar", "cancel", "ya no", "no gracias"]

        if not respuesta_positiva and not respuesta_negativa:
            # Mensaje no reconocido - responder con ayuda
            twiml_response = _generate_twiml(
                "Hola, no entiendo tu mensaje. Responde SÍ para confirmar la mesa o NO si ya no la necesitas. "
                "Si quieres hablar con alguien, llama al 941 57 84 51."
            )
            return Response(content=twiml_response, media_type="application/xml")

        # Buscar entrada en waitlist NOTIFIED para este teléfono
        entries = await waitlist_service.waitlist_repository.list_by_status(
            status=WaitlistStatus.NOTIFIED,
            fecha=None  # Buscar en todos los días
        )

        # Filtrar por teléfono
        matching_entry = None
        for entry in entries:
            # Normalizar números para comparación (quitar espacios, guiones, prefijos)
            entry_phone = entry.telefono_cliente.replace(" ", "").replace("-", "").replace("+", "")
            from_phone = from_number.replace(" ", "").replace("-", "").replace("+", "")

            if entry_phone.endswith(from_phone[-9:]) or from_phone.endswith(entry_phone[-9:]):
                matching_entry = entry
                break

        if not matching_entry:
            # No hay entrada pendiente para este número
            twiml_response = _generate_twiml(
                "No tengo ninguna reserva pendiente de confirmación para este número. "
                "Si tienes dudas, llama al 941 57 84 51."
            )
            return Response(content=twiml_response, media_type="application/xml")

        # Procesar respuesta
        if respuesta_positiva:
            # Confirmar
            try:
                await waitlist_service.confirm_from_waitlist(matching_entry.airtable_id)

                fecha_str = matching_entry.fecha.strftime("%d/%m/%Y")
                hora_str = matching_entry.hora.strftime("%H:%M")

                twiml_response = _generate_twiml(
                    f"¡Perfecto {matching_entry.nombre_cliente}! Mesa confirmada para el {fecha_str} a las {hora_str} "
                    f"para {matching_entry.num_personas} personas. Te esperamos en En Las Nubes ☁️\n\n"
                    f"📍 C/ Mª Teresa Gil de Gárate 16, Logroño\n"
                    f"🅿️ Aparcamiento en C/ Pérez Galdós o Gran Vía"
                )

                logger.info(f"Waitlist entry {matching_entry.airtable_id} confirmed by client {from_number}")

            except Exception as e:
                logger.error(f"Error confirming waitlist entry: {e}", exc_info=True)
                twiml_response = _generate_twiml(
                    "Hubo un error al confirmar tu reserva. Por favor, llama al 941 57 84 51."
                )

        else:  # respuesta_negativa
            # Cancelar
            try:
                await waitlist_service.cancel_from_waitlist(matching_entry.airtable_id)

                twiml_response = _generate_twiml(
                    f"Entendido {matching_entry.nombre_cliente}, he cancelado tu posición en la lista de espera. "
                    f"¡Esperamos verte en otra ocasión en En Las Nubes! ☁️"
                )

                logger.info(f"Waitlist entry {matching_entry.airtable_id} cancelled by client {from_number}")

            except Exception as e:
                logger.error(f"Error cancelling waitlist entry: {e}", exc_info=True)
                twiml_response = _generate_twiml(
                    "Hubo un error al procesar tu cancelación. Por favor, llama al 941 57 84 51."
                )

        return Response(content=twiml_response, media_type="application/xml")

    except Exception as e:
        logger.error(f"Error processing incoming WhatsApp: {e}", exc_info=True)
        twiml_response = _generate_twiml(
            "Lo siento, hubo un error técnico. Por favor, llama al restaurante al 941 57 84 51."
        )
        return Response(content=twiml_response, media_type="application/xml")


def _generate_twiml(message: str) -> str:
    """Genera respuesta TwiML para enviar mensaje de vuelta."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{message}</Message>
</Response>"""
