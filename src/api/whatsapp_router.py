"""
WhatsApp Router: Handles incoming messages from Twilio WhatsApp.
"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import Response

from src.application.orchestrator import Orchestrator
# from src.api.middleware.rate_limiting import webhook_limit  # TODO: Re-enable after fixing slowapi

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])
from loguru import logger

# Lazy-loaded orchestrator
_orchestrator = None


def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator


@router.post("/webhook")
# @webhook_limit()  # TODO: Re-enable after fixing slowapi integration
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
    ProfileName: str = Form(None),
):
    """
    Twilio WhatsApp webhook endpoint.
    Receives messages and responds via TwiML.
    """
    try:
        # Clean phone number (remove 'whatsapp:' prefix)
        phone = From.replace("whatsapp:", "")
        message = Body.strip()
        name = ProfileName or "Cliente"

        logger.info(f"💬 WhatsApp from {name} ({phone}): {message}")

        # --- Lógica de Confirmación Bidireccional SÍ/NO ---
        msg_upper = message.upper()
        if msg_upper in ["SÍ", "SI", "NO"]:
            try:
                from src.infrastructure.external.airtable_service import AirtableService
                airtable_service = AirtableService()
                
                # Fetch recent reservations for this phone
                lista_reservas = await airtable_service.get_records_by_formula(
                    formula=f"{{Teléfono}} = '{phone}'",
                    table_name="Reservas",
                    sort=["-createdTime"]
                )
                
                if lista_reservas:
                    # Buscar la más reciente que esté Pendiente
                    pendientes = [r for r in lista_reservas if r.get("fields", {}).get("Estado de Reserva") == "Pendiente"]
                    if pendientes:
                        reserva = pendientes[0]  # La primera al estar ordenado descendente
                        reserva_id = reserva.get("id")
                        
                        nuevo_estado = "Confirmada" if msg_upper in ["SÍ", "SI"] else "Cancelada"
                        
                        await airtable_service.update_record(
                            record_id=reserva_id,
                            fields={"Estado de Reserva": nuevo_estado},
                            table_name="Reservas"
                        )
                        
                        logger.info(f"Reserva {reserva_id} actualizada a {nuevo_estado} vía WhatsApp interactivo.")
                        
                        resp_text = (
                            "¡Genial! Hemos confirmado tu reserva. ¡Nos vemos pronto en En Las Nubes!" 
                            if nuevo_estado == "Confirmada" 
                            else "Entendido, hemos cancelado tu reserva. ¡Esperamos verte en otra ocasión!"
                        )
                        
                        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{resp_text}</Message>
</Response>"""
                        return Response(content=twiml, media_type="application/xml")
            except Exception as e:
                logger.error(f"Error procesando confirmación rápida: {e}")

        # Process through orchestrator
        orchestrator = get_orchestrator()
        result = await orchestrator.process_message(
            message,
            metadata={
                "client_phone": phone,
                "client_name": name,
                "channel": "whatsapp",
            },
        )

        response_text = result.get(
            "response", "Lo siento, no he podido procesar tu mensaje."
        )

        # Return TwiML response
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response_text}</Message>
</Response>"""

        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        logger.error(f"❌ WhatsApp Webhook Error: {e}")
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Lo siento, ha ocurrido un error. Por favor, llámanos al restaurante.</Message>
</Response>"""
        return Response(content=twiml, media_type="application/xml")


@router.get("/status")
async def whatsapp_status():
    """Health check for WhatsApp integration."""
    return {"status": "active", "channel": "WhatsApp"}