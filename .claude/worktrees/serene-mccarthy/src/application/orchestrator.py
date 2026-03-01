"""
Orchestrator: Coordinates the multi-agent pipeline.
Routes messages through Router -> Logic -> Human agents.
Now integrated with WhatsAppService for closed-loop notifications.
"""
from typing import Dict, Any
from src.application.agents.router_agent import RouterAgent
from src.application.agents.logic_agent import LogicAgent
from src.application.agents.human_agent import HumanAgent
from src.infrastructure.services.whatsapp_service import WhatsAppService

class Orchestrator:
    """
    Main coordinator for the AI system.
    Handles the full conversation flow:
    1. Router classifies intent
    2. Logic processes bookings (if needed)
    3. Human generates response
    4. WhatsApp Service handles notifications
    """
    
    def __init__(self):
        self.router = RouterAgent()
        self.logic = LogicAgent()
        self.human = HumanAgent()
        self.whatsapp = WhatsAppService()

    async def process_message(self, message: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process an incoming customer message through the full pipeline.
        """
        metadata = metadata or {}
        client_phone = metadata.get("client_phone", "")
        
        # Step 1: Classify Intent
        # We pass phone context implicitly? Not needed for classification yet.
        routing = await self.router.process({"message": message})
        intent = routing.get("intent", "other")
        guest_count = routing.get("guest_count")
        
        result = {
            "intent": intent,
            "confidence": routing.get("confidence", 0),
            "response": ""
        }
        
        # Step 2: Route to appropriate handler
        
        # --- NEW: WhatsApp Interactive Flow Intents ---
        if intent == "confirmation":
            # Client said "Sí" / "Confirmo"
            logic_res = self.logic.confirm_booking_by_phone(client_phone)
            result["response"] = logic_res.get("message")
            return result
            
        elif intent == "cancellation":
            # Client said "Cancelar"
            logic_res = self.logic.cancel_booking_by_phone(client_phone)
            result["response"] = logic_res.get("message")
            return result
        
        elif intent == "update_notes":
            # Client noted an allergy or request
            # Router should ideally extract the note content?
            # Or we just use the full message as the note.
            logic_res = self.logic.update_notes_by_phone(client_phone, message)
            result["response"] = logic_res.get("message")
            return result
        
        # --- Standard AI Conversation ---
        
        if intent == "reservation":
            # Extract booking details and process
            logic_result = await self.logic.process({
                "date": metadata.get("date", ""),
                "time": metadata.get("time", ""),
                "pax": guest_count or metadata.get("pax", 2),
                "client_name": metadata.get("client_name", ""),
                "client_phone": client_phone,
                "action": "create_reservation" if _is_confirmation_intent(message) else "check_availability"
            })
            
            result["booking_result"] = logic_result
            
            # --- CRITICAL: Send WhatsApp Notification on Success ---
            if logic_result.get("booking_created"):
                booking_obj = logic_result.get("booking_obj")
                if booking_obj:
                    # Fire and forget (or log result)
                    self.whatsapp.send_premium_confirmation(booking_obj)
            
            # Generate human response based on result
            if logic_result.get("available"):
                if logic_result.get("booking_created"):
                    # Special response for created
                    result["response"] = f"¡Perfecto! Hemos pre-reservado su mesa. Le acabo de enviar un WhatsApp con los detalles. Por favor, responda SÍ a ese mensaje para confirmar definitivamente."
                else:
                    human_result = await self.human.process({
                        "situation": "confirm_booking",
                        "data": {
                            "table": logic_result.get("assigned_table"),
                            "date": logic_result.get("date", metadata.get("date")),
                            "time": logic_result.get("time", metadata.get("time")),
                            "pax": logic_result.get("pax", guest_count),
                            "client_name": metadata.get("client_name")
                        }
                    })
                    result["response"] = human_result.get("response", "")
            else:
                human_result = await self.human.process({
                    "situation": "no_availability",
                    "data": {"date": metadata.get("date"), "time": metadata.get("time"), "pax": guest_count}
                })
                result["response"] = human_result.get("response", "")
                
        elif intent == "faq":
            human_result = await self.human.process({
                "situation": "faq",
                "data": {"question": message}
            })
            result["response"] = human_result.get("response", "")
            
        elif intent == "human":
            result["response"] = "Un momento, le paso con un compañero..."
            result["needs_human_handoff"] = True
            
        else:
            # Generic response
            human_result = await self.human.process({
                "situation": "generic",
                "data": {"message": message}
            })
            result["response"] = human_result.get("response", "Lo siento, no he entendido bien.")
        
        return result

def _is_confirmation_intent(msg: str) -> bool:
    """Heuristic to check if user wants to create booking vs just checking."""
    # This logic should be in Router, but kept simple here for now.
    msg = msg.lower()
    return any(x in msg for x in ["reservar", "quiero mesa", "guardame", "confirmar"])
