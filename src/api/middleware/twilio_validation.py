"""
Middleware de validación de firma Twilio para webhooks.
Protege contra requests falsas que simulen ser de Twilio.
"""
import os
import hmac
import hashlib
from functools import wraps
from flask import request, abort
import logging

logger = logging.getLogger(__name__)


def validate_twilio_signature(func):
    """
    Decorador para validar la firma X-Twilio-Signature en webhooks.
    
    Usage:
        @app.route('/twilio/webhook', methods=['POST'])
        @validate_twilio_signature
        def twilio_webhook():
            # Tu código aquí - la firma ya fue validada
            pass
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # En desarrollo, permitir bypass con variable de entorno
        if os.getenv('TWILIO_SKIP_VALIDATION', 'false').lower() == 'true':
            logger.warning("⚠️  Validación Twilio deshabilitada (modo desarrollo)")
            return func(*args, **kwargs)
        
        # Obtener credenciales
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        if not auth_token:
            logger.error("❌ TWILIO_AUTH_TOKEN no configurado")
            abort(500, "Configuración incompleta")
        
        # Obtener firma del header
        signature = request.headers.get('X-Twilio-Signature', '')
        if not signature:
            logger.warning("🚫 Webhook sin firma Twilio")
            abort(403, "Firma requerida")
        
        # Construir URL completa
        url = request.url
        
        # Obtener parámetros del formulario
        params = request.form.to_dict()
        
        # Calcular firma esperada
        # Twilio concatena: URL + todos los valores de los parámetros ordenados
        sorted_params = sorted(params.items())
        data = url + ''.join([v for k, v in sorted_params])
        
        expected_signature = hmac.new(
            auth_token.encode(),
            data.encode(),
            hashlib.sha1
        ).hexdigest()
        
        # Comparar firmas (timing-safe)
        if not hmac.compare_digest(signature, expected_signature):
            logger.warning(f"🚫 Firma Twilio inválida. Esperada: {expected_signature[:20]}..., Recibida: {signature[:20]}...")
            abort(403, "Firma inválida")
        
        logger.info("✅ Firma Twilio validada correctamente")
        return func(*args, **kwargs)
    
    return decorated_function


def validate_twilio_request_flask():
    """
    Función standalone para validar requests Twilio en Flask.
    Retorna True si es válido, False si no.
    """
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    if not auth_token:
        logger.error("❌ TWILIO_AUTH_TOKEN no configurado")
        return False
    
    signature = request.headers.get('X-Twilio-Signature', '')
    if not signature:
        return False
    
    url = request.url
    params = request.form.to_dict()
    
    # Calcular firma esperada
    sorted_params = sorted(params.items())
    data = url + ''.join([v for k, v in sorted_params])
    
    expected_signature = hmac.new(
        auth_token.encode(),
        data.encode(),
        hashlib.sha1
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
