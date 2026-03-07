"""
Middleware de seguridad para FastAPI.

Exports:
- TwilioValidationMiddleware: Valida firma de requests de Twilio
- limiter: Rate limiter de slowapi
- setup_security_middleware: Configuración completa de seguridad
"""

from src.api.middleware.twilio_validation import (
    TwilioValidationMiddleware,
    validate_twilio_signature,
)
from src.api.middleware.rate_limiting import (
    limiter,
    rate_limit_exceeded_handler,
    webhook_limit,
    auth_limit,
    api_limit,
    expensive_limit,
)
from src.api.middleware.security import (
    setup_security_middleware,
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware,
    SuspiciousActivityMiddleware,
    SECURITY_HEADERS,
)

__all__ = [
    # Twilio validation
    "TwilioValidationMiddleware",
    "validate_twilio_signature",
    # Rate limiting
    "limiter",
    "rate_limit_exceeded_handler",
    "webhook_limit",
    "auth_limit",
    "api_limit",
    "expensive_limit",
    # Security middleware
    "setup_security_middleware",
    "SecurityHeadersMiddleware",
    "RequestLoggingMiddleware",
    "SuspiciousActivityMiddleware",
    "SECURITY_HEADERS",
]
