"""
Middleware de validación de firma Twilio para webhooks FastAPI.

Protege contra requests falsas que simulen ser de Twilio.
Usa la biblioteca oficial de Twilio para validar firmas HMAC-SHA1.

Documentación oficial:
https://www.twilio.com/docs/usage/security#validating-requests

IMPORTANTE: Este middleware valida que las requests provengan realmente
de Twilio verificando la firma X-Twilio-Signature en los headers.
"""
import os
from typing import Optional
from fastapi import Request, HTTPException, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import FormData
from twilio.request_validator import RequestValidator
from src.core.config import settings
from src.core.logging import logger


# Rutas que requieren validación de firma Twilio
TWILIO_PROTECTED_PATHS = [
    "/twilio/whatsapp/incoming",
    "/twilio/whatsapp/webhook",
    "/whatsapp/webhook",
]


def get_auth_token() -> Optional[str]:
    """
    Obtiene el token de autenticación de Twilio desde settings o env.
    
    Returns:
        El token de autenticación o None si no está configurado.
    """
    token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
    if not token:
        token = os.getenv("TWILIO_AUTH_TOKEN")
    return token


async def validate_twilio_signature(
    request: Request,
    body_bytes: bytes
) -> bool:
    """
    Valida la firma de una request de Twilio usando RequestValidator oficial.
    
    Esta función implementa la validación según la documentación oficial de Twilio:
    https://www.twilio.com/docs/usage/security#validating-requests
    
    Args:
        request: La request de FastAPI
        body_bytes: El cuerpo de la request ya leído (bytes)
        
    Returns:
        True si la firma es válida, False en caso contrario.
    
    Example:
        >>> is_valid = await validate_twilio_signature(request, body)
        >>> if not is_valid:
        ...     raise HTTPException(status_code=403, detail="Invalid signature")
    """
    auth_token = get_auth_token()
    if not auth_token:
        logger.error(
            "❌ TWILIO_AUTH_TOKEN no configurado - "
            "La validación de firma está deshabilitada"
        )
        return False

    # Obtener la firma del header
    signature = request.headers.get("X-Twilio-Signature", "")
    if not signature:
        logger.warning("⚠️ Request sin header X-Twilio-Signature")
        return False

    # Construir la URL completa como la ve Twilio
    # IMPORTANTE: Twilio usa la URL exacta que configuraste en el webhook
    # Si usas HTTPS detrás de un proxy, la URL puede diferir
    url = str(request.url)
    
    # Si hay un header X-Forwarded-Proto, reconstruir la URL con HTTPS
    forwarded_proto = request.headers.get("X-Forwarded-Proto")
    if forwarded_proto == "https" and url.startswith("http://"):
        url = "https://" + url[7:]
    
    # Parsear los parámetros del form
    # Para validar, necesitamos los parámetros como dict
    try:
        from starlette.datastructures import FormData
        from urllib.parse import parse_qs
        
        # Decodificar el body como form data
        body_str = body_bytes.decode("utf-8")
        parsed = parse_qs(body_str, keep_blank_values=True)
        # parse_qs devuelve listas, necesitamos valores simples
        params = {k: v[0] if v else "" for k, v in parsed.items()}
    except Exception as e:
        logger.error(f"❌ Error parseando form data para validación: {e}")
        return False

    # Usar RequestValidator oficial de Twilio
    validator = RequestValidator(auth_token)
    
    try:
        is_valid = validator.validate(url, params, signature)
        
        if is_valid:
            logger.debug(f"✅ Firma Twilio válida para {request.url.path}")
        else:
            logger.warning(
                f"⚠️ Firma Twilio inválida - URL: {url}, "
                f"Signature: {signature[:20]}..."
            )
            
        return is_valid
        
    except Exception as e:
        logger.error(f"❌ Error validando firma Twilio: {e}")
        return False


def should_validate_request(request: Request) -> bool:
    """
    Determina si una request debe ser validada.
    
    Args:
        request: La request de FastAPI
        
    Returns:
        True si la request debe validarse, False en caso contrario.
    """
    if request.method != "POST":
        return False
        
    path = request.url.path.rstrip("/")
    
    for protected_path in TWILIO_PROTECTED_PATHS:
        if path.endswith(protected_path.rstrip("/")):
            return True
            
    return False


class TwilioValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware que valida la firma de requests de Twilio.
    
    Este middleware intercepta requests a endpoints de webhook de Twilio
    y valida que provengan realmente de Twilio verificando el header
    X-Twilio-Signature.
    
    Configuración:
        - TWILIO_AUTH_TOKEN: Token de autenticación de Twilio (requerido)
        - TWILIO_SKIP_VALIDATION: "true" para deshabilitar (solo desarrollo)
    
    Example:
        ```python
        from fastapi import FastAPI
        from src.api.middleware.twilio_validation import TwilioValidationMiddleware
        
        app = FastAPI()
        app.add_middleware(TwilioValidationMiddleware)
        ```
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Procesa la request y valida la firma si es necesario.
        """
        # Solo validar requests POST a rutas protegidas
        if not should_validate_request(request):
            return await call_next(request)
        
        # Verificar si la validación está deshabilitada (solo para desarrollo)
        skip_validation = os.getenv("TWILIO_SKIP_VALIDATION", "false").lower()
        if skip_validation == "true":
            logger.warning(
                "⚠️ TWILIO_SKIP_VALIDATION=true - "
                "Validación de firma deshabilitada (NO usar en producción)"
            )
            return await call_next(request)
        
        # Leer el body para validación (necesitamos hacerlo antes del dispatch)
        try:
            body_bytes = await request.body()
        except Exception as e:
            logger.error(f"❌ Error leyendo body de request: {e}")
            raise HTTPException(
                status_code=400,
                detail="Error reading request body"
            )
        
        # Validar la firma
        is_valid = await validate_twilio_signature(request, body_bytes)
        
        if not is_valid:
            logger.warning(
                f"🚫 Request rechazada - Firma Twilio inválida desde "
                f"{request.client.host if request.client else 'unknown'}"
            )
            raise HTTPException(
                status_code=403,
                detail="Invalid Twilio signature"
            )
        
        # Continuar con la request
        return await call_next(request)
