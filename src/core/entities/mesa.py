"""
Modelos Pydantic para el sistema de mesas del restobar "En Las Nubes".

Este módulo define los modelos de datos para:
- Mesa individual (interior y terraza)
- Configuraciones de mesas combinadas
- Solicitud de asignación
- Resultado del algoritmo de asignación
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from enum import Enum
from datetime import datetime


class ZonaMesa(str, Enum):
    """Zonas del restobar según planos físicos."""
    SALA_EXTERIOR = "Sala Exterior"
    SALA_INTERIOR = "Sala Interior"
    SOFAS = "Sofás"
    BARRA = "Barra"
    TERRAZA = "Terraza"


class EstadoMesa(str, Enum):
    """Estados posibles de una mesa.
    
    Nota: Los valores coinciden con los del campo 'Estado' en Airtable.
    """
    LIBRE = "Libre"
    OCUPADA = "Ocupada"
    RESERVADA = "Reservada"
    BLOQUEADA = "Bloqueada"
    
    # Alias para compatibilidad
    DISPONIBLE = "Libre"  # Alias backward compatibility
    MANTENIMIENTO = "Bloqueada"  # Alias backward compatibility


class Mesa(BaseModel):
    """Modelo de mesa individual.
    
    Representa una mesa física del restobar, ya sea de interior
    o terraza. Incluye información de capacidad, combinabilidad
    y estado actual.
    
    Attributes:
        id: ID del registro en Airtable (recXXX...)
        id_mesa: ID único de la mesa (SE-1, T-1, etc.)
        nombre: Nombre descriptivo de la mesa
        zona: Zona donde se encuentra la mesa
        ubicacion_detallada: Descripción adicional de ubicación
        capacidad_estandar: Capacidad normal de la mesa
        capacidad_ampliada: Capacidad con sillas extra
        mesas_auxiliares: IDs de mesas auxiliares (para SE-1 a SE-4)
        es_combinable: Si la mesa puede combinarse con otras
        mesas_compatibles: IDs de mesas con las que puede combinarse
        estado: Estado actual de la mesa
        notas: Notas especiales (accesibilidad, vistas, etc.)
        orden_prioridad: Prioridad para el algoritmo de asignación
        activa: Si la mesa está en servicio
    """
    id: Optional[str] = None
    id_mesa: str = Field(..., description="ID único: SE-1, T-1, etc.")
    nombre: str = Field(..., description="Nombre descriptivo")
    zona: ZonaMesa = Field(..., description="Zona del restobar")
    ubicacion_detallada: Optional[str] = Field(None, description="Ubicación específica")
    capacidad_estandar: int = Field(..., ge=1, le=12, description="Capacidad normal")
    capacidad_ampliada: int = Field(..., ge=1, le=14, description="Capacidad con sillas extra")
    mesas_auxiliares: Optional[List[str]] = Field(None, description="IDs de mesas auxiliares")
    es_combinable: bool = Field(False, description="Si puede combinarse con otras")
    mesas_compatibles: Optional[List[str]] = Field(None, description="IDs de mesas compatibles")
    estado: EstadoMesa = Field(EstadoMesa.DISPONIBLE, description="Estado actual")
    notas: Optional[str] = Field(None, description="Notas especiales")
    orden_prioridad: int = Field(1, ge=1, le=100, description="Prioridad de asignación")
    activa: bool = Field(True, description="Si está en servicio")
    
    class Config:
        use_enum_values = True


class ConfiguracionMesa(BaseModel):
    """Configuración de mesas combinadas.
    
    Representa una combinación predefinida de mesas de terraza
    para grupos grandes. Por ejemplo, T-1 + T-2 para
    4-8 personas.
    
    Attributes:
        id: ID del registro en Airtable
        id_configuracion: ID único (CONF-T-1-2, etc.)
        nombre: Nombre descriptivo
        mesas_incluidas: Lista de IDs de mesas que componen la configuración
        capacidad_total: Capacidad total de la configuración
        ubicacion: Siempre "Terraza"
        activa: Si la configuración está disponible
        notas: Notas adicionales
    """
    id: Optional[str] = None
    id_configuracion: str = Field(..., description="ID único: CONF-T-1-2")
    nombre: str = Field(..., description="Nombre descriptivo")
    mesas_incluidas: List[str] = Field(..., description="IDs de mesas incluidas")
    capacidad_total: int = Field(..., ge=2, le=20, description="Capacidad total")
    ubicacion: str = Field("Terraza", description="Ubicación (siempre Terraza)")
    activa: bool = Field(True, description="Si está disponible")
    notas: Optional[str] = Field(None, description="Notas adicionales")


class SolicitudAsignacion(BaseModel):
    """Solicitud de asignación de mesa.
    
    Contiene los datos necesarios para que el algoritmo
    de 3 fases asigne la mesa óptima.
    
    Attributes:
        num_personas: Número de comensales (1-20)
        fecha: Fecha de la reserva (YYYY-MM-DD)
        hora: Hora de la reserva (HH:MM)
        preferencia_zona: Zona preferida (opcional)
        preferencia_mesa: ID de mesa específica (opcional)
        requiere_accesibilidad: Si necesita acceso adaptado
    """
    num_personas: int = Field(..., ge=1, le=20, description="Número de comensales")
    fecha: str = Field(..., description="Fecha YYYY-MM-DD")
    hora: str = Field(..., description="Hora HH:MM")
    preferencia_zona: Optional[ZonaMesa] = Field(None, description="Zona preferida")
    preferencia_mesa: Optional[str] = Field(None, description="ID de mesa específica")
    requiere_accesibilidad: bool = Field(False, description="Si necesita acceso adaptado")
    
    @field_validator('fecha')
    @classmethod
    def validar_fecha(cls, v):
        """Valida formato de fecha YYYY-MM-DD."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Fecha debe tener formato YYYY-MM-DD")

    @field_validator('hora')
    @classmethod
    def validar_hora(cls, v):
        """Valida formato de hora HH:MM."""
        try:
            datetime.strptime(v, "%H:%M")
            return v
        except ValueError:
            raise ValueError("Hora debe tener formato HH:MM")


class ResultadoAsignacion(BaseModel):
    """Resultado del algoritmo de asignación de mesas.
    
    Contiene la mesa o configuración asignada, o información
    sobre alternativas si no se encontró disponibilidad.
    
    Attributes:
        exito: Si se asignó una mesa correctamente
        mesa_asignada: Mesa individual asignada (si aplica)
        configuracion_asignada: Configuración de mesas asignada (si aplica)
        mensaje: Mensaje descriptivo del resultado
        alternativas: Lista de mesas alternativas (si no hay disponibilidad exacta)
    """
    exito: bool = Field(..., description="Si se asignó mesa correctamente")
    mesa_asignada: Optional[Mesa] = Field(None, description="Mesa individual asignada")
    configuracion_asignada: Optional[ConfiguracionMesa] = Field(None, description="Configuración asignada")
    mensaje: str = Field(..., description="Mensaje descriptivo")
    alternativas: Optional[List[Mesa]] = Field(None, description="Mesas alternativas disponibles")


class DisponibilidadMesa(BaseModel):
    """Información de disponibilidad de una mesa para una fecha/hora.
    
    Attributes:
        mesa: Datos de la mesa
        disponible: Si está disponible
        motivo_no_disponibilidad: Razón si no está disponible
        reserva_id: ID de la reserva que ocupa la mesa (si aplica)
    """
    mesa: Mesa = Field(..., description="Datos de la mesa")
    disponible: bool = Field(..., description="Si está disponible")
    motivo_no_disponibilidad: Optional[str] = Field(None, description="Razón si no está disponible")
    reserva_id: Optional[str] = Field(None, description="ID de la reserva que ocupa la mesa")


class EstadisticasAsignacion(BaseModel):
    """Estadísticas del algoritmo de asignación.
    
    Attributes:
        total_mesas: Total de mesas en el sistema
        mesas_disponibles: Mesas disponibles en un momento dado
        mesas_interior: Mesas de interior
        mesas_terraza: Mesas de terraza
        configuraciones_activas: Configuraciones de terraza activas
        capacidad_total: Capacidad total del restobar
    """
    total_mesas: int = Field(..., description="Total de mesas")
    mesas_disponibles: int = Field(..., description="Mesas disponibles")
    mesas_interior: int = Field(..., description="Mesas de interior")
    mesas_terraza: int = Field(..., description="Mesas de terraza")
    configuraciones_activas: int = Field(..., description="Configuraciones activas")
    capacidad_total: int = Field(..., description="Capacidad total del restobar")
