from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class BookingStatus(str, Enum):
    PENDING = "Pendiente"
    CONFIRMED = "Confirmada"
    CANCELLED = "Cancelada"
    SEATED = "Sentada"
    COMPLETED = "Completada"

class Booking(BaseModel):
    id: Optional[str] = Field(None, description="Airtable Record ID (null si es nueva)")
    client_name: str
    client_phone: str
    date_time: datetime
    pax: int
    notes: Optional[str] = None
    status: BookingStatus = Field(BookingStatus.PENDING)
    
    # Asignación
    assigned_table_id: Optional[str] = None
    
    # Origen (Vital para métricas)
    source: str = Field("Voice AI", description="Canal de entrada (Voice, WhatsApp, Web)")

    class Config:
        use_enum_values = True
