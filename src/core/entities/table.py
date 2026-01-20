from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

# Zones are now flexible strings (Airtable may have custom values like "Junto Baño")
# Common known values:
# - "Interior"
# - "Terraza"
# - "Junto Baño"
# - etc.
class TableStatus(str, Enum):
    AVAILABLE = "Disponible"
    OCCUPIED = "Ocupada"
    RESERVED = "Reservada"
    BLOCKED = "Bloqueada"

class Table(BaseModel):
    id: str = Field(..., description="Airtable Record ID")
    name: str = Field(..., description="Nombre de la mesa (ej. T1, T2)")
    capacity_min: int = Field(2, description="Capacidad mínima óptima")
    capacity_max: int = Field(..., description="Capacidad máxima absoluta")
    zone: str = Field("Interior", description="Zona de ubicación (flexible)")
    is_combinable: bool = Field(False, description="Si se puede juntar con otras")
    status: TableStatus = Field(TableStatus.AVAILABLE, description="Estado actual")
    
    # Metadata para el algoritmo
    priority_score: int = Field(0, description="Puntuación para priorizar asignación")

    class Config:
        use_enum_values = True
