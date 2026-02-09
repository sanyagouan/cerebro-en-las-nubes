"""
Middleware de validacion de firma Twilio para webhooks FastAPI.
Protege contra requests falsas que simulen ser de Twilio.
"""
import hmac
import hashlib
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.config import settings
from src.core.logging import logger


async def validate_twilio_signature(request: Request) -> bool:
    auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
    if not auth_token:
        logger.error("TWILIO_AUTH_TOKEN no configurado")
        return False

    signature = request.headers.get("X-Twilio-Signature", "")
    if not signature:
        return False

    url = str(request.url)
    form_data = await request.form()
    params = {k: v if isinstance(v, str) else str(v) for k, v in form_data.items()}

    sorted_params = sorted(params.items())
    data = url + "".join([v for k, v in sorted_params])

    expected = hmac.new(
        auth_token.encode(),
        data.encode(),
        hashlib.sha1
    ).hexdigest()

    return hmac.compare_digest(signature, expected)


class TwilioValidationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if "/whatsapp/webhook" in request.url.path and request.method == "POST":
            skip = getattr(settings, "TWILIO_SKIP_VALIDATION", "false").lower() == "true"
            if not skip:
                is_valid = await validate_twilio_signature(request)
                if not is_valid:
                    logger.warning("Firma Twilio invalida rechazada")
                    raise HTTPException(status_code=403, detail="Invalid Twilio signature")
        return await call_next(request)
