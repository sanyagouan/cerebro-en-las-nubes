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
                "client_phone": "..."
            }
        """
        try:
            # Build booking request
            date_str = context.get("date", datetime.now().strftime("%Y-%m-%d"))
            time_str = context.get("time", "14:00")
            booking_dt = datetime.fromisoformat(f"{date_str}T{time_str}")
            
            booking_request = Booking(
                client_name=context.get("client_name", "Pending"),
                client_phone=context.get("client_phone", ""),
                date_time=booking_dt,
                pax=context.get("pax", 2)
            )
            
            # Use BookingEngine to find best table
            best_table = self.booking_engine.find_best_table(booking_request)
            
            if best_table:
                return {
                    "available": True,
                    "assigned_table": best_table.name,
                    "table_id": best_table.id,
                    "reasoning": f"Mesa {best_table.name} es óptima para {booking_request.pax} personas."
                }
            else:
                # Ask DeepSeek for alternatives
                user_msg = f"No hay mesa disponible para {booking_request.pax} personas el {date_str} a las {time_str}. ¿Qué alternativas puedo ofrecer?"
                reasoning = await self._call_llm(self.system_prompt, user_msg, temperature=0.3)
                
                return {
                    "available": False,
                    "assigned_table": None,
                    "alternatives": ["Cambiar hora", "Lista de espera"],
                    "reasoning": reasoning or "No hay disponibilidad en ese horario."
                }
                
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "reasoning": "Error procesando la solicitud."
            }
