"""
Modelos Pydantic para entidades de Cliente.

Representa los clientes del restobar con sus preferencias y notas.
Incluye validaciones específicas para datos españoles (teléfono E.164).

⚠️ IMPORTANTE: Los nombres de campos coinciden EXACTAMENTE con Airtable.
Ver docs/TABLA_CLIENTES_AIRTABLE.md para referencia completa.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TipoPreferencia(str, Enum):
    """Tipos de preferencias del cliente.
    
    ⚠️ IMPORTANTE: Valores deben coincidir EXACTAMENTE con opciones en Airtable.
    Ver docs/TABLA_CLIENTES_AIRTABLE.md líneas 115-123.
    """
    ZONA_FAVORITA = "zona_favorita"
    SOLICITUD_ESPECIAL = "solicitud_especial"
    RESTRICCION_DIETETICA = "restriccion_dietetica"
    OCASION_CELEBRACION = "ocasion_celebracion"


class ClientePreferencia(BaseModel):
    """Modelo para preferencias de cliente.
    
    ⚠️ NOTA: La tabla ClientePreferencias NO tiene campo Es_Importante.
    Ese campo solo existe en la tabla ClienteNotas.
    
    Campos en Airtable:
    - Descripcion (singleLineText - Primary)
    - Tipo (singleSelect)
    - Fecha_Creacion (singleLineText)
    - Cliente (multipleRecordLinks)
    """
    id: Optional[str] = None
    cliente_id: str = Field(..., description="ID del cliente (linked record)")
    tipo: TipoPreferencia  # ✅ Campo "Tipo" en Airtable
    descripcion: str
    creado: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class ClienteNota(BaseModel):
    """Modelo para notas de cliente.
    
    ⚠️ CAMPOS RENOMBRADOS para coincidir con Airtable:
    - contenido: Campo "Contenido" en Airtable (NO "Nota")
    - fecha_creacion: Campo "Fecha_Creacion" en Airtable (NO "Fecha")
    - staff_nombre: Campo "Staff_Nombre" en Airtable (NO "Autor")
    """
    id: Optional[str] = None
    cliente_id: str = Field(..., description="ID del cliente (linked record)")
    contenido: str  # ✅ Campo "Contenido" en Airtable
    fecha_creacion: datetime = Field(default_factory=datetime.now)  # ✅ Campo "Fecha_Creacion"
    staff_nombre: str  # ✅ Campo "Staff_Nombre" en Airtable
    

class Cliente(BaseModel):
    """Modelo principal de cliente.
    
    ⚠️ CAMPOS RENOMBRADOS para coincidir con Airtable:
    - primera_reserva: Campo "Primera_Reserva" en Airtable (NO "Fecha_Primera_Visita")
    - ultima_reserva: Campo "Ultima_Reserva" en Airtable (NO "Ultima_Visita")
    
    ⚠️ VALIDACIÓN TELÉFONO:
    - Campo telefono es Optional para soportar registros legacy sin teléfono
    - Si presente, debe ser formato E.164 español: +34XXXXXXXXX (12 caracteres)
    - Validación custom en validate_spanish_phone() (NO usar pattern en Field)
    """
    id: Optional[str] = None
    nombre: str
    telefono: Optional[str] = None  # ✅ Optional, sin pattern (deja que validator maneje)
    email: Optional[EmailStr] = None
    primera_reserva: Optional[datetime] = None  # ✅ Campo "Primera_Reserva" en Airtable
    total_visitas: int = 0
    ultima_reserva: Optional[datetime] = None  # ✅ Campo "Ultima_Reserva" en Airtable
    notas_generales: Optional[str] = None
    
    # Relaciones (populated cuando se solicite)
    preferencias: Optional[List[ClientePreferencia]] = None
    notas: Optional[List[ClienteNota]] = None
    
    @field_validator('telefono')
    @classmethod
    def validate_spanish_phone(cls, v: Optional[str]) -> Optional[str]:
        """Valida formato teléfono español E.164.
        
        ⚠️ IMPORTANTE: 
        - Este validator permite valores None/vacíos (para registros legacy)
        - Solo valida si hay un valor presente
        - NO usar Field(pattern=...) porque bloquea valores vacíos antes del validator
        
        Args:
            v: Teléfono a validar o None
            
        Returns:
            Teléfono validado o None
            
        Raises:
            ValueError: Si formato incorrecto
        """
        # Permitir None o string vacía (registros legacy)
        if v is None or v == "":
            return v
        
        # Validar formato E.164 español
        if not v.startswith('+34'):
            raise ValueError('Debe ser número español (+34XXXXXXXXX)')
        
        # Validar longitud: +34 (3 chars) + 9 dígitos = 12 total
        if len(v) != 12:
            raise ValueError(f'Formato incorrecto. Esperado: +34XXXXXXXXX (12 caracteres), recibido: {len(v)} caracteres')
        
        # Validar que los 9 caracteres después de +34 sean dígitos
        phone_digits = v[3:]  # Extraer parte después de +34
        if not phone_digits.isdigit():
            raise ValueError('Los 9 caracteres después de +34 deben ser dígitos')
        
        return v
