"""
Logic Agent: Uses DeepSeek for complex reasoning about availability.
Cost-effective for heavy logic tasks.
"""
import os
import json
from typing import Dict, Any
from datetime import datetime
from src.application.agents.base_agent import BaseAgent
from src.core.logic.booking_engine import BookingEngine
from src.core.entities.booking import Booking
from src.infrastructure.repositories.booking_repo import AirtableBookingRepository

class LogicAgent(BaseAgent):
    """Reasons about availability and suggests optimal booking options."""
    
    def __init__(self):
        super().__init__(
            model="deepseek-chat",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
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
            # Build booking request
            date_str = context.get("date", datetime.now().strftime("%Y-%m-%d"))
            time_str = context.get("time", "14:00")
            action = context.get("action", "check_availability")
            
            booking_dt = datetime.fromisoformat(f"{date_str}T{time_str}")
            
            booking_request = Booking(
                client_name=context.get("client_name", "Pendiente"),
                client_phone=context.get("client_phone", ""),
                date_time=booking_dt,
                pax=context.get("pax", 2),
                source="Voice AI"
            )
            
            # Use BookingEngine to find best table
            best_table = self.booking_engine.find_best_table(booking_request)
            
            if best_table:
                # If just checking availability, return result without saving
                if action == "check_availability":
                    return {
                        "available": True,
                        "assigned_table": best_table.name,
                        "table_id": best_table.id,
                        "reasoning": f"Mesa {best_table.name} disponible para {booking_request.pax} personas."
                    }
                
                # If creating reservation, ACTUALLY SAVE TO AIRTABLE
                if action == "create_reservation":
                    booking_request.assigned_table_id = best_table.id
                    # Status is Pending until WhatsApp confirmation? Or Confirmed immediately for Voice?
                    # Plan says: Create -> Send Whatsapp -> Reply YES -> Confirm.
                    # Voice callers usually consider it confirmed. 
                    # Let's set to PENDING for the closed loop flow? 
                    # Or 'Confirmada' but send confirmation msg?
                    # User said: "Responde SI para reconfirmar".
                    # Let's start with PENDING (or a specific 'A Reconfirmar' status if enum allows).
                    # Enum has 'Pendiente' and 'Confirmada'.
                    # Let's stick to 'Confirmada' for Voice (since they talked to AI), and use WhatsApp for RE-confirmation or just details.
                    # Wait, user wants "Si responde SI -> Airtable se actualiza". That implies status is NOT confirmed yet.
                    # So we set to PENDING.
                    booking_request.status = "Pendiente"
                    
                    # Save to Airtable
                    saved_booking = self.booking_engine.repo.create_booking(booking_request)
                    
                    return {
                        "available": True,
                        "booking_created": True,
                        "booking_id": saved_booking.id,
                        # Return created booking object for notification usage
                        "booking_obj": saved_booking, 
                        "assigned_table": best_table.name,
                        "table_id": best_table.id,
                        "client_name": booking_request.client_name,
                        "date": date_str,
                        "time": time_str,
                        "pax": booking_request.pax,
                        "reasoning": f"Pre-reserva creada. Esperando confirmación WhatsApp."
                    }
                
                # Default: return availability
                return {
                    "available": True,
                    "assigned_table": best_table.name,
                    "table_id": best_table.id,
                    "reasoning": f"Mesa {best_table.name} es óptima para {booking_request.pax} personas."
                }
            else:
                return {
                    "available": False,
                    "assigned_table": None,
                    "alternatives": ["Cambiar hora", "Lista de espera"],
                    "reasoning": f"No hay disponibilidad para {booking_request.pax} personas el {date_str} a las {time_str}."
                }
                
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "reasoning": "Error procesando la solicitud."
            }

    def confirm_booking_by_phone(self, phone: str) -> Dict[str, Any]:
        """Confirm latest pending booking for this phone."""
        booking = self.booking_engine.repo.find_pending_booking_by_phone(phone)
        if not booking:
            return {"success": False, "message": "No tengo ninguna reserva pendiente con este número."}
            
        success = self.booking_engine.repo.update_booking_status(booking.id, "Confirmada")
        if success:
            return {"success": True, "message": "¡Reserva confirmada! Nos vemos pronto. 🍷"}
        else:
            return {"success": False, "message": "Hubo un error técnico confirmando la reserva."}

    def cancel_booking_by_phone(self, phone: str) -> Dict[str, Any]:
        """Cancel latest pending booking."""
        # We try to find pending first. If not, maybe confirmed?
        # User might want to cancel a confirmed one via WhatsApp too.
        # Let's stick to 'find_pending' first for safety, or improve find method.
        # For now, let's assume filtering relies on the Repo's capabilities.
        booking = self.booking_engine.repo.find_pending_booking_by_phone(phone)
        if not booking:
             # Try to simply log it or return specific msg
            return {"success": False, "message": "No encontré una reserva pendiente para cancelar."}
            
        success = self.booking_engine.repo.update_booking_status(booking.id, "Cancelada")
        if success:
            return {"success": True, "message": "Reserva cancelada correctamente. Esperamos verle en otra ocasión."}
        else:
            return {"success": False, "message": "Error al cancelar."}

    def update_notes_by_phone(self, phone: str, note: str) -> Dict[str, Any]:
        """Add notes to latest pending booking."""
        booking = self.booking_engine.repo.find_pending_booking_by_phone(phone)
        if not booking:
             # Just note it generally? No, needs booking context.
            return {"success": False, "message": "No encontré su reserva para anotar eso."}
            
        success = self.booking_engine.repo.update_booking_notes(booking.id, note)
        if success:
            return {"success": True, "message": "¡Oído! Hemos añadido esa nota a su reserva. 📝"}
        else:
            return {"success": False, "message": "Error guardando la nota."}
