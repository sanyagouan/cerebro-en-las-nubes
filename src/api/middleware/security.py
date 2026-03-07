"""
Middleware de Seguridad Consolidado para FastAPI.

Este módulo centraliza todas las medidas de seguridad:
1. Validación de firma Twilio
2. Rate limiting por IP y endpoint
3. Headers de seguridad HTTP
4. Protección contra ataques comunes

Uso:
    from fastapi import FastAPI
    from src.api.middleware.security import setup_security_middleware
    
    app = FastAPI()
    setup_security_middleware(app)

Referencias:
- OWASP Security Headers: https://owasp.org/www-project-secure-headers/
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
"""

import os
import time
from typing import Callable
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.logging import logger

# Import security components
from src.api.middleware.twilio_validation import TwilioValidationMiddleware
from src.api.middleware.rate_limiting import (
    limiter,
    rate_limit_exceeded_handler,
)
from slowapi.errors import RateLimitExceeded


# Security Headers según OWASP
SECURITY_HEADERS = {
    # Prevenir clickjacking
    "X-Frame-Options": "DENY",
    # Prevenir MIME type sniffing
    "X-Content-Type-Options": "nosniff",
    # Habilitar XSS filter del navegador
    "X-XSS-Protection": "1; mode=block",
    # Política de referrer
    "Referrer-Policy": "strict-origin-when-cross-origin",
    # Permisos de features del navegador
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    # Content Security Policy básica (ajustar según necesidades)
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware que añade headers de seguridad HTTP a todas las respuestas.
    
    Implementa recomendaciones de OWASP para prevenir ataques comunes:
    - Clickjacking (X-Frame-Options)
    - MIME sniffing (X-Content-Type-Options)
    - XSS (X-XSS-Protection, Content-Security-Policy)
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Añadir headers de seguridad
        for header, value in SECURITY_HEADERS.items():
            # Solo añadir si no existe ya
            if header not in response.headers:
                response.headers[header] = value
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware de logging de requests para auditoría de seguridad.
    
    Registra información relevante de cada request para:
    - Detectar patrones de ataque
    - Auditoría de acceso
    - Debugging de problemas
    """
    
    async def dispatch(self, request: Request, call_next):
        # Registrar inicio
        start_time = time.time()
        
        # Información de la request
        client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if not client_ip:
            client_ip = request.headers.get("X-Real-IP", "")
        if not client_ip and request.client:
            client_ip = request.client.host
        
        path = request.url.path
        method = request.method
        
        # Log solo para rutas que no son health check
        if not path.endswith("/health"):
            logger.debug(
                f"🔍 Request: {method} {path} from {client_ip}"
            )
        
        try:
            response = await call_next(request)
            
            # Calcular duración
            duration_ms = (time.time() - start_time) * 1000
            
            # Log de respuesta (solo si es lenta o error)
            if duration_ms > 1000 or response.status_code >= 400:
                logger.info(
                    f"📊 Response: {method} {path} -> {response.status_code} "
                    f"({duration_ms:.0f}ms) from {client_ip}"
                )
            
            return response
            
        except Exception as e:
            # Log de error
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"❌ Error: {method} {path} -> {type(e).__name__}: {e} "
                f"({duration_ms:.0f}ms) from {client_ip}"
            )
            raise


class SuspiciousActivityMiddleware(BaseHTTPMiddleware):
    """
    Middleware para detectar y bloquear actividad sospechosa.
    
    Detecta:
    - User agents conocidos de bots maliciosos
    - Patrones de path traversal
    - Intentos de SQL injection en URLs
    """
    
    # User agents conocidos de bots maliciosos
    BLOCKED_USER_AGENTS = [
        "sqlmap",
        "nikto",
        "nmap",
        "masscan",
        "python-requests/1",  # Versiones antiguas de requests
        "curl/1",  # Versiones muy antiguas
    ]
    
    # Patrones sospechosos en URLs
    SUSPICIOUS_PATTERNS = [
        "../",           # Path traversal
        "..\\",          # Path traversal Windows
        "<script",       # XSS attempt
        "javascript:",   # XSS attempt
        "SELECT ",       # SQL injection
        "UNION ",        # SQL injection
        "INSERT ",       # SQL injection
        "DROP ",         # SQL injection
        "%00",           # Null byte injection
        "etc/passwd",    # File inclusion
        "etc/shadow",    # File inclusion
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Verificar User Agent
        user_agent = request.headers.get("User-Agent", "").lower()
        for blocked in self.BLOCKED_USER_AGENTS:
            if blocked.lower() in user_agent:
                logger.warning(
                    f"🚫 User agent bloqueado: {user_agent} desde "
                    f"{request.client.host if request.client else 'unknown'}"
                )
                return Response(
                    content="Forbidden",
                    status_code=403,
                )
        
        # Verificar patrones sospechosos en URL
        full_url = str(request.url).lower()
        for pattern in self.SUSPICIOUS_PATTERNS:
            if pattern.lower() in full_url:
                logger.warning(
                    f"🚫 Patrón sospechoso detectado en URL: {request.url.path} "
                    f"desde {request.client.host if request.client else 'unknown'}"
                )
                return Response(
                    content="Bad Request",
                    status_code=400,
                )
        
        return await call_next(request)


def setup_security_middleware(app: FastAPI) -> None:
    """
    Configura todos los middlewares de seguridad en la aplicación FastAPI.
    
    El orden de los middlewares es importante:
    1. Security Headers (más externo, se aplica a todas las respuestas)
    2. Request Logging (auditoría)
    3. Suspicious Activity Detection (bloqueo temprano)
    4. Rate Limiting (control de abuso)
    5. Twilio Validation (validación específica de webhooks)
    
    Args:
        app: Instancia de FastAPI
    
    Example:
        ```python
        from fastapi import FastAPI
        from src.api.middleware.security import setup_security_middleware
        
        app = FastAPI()
        setup_security_middleware(app)
        ```
    """
    # Verificar si estamos en modo desarrollo
    is_development = os.getenv("ENVIRONMENT", "development").lower() == "development"
    
    if is_development:
        logger.warning(
            "⚠️ Ejecutando en modo DEVELOPMENT - "
            "Algunas protecciones pueden estar reducidas"
        )
    
    # 1. Rate Limiter state (requerido por slowapi)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    logger.info("✅ Rate limiting configurado")
    
    # 2. Twilio Validation Middleware
    app.add_middleware(TwilioValidationMiddleware)
    logger.info("✅ Validación de firma Twilio configurada")
    
    # 3. Suspicious Activity Detection
    if not is_development:
        app.add_middleware(SuspiciousActivityMiddleware)
        logger.info("✅ Detección de actividad sospechosa configurada")
    
    # 4. Request Logging
    app.add_middleware(RequestLoggingMiddleware)
    logger.info("✅ Logging de requests configurado")
    
    # 5. Security Headers
    app.add_middleware(SecurityHeadersMiddleware)
    logger.info("✅ Headers de seguridad configurados")
    
    logger.info("🔒 Middleware de seguridad inicializado correctamente")


# Exports
__all__ = [
    "setup_security_middleware",
    "SecurityHeadersMiddleware",
    "RequestLoggingMiddleware",
    "SuspiciousActivityMiddleware",
    "SECURITY_HEADERS",
]
