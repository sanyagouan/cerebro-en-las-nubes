"""
Human Agent: Generates empathetic, natural responses using GPT-4o.
The 'voice' of the restaurant that speaks to customers.
"""
from typing import Dict, Any
from src.application.agents.base_agent import BaseAgent

class HumanAgent(BaseAgent):
    """Generates natural, empathetic responses for customer interaction."""
    
    def __init__(self):
        super().__init__(model="gpt-4o")
        
        self.system_prompt = """Eres Alba, la recepcionista virtual de En Las Nubes Restobar en Logroño.

Tu personalidad:
- Amable, cálida y profesional
- Tono conversacional pero respetuoso
- Eficiente (no te enrollas)
- Transmites calidez y cercanía

Información del restaurante:
- Dirección: Calle Marqués de San Nicolás 136, Logroño
- Horario comidas: 13:30 a 17:30
- Horario cenas: 21:00 a 22:30
- CERRADO: Lunes (todo el día) y Domingo noche
- Viernes y Sábado: dos turnos de cena (21:00 y 22:30)

Reglas especiales:
- Grupos 7+ personas: solo turno 1 (21:00) en fines de semana
- Máximo 2 tronas
- Cachopo sin gluten: 24h antelación

Responde SIEMPRE en español de España.
NO uses frases robóticas como "¿En qué puedo ayudarte?"
SÍ usa expresiones naturales: "¡Perfecto!", "Estupendo", "Genial".
"""

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a natural response based on the situation.
        
        Args:
            context: {
                "situation": "confirm_booking",
                "data": {"table": "Mesa 4", "date": "25 enero", "time": "14:00", "pax": 4}
            }
        """
        situation = context.get("situation", "generic")
        data = context.get("data", {})
        
        # Build contextual prompt
        if situation == "confirm_booking":
            user_msg = f"""
            Confirma esta reserva al cliente de forma natural y cálida:
            - Mesa: {data.get('table', 'asignada')}
            - Fecha: {data.get('date', 'pendiente')}
            - Hora: {data.get('time', 'pendiente')}
            - Personas: {data.get('pax', 'pendiente')}
            - Nombre: {data.get('client_name', 'cliente')}
            """
        elif situation == "no_availability":
            user_msg = f"""
            Informa amablemente que no hay disponibilidad para:
            - Fecha: {data.get('date', 'la fecha solicitada')}
            - Hora: {data.get('time', 'la hora solicitada')}
            - Personas: {data.get('pax', 'el grupo')}
            
            Ofrece alternativas (cambiar hora, lista de espera).
            """
        elif situation == "faq":
            user_msg = f"Responde a esta pregunta: {data.get('question', '')}"
        else:
            user_msg = f"Genera una respuesta apropiada para: {data}"
        
        response = await self._call_llm(self.system_prompt, user_msg, temperature=0.8)
        
        return {
            "response": response,
            "situation": situation
        }
