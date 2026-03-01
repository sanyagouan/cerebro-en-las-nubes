from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum


class TableZone(str, Enum):
    TERRAZA = "Terraza"
    INTERIOR = "Interior"


class TableStatus(str, Enum):
    AVAILABLE = "Libre"
    OCCUPIED = "Ocupada"
    RESERVED = "Reservada"
    BLOCKED = "Bloqueada"


class Table(BaseModel):
    """Modelo de Mesa V2 - Configuración completa del restaurante."""
    
    id: str = Field(..., description="ID único (T1, C2-A, AUX-1, etc.)")
    nombre: str = Field(..., description="Nombre descriptivo")
    zona: TableZone = Field(..., description="Zona: Terraza o Interior")
    
    # Capacidades
    capacidad_min: int = Field(..., description="Mínimo de comensales óptimo")
    capacidad_max: int = Field(..., description="Máximo de comensales sin ampliar")
    
    # Ampliación con auxiliares
    ampliable: bool = Field(False, description="Si puede ampliarse con mesa auxiliar")
    auxiliar_requerida: Optional[str] = Field(None, description="ID de la mesa auxiliar necesaria")
    capacidad_ampliada: Optional[int] = Field(None, description="Capacidad máxima con auxiliar")
    
    # Notas y restricciones
    notas: Optional[str] = Field(None, description="Avisos obligatorios (ej: 'Junto al baño')")
    requiere_aviso: bool = Field(False, description="Si hay que avisar algo al cliente")
    
    # Prioridad de asignación (1 = más prioritaria)
    prioridad: int = Field(5, description="Orden de asignación (1-10)")
    
    # Estado actual
    status: TableStatus = Field(TableStatus.AVAILABLE)

    class Config:
        use_enum_values = True


# ========== CONFIGURACIÓN DE MESAS DEL RESTAURANTE ==========

MESAS_TERRAZA: List[dict] = [
    {"id": "T1", "nombre": "Terraza 1", "zona": "Terraza", "capacidad_min": 2, "capacidad_max": 6, "prioridad": 5, "notas": "Clima dependiente"},
    {"id": "T2", "nombre": "Terraza 2", "zona": "Terraza", "capacidad_min": 2, "capacidad_max": 6, "prioridad": 5, "notas": "Clima dependiente"},
    {"id": "T3", "nombre": "Terraza 3", "zona": "Terraza", "capacidad_min": 2, "capacidad_max": 6, "prioridad": 5, "notas": "Clima dependiente"},
    {"id": "T4", "nombre": "Terraza 4", "zona": "Terraza", "capacidad_min": 2, "capacidad_max": 6, "prioridad": 5, "notas": "Clima dependiente"},
    {"id": "T5", "nombre": "Terraza 5", "zona": "Terraza", "capacidad_min": 2, "capacidad_max": 6, "prioridad": 5, "notas": "Clima dependiente"},
    {"id": "T6", "nombre": "Terraza 6", "zona": "Terraza", "capacidad_min": 2, "capacidad_max": 6, "prioridad": 5, "notas": "Clima dependiente"},
    {"id": "T7", "nombre": "Terraza 7", "zona": "Terraza", "capacidad_min": 2, "capacidad_max": 6, "prioridad": 5, "notas": "Clima dependiente"},
    {"id": "T8", "nombre": "Terraza 8", "zona": "Terraza", "capacidad_min": 2, "capacidad_max": 6, "prioridad": 5, "notas": "Clima dependiente"},
]

MESAS_INTERIOR: List[dict] = [
    # Mesas de 2 personas
    {"id": "C2-A", "nombre": "Mesa 2A", "zona": "Interior", "capacidad_min": 1, "capacidad_max": 2, "prioridad": 1},
    {"id": "C2-B", "nombre": "Mesa 2B", "zona": "Interior", "capacidad_min": 1, "capacidad_max": 3, "prioridad": 2, "notas": "Flexible hasta 3"},
    {"id": "C2-C", "nombre": "Mesa 2C", "zona": "Interior", "capacidad_min": 1, "capacidad_max": 2, "prioridad": 3, "notas": "Junto al baño - AVISAR", "requiere_aviso": True},
    
    # Mesas de 6 personas
    {"id": "C6-A", "nombre": "Mesa 6A", "zona": "Interior", "capacidad_min": 3, "capacidad_max": 6, "prioridad": 6},
    {"id": "C6-B", "nombre": "Mesa 6B", "zona": "Interior", "capacidad_min": 3, "capacidad_max": 6, "prioridad": 7, 
     "ampliable": True, "auxiliar_requerida": "AUX-4", "capacidad_ampliada": 8},
    
    # Mesas de 8 personas
    {"id": "C8-A", "nombre": "Mesa 8A", "zona": "Interior", "capacidad_min": 4, "capacidad_max": 8, "prioridad": 8,
     "ampliable": True, "auxiliar_requerida": "AUX-1", "capacidad_ampliada": 10},
    {"id": "C8-B", "nombre": "Mesa 8B", "zona": "Interior", "capacidad_min": 4, "capacidad_max": 8, "prioridad": 8,
     "ampliable": True, "auxiliar_requerida": "AUX-2", "capacidad_ampliada": 10},
    {"id": "C8-C", "nombre": "Mesa 8C", "zona": "Interior", "capacidad_min": 4, "capacidad_max": 8, "prioridad": 8,
     "ampliable": True, "auxiliar_requerida": "AUX-3", "capacidad_ampliada": 10},
    
    # Mesa de 7 personas
    {"id": "C7", "nombre": "Mesa 7", "zona": "Interior", "capacidad_min": 4, "capacidad_max": 8, "prioridad": 9},
]

MESAS_AUXILIARES: List[dict] = [
    {"id": "AUX-1", "nombre": "Auxiliar 1", "zona": "Interior", "capacidad_min": 0, "capacidad_max": 2, "prioridad": 99, "notas": "Para ampliar C8-A"},
    {"id": "AUX-2", "nombre": "Auxiliar 2", "zona": "Interior", "capacidad_min": 0, "capacidad_max": 2, "prioridad": 99, "notas": "Para ampliar C8-B"},
    {"id": "AUX-3", "nombre": "Auxiliar 3", "zona": "Interior", "capacidad_min": 0, "capacidad_max": 2, "prioridad": 99, "notas": "Para ampliar C8-C"},
    {"id": "AUX-4", "nombre": "Auxiliar 4", "zona": "Interior", "capacidad_min": 0, "capacidad_max": 2, "prioridad": 99, "notas": "Para ampliar C6-B"},
]

# Todas las mesas
ALL_MESAS = MESAS_TERRAZA + MESAS_INTERIOR + MESAS_AUXILIARES


def get_all_tables() -> List[Table]:
    """Devuelve todas las mesas como objetos Table."""
    return [Table(**mesa) for mesa in ALL_MESAS]


def get_tables_by_zone(zona: TableZone) -> List[Table]:
    """Devuelve mesas filtradas por zona."""
    return [t for t in get_all_tables() if t.zona == zona.value]


def get_table_by_id(table_id: str) -> Optional[Table]:
    """Busca una mesa por su ID."""
    for mesa in ALL_MESAS:
        if mesa["id"] == table_id:
            return Table(**mesa)
    return None
