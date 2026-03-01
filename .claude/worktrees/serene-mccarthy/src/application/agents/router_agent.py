"""
Router Agent: Classifies customer intent using GPT-4o-mini.
Fast, cheap, and accurate for simple classification tasks.
"""
import json
from typing import Dict, Any
from src.application.agents.base_agent import BaseAgent

class RouterAgent(BaseAgent):
    """Classifies intent: reservation, faq, provider, other."""
    
    def __init__(self):
        super().__init__(model="gpt-4o-mini")
        
        self.system_prompt = """Eres un asistente de clasificación para En Las Nubes Restobar.
Tu tarea es clasificar la intención del cliente en UNA de estas categorías:

- "confirmation": El usuario confirma una reserva existente (ej: "sí", "confirmar", "ok", "voy").
- "cancellation": El usuario quiere cancelar (ej: "cancelar", "anular", "no puedo ir").
- "update_notes": El usuario da información extra (alergias, tronas, terraza, cumpleaños).
- "reservation": Quiere hacer una NUEVA reserva o buscar disponibilidad.
- "faq": Pregunta general (horarios, ubicación, menú, precios).
- "provider": Es un proveedor o vendedor.
- "human": Pide hablar con una persona.
- "other": Cualquier cosa que no encaje.

IMPORTANTE:
- Si dicen "quiero reservar" -> es "reservation".
- Si dicen solo "sí" o "ok" tras un mensaje nuestro -> es "confirmation".
- Si dicen "soy celíaco" -> es "update_notes".

RESPONDE SOLO con JSON válido:
{"intent": "categoria", "guest_count": numero o null, "confidence": 0.0-1.0}
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
        
        response = await self._call_llm(self.system_prompt, user_message, temperature=0.1)
        
        try:
            # Parse JSON response
            result = json.loads(response)
            return {
                "intent": result.get("intent", "other"),
                "guest_count": result.get("guest_count"),
                "confidence": result.get("confidence", 0.5)
            }
        except json.JSONDecodeError:
            # Fallback if LLM doesn't return valid JSON
            return {"intent": "other", "guest_count": None, "confidence": 0.0}
