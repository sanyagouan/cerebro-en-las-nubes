from pydantic import BaseModel, Field
from typing import Optional

class Reservation(BaseModel):
    """
    Domain Model for a Restaurant Reservation.
    """
    nombre_cliente: str
    telefono_cliente: str
    fecha: str # YYYY-MM-DD
    hora: str # HH:MM
    num_personas: int
    notas: Optional[str] = ""
    origen: Optional[str] = "VAPI_VOICE"
    
    # Optional fields for internal tracking
    id: Optional[str] = None
    created_at: Optional[str] = None
    status: Optional[str] = "pending"
