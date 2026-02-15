"""
Pydantic models para API móvil.
Request/Response models para endpoints CRUD.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, time, datetime
from src.core.entities.booking import BookingStatus, ZonePreference, BookingChannel, SpecialRequest


# ============ REQUEST MODELS ============

class CreateReservationRequest(BaseModel):
    """Request para crear una reserva nueva."""
    
    # Datos del cliente
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre completo del cliente")
    telefono: str = Field(..., pattern=r"^\+?[0-9\s\-\(\)]{9,20}$", description="Teléfono de contacto")
    email: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    
    # Datos de la reserva
    fecha: date = Field(..., description="Fecha de la reserva (YYYY-MM-DD)")
    hora: time = Field(..., description="Hora de llegada (HH:MM)")
    pax: int = Field(..., ge=1, le=20, description="Número de personas (1-20)")
    
    # Preferencias
    zona_preferencia: ZonePreference = Field(ZonePreference.NO_PREFERENCE)
    notas: Optional[str] = Field(None, max_length=500)
    
    # Metadatos
    canal: BookingChannel = Field(BookingChannel.PHONE, description="Canal de origen")
    vapi_call_id: Optional[str] = Field(None, description="ID de llamada VAPI si aplica")
    
    @field_validator('fecha')
    @classmethod
    def validate_fecha_futura(cls, v):
        """Verifica que la fecha sea futura."""
        if v < date.today():
            raise ValueError("La fecha debe ser futura")
        return v
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "nombre": "Juan Pérez",
                "telefono": "+34612345678",
                "email": "juan@example.com",
                "fecha": "2026-02-15",
                "hora": "20:30",
                "pax": 4,
                "zona_preferencia": "Interior",
                "notas": "Cumpleaños, necesitamos trona",
                "canal": "Telefono"
            }
        }


class UpdateReservationRequest(BaseModel):
    """Request para actualizar una reserva existente."""
    
    # Todos los campos son opcionales para permitir updates parciales
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    telefono: Optional[str] = Field(None, pattern=r"^\+?[0-9\s\-\(\)]{9,20}$")
    email: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    
    fecha: Optional[date] = None
    hora: Optional[time] = None
    pax: Optional[int] = Field(None, ge=1, le=20)
    
    zona_preferencia: Optional[ZonePreference] = None
    notas: Optional[str] = Field(None, max_length=500)
    estado: Optional[BookingStatus] = None
    
    mesa_asignada: Optional[str] = Field(None, description="Airtable record ID de mesa")
    
    @field_validator('fecha')
    @classmethod
    def validate_fecha_futura(cls, v):
        """Verifica que la fecha sea futura si se proporciona."""
        if v and v < date.today():
            raise ValueError("La fecha debe ser futura")
        return v
    
    class Config:
        use_enum_values = True


class CancelReservationRequest(BaseModel):
    """Request para cancelar una reserva."""

    motivo: Optional[str] = Field(None, max_length=300, description="Motivo de cancelación (opcional)")
    notificar_cliente: bool = Field(True, description="Enviar SMS/WhatsApp al cliente")

    class Config:
        json_schema_extra = {
            "example": {
                "motivo": "El cliente canceló con 2 horas de anticipación",
                "notificar_cliente": True
            }
        }


# ============ RESPONSE MODELS ============

class ReservationResponse(BaseModel):
    """Response con datos completos de una reserva."""
    
    id: str = Field(..., description="Airtable Record ID")
    
    # Datos del cliente
    nombre: str
    telefono: str
    email: Optional[str] = None
    
    # Datos de la reserva
    fecha: date
    hora: time
    pax: int
    
    # Estado y asignación
    estado: BookingStatus
    mesa_asignada: Optional[str] = None
    mesa_nombre: Optional[str] = None
    zona_preferencia: ZonePreference
    
    # Metadatos
    notas: Optional[str] = None
    canal: BookingChannel
    vapi_call_id: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "id": "rec1234567890",
                "nombre": "Juan Pérez",
                "telefono": "+34612345678",
                "email": "juan@example.com",
                "fecha": "2026-02-15",
                "hora": "20:30:00",
                "pax": 4,
                "estado": "Confirmada",
                "mesa_asignada": "recMESA123",
                "mesa_nombre": "T1",
                "zona_preferencia": "Interior",
                "notas": "Cumpleaños",
                "canal": "Telefono",
                "vapi_call_id": None,
                "created_at": "2026-02-11T10:00:00Z",
                "updated_at": "2026-02-11T15:30:00Z"
            }
        }


class PaginatedReservationsResponse(BaseModel):
    """Response paginado para lista de reservas."""

    reservations: List[ReservationResponse]
    total: int
    offset: int
    limit: int
    has_more: bool

    class Config:
        json_schema_extra = {
            "example": {
                "reservations": [],
                "total": 150,
                "offset": 0,
                "limit": 20,
                "has_more": True
            }
        }


# ============ TABLE MODELS ============

class CreateTableRequest(BaseModel):
    """Request para crear una mesa nueva."""

    id: str = Field(..., min_length=1, max_length=20, description="ID único (T1, C2-A, etc.)")
    nombre: str = Field(..., min_length=2, max_length=50, description="Nombre descriptivo")
    zona: str = Field(..., pattern="^(Terraza|Interior)$", description="Zona: Terraza o Interior")

    capacidad_min: int = Field(..., ge=0, le=20, description="Mínimo de comensales óptimo")
    capacidad_max: int = Field(..., ge=1, le=20, description="Máximo de comensales sin ampliar")

    ampliable: bool = Field(False, description="Si puede ampliarse con mesa auxiliar")
    auxiliar_requerida: Optional[str] = Field(None, max_length=20, description="ID de la mesa auxiliar necesaria")
    capacidad_ampliada: Optional[int] = Field(None, ge=1, le=30, description="Capacidad máxima con auxiliar")

    notas: Optional[str] = Field(None, max_length=300, description="Avisos obligatorios (ej: 'Junto al baño')")
    requiere_aviso: bool = Field(False, description="Si hay que avisar algo al cliente")

    prioridad: int = Field(5, ge=1, le=100, description="Orden de asignación (1-100, menor = más prioritaria)")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "T9",
                "nombre": "Terraza 9",
                "zona": "Terraza",
                "capacidad_min": 2,
                "capacidad_max": 6,
                "prioridad": 5,
                "notas": "Clima dependiente"
            }
        }


class UpdateTableRequest(BaseModel):
    """Request para actualizar una mesa existente."""

    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    zona: Optional[str] = Field(None, pattern="^(Terraza|Interior)$")

    capacidad_min: Optional[int] = Field(None, ge=0, le=20)
    capacidad_max: Optional[int] = Field(None, ge=1, le=20)

    ampliable: Optional[bool] = None
    auxiliar_requerida: Optional[str] = Field(None, max_length=20)
    capacidad_ampliada: Optional[int] = Field(None, ge=1, le=30)

    notas: Optional[str] = Field(None, max_length=300)
    requiere_aviso: Optional[bool] = None

    prioridad: Optional[int] = Field(None, ge=1, le=100)
    status: Optional[str] = Field(None, pattern="^(Libre|Ocupada|Reservada|Bloqueada)$", description="Estado de la mesa")

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Terraza VIP",
                "prioridad": 1,
                "notas": "Vista privilegiada"
            }
        }


class TableResponse(BaseModel):
    """Response con datos completos de una mesa."""

    id: str
    nombre: str
    zona: str  # "Terraza" | "Interior"

    capacidad_min: int
    capacidad_max: int

    ampliable: bool
    auxiliar_requerida: Optional[str] = None
    capacidad_ampliada: Optional[int] = None

    notas: Optional[str] = None
    requiere_aviso: bool

    prioridad: int
    status: str  # "Libre" | "Ocupada" | "Reservada" | "Bloqueada"

    class Config:
        json_schema_extra = {
            "example": {
                "id": "T1",
                "nombre": "Terraza 1",
                "zona": "Terraza",
                "capacidad_min": 2,
                "capacidad_max": 6,
                "ampliable": False,
                "auxiliar_requerida": None,
                "capacidad_ampliada": None,
                "notas": "Clima dependiente",
                "requiere_aviso": False,
                "prioridad": 5,
                "status": "Libre"
            }
        }
