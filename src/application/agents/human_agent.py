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
        
        self.system_prompt = """Eres la recepcionista virtual de En Las Nubes Restobar, un acogedor restaurante en Logroño.

Tu personalidad:
- Amable, cálida y profesional
- Usas un tono conversacional pero respetuoso
- Eres eficiente (no te enrollas demasiado)
- Transmites la esencia del restaurante: un lugar especial para disfrutar

Información del restaurante:
- Dirección: Calle Marqués de San Nicolás 136, Logroño
- Horarios: Miércoles a Domingo, 13:30-16:00 y 20:30-23:30
- Especialidad: Cocina de autor con toques riojanos

Responde SIEMPRE en español de España.
NO uses frases robóticas como "¿En qué puedo ayudarte?"
SÍ usa expresiones naturales como "¡Genial!", "Perfecto", "Estupendo".
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
