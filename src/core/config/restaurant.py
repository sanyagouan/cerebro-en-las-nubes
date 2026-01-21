"""
Configuración Completa del Restaurante En Las Nubes
Base de Conocimiento para el Agente IA
"""

# ============================================
# INFORMACIÓN BÁSICA
# ============================================
RESTAURANT_INFO = {
    "name": "En Las Nubes Restobar",
    "address": "Calle María Teresa Gil de Gárate, 16, 26002 Logroño, La Rioja",
    "phone": "941578451",
    "timezone": "Europe/Madrid",
    "website": None,  # Próximamente
}

# ============================================
# HORARIOS DETALLADOS
# ============================================
BUSINESS_HOURS = {
    # Martes a Viernes
    "tuesday": {"lunch": {"open": "13:00", "close": "17:00"}, "dinner": None},
    "wednesday": {"lunch": {"open": "13:00", "close": "17:00"}, "dinner": None},
    "thursday": {"lunch": {"open": "13:00", "close": "17:00"}, "dinner": {"open": "20:00", "close": "00:00"}},
    "friday": {"lunch": {"open": "13:00", "close": "17:00"}, "dinner": {"open": "20:00", "close": "00:30"}},
    "saturday": {"lunch": {"open": "13:00", "close": "17:30"}, "dinner": {"open": "20:00", "close": "01:00"}},
    "sunday": {"lunch": {"open": "13:00", "close": "17:30"}, "dinner": None},
    "monday": None,  # CERRADO
}

CLOSED_RULES = {
    "monday": "Los lunes estamos cerrados.",
    "sunday_dinner": "Los domingos por la noche cerramos.",
    "tuesday_after_holiday_monday": "Si el lunes es festivo, pasamos el día de cierre al martes.",
}

# ============================================
# MENÚ Y ESPECIALIDADES
# ============================================
MENU = {
    "specialties": [
        "Cachopos (nuestra especialidad principal, varias variedades)",
        "Platos de inspiración alemana: salchichas y codillo",
        "Hamburguesas",
        "Postres caseros"
    ],
    "menu_del_dia": {
        "available": True,
        "days": ["martes", "miércoles", "jueves", "viernes"],
        "hours": "Mediodía hasta las 16:00",
        "excludes": ["fines de semana", "festivos"]
    },
    "vegetarian_options": True,
    "vegan_options": ["Papas arrugadas", "Carpaccio de calabacín con salsa de mango y frutos secos", "Ensaladas variadas", "Tempura de verduras"],
    "gluten_free": {
        "available": True,
        "cachopo_sin_gluten": {"available": True, "notice_hours": 24, "message": "El cachopo sin gluten requiere 24 horas de antelación"},
    }
}

# ============================================
# SERVICIOS Y COMODIDADES
# ============================================
AMENITIES = {
    "tronas": {"available": True, "quantity": 2, "message": "Solo tenemos 2 tronas, recomendamos reservar con antelación"},
    "mascotas": {"interior": False, "terraza": True, "message": "Las mascotas solo se admiten en terraza"},
    "parking": {"propio": False, "cercano": "Gran Vía (cercano)", "calle_peatonal": True},
    "wifi": True,
    "aire_acondicionado": True,
    "calefaccion": True,
}

# ============================================
# ACCESIBILIDAD
# ============================================
ACCESSIBILITY = {
    "silla_ruedas": True,
    "rampa_acceso": True,
    "baños_adaptados": False,
    "mesas_accesibles": "limitadas",  # Avisar si reservan con silla de ruedas
}

# ============================================
# POLÍTICAS
# ============================================
POLICIES = {
    "vino_propio": True,
    "descorche": {"allowed": True, "price": 5, "currency": "EUR"},
    "grupos_grandes": {
        "threshold": 11,  # A partir de 11 personas
        "action": "derivar_humano",
        "message": "Grupos grandes (a partir de ~11 personas) requieren gestión humana. Te voy a derivar con el encargado."
    },
    "cancelacion": {"hours": 24},
    "eventos": {"available": True, "requires_human": True},
}

# ============================================
# BASE DE CONOCIMIENTO FAQs
# ============================================
FAQS = {
    # HORARIOS
    "horarios": {
        "apertura_general": "Abrimos de martes a domingo. Martes a viernes de 13:00 a 17:00 para comidas. Jueves también abrimos por la noche de 20:00 a 24:00. Viernes de 20:00 a 00:30. Sábados mediodía de 13:00 a 17:30 y noche de 20:00 a 01:00. Domingos solo mediodía de 13:00 a 17:30.",
        "lunes_cerrado": "Los lunes estamos cerrados, excepto si es festivo. Si el lunes es festivo, pasamos el día de cierre al martes.",
        "domingo_noche": "Los domingos por la noche no abrimos.",
    },
    
    # MENÚ
    "menu": {
        "menu_del_dia": "Sí, tenemos menú del día de martes a viernes al mediodía, hasta las 16:00 que cierra la cocina. No disponible fines de semana ni festivos.",
        "especialidad": "Somos especialistas en cachopos y platos de inspiración alemana como salchichas y codillo. También tenemos hamburguesas y postres caseros.",
        "vegetariano": "Sí, tenemos opciones vegetarianas en nuestro menú.",
        "vegano": "Sí, tenemos opciones veganas: papas arrugadas, carpaccio de calabacín con salsa de mango y frutos secos, ensaladas variadas y tempura de verduras.",
        "sin_gluten": "Sí, tenemos opciones sin gluten. Para el cachopo sin gluten, necesitamos aviso mínimo de 24 horas por protocolo especial.",
        "alergias": "Sí, podemos atender a personas con alergias. Por favor, indícanos qué alergia tienes al hacer la reserva para asesorarte adecuadamente.",
    },
    
    # SERVICIOS
    "servicios": {
        "tronas": "Sí, pero solo tenemos 2 tronas disponibles. Se recomienda reservar con antelación.",
        "mascotas": "Las mascotas solo se admiten en terraza, no en interior.",
        "parking": "No tenemos aparcamiento propio, pero hay zonas de aparcamiento cercanas. La calle del restaurante es peatonal y en la Gran Vía hay un parking muy cerca.",
        "wifi": "Sí, tenemos WiFi gratuito para nuestros clientes.",
        "aire_acondicionado": "Sí, tenemos aire acondicionado.",
        "calefaccion": "Sí, tenemos calefacción.",
    },
    
    # ACCESIBILIDAD
    "accesibilidad": {
        "silla_ruedas": "Sí, tenemos acceso para silla de ruedas y rampa de acceso, pero los baños NO están adaptados. Si vienes en silla de ruedas, por favor avísanos al reservar ya que hay un número limitado de mesas accesibles.",
        "baños_adaptados": "No, los baños no están adaptados para sillas de ruedas.",
    },
    
    # BEBIDAS
    "bebidas": {
        "vino_propio": "Sí, se puede traer vino propio, pero cobramos un cargo de descorche de 5 euros por botella.",
        "carta_vinos": "Sí, tenemos una carta de vinos variada con diferentes opciones.",
        "cerveza_artesanal": "No, no disponemos de cerveza artesanal.",
    },
    
    # GRUPOS
    "grupos": {
        "grandes": "Grupos grandes (a partir de 11 personas) requieren gestión humana. Te voy a derivar con el encargado para que te atienda.",
        "menu_grupos": "Sí, tenemos menús especiales para grupos. Para más información, te derivo con el encargado.",
        "eventos": "Sí, organizamos eventos. Para detalles y reservas de eventos, te voy a derivar con el encargado.",
    },
    
    # UBICACIÓN
    "ubicacion": {
        "direccion": "Estamos en Calle María Teresa Gil de Gárate, 16, 26002 Logroño.",
        "telefono": "Nuestro teléfono es 941 57 84 51.",
        "web": "No disponemos de página web todavía, pero la tendremos en breve.",
    },
}

# ============================================
# PROMPT OPTIMIZADO PARA VAPI
# ============================================
VAPI_SYSTEM_PROMPT = """
Eres Alba, la recepcionista virtual de EN LAS NUBES RESTOBAR en Logroño.

## INFORMACIÓN DEL RESTAURANTE

**Nombre:** En Las Nubes Restobar
**Dirección:** Calle María Teresa Gil de Gárate, 16, 26002 Logroño
**Teléfono:** 941 57 84 51

## HORARIOS DE APERTURA

- **Martes a Viernes mediodía:** 13:00 - 17:00 (cocina cierra a las 16:00)
- **Jueves noche:** 20:00 - 00:00
- **Viernes noche:** 20:00 - 00:30
- **Sábado mediodía:** 13:00 - 17:30
- **Sábado noche:** 20:00 - 01:00
- **Domingo mediodía:** 13:00 - 17:30
- **CERRADO:** Lunes (excepto festivos) y Domingo noche
- Si lunes es festivo → cerramos el martes

## ESPECIALIDADES

- **CACHOPOS** (nuestra especialidad principal)
- **Cocina alemana:** salchichas y codillo
- Hamburguesas
- Postres caseros

## MENÚ DEL DÍA
Solo martes a viernes mediodía hasta las 16:00. NO los fines de semana ni festivos.

## RESTRICCIONES DIETÉTICAS

- **Vegetariano:** Sí, tenemos opciones
- **Vegano:** Papas arrugadas, carpaccio de calabacín, ensaladas, tempura de verduras
- **Sin gluten:** Sí, opciones disponibles
- **Cachopo sin gluten:** Requiere 24 HORAS de antelación

## SERVICIOS

- **Tronas:** Sí, pero solo 2 (reservar con antelación)
- **Mascotas:** SOLO en terraza
- **WiFi:** Gratuito
- **Parking:** No propio (cercano en Gran Vía, calle peatonal)
- **Aire/calefacción:** Sí

## ACCESIBILIDAD
Acceso silla de ruedas: SÍ (rampa). Baños adaptados: NO.
Si reservan con silla de ruedas, avisar para asignar mesa accesible.

## BEBIDAS
- Vino propio permitido (descorche 5€/botella)
- Carta de vinos variada
- NO cerveza artesanal

## GRUPOS Y EVENTOS
- Grupos 11+ personas → derivar al encargado
- Eventos → derivar al encargado
- Menús para grupos disponibles (consultar con encargado)

## TUS FUNCIONES

1. **RESERVAS:** Recoger fecha, hora, nº personas, nombre y teléfono
2. **CONSULTAS:** Responder TODO lo anterior de forma autónoma
3. **DERIVAR:** SOLO si:
   - Grupo 11+ personas
   - Eventos especiales
   - El cliente INSISTE en hablar con humano
   - Quejas o situaciones complejas

## ESTILO DE COMUNICACIÓN

- Español de España natural y cercano
- Expresiones: "¡Genial!", "Perfecto", "Estupendo"
- Concisa y eficiente (no te enrolles)
- Siempre confirma los datos de la reserva antes de cerrar
- NO digas "¿En qué más puedo ayudarte?" de forma robótica
"""

# ============================================
# PROMPT PARA WHATSAPP
# ============================================
WHATSAPP_SYSTEM_PROMPT = """
Eres Alba, la asistente virtual de En Las Nubes Restobar por WhatsApp.

Información clave:
- Dirección: Calle María Teresa Gil de Gárate, 16, Logroño
- Teléfono: 941 57 84 51
- Especialidad: Cachopos y cocina alemana
- Horarios: Ma-Vi 13:00-17:00, Ju-Sa noches, Do mediodía
- Cerrado: Lunes y Domingo noche

Para reservas necesito: fecha, hora, personas, nombre.
Respondo consultas sobre horarios, menú, servicios.
Grupos +11 personas → contactar encargado.
"""
