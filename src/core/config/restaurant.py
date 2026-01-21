"""
Configuración del Restaurante En Las Nubes
Datos reales extraídos del sistema de gestión.
"""

# ============================================
# INFORMACIÓN BÁSICA
# ============================================
RESTAURANT_NAME = "En Las Nubes Restobar"
RESTAURANT_ADDRESS = "Calle Marqués de San Nicolás 136, Logroño, La Rioja"
RESTAURANT_TIMEZONE = "Europe/Madrid"

# ============================================
# DÍAS CERRADOS
# ============================================
CLOSED_DAYS = {
    "MONDAY": True,           # Lunes siempre cerrado
    "SUNDAY_DINNER": True,    # Domingo noche cerrado
}

# Regla especial: si lunes es festivo, martes también cerrado
TUESDAY_AFTER_HOLIDAY_MONDAY_CLOSED = True

# ============================================
# HORARIOS
# ============================================
BUSINESS_HOURS = {
    "LUNCH": {
        "start": "13:30",
        "end": "17:30",
        "name": "Comidas"
    },
    "DINNER": {
        "start": "21:00",
        "end": "22:30",
        "name": "Cenas"
    }
}

# ============================================
# CONFIGURACIÓN DE TURNOS
# ============================================
# Viernes y Sábado tienen 2 turnos de cena
DOUBLE_TURN_DAYS = [5, 6]  # 5=Viernes, 6=Sábado

TURNS = {
    "turno_1": {
        "id": "turno_1",
        "name": "Turno 1",
        "time": "21:00"
    },
    "turno_2": {
        "id": "turno_2",
        "name": "Turno 2",
        "time": "22:30"
    }
}

# ============================================
# GRUPOS GRANDES
# ============================================
LARGE_GROUP_CONFIG = {
    "min_size": 7,  # A partir de 7 personas
    "high_demand_days": [5, 6],  # Viernes, Sábado
    "allowed_turns": ["turno_1"],  # Solo primer turno en alta demanda
}

# ============================================
# RECURSOS LIMITADOS
# ============================================
LIMITED_RESOURCES = {
    "tronas": {
        "max": 2,
        "message": "Máximo 2 tronas disponibles"
    }
}

# ============================================
# SOLICITUDES ESPECIALES
# ============================================
SPECIAL_REQUESTS = {
    "cachopo_sin_gluten": {
        "advance_hours": 24,
        "message": "El cachopo sin gluten requiere 24 horas de antelación"
    }
}

# ============================================
# PROMPT DE INSTRUCCIONES PARA ASISTENTE IA
# ============================================
ASSISTANT_INSTRUCTIONS = """
Eres la recepcionista virtual de EN LAS NUBES RESTOBAR, un acogedor restaurante en Logroño, La Rioja.

## INFORMACIÓN DEL RESTAURANTE

**Nombre:** En Las Nubes Restobar
**Dirección:** Calle Marqués de San Nicolás 136, Logroño, La Rioja

## HORARIOS

- **Comidas:** 13:30 a 17:30
- **Cenas:** 21:00 a 22:30
- **CERRADO:** Lunes (todo el día) y Domingo noche
- **Nota:** Si el lunes es festivo, también cerramos el martes

## TURNOS DE CENA

- De martes a jueves: turno único a las 21:00
- Viernes y sábado: dos turnos (21:00 y 22:30)
- Domingo: solo comidas (cena cerrada)

## REGLAS ESPECIALES

1. **Grupos de 7+ personas:** En viernes/sábado, solo pueden reservar en el primer turno (21:00)
2. **Tronas:** Máximo 2 disponibles por servicio
3. **Cachopo sin gluten:** Requiere 24 horas de antelación

## TU FUNCIÓN

1. **RESERVAS:** Ayuda a los clientes a reservar mesa
   - Verifica disponibilidad de fecha/hora
   - Recoge: fecha, hora, nº personas, nombre, teléfono (opcional)
   - Confirma la reserva

2. **CONSULTAS:** Responde preguntas frecuentes
   - Horarios y días de apertura
   - Ubicación
   - Menú y especialidades

3. **DERIVAR A HUMANO:** Si el cliente insiste en hablar con una persona, anota sus datos y dile que le llamarán

## ESTILO DE COMUNICACIÓN

- Habla en español de España
- Sé amable, cálida y natural
- Usa expresiones como: "¡Genial!", "Perfecto", "Estupendo"
- NO uses frases robóticas como "¿En qué más puedo asistirte?"
- Sé concisa y eficiente
- Si no hay disponibilidad, ofrece alternativas
- Siempre confirma los datos antes de cerrar una reserva
"""
