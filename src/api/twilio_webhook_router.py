"""
Router profesional para webhooks de Twilio (WhatsApp entrante).
Sistema conversacional completo conectado al Orchestrator multi-agente.

Maneja TODOS los intents:
- confirmation: Cliente confirma reserva (SÍ, confirmo, ok...)
- cancellation: Cliente cancela (NO, cancelar, no puedo...)
- update_notes: Peticiones especiales (alergias, tronas, cachopo sin gluten...)
- faq: Preguntas sobre el restaurante (horarios, ubicación, carta...)
- reservation: Nueva reserva por WhatsApp
- human: Derivación a atención humana

Best Practices implementadas:
- Respuestas naturales con Alba (HumanAgent)
- Contexto de sesión para conversaciones fluidas
- Manejo inteligente de todas las intenciones
- Logging estructurado para debugging
"""

from fastapi import APIRouter, Request, Response, HTTPException
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import json
from xml.sax.saxutils import escape as xml_escape
from cachetools import TTLCache

from src.application.orchestrator import Orchestrator
from src.infrastructure.services.whatsapp_service import WhatsAppService
from src.api.middleware.rate_limiting import webhook_limit

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/twilio", tags=["twilio"])

# Instanciar Orchestrator (conecta Router → Logic → Human agents)
orchestrator = Orchestrator()
whatsapp_service = WhatsAppService()

# Contexto de sesiones con TTL (1 hora) y límite de 10,000 entradas
# Estructura: {phone: {"last_intent": str, "booking_context": dict, "timestamp": datetime}}
session_context: TTLCache = TTLCache(maxsize=10000, ttl=3600)


def _normalize_phone(phone: str) -> str:
    """Normaliza número de teléfono para comparación."""
    return (
        phone.replace(" ", "")
        .replace("-", "")
        .replace("+", "")
        .replace("whatsapp:", "")
    )


def _get_session(phone: str) -> Dict[str, Any]:
    """Obtiene o crea contexto de sesión para un teléfono."""
    normalized = _normalize_phone(phone)
    if normalized not in session_context:
        session_context[normalized] = {
            "last_intent": None,
            "booking_context": {},
            "conversation_history": [],
            "timestamp": datetime.now(),
        }
    return session_context[normalized]


def _update_session(phone: str, intent: str, context_update: Dict[str, Any] = None):
    """Actualiza el contexto de sesión."""
    normalized = _normalize_phone(phone)
    session = _get_session(phone)
    session["last_intent"] = intent
    session["timestamp"] = datetime.now()
    if context_update:
        session["booking_context"].update(context_update)


def _generate_twiml(message: str) -> str:
    """Genera respuesta TwiML para enviar mensaje de vuelta.

    Escapa caracteres especiales XML para evitar errores de parsing.
    """
    # Escapar caracteres especiales XML: & < > " '
    escaped_message = xml_escape(message)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{escaped_message}</Message>
</Response>"""


@router.post("/whatsapp/incoming")
@webhook_limit()
async def handle_incoming_whatsapp(request: Request):
    """
    Webhook profesional para mensajes WhatsApp entrantes de Twilio.

    Flujo:
    1. Recibir mensaje del cliente
    2. Obtener contexto de sesión
    3. Pasar por Orchestrator (Router → Logic → Human)
    4. Responder con mensaje natural de Alba

    Twilio envía:
    - From: whatsapp:+34666123456
    - To: whatsapp:+14155238886 (tu número Twilio)
    - Body: Mensaje del cliente
    - MessageSid: Identificador único
    """
    try:
        form_data = await request.form()
        from_number = form_data.get("From", "").replace("whatsapp:", "")
        body = form_data.get("Body", "").strip()
        message_sid = form_data.get("MessageSid", "")

        logger.info(
            f"📱 WhatsApp entrante de {from_number}: '{body}' (SID: {message_sid})"
        )

        # Validar entrada
        if not body or not from_number:
            logger.warning("Mensaje vacío o sin número")
            return Response(
                content=_generate_twiml(
                    "No he recibido tu mensaje correctamente. ¿Puedes repetir?"
                ),
                media_type="application/xml",
            )

        # Obtener contexto de sesión
        session = _get_session(from_number)

        # === PASAR POR ORCHESTRATOR (Router → Logic → Human) ===
        # El Orchestrator clasifica la intención y genera respuesta natural

        result = await orchestrator.process_message(
            message=body,
            metadata={
                "client_phone": from_number,
                "channel": "whatsapp",
                "session": session,
                "message_sid": message_sid,
            },
        )

        intent = result.get("intent", "other")
        response_text = result.get("response", "")

        # Actualizar sesión
        _update_session(from_number, intent, {"last_response": response_text})

        logger.info(f"✅ Intención: {intent} | Respuesta: {response_text[:50]}...")

        # Generar respuesta TwiML
        twiml_response = _generate_twiml(response_text)
        return Response(content=twiml_response, media_type="application/xml")

    except Exception as e:
        logger.error(f"❌ Error procesando WhatsApp: {e}", exc_info=True)
        twiml_response = _generate_twiml(
            "Lo siento, ha habido un error técnico. "
            "Por favor, llama al restaurante al 941 57 84 51."
        )
        return Response(content=twiml_response, media_type="application/xml")


@router.post("/whatsapp/webhook")
@webhook_limit()
async def handle_whatsapp_webhook(request: Request):
    """
    Endpoint alternativo para compatibilidad.
    Redirige al handler principal.
    """
    return await handle_incoming_whatsapp(request)


# === ENDPOINTS DE TESTING ===


@router.get("/session/{phone}")
async def get_session_debug(phone: str):
    """Debug: Ver contexto de sesión de un teléfono."""
    session = _get_session(phone)
    return {
        "phone": phone,
        "session": {
            "last_intent": session.get("last_intent"),
            "booking_context": session.get("booking_context"),
            "timestamp": session.get("timestamp").isoformat()
            if session.get("timestamp")
            else None,
        },
    }


@router.delete("/session/{phone}")
async def clear_session_debug(phone: str):
    """Debug: Limpiar sesión de un teléfono."""
    normalized = _normalize_phone(phone)
    if normalized in session_context:
        del session_context[normalized]
        return {"status": "cleared", "phone": phone}
    return {"status": "not_found", "phone": phone}


@router.get("/health")
async def webhook_health():
    """Health check del webhook."""
    return {
        "status": "healthy",
        "service": "Twilio WhatsApp Webhook",
        "orchestrator": "connected",
        "active_sessions": len(session_context),
        "timestamp": datetime.now().isoformat(),
    }
