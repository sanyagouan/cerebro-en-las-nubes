from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime, date, time
from enum import Enum


class BookingStatus(str, Enum):
    PENDING = "Pendiente"
    CONFIRMED = "Confirmada"
    SEATED = "Sentada"
    COMPLETED = "Completada"
    CANCELLED = "Cancelada"
    NO_SHOW = "NoShow"


class BookingChannel(str, Enum):
    VAPI = "VAPI"
    WHATSAPP = "WhatsApp"
    PHONE = "Telefono"
    WALKIN = "Presencial"


class ZonePreference(str, Enum):
    TERRAZA = "Terraza"
    INTERIOR = "Interior"
    NO_PREFERENCE = "Sin preferencia"


class SpecialRequest(str, Enum):
    CACHOPO_SIN_GLUTEN = "cachopo_sin_gluten"
    TRONA = "trona"
    MASCOTA = "mascota"
    SILLA_RUEDAS = "silla_ruedas"
    CUMPLEANOS = "cumpleanos"
    EVENTO_PRIVADO = "evento_privado"


class Booking(BaseModel):
    """Modelo de Reserva V2 - Sistema completo de gestión."""
    
    # Identificadores
    id: Optional[str] = Field(None, description="Airtable Record ID (null si es nueva)")
    vapi_call_id: Optional[str] = Field(None, description="ID de llamada VAPI para trazabilidad")
    
    # Datos del cliente
    nombre: str = Field(..., description="Nombre completo del cliente")
    telefono: str = Field(..., description="Teléfono de contacto (WhatsApp preferiblemente)")
    email: Optional[str] = Field(None, description="Email (opcional)")
    
    # Datos de la reserva
    fecha: date = Field(..., description="Fecha de la reserva")
    hora: time = Field(..., description="Hora de llegada")
    turno: Literal["T1", "T2"] = Field("T1", description="Turno (T1 = primero, T2 = segundo)")
    pax: int = Field(..., description="Número de personas")
    
    # Asignación
    mesa_asignada: Optional[str] = Field(None, description="ID de la mesa asignada")
    zona_preferencia: ZonePreference = Field(ZonePreference.NO_PREFERENCE)
    usa_auxiliar: bool = Field(False, description="Si requiere mesa auxiliar")
    
    # Estado y confirmación
    estado: BookingStatus = Field(BookingStatus.PENDING)
    confirmada_whatsapp: bool = Field(False, description="Si confirmó por WhatsApp")
    recordatorio_enviado: bool = Field(False, description="Si se envió recordatorio 24h antes")
    recordatorio_enviado_at: Optional[datetime] = Field(None, description="Timestamp de envío de recordatorio")
    
    # Solicitudes especiales
    solicitudes: List[SpecialRequest] = Field(default_factory=list)
    notas: Optional[str] = Field(None, description="Notas adicionales")
    
    # Origen y trazabilidad
    canal: BookingChannel = Field(BookingChannel.VAPI)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True

    @property
    def datetime_completo(self) -> datetime:
        """Combina fecha y hora en un datetime."""
        return datetime.combine(self.fecha, self.hora)
    
    @property
    def requiere_24h_anticipacion(self) -> bool:
        """Verifica si alguna solicitud requiere 24h de antelación."""
        return SpecialRequest.CACHOPO_SIN_GLUTEN in self.solicitudes
    
    @property
    def solo_terraza(self) -> bool:
        """Verifica si debe ir obligatoriamente a terraza (ej: mascota)."""
        return SpecialRequest.MASCOTA in self.solicitudes
    
    @property
    def es_grupo_grande(self) -> bool:
        """Verifica si es un grupo que requiere escalado (>10 personas)."""
        return self.pax > 10
