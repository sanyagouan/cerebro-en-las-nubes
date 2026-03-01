"""
Entidad User - Usuario del sistema de gestión del restaurante.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class RolUsuario(str, Enum):
    """Roles de usuario en el sistema (español de España)."""

    ADMINISTRADORA = "administradora"
    ENCARGADA = "encargada"
    CAMARERO = "camarero"
    COCINA = "cocina"


@dataclass
class User:
    """
    Usuario del sistema de gestión.

    Attributes:
        id: ID del registro en Airtable
        usuario: Nombre de usuario único (para login)
        nombre: Nombre completo para mostrar
        password_hash: Contraseña hasheada con bcrypt
        rol: Rol del usuario (administradora, encargada, camarero, cocina)
        telefono: Teléfono de contacto (opcional)
        device_token: Token FCM para notificaciones push (opcional)
        activo: Si el usuario está activo (soft delete)
        ultimo_login: Fecha y hora del último inicio de sesión
        creado: Fecha de creación
        modificado: Fecha de última modificación
    """

    id: str
    usuario: str
    nombre: str
    password_hash: str
    rol: RolUsuario
    telefono: Optional[str] = None
    device_token: Optional[str] = None
    activo: bool = True
    ultimo_login: Optional[datetime] = None
    creado: Optional[datetime] = None
    modificado: Optional[datetime] = None

    @classmethod
    def from_airtable(cls, record: dict) -> "User":
        """
        Crea un User desde un registro de Airtable.

        Args:
            record: Registro de Airtable con 'id' y 'fields'

        Returns:
            Instancia de User
        """
        fields = record.get("fields", {})

        return cls(
            id=record.get("id", ""),
            usuario=fields.get("Usuario", ""),
            nombre=fields.get("Nombre", ""),
            password_hash=fields.get("Password_Hash", ""),
            rol=RolUsuario(fields.get("Rol", "camarero")),
            telefono=fields.get("Teléfono"),
            device_token=fields.get("Device_Token"),
            activo=fields.get("Activo", True),
            ultimo_login=cls._parse_datetime(fields.get("Último_Login")),
            creado=cls._parse_datetime(fields.get("Creado")),
            modificado=cls._parse_datetime(fields.get("Modificado")),
        )

    @staticmethod
    def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
        """Parsea una fecha ISO string a datetime."""
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None

    def to_dict(self) -> dict:
        """Convierte el User a diccionario para respuestas API."""
        return {
            "id": self.id,
            "usuario": self.usuario,
            "nombre": self.nombre,
            "rol": self.rol.value,
            "telefono": self.telefono,
            "activo": self.activo,
            "ultimo_login": self.ultimo_login.isoformat()
            if self.ultimo_login
            else None,
        }
