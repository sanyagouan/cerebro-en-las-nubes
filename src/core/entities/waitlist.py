"""
Entidad de dominio: Waitlist Entry
Representa una entrada en la lista de espera cuando no hay mesas disponibles.
"""

from datetime import datetime, date, time
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class WaitlistStatus(str, Enum):
    """Estados posibles de una entrada en la waitlist."""
    WAITING = "waiting"          # Esperando disponibilidad
    NOTIFIED = "notified"        # Cliente notificado de disponibilidad
    CONFIRMED = "confirmed"      # Cliente confirmó la reserva
    EXPIRED = "expired"          # Expiró el tiempo de espera (15 min)
    CANCELLED = "cancelled"      # Cliente canceló su posición


class WaitlistEntry(BaseModel):
    """
    Modelo de una entrada en la lista de espera.
    
    Flujo:
    1. Cliente llama → No hay mesa → Se añade a waitlist (WAITING)
    2. Mesa disponible → Sistema notifica por WhatsApp (NOTIFIED)
    3. Cliente responde "SÍ" → Crea reserva (CONFIRMED)
    4. Cliente no responde en 15min → Expira (EXPIRED)
    5. Cliente responde "NO" → Se cancela (CANCELLED)
    """
    
    # Identificación
    id: Optional[str] = None
    airtable_id: Optional[str] = Field(None, description="ID del registro en Airtable")
    
    # Datos del cliente
    nombre_cliente: str = Field(..., min_length=2, max_length=100)
    telefono_cliente: str = Field(..., pattern=r"^\+\d{10,15}$")
    
    # Datos de la reserva deseada
    fecha: date
    hora: time
    num_personas: int = Field(..., ge=1, le=20)
    zona_preferida: Optional[str] = None  # "terraza", "interior", None = cualquiera
    
    # Estado y tracking
    estado: WaitlistStatus = WaitlistStatus.WAITING
    posicion: Optional[int] = None  # Posición en la cola (1 = primero)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    notified_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    # Metadata
    notas: Optional[str] = None
    origen: str = "VAPI_VOICE"  # VAPI_VOICE, WEB_DASHBOARD, MOBILE_APP
    notificacion_sid: Optional[str] = None  # SID del WhatsApp enviado
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            time: lambda v: v.strftime("%H:%M")
        }
    
    def puede_notificar(self) -> bool:
        """Verifica si esta entrada puede recibir notificación."""
        return self.estado == WaitlistStatus.WAITING
    
    def ha_expirado(self) -> bool:
        """
        Verifica si la notificación expiró (15 minutos sin respuesta).
        Solo aplica si ya fue notificado.
        """
        if self.estado != WaitlistStatus.NOTIFIED or not self.notified_at:
            return False
        
        elapsed = datetime.now() - self.notified_at
        return elapsed.total_seconds() > (15 * 60)  # 15 minutos
    
    def marcar_como_notificado(self, whatsapp_sid: str) -> None:
        """Marca la entrada como notificada con el SID del WhatsApp."""
        self.estado = WaitlistStatus.NOTIFIED
        self.notified_at = datetime.now()
        self.notificacion_sid = whatsapp_sid
    
    def marcar_como_confirmada(self) -> None:
        """Marca la entrada como confirmada (cliente aceptó)."""
        self.estado = WaitlistStatus.CONFIRMED
        self.confirmed_at = datetime.now()
    
    def marcar_como_expirada(self) -> None:
        """Marca la entrada como expirada (no respondió en 15min)."""
        self.estado = WaitlistStatus.EXPIRED
        self.expired_at = datetime.now()
    
    def marcar_como_cancelada(self) -> None:
        """Marca la entrada como cancelada (cliente rechazó)."""
        self.estado = WaitlistStatus.CANCELLED
        self.cancelled_at = datetime.now()
