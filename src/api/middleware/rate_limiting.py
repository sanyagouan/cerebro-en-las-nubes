"""
Rate Limiting Middleware - Protege los endpoints de abuso.

Implementa límites de tasa usando slowapi para prevenir:
- Ataques DDoS
- Abuso de webhooks
- Spam de API
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from loguru import logger


def get_identifier(request: Request) -> str:
    """
    Obtiene el identificador único para rate limiting.

    Prioridad:
    1. X-Forwarded-For header (proxy/load balancer)
    2. X-Real-IP header (nginx)
    3. Direct IP address
    """
    # Check for forwarded IP (behind proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Get first IP in chain (original client)
        return forwarded.split(",")[0].strip()

    # Check for real IP header (nginx)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fallback to direct address
    return get_remote_address(request)


# Initialize limiter
limiter = Limiter(
    key_func=get_identifier,
    default_limits=["60/minute"],  # Default: 60 requests por minuto
    storage_uri="memory://",  # Use Redis in production for distributed systems
    headers_enabled=True,  # Add rate limit headers to responses
)


# Custom rate limit handler
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Maneja errores de rate limit con respuesta personalizada.
    """
    client_ip = get_identifier(request)
    path = request.url.path

    logger.warning(
        f"Rate limit exceeded - IP: {client_ip}, Path: {path}, Limit: {exc.detail}"
    )

    return HTTPException(
        status_code=429,
        detail={
            "error": "rate_limit_exceeded",
            "message": "Demasiadas solicitudes. Por favor intente más tarde.",
            "retry_after": exc.detail  # Seconds until rate limit resets
        },
        headers={
            "Retry-After": str(exc.detail),
            "X-RateLimit-Limit": "60",
            "X-RateLimit-Remaining": "0",
        }
    )


# Decorators for specific limits
def webhook_limit():
    """
    Límite estricto para webhooks: 10 req/min
    Protege contra webhooks mal configurados o ataques.
    """
    return limiter.limit("10/minute")


def auth_limit():
    """
    Límite para autenticación: 5 req/min
    Previene brute force attacks.
    """
    return limiter.limit("5/minute")


def api_limit():
    """
    Límite general para API: 60 req/min
    Balance entre UX y protección.
    """
    return limiter.limit("60/minute")


def expensive_limit():
    """
    Límite para operaciones costosas: 10 req/min
    (Exportaciones, analytics pesados, etc.)
    """
    return limiter.limit("10/minute")
