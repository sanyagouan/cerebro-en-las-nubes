import os
import httpx
from datetime import datetime
from typing import List, Dict, Any, Optional
from loguru import logger

class VAPIService:
    """
    Servicio para interactuar con la API de VAPI.ai.
    Documentación: https://docs.vapi.ai/api-reference/
    """
    
    def __init__(self):
        self.api_key = os.getenv("VAPI_API_KEY")
        self.base_url = "https://api.vapi.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

    async def get_calls(self, limit: int = 100) -> Dict[str, Any]:
        """
        Recupera la lista de llamadas de VAPI.
        """
        if not self.api_key:
            logger.warning("VAPI_API_KEY no configurada")
            return {"calls": [], "total": 0}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/call",
                    headers=self.headers,
                    params={"limit": limit}
                )
                response.raise_for_status()
                calls_data = response.json()
                
                # Mapear al formato esperado por el frontend
                formatted_calls = []
                for call in calls_data:
                    # Intentar extraer metadatos de la reserva si existen
                    metadata = call.get("analysis", {}).get("structuredData", {})
                    
                    formatted_calls.append({
                        "id": call.get("id"),
                        "call_id": call.get("id"),
                        "phone_number": call.get("customer", {}).get("number", "N/A"),
                        "direction": call.get("type", "inbound"),
                        "status": self._map_status(call.get("status", "")),
                        "duration_seconds": call.get("duration", 0),
                        "started_at": call.get("createdAt", datetime.now().isoformat()),
                        "ended_at": call.get("endedAt"),
                        "transcript": call.get("transcript"),
                        "summary": call.get("analysis", {}).get("summary"),
                        "reservation_created": bool(metadata.get("reservation_id") or metadata.get("date")),
                        "reservation_id": metadata.get("reservation_id"),
                        "cost": call.get("cost", 0),
                        "metadata": {
                            "customer_name": metadata.get("customerName"),
                            "party_size": metadata.get("partySize"),
                            "date": metadata.get("date"),
                            "time": metadata.get("time"),
                            "error_message": call.get("error")
                        }
                    })
                
                return {
                    "calls": formatted_calls,
                    "total": len(formatted_calls)
                }
        except Exception as e:
            logger.error(f"Error recuperando llamadas de VAPI: {e}")
            return {"calls": [], "total": 0, "error": str(e)}

    async def get_analytics(self) -> Dict[str, Any]:
        """
        Calcula analíticas agregadas de las llamadas de VAPI.
        """
        res = await self.get_calls(limit=100)
        calls = res.get("calls", [])
        
        if not calls:
            return self._empty_analytics()

        total_calls = len(calls)
        completed = [c for c in calls if c["status"] == "completed"]
        failed = [c for c in calls if c["status"] == "failed"]
        no_answer = [c for c in calls if c["status"] == "no-answer"]
        busy = [c for c in calls if c["status"] == "busy"]
        
        reservations = [c for c in calls if c["reservation_created"]]
        
        total_duration = sum(c.get("duration_seconds", 0) or 0 for c in calls)
        total_cost = sum(c.get("cost", 0) or 0 for c in calls)

        return {
            "total_calls": total_calls,
            "completed_calls": len(completed),
            "failed_calls": len(failed),
            "avg_duration_seconds": total_duration / total_calls if total_calls > 0 else 0,
            "total_cost": total_cost,
            "conversion_rate": len(reservations) / total_calls if total_calls > 0 else 0,
            "reservations_created": len(reservations),
            "calls_by_status": {
                "completed": len(completed),
                "failed": len(failed),
                "no_answer": len(no_answer),
                "busy": len(busy)
            },
            "calls_by_hour": [] # Opcional: implementar si se requiere gráfica temporal
        }

    def _map_status(self, vapi_status: str) -> str:
        mapping = {
            "ended": "completed",
            "failed": "failed",
            "in-progress": "in-progress",
            "no-answer": "no-answer",
            "busy": "busy"
        }
        return mapping.get(vapi_status, "completed")

    def _empty_analytics(self) -> Dict[str, Any]:
        return {
            "total_calls": 0,
            "completed_calls": 0,
            "failed_calls": 0,
            "avg_duration_seconds": 0,
            "total_cost": 0,
            "conversion_rate": 0,
            "reservations_created": 0,
            "calls_by_status": {
                "completed": 0,
                "failed": 0,
                "no_answer": 0,
                "busy": 0
            },
            "calls_by_hour": []
        }

vapi_service = VAPIService()
