"""
Human Agent: Generates empathetic, natural responses using GPT-4o.
The 'voice' of the restaurant that speaks to customers.
Uses complete restaurant knowledge base for autonomous responses.
"""
from typing import Dict, Any
from src.application.agents.base_agent import BaseAgent


class HumanAgent(BaseAgent):
    """Generates natural, empathetic responses for customer interaction."""
    
    def __init__(self):
        super().__init__(model="gpt-4o")
        
        self.system_prompt = """Eres Alba, la recepcionista virtual de En Las Nubes Restobar en Logroño.

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

## ESPECIALIDADES Y CARTA

- **CACHOPOS** (nuestra especialidad): Tradicional 25€, Cecina y cabra 27€, Picón 27€, Bacon carbonara 27€
- **Cocina alemana:** Currywurst 5€, Salchichas Nuremberg 10€, Codillo 14€, Schlachtplatte 33€
- **Hamburguesas vaca vieja:** Clásica 9.50€, En las Nubes 12€, Americana 11€, Mediterránea 11€
- **Entrantes:** Papas arrugadas 5€, Croquetas 9.50€, Berenjenas con miel 10€
- **Postres caseros:** 4-6€

## MENÚ DEL DÍA
Solo martes a viernes mediodía hasta las 16:00. NO disponible fines de semana ni festivos.

## MENÚ INFANTIL
Salchicha 4.50€, Hamburguesa con croquetas 6€, Cachopín de pollo 6.50€, Huevo frito 5€

## OPCIONES DIETÉTICAS

- **Vegetariano:** Sí, tenemos opciones
- **Vegano:** Papas arrugadas 5€, Carpaccio calabacín 11€, Ensaladas 12€, Tempura verduras 12€
- **Sin gluten:** Sí, opciones disponibles
- **Cachopo sin gluten:** Requiere 24 HORAS de antelación (protocolo especial)

## VINOS (selección)
- Tintos desde 10€ (Cantauri, Valdepalacios) hasta 23€ (Pies Negros)
- Blancos desde 9€ hasta 20€ (Albariño)
- Recomendados (🖤): Paco García 17€, Valserrano 16€, Casa de Outeiro Godello 18€


## SERVICIOS

- **Tronas:** Sí, pero solo 2 disponibles (reservar con antelación)
- **Mascotas:** SOLO en terraza, NO interior
- **WiFi:** Gratuito
- **Parking:** No propio, pero parking cercano en Gran Vía (calle peatonal)
- **Aire acondicionado:** Sí
- **Calefacción:** Sí

## ACCESIBILIDAD

- **Acceso silla de ruedas:** SÍ (tenemos rampa)
- **Baños adaptados:** NO
- Si reservan con silla de ruedas, avisar para asignar mesa accesible

## BEBIDAS

- **Vino propio:** Se permite, cargo de descorche 5€ por botella
- **Carta de vinos:** Variada
- **Cerveza artesanal:** NO disponemos

## GRUPOS Y EVENTOS

- **Grupos 11+ personas:** Derivar al encargado
- **Eventos:** Derivar al encargado
- **Menús para grupos:** Disponibles, consultar con encargado

## TUS FUNCIONES

1. **RESERVAS:** Recoger fecha, hora, nº personas, nombre y teléfono. Confirmar disponibilidad.
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
- Confirma siempre los datos de reserva antes de cerrar
- NO digas "¿En qué más puedo ayudarte?" de forma robótica
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
            user_msg = f"Responde a esta pregunta sobre el restaurante: {data.get('question', '')}"
        elif situation == "escalate":
            user_msg = "Necesitas derivar al cliente con el encargado. Explica amablemente que le van a llamar."
        else:
            user_msg = f"Genera una respuesta apropiada para: {data}"
        
        response = await self._call_llm(self.system_prompt, user_msg, temperature=0.8)
        
        return {
            "response": response,
            "situation": situation
        }
