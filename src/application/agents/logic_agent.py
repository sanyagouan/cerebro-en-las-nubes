"""
Logic Agent: Uses DeepSeek for complex reasoning about availability.
Cost-effective for heavy logic tasks.
"""

import os
import json
from typing import Dict, Any
from datetime import datetime, date, time
from src.application.agents.base_agent import BaseAgent
from src.core.logic.booking_engine import BookingEngine
from src.core.entities.booking import Booking, BookingChannel
from src.infrastructure.repositories.booking_repo import AirtableBookingRepository
from src.core.config.restaurant import BUSINESS_HOURS, CLOSED_RULES
from src.core.logging import logger


def validate_business_hours(fecha: date, hora: time) -> Dict[str, Any]:
    """
    Valida si el restaurante está abierto en la fecha y hora dadas.

    Returns:
        {"valid": True} si está abierto
        {"valid": False, "reason": "mensaje"} si está cerrado
    """
    day_names = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    day_name = day_names[fecha.weekday()]

    # Check if Monday (always closed)
    if day_name == "monday":
        return {
            "valid": False,
            "reason": CLOSED_RULES.get("monday", "Los lunes estamos cerrados."),
        }

    day_hours = BUSINESS_HOURS.get(day_name)
    if not day_hours:
        return {
            "valid": False,
            "reason": f"No tenemos horario registrado para {day_name}.",
        }

    # Determine if lunch or dinner based on hour
    hour_int = hora.hour

    # Lunch: 13:00 - 17:30
    # Dinner: 20:00 - 01:00
    is_lunch = 13 <= hour_int < 18
    is_dinner = hour_int >= 20 or hour_int <= 1

    if is_lunch:
        lunch_hours = day_hours.get("lunch")
        if not lunch_hours:
            return {"valid": False, "reason": f"No abrimos para comer los {day_name}s."}
        # Check if within lunch hours
        open_parts = lunch_hours["open"].split(":")
        close_parts = lunch_hours["close"].split(":")
        open_minutes = int(open_parts[0]) * 60 + int(open_parts[1])
        close_minutes = int(close_parts[0]) * 60 + int(close_parts[1])
        request_minutes = hour_int * 60 + hora.minute

        # Handle close after midnight (e.g., 00:30)
        if close_minutes < open_minutes:  # closes next day
            close_minutes += 24 * 60

        if not (open_minutes <= request_minutes <= close_minutes):
            return {
                "valid": False,
                "reason": f"Nuestro horario de comidas es de {lunch_hours['open']} a {lunch_hours['close']}.",
            }

    elif is_dinner:
        dinner_hours = day_hours.get("dinner")
        if not dinner_hours:
            # Sunday night special message
            if day_name == "sunday":
                return {
                    "valid": False,
                    "reason": CLOSED_RULES.get(
                        "sunday_dinner", "Los domingos por la noche cerramos."
                    ),
                }
            return {"valid": False, "reason": f"No abrimos para cenar los {day_name}s."}

        # Check if within dinner hours
        open_parts = dinner_hours["open"].split(":")
        close_parts = dinner_hours["close"].split(":")
        open_minutes = int(open_parts[0]) * 60 + int(open_parts[1])
        close_minutes = int(close_parts[0]) * 60 + int(close_parts[1])
        request_minutes = hour_int * 60 + hora.minute

        # Handle hours after midnight (e.g., 01:00)
        if hour_int <= 1:  # After midnight
            request_minutes += 24 * 60
        if close_minutes < open_minutes:  # closes next day
            close_minutes += 24 * 60

        if not (open_minutes <= request_minutes <= close_minutes):
            return {
                "valid": False,
                "reason": f"Nuestro horario de cenas es de {dinner_hours['open']} a {dinner_hours['close']}.",
            }

    else:
        # Neither lunch nor dinner time
        return {
            "valid": False,
            "reason": "Solo abrimos para comer (13:00-17:30) o cenar (20:00-01:00).",
        }

    return {"valid": True}


class LogicAgent(BaseAgent):
    """Reasons about availability and suggests optimal booking options."""

    def __init__(self):
        super().__init__(
            model="deepseek-chat",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )
        self.booking_engine = BookingEngine(AirtableBookingRepository())

        self.system_prompt = """Eres el motor lógico de reservas de En Las Nubes Restobar.
Tu trabajo es analizar disponibilidad y proponer soluciones.

Recibirás información sobre:
- La petición del cliente (fecha, hora, personas)
- Las mesas disponibles
- Las restricciones del día

Debes responder en JSON con:
{
  "available": true/false,
  "assigned_table": "nombre de mesa" o null,
  "alternatives": ["otras opciones si no hay disponibilidad"],
  "reasoning": "Explicación breve de tu decisión"
}

Prioriza el mejor ajuste (no desperdiciar sillas grandes para grupos pequeños).
"""

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze availability and assign table.

        Args:
            context: {
                "date": "2026-01-25",
                "time": "14:00",
                "pax": 4,
                "client_name": "...",
                "client_phone": "...",
                "action": "check_availability" or "create_reservation"
            }
        """
        try:
            # Debug logging
            logger.debug(f"[LOGIC_AGENT] context received: {context}")

            # Build booking request
            date_str = context.get("date", datetime.now().strftime("%Y-%m-%d"))
            time_str = context.get("time", "14:00")
            action = context.get("action", "check_availability")

            logger.debug(
                f"[LOGIC_AGENT] date_str={date_str}, time_str={time_str}, pax={context.get('pax', 2)}"
            )

            # Parse date and time separately for Booking entity v2
            try:
                fecha_parsed = date.fromisoformat(date_str)
                hora_parts = time_str.split(":")
                hora_parsed = time(int(hora_parts[0]), int(hora_parts[1]))
            except (ValueError, IndexError) as parse_err:
                logger.warning(f"[LOGIC_AGENT] Date/time parse error: {parse_err}")
                return {
                    "available": False,
                    "error": f"Fecha/hora inválida: {date_str} {time_str}",
                    "reasoning": "Error parseando fecha u hora.",
                }

            # === VALIDACIÓN DE HORARIOS DE NEGOCIO ===
            hours_validation = validate_business_hours(fecha_parsed, hora_parsed)
            if not hours_validation["valid"]:
                return {
                    "available": False,
                    "error": "closed",
                    "reasoning": hours_validation["reason"],
                    "message": hours_validation["reason"],
                }

            # Create Booking with correct field names (v2 entity)
            booking_request = Booking(
                nombre=context.get("client_name") or "Pendiente",
                telefono=context.get("client_phone") or "",
                fecha=fecha_parsed,
                hora=hora_parsed,
                pax=context.get("pax", 2),
                canal=BookingChannel.WHATSAPP,  # WhatsApp channel
            )

            # Use BookingEngine to find best table
            best_table = self.booking_engine.find_best_table(booking_request)

            if best_table:
                # If just checking availability, return result without saving
                if action == "check_availability":
                    return {
                        "available": True,
                        "assigned_table": best_table.nombre,
                        "table_id": best_table.id,
                        "reasoning": f"Mesa {best_table.nombre} disponible para {booking_request.pax} personas.",
                    }

                # If creating reservation, ACTUALLY SAVE TO AIRTABLE
                if action == "create_reservation":
                    from src.core.entities.booking import BookingStatus

                    booking_request.mesa_asignada = best_table.id
                    # Status is Pending until WhatsApp confirmation
                    booking_request.estado = BookingStatus.PENDING

                    # Save to Airtable
                    saved_booking = self.booking_engine.repo.create_booking(
                        booking_request
                    )

                    return {
                        "available": True,
                        "booking_created": True,
                        "booking_id": saved_booking.id,
                        # Return created booking object for notification usage
                        "booking_obj": saved_booking,
                        "assigned_table": best_table.nombre,
                        "table_id": best_table.id,
                        "client_name": booking_request.nombre,
                        "date": date_str,
                        "time": time_str,
                        "pax": booking_request.pax,
                        "reasoning": f"Pre-reserva creada. Esperando confirmación WhatsApp.",
                    }

                # Default: return availability
                return {
                    "available": True,
                    "assigned_table": best_table.nombre,
                    "table_id": best_table.id,
                    "reasoning": f"Mesa {best_table.nombre} es óptima para {booking_request.pax} personas.",
                }
            else:
                return {
                    "available": False,
                    "assigned_table": None,
                    "alternatives": ["Cambiar hora", "Lista de espera"],
                    "reasoning": f"No hay disponibilidad para {booking_request.pax} personas el {date_str} a las {time_str}.",
                }

        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "reasoning": "Error procesando la solicitud.",
            }

    def confirm_booking_by_phone(self, phone: str) -> Dict[str, Any]:
        """Confirm latest pending booking for this phone."""
        booking = self.booking_engine.repo.find_pending_booking_by_phone(phone)
        if not booking:
            return {
                "success": False,
                "message": "No tengo ninguna reserva pendiente con este número.",
            }

        success = self.booking_engine.repo.update_booking_status(
            booking.id, "Confirmada"
        )
        if success:
            return {
                "success": True,
                "message": "¡Reserva confirmada! Nos vemos pronto. 🍷",
            }
        else:
            return {
                "success": False,
                "message": "Hubo un error técnico confirmando la reserva.",
            }

    def cancel_booking_by_phone(self, phone: str) -> Dict[str, Any]:
        """Cancel latest pending booking."""
        # We try to find pending first. If not, maybe confirmed?
        # User might want to cancel a confirmed one via WhatsApp too.
        # Let's stick to 'find_pending' first for safety, or improve find method.
        # For now, let's assume filtering relies on the Repo's capabilities.
        booking = self.booking_engine.repo.find_pending_booking_by_phone(phone)
        if not booking:
            # Try to simply log it or return specific msg
            return {
                "success": False,
                "message": "No encontré una reserva pendiente para cancelar.",
            }

        success = self.booking_engine.repo.update_booking_status(
            booking.id, "Cancelada"
        )
        if success:
            return {
                "success": True,
                "message": "Reserva cancelada correctamente. Esperamos verle en otra ocasión.",
            }
        else:
            return {"success": False, "message": "Error al cancelar."}

    def update_notes_by_phone(self, phone: str, note: str) -> Dict[str, Any]:
        """Add notes to latest pending booking."""
        booking = self.booking_engine.repo.find_pending_booking_by_phone(phone)
        if not booking:
            # Just note it generally? No, needs booking context.
            return {
                "success": False,
                "message": "No encontré su reserva para anotar eso.",
            }

        success = self.booking_engine.repo.update_booking_notes(booking.id, note)
        if success:
            return {
                "success": True,
                "message": "¡Oído! Hemos añadido esa nota a su reserva. 📝",
            }
        else:
            return {"success": False, "message": "Error guardando la nota."}

    def modify_booking_by_phone(
        self,
        phone: str,
        new_date: str = None,
        new_time: str = None,
        new_pax: int = None,
    ) -> Dict[str, Any]:
        """
        Modify an existing booking by phone number.
        Can change date, time, or number of people.
        """
        booking = self.booking_engine.repo.find_pending_booking_by_phone(phone)
        if not booking:
            return {
                "success": False,
                "message": "No encontré una reserva pendiente para modificar.",
            }

        # Build update description for response
        changes = []
        if new_date:
            changes.append(f"fecha al {new_date}")
        if new_time:
            changes.append(f"hora a las {new_time}")
        if new_pax:
            changes.append(f"{new_pax} personas")

        if not changes:
            return {
                "success": False,
                "message": "No especificaste qué cambiar de tu reserva.",
            }

        # Perform the modification
        success = self.booking_engine.repo.modify_booking(
            booking.id, new_date=new_date, new_time=new_time, new_pax=new_pax
        )

        if success:
            changes_str = ", ".join(changes)
            return {
                "success": True,
                "message": f"✅ Reserva actualizada: {changes_str}. ¡Nos vemos pronto! 🍷",
            }
        else:
            return {
                "success": False,
                "message": "Hubo un error al modificar tu reserva. Llama al 941 57 84 51.",
            }
