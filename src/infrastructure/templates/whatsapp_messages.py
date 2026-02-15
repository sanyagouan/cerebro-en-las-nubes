"""
Templates de Mensajes WhatsApp para Notificaciones
Sistema de recordatorios automáticos y feedback post-visita.
"""
from datetime import date, time
from typing import Optional


def recordatorio_24h_template(
    nombre_cliente: str,
    fecha: date,
    hora: time,
    num_personas: int,
    mesa_asignada: Optional[str] = None
) -> str:
    """
    Template para recordatorio 24 horas antes de la reserva.

    Args:
        nombre_cliente: Nombre del cliente
        fecha: Fecha de la reserva
        hora: Hora de la reserva
        num_personas: Cantidad de personas
        mesa_asignada: Número de mesa (opcional)

    Returns:
        Mensaje formateado para WhatsApp
    """
    # Formatear fecha en español
    dias_semana = {
        0: "Lunes",
        1: "Martes",
        2: "Miércoles",
        3: "Jueves",
        4: "Viernes",
        5: "Sábado",
        6: "Domingo"
    }

    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }

    dia_semana = dias_semana[fecha.weekday()]
    mes = meses[fecha.month]
    fecha_formateada = f"{dia_semana} {fecha.day} de {mes}"
    hora_formateada = hora.strftime("%H:%M")

    # Construir mensaje
    mensaje = f"""👋 ¡Hola {nombre_cliente}!

Te recordamos tu reserva para MAÑANA:

📅 {fecha_formateada}
🕐 {hora_formateada}
👥 {num_personas} persona{"s" if num_personas > 1 else ""}"""

    # Agregar mesa si está asignada
    if mesa_asignada:
        mensaje += f"\n🪑 Mesa {mesa_asignada}"

    mensaje += f"""

📍 En Las Nubes Restobar
C/ Principal, Logroño

¿Todo listo? 👍

Para cancelar o modificar, responde CANCELAR y te llamamos enseguida.

¡Te esperamos! 🍽️✨"""

    return mensaje


def confirmacion_reserva_template(
    nombre_cliente: str,
    fecha: date,
    hora: time,
    num_personas: int,
    mesa_asignada: Optional[str] = None,
    zona: Optional[str] = None
) -> str:
    """
    Template para confirmación inmediata al crear la reserva.

    Args:
        nombre_cliente: Nombre del cliente
        fecha: Fecha de la reserva
        hora: Hora de la reserva
        num_personas: Cantidad de personas
        mesa_asignada: Número de mesa (opcional)
        zona: Zona (Terraza/Interior)

    Returns:
        Mensaje formateado para WhatsApp
    """
    # Formatear fecha
    dias_semana = {
        0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
        4: "Viernes", 5: "Sábado", 6: "Domingo"
    }

    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }

    dia_semana = dias_semana[fecha.weekday()]
    mes = meses[fecha.month]
    fecha_formateada = f"{dia_semana} {fecha.day} de {mes}"
    hora_formateada = hora.strftime("%H:%M")

    mensaje = f"""✅ ¡Reserva confirmada, {nombre_cliente}!

📅 {fecha_formateada}
🕐 {hora_formateada}
👥 {num_personas} persona{"s" if num_personas > 1 else ""}"""

    if zona:
        mensaje += f"\n🏠 Zona: {zona}"

    if mesa_asignada:
        mensaje += f"\n🪑 Mesa {mesa_asignada}"

    mensaje += f"""

📍 En Las Nubes Restobar
C/ Principal, Logroño

Te enviaremos un recordatorio 24h antes.

Para cancelar: Responde CANCELAR

¡Nos vemos pronto! 🎉"""

    return mensaje


def cancelacion_reserva_template(
    nombre_cliente: str,
    fecha: date,
    hora: time
) -> str:
    """
    Template para confirmación de cancelación.

    Args:
        nombre_cliente: Nombre del cliente
        fecha: Fecha de la reserva cancelada
        hora: Hora de la reserva cancelada

    Returns:
        Mensaje formateado para WhatsApp
    """
    # Formatear fecha
    dias_semana = {
        0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
        4: "Viernes", 5: "Sábado", 6: "Domingo"
    }

    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }

    dia_semana = dias_semana[fecha.weekday()]
    mes = meses[fecha.month]
    fecha_formateada = f"{dia_semana} {fecha.day} de {mes}"
    hora_formateada = hora.strftime("%H:%M")

    mensaje = f"""❌ Reserva cancelada, {nombre_cliente}

Hemos cancelado tu reserva para:
📅 {fecha_formateada}
🕐 {hora_formateada}

¿Quieres hacer una nueva reserva?
📞 Llámanos: 941 57 84 51

¡Hasta la próxima! 👋"""

    return mensaje


def post_visit_feedback_template(
    nombre_cliente: str,
    fecha: date
) -> str:
    """
    Template OPCIONAL para pedir feedback después de la visita.

    Args:
        nombre_cliente: Nombre del cliente
        fecha: Fecha de la visita

    Returns:
        Mensaje formateado para WhatsApp
    """
    dias_semana = {
        0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
        4: "Viernes", 5: "Sábado", 6: "Domingo"
    }

    dia_semana = dias_semana[fecha.weekday()]

    mensaje = f"""👋 ¡Hola {nombre_cliente}!

Esperamos que hayas disfrutado tu visita el {dia_semana} en En Las Nubes 🍽️

¿Nos dejarías tu opinión?
⭐⭐⭐⭐⭐

Tu feedback nos ayuda a mejorar 💙

📝 Responde con 1-5 estrellas o déjanos un comentario.

¡Gracias por elegirnos! ✨"""

    return mensaje
