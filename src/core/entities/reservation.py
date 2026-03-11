"""
Entidad Reservation - Sistema Unificado de Estados

Define el modelo de datos para las reservas del restobar "En Las Nubes".
Incluye sistema de estados unificado y soporte para confirmación multi-canal.

Autor: Sistema Cerebro En Las Nubes
Fecha: 2026-03-10
"""

from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


class ReservationState(str, Enum):
    """
    Estados estándar de reserva - Sistema unificado.
    
    Ciclo de vida típico:
    Pre-reserva → Confirmada → En curso → Completada
    
    Estados alternativos:
    - Cancelada: Cliente o sistema cancela antes de llegar
    - No Show: Cliente no se presentó a reserva confirmada
    """
    PRE_RESERVA = "Pre-reserva"
    CONFIRMADA = "Confirmada"
    EN_CURSO = "En curso"
    COMPLETADA = "Completada"
    CANCELADA = "Cancelada"
    NO_SHOW = "No Show"


class TipoTelefono(str, Enum):
    """
    Tipo de teléfono detectado automáticamente.
    
    Detección basada en formato E.164 para España:
    - movil: +346XX o +347XX
    - fijo: +349XX (excluyendo 96X y 97X)
    - desconocido: No se puede determinar o no es +34
    """
    MOVIL = "movil"
    FIJO = "fijo"
    DESCONOCIDO = "desconocido"


class TipoConfirmacion(str, Enum):
    """
    Método de confirmación de la reserva.
    
    - pendiente: Reserva creada, esperando confirmación
    - whatsapp: Confirmada vía mensaje WhatsApp (móviles)
    - verbal: Confirmada verbalmente durante llamada VAPI (fijos)
    """
    WHATSAPP = "whatsapp"
    VERBAL = "verbal"
    PENDIENTE = "pendiente"


class Reservation(BaseModel):
    """
    Modelo de dominio para Reservas.
    
    Representa una reserva en el restobar con todos sus datos
    y metadatos de confirmación/estado.
    """
    
    # Identificación
    id: Optional[str] = Field(None, description="ID único de Airtable (ej: recXXXXXX)")
    
    # Datos del cliente
    nombre_cliente: str = Field(..., min_length=1, max_length=100)
    telefono: str = Field(..., pattern=r"^\+\d{10,15}$", description="Formato E.164")
    email: Optional[str] = Field(None, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    
    # Datos de la reserva
    fecha_reserva: str = Field(..., description="Fecha en formato YYYY-MM-DD")
    hora: datetime = Field(..., description="Hora en ISO 8601 con timezone")
    cantidad_personas: int = Field(..., ge=1, le=20)
    
    # Sistema de mesas (opcional en esta fase)
    mesa_id: Optional[str] = Field(None, description="ID de la mesa asignada")
    mesa_nombre: Optional[str] = Field(None, description="Nombre visual de la mesa")
    
    # Notas generales
    notas: Optional[str] = Field(None, description="Peticiones especiales del cliente")
    
    # **SISTEMA UNIFICADO DE ESTADOS**
    estado: ReservationState = Field(
        default=ReservationState.PRE_RESERVA,
        description="Estado actual de la reserva"
    )
    
    # **CAMPOS MULTI-CANAL**
    tipo_telefono: TipoTelefono = Field(
        default=TipoTelefono.DESCONOCIDO,
        description="Tipo de teléfono detectado automáticamente"
    )
    
    tipo_confirmacion: TipoConfirmacion = Field(
        default=TipoConfirmacion.PENDIENTE,
        description="Método utilizado para confirmar la reserva"
    )
    
    requiere_recordatorio: bool = Field(
        default=False,
        description="True si necesita recordatorio manual (típicamente fijos)"
    )
    
    notas_confirmacion: Optional[str] = Field(
        None,
        description="Detalles de cómo/cuándo se confirmó la reserva"
    )
    
    # Metadatos temporales
    creado: Optional[datetime] = Field(None, description="Timestamp de creación")
    modificado: Optional[datetime] = Field(None, description="Último timestamp de modificación")
    
    class Config:
        """Configuración del modelo Pydantic."""
        use_enum_values = True  # Serializar enums como strings
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @validator('telefono')
    def validar_formato_telefono(cls, v):
        """
        Valida que el teléfono esté en formato E.164.
        
        Formato esperado: +[código país][número]
        Ejemplo: +34612345678
        """
        if not v.startswith('+'):
            raise ValueError('El teléfono debe estar en formato E.164 (+código país + número)')
        
        if len(v) < 11:  # Mínimo: +XX más 9 dígitos
            raise ValueError('El teléfono es demasiado corto')
        
        return v
    
    @validator('cantidad_personas')
    def validar_cantidad_personas(cls, v):
        """
        Valida que el número de personas esté en rango razonable.
        
        - Mínimo: 1 persona
        - Máximo: 20 personas (grupos más grandes requieren handoff humano)
        """
        if v < 1:
            raise ValueError('La cantidad de personas debe ser al menos 1')
        
        if v > 20:
            raise ValueError(
                'Grupos de más de 20 personas requieren coordinación manual. '
                'Por favor, contacte directamente con el restobar.'
            )
        
        return v
    
    def puede_transicionar_a(self, nuevo_estado: ReservationState) -> bool:
        """
        Valida si la transición de estado es válida.
        
        Transiciones permitidas:
        - Pre-reserva → Confirmada, Cancelada
        - Confirmada → En curso, Cancelada, No Show
        - En curso → Completada
        - Completada → [ninguna] (estado final)
        - Cancelada → [ninguna] (estado final)
        - No Show → [ninguna] (estado final)
        
        Args:
            nuevo_estado: Estado al que se quiere transicionar
        
        Returns:
            True si la transición es válida, False en caso contrario
        """
        transiciones_validas = {
            ReservationState.PRE_RESERVA: [
                ReservationState.CONFIRMADA,
                ReservationState.CANCELADA
            ],
            ReservationState.CONFIRMADA: [
                ReservationState.EN_CURSO,
                ReservationState.CANCELADA,
                ReservationState.NO_SHOW
            ],
            ReservationState.EN_CURSO: [
                ReservationState.COMPLETADA
            ],
            # Estados finales - sin transiciones permitidas
            ReservationState.COMPLETADA: [],
            ReservationState.CANCELADA: [],
            ReservationState.NO_SHOW: []
        }
        
        estados_permitidos = transiciones_validas.get(self.estado, [])
        return nuevo_estado in estados_permitidos
    
    def es_movil(self) -> bool:
        """Retorna True si el teléfono es móvil."""
        return self.tipo_telefono == TipoTelefono.MOVIL
    
    def es_fijo(self) -> bool:
        """Retorna True si el teléfono es fijo."""
        return self.tipo_telefono == TipoTelefono.FIJO
    
    def esta_confirmada(self) -> bool:
        """Retorna True si la reserva está confirmada."""
        return self.estado == ReservationState.CONFIRMADA
    
    def esta_activa(self) -> bool:
        """
        Retorna True si la reserva está en estado activo.
        
        Estados activos: Pre-reserva, Confirmada, En curso
        Estados inactivos: Completada, Cancelada, No Show
        """
        return self.estado in [
            ReservationState.PRE_RESERVA,
            ReservationState.CONFIRMADA,
            ReservationState.EN_CURSO
        ]
    
    def to_airtable_dict(self) -> dict:
        """
        Convierte el modelo a formato compatible con Airtable.
        
        Mapea los nombres de campos Python a los nombres de Airtable.
        
        Returns:
            Diccionario con estructura de Airtable
        """
        return {
            "Nombre del Cliente": self.nombre_cliente,
            "Teléfono": self.telefono,
            "Email": self.email,
            "Fecha de Reserva": self.fecha_reserva,
            "Hora": self.hora.isoformat(),
            "Cantidad de Personas": self.cantidad_personas,
            "Notas": self.notas,
            
            # Sistema unificado de estados
            "Estado": self.estado,
            
            # Campos multi-canal
            "Tipo_Telefono": self.tipo_telefono,
            "Tipo_Confirmacion": self.tipo_confirmacion,
            "Requiere_Recordatorio": self.requiere_recordatorio,
            "Notas_Confirmacion": self.notas_confirmacion,
            
            # Mesa (si está asignada)
            **({"Mesa": [self.mesa_id]} if self.mesa_id else {})
        }
    
    @classmethod
    def from_airtable_record(cls, record: dict) -> "Reservation":
        """
        Crea una instancia de Reservation desde un registro de Airtable.
        
        Args:
            record: Diccionario con estructura de Airtable
        
        Returns:
            Instancia de Reservation
        """
        fields = record.get("fields", {})
        
        return cls(
            id=record.get("id"),
            nombre_cliente=fields.get("Nombre del Cliente", ""),
            telefono=fields.get("Teléfono", ""),
            email=fields.get("Email"),
            fecha_reserva=fields.get("Fecha de Reserva", ""),
            hora=datetime.fromisoformat(fields.get("Hora", "")),
            cantidad_personas=fields.get("Cantidad de Personas", 1),
            notas=fields.get("Notas"),
            
            # Sistema unificado de estados
            estado=ReservationState(fields.get("Estado", "Pre-reserva")),
            
            # Campos multi-canal
            tipo_telefono=TipoTelefono(fields.get("Tipo_Telefono", "desconocido")),
            tipo_confirmacion=TipoConfirmacion(fields.get("Tipo_Confirmacion", "pendiente")),
            requiere_recordatorio=fields.get("Requiere_Recordatorio", False),
            notas_confirmacion=fields.get("Notas_Confirmacion"),
            
            # Mesa
            mesa_id=fields.get("Mesa", [None])[0] if fields.get("Mesa") else None,
            
            # Metadatos
            creado=datetime.fromisoformat(fields["Creado"]) if "Creado" in fields else None,
            modificado=datetime.fromisoformat(fields["Modificado"]) if "Modificado" in fields else None
        )
