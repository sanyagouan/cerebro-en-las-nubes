"""
WhatsApp Router: Handles incoming messages from Twilio WhatsApp.
"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import Response
import logging

from src.application.orchestrator import Orchestrator
from src.api.middleware.rate_limiting import webhook_limit

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])
logger = logging.getLogger(__name__)

# Lazy-loaded orchestrator
_orchestrator = None


def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator


@router.post("/webhook")
@webhook_limit()
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

        # Process through orchestrator
        orchestrator = get_orchestrator()
        result = await orchestrator.process_message(
            message,
            metadata={
                "client_phone": phone,
                "client_name": name,
                "channel": "WhatsApp",
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
