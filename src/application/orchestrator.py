"""
Orchestrator: Coordinates the multi-agent pipeline.
Routes messages through Router -> Logic -> Human agents.
"""
from typing import Dict, Any
from src.application.agents.router_agent import RouterAgent
from src.application.agents.logic_agent import LogicAgent
from src.application.agents.human_agent import HumanAgent

class Orchestrator:
    """
    Main coordinator for the AI system.
    Handles the full conversation flow:
    1. Router classifies intent
    2. Logic processes bookings (if needed)
    3. Human generates response
    """
    
    def __init__(self):
        self.router = RouterAgent()
        self.logic = LogicAgent()
        self.human = HumanAgent()

    async def process_message(self, message: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process an incoming customer message through the full pipeline.
        
        Args:
            message: Customer's message text
            metadata: Optional context (phone, channel, etc.)
            
        Returns:
            {"response": "...", "intent": "...", "booking_result": {...}}
        """
        metadata = metadata or {}
        
        # Step 1: Classify Intent
        routing = await self.router.process({"message": message})
        intent = routing.get("intent", "other")
        guest_count = routing.get("guest_count")
        
        result = {
            "intent": intent,
            "confidence": routing.get("confidence", 0),
            "response": ""
        }
        
        # Step 2: Route to appropriate handler
        if intent == "reservation":
            # Extract booking details and process
            logic_result = await self.logic.process({
                "date": metadata.get("date", ""),
                "time": metadata.get("time", ""),
                "pax": guest_count or metadata.get("pax", 2),
                "client_name": metadata.get("client_name", ""),
                "client_phone": metadata.get("client_phone", "")
            })
            
            result["booking_result"] = logic_result
            
            # Generate human response based on result
            if logic_result.get("available"):
                human_result = await self.human.process({
                    "situation": "confirm_booking",
                    "data": {
                        "table": logic_result.get("assigned_table"),
                        "date": metadata.get("date"),
                        "time": metadata.get("time"),
                        "pax": guest_count,
                        "client_name": metadata.get("client_name")
                    }
                })
            else:
                human_result = await self.human.process({
                    "situation": "no_availability",
                    "data": {"date": metadata.get("date"), "time": metadata.get("time"), "pax": guest_count}
                })
                
            result["response"] = human_result.get("response", "")
            
        elif intent == "faq":
            # Handle FAQ directly with Human agent
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
