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

- "reservation": Quiere hacer, modificar o cancelar una reserva.
- "faq": Pregunta general (horarios, ubicación, menú, alergias, etc.).
- "provider": Es un proveedor o vendedor (no un cliente).
- "human": Pide hablar con una persona explícitamente.
- "other": Cualquier cosa que no encaje.

También extrae el número de personas (guest_count) si se menciona.

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
