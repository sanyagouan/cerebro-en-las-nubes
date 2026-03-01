"""
Router Agent: Classifies customer intent using GPT-4o-mini.
Fast, cheap, and accurate for simple classification tasks.
"""

import json
from datetime import datetime
from typing import Dict, Any
from src.application.agents.base_agent import BaseAgent


class RouterAgent(BaseAgent):
    """Classifies intent: reservation, faq, provider, other."""

    def __init__(self):
        super().__init__(model="gpt-4o-mini")

        self.base_system_prompt = """Eres un asistente de clasificación para En Las Nubes Restobar.
Tu tarea es clasificar la intención del cliente en UNA de estas categorías:

- "confirmation": El usuario confirma una reserva existente (ej: "sí", "confirmar", "ok", "voy").
- "cancellation": El usuario quiere cancelar (ej: "cancelar", "anular", "no puedo ir").
- "modify_reservation": El usuario quiere CAMBIAR su reserva existente (hora, fecha, personas).
  Ejemplos: "cambio la hora a las 22:00", "somos 6 en vez de 4", "quiero cambiar al viernes".
- "update_notes": El usuario da información extra (alergias, tronas, terraza, cumpleaños, mascota).
  Ejemplos: "quiero una trona", "somos celíacos", "tenemos un bebé", "vengo con perro".
- "reservation": Quiere hacer una NUEVA reserva o buscar disponibilidad.
- "faq": Pregunta general sobre el restaurante (horarios, ubicación, menú, precios, carta).
  Ejemplos: "¿tenéis cachopo sin gluten?", "¿cuál es el horario?", "¿hay parking?".
- "provider": Es un proveedor o vendedor.
- "human": Pide hablar con una persona.
- "other": Cualquier cosa que no encaje.

IMPORTANTE - DISAMBIGUACIÓN:
- "¿Tenéis cachopo sin gluten?" -> es "faq" (pregunta sobre disponibilidad del menú).
- "Quiero el cachopo sin gluten" -> es "update_notes" (petición para su reserva).
- "Cambio la hora" -> es "modify_reservation".
- "Quiero reservar" -> es "reservation".
- Solo "sí" o "ok" tras mensaje nuestro -> es "confirmation".

EXTRACCIÓN DE PARÁMETROS:
Si detectas fecha, hora, o número de personas en el mensaje, extraelos:
- new_time: hora en formato HH:MM (ej: "22:00")
- new_date: fecha en formato YYYY-MM-DD (ej: "2026-03-01")  
- new_pax: número de personas (ej: 6)
- special_request: texto de la petición especial

RESPONDE SOLO con JSON válido:
{
  "intent": "categoria",
  "guest_count": numero o null,
  "confidence": 0.0-1.0,
  "new_time": "HH:MM" o null,
  "new_date": "YYYY-MM-DD" o null,
  "new_pax": numero o null,
  "special_request": "texto" o null
}
"""

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify the customer's message.

        Args:
            context: {"message": "Quiero reservar para 4 personas"}

        Returns:
            {"intent": "reservation", "guest_count": 4, "confidence": 0.95}
        """
        user_message = context.get("message", "")

        if not user_message:
            return {"intent": "other", "guest_count": None, "confidence": 0.0}

        # Inject current date so LLM can calculate correct year
        now = datetime.now()
        current_date_info = f"""
FECHA ACTUAL PARA REFERENCIA:
- Hoy es: {now.strftime("%Y-%m-%d")} ({now.strftime("%A")} en español)
- Cuando el usuario diga "mañana", "sábado", "el 1 de marzo", etc., calcula la fecha correcta usando {now.year} como año actual.
"""
        system_prompt = self.base_system_prompt + current_date_info

        response = await self._call_llm(system_prompt, user_message, temperature=0.1)

        try:
            # Parse JSON response
            result = json.loads(response)
            return {
                "intent": result.get("intent", "other"),
                "guest_count": result.get("guest_count"),
                "confidence": result.get("confidence", 0.5),
                # Nuevos campos para modify_reservation y update_notes
                "new_time": result.get("new_time"),
                "new_date": result.get("new_date"),
                "new_pax": result.get("new_pax"),
                "special_request": result.get("special_request"),
            }
        except json.JSONDecodeError:
            # Fallback if LLM doesn't return valid JSON
            return {"intent": "other", "guest_count": None, "confidence": 0.0}
