"""
Utilidades para manejo de teléfonos.

Este módulo proporciona funciones para detectar el tipo de teléfono español
(móvil vs fijo) basándose en el prefijo del número en formato E.164.

Author: Sistema Cerebro En Las Nubes
Date: 2026-03-10
"""


def detectar_tipo_telefono(telefono: str) -> str:
    """
    Detecta si un número de teléfono español es móvil o fijo.
    
    Reglas de clasificación para España (+34):
    - +346XX... = Móvil (serie 6XX: 600-699)
    - +347XX... = Móvil (serie 7XX: 700-799)
    - +349XX... = Fijo (todos los 9XX incluyendo 91X, 93X, 96X, 97X, etc.)
    - Otros = Desconocido (incluye números internacionales no españoles)
    
    Args:
        telefono: Número en formato E.164 (ej: "+34612345678")
    
    Returns:
        str: Uno de los siguientes valores:
            - "movil": Número de teléfono móvil
            - "fijo": Número de teléfono fijo
            - "desconocido": No se puede determinar (número internacional o formato inválido)
    
    Examples:
        >>> detectar_tipo_telefono("+34612345678")
        "movil"
        
        >>> detectar_tipo_telefono("+34941123456")
        "fijo"
        
        >>> detectar_tipo_telefono("+1234567890")
        "desconocido"
    
    Notas:
        - Solo funciona para números españoles (+34)
        - Números con otros códigos de país retornan "desconocido"
        - La función no valida si el número existe, solo clasifica por prefijo
    """
    # Validar formato básico
    if not telefono or not isinstance(telefono, str):
        return "desconocido"
    
    # Debe comenzar con +34 (código de país de España)
    if not telefono.startswith("+34"):
        return "desconocido"
    
    # Debe tener al menos 12 caracteres (+34 + 9 dígitos)
    if len(telefono) < 12:
        return "desconocido"
    
    # Extraer primer dígito después del código de país
    primer_digito = telefono[3:4]
    
    # Serie 6XX o 7XX = Móvil
    if primer_digito in ["6", "7"]:
        return "movil"
    
    # Serie 9XX = Fijo (todos: 91X Madrid, 93X Barcelona, 96X Valencia, 97X Baleares, etc.)
    elif primer_digito == "9":
        return "fijo"
    
    # Otros casos (8XX, 5XX, 1-4, etc.) = Desconocido
    return "desconocido"


def formato_visual_telefono(telefono: str) -> str:
    """
    Formatea un número de teléfono para visualización amigable.
    
    Convierte "+34612345678" en "612 345 678" (formato español estándar).
    
    Args:
        telefono: Número en formato E.164
    
    Returns:
        str: Número formateado para visualización
    
    Examples:
        >>> formato_visual_telefono("+34612345678")
        "612 345 678"
        
        >>> formato_visual_telefono("+34941123456")
        "941 123 456"
    """
    if not telefono or not isinstance(telefono, str):
        return telefono
    
    # Remover código de país si es español
    if telefono.startswith("+34"):
        numero = telefono[3:]
        # Formatear: XXX XXX XXX
        if len(numero) == 9:
            return f"{numero[0:3]} {numero[3:6]} {numero[6:9]}"
    
    return telefono


def es_numero_valido_espanol(telefono: str) -> bool:
    """
    Valida que un número sea un teléfono español válido en formato E.164.
    
    Args:
        telefono: Número a validar
    
    Returns:
        bool: True si es válido, False en caso contrario
    
    Examples:
        >>> es_numero_valido_espanol("+34612345678")
        True
        
        >>> es_numero_valido_espanol("+1234567890")
        False
        
        >>> es_numero_valido_espanol("612345678")
        False
    """
    if not telefono or not isinstance(telefono, str):
        return False
    
    # Debe comenzar con +34
    if not telefono.startswith("+34"):
        return False
    
    # Debe tener exactamente 12 caracteres (+34 + 9 dígitos)
    if len(telefono) != 12:
        return False
    
    # Los 9 dígitos después de +34 deben ser numéricos
    digitos = telefono[3:]
    if not digitos.isdigit():
        return False
    
    # Primer dígito debe ser válido (6, 7, 8, 9)
    primer_digito = digitos[0]
    if primer_digito not in ["6", "7", "8", "9"]:
        return False
    
    return True
