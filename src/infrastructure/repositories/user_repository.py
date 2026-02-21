"""
UserRepository - Repositorio para gestión de usuarios en Airtable.
"""

import logging
from typing import Optional, List

from src.core.entities.user import User, RolUsuario
from src.infrastructure.mcp.airtable_client import airtable_client

logger = logging.getLogger(__name__)

# Constantes de Airtable
BASE_ID = "appQ2ZXAR68cqDmJt"
TABLE_NAME = "Usuarios"

# Mapeo de campos Python -> Airtable
FIELD_MAP = {
    "usuario": "Usuario",
    "nombre": "Nombre",
    "password_hash": "Password_Hash",
    "rol": "Rol",
    "telefono": "Teléfono",
    "device_token": "Device_Token",
    "activo": "Activo",
    "ultimo_login": "Último_Login",
}


class UserRepository:
    """Repositorio para operaciones CRUD de usuarios en Airtable."""

    async def get_by_usuario(self, usuario: str) -> Optional[User]:
        """
        Busca un usuario por su nombre de usuario.

        Args:
            usuario: Nombre de usuario único

        Returns:
            User si existe, None si no
        """
        try:
            formula = f"{{{FIELD_MAP['usuario']}}} = '{usuario}'"
            result = await airtable_client.list_records(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                filterByFormula=formula,
                max_records=1,
            )

            records = result.get("records", [])
            if records:
                return User.from_airtable(records[0])
            return None

        except Exception as e:
            logger.error(f"Error buscando usuario '{usuario}': {e}")
            return None

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Obtiene un usuario por su ID de Airtable.

        Args:
            user_id: ID del registro en Airtable

        Returns:
            User si existe, None si no
        """
        try:
            record = await airtable_client.get_record(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                record_id=user_id,
            )

            if record:
                return User.from_airtable(record)
            return None

        except Exception as e:
            logger.error(f"Error obteniendo usuario {user_id}: {e}")
            return None

    async def create(
        self,
        usuario: str,
        nombre: str,
        password_hash: str,
        rol: str,
        telefono: Optional[str] = None,
    ) -> User:
        """
        Crea un nuevo usuario en Airtable.

        Args:
            usuario: Nombre de usuario único
            nombre: Nombre completo para mostrar
            password_hash: Contraseña hasheada con bcrypt
            rol: Rol del usuario (administradora, encargada, camarero, cocina)
            telefono: Teléfono de contacto (opcional)

        Returns:
            User creado
        """
        fields = {
            FIELD_MAP["usuario"]: usuario,
            FIELD_MAP["nombre"]: nombre,
            FIELD_MAP["password_hash"]: password_hash,
            FIELD_MAP["rol"]: rol,
            FIELD_MAP["activo"]: True,
        }

        if telefono:
            fields[FIELD_MAP["telefono"]] = telefono

        record = await airtable_client.create_record(
            base_id=BASE_ID,
            table_name=TABLE_NAME,
            fields=fields,
        )

        logger.info(f"Usuario creado: {usuario} (rol: {rol})")
        return User.from_airtable(record)

    async def update(self, user_id: str, **fields) -> Optional[User]:
        """
        Actualiza campos de un usuario existente.

        Args:
            user_id: ID del usuario en Airtable
            **fields: Campos a actualizar (nombre, telefono, rol, etc.)

        Returns:
            User actualizado
        """
        # Mapear nombres de campos Python a Airtable
        airtable_fields = {}
        for key, value in fields.items():
            if key in FIELD_MAP:
                airtable_fields[FIELD_MAP[key]] = value

        if not airtable_fields:
            logger.warning(f"No hay campos para actualizar en usuario {user_id}")
            return await self.get_by_id(user_id)

        record = await airtable_client.update_record(
            base_id=BASE_ID,
            table_name=TABLE_NAME,
            record_id=user_id,
            fields=airtable_fields,
        )

        logger.info(f"Usuario {user_id} actualizado")
        return User.from_airtable(record)

    async def update_password(self, user_id: str, password_hash: str) -> bool:
        """
        Actualiza la contraseña hasheada de un usuario.

        Args:
            user_id: ID del usuario
            password_hash: Nueva contraseña hasheada

        Returns:
            True si se actualizó correctamente
        """
        try:
            await airtable_client.update_record(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                record_id=user_id,
                fields={FIELD_MAP["password_hash"]: password_hash},
            )
            logger.info(f"Contraseña actualizada para usuario {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error actualizando contraseña de {user_id}: {e}")
            return False

    async def update_device_token(self, user_id: str, device_token: str) -> bool:
        """
        Actualiza el token FCM del dispositivo del usuario.

        Args:
            user_id: ID del usuario
            device_token: Token FCM para notificaciones push

        Returns:
            True si se actualizó correctamente
        """
        try:
            await airtable_client.update_record(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                record_id=user_id,
                fields={FIELD_MAP["device_token"]: device_token},
            )
            logger.info(f"Device token actualizado para usuario {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error actualizando device token de {user_id}: {e}")
            return False

    async def deactivate(self, user_id: str) -> bool:
        """
        Desactiva un usuario (soft delete).

        Args:
            user_id: ID del usuario a desactivar

        Returns:
            True si se desactivó correctamente
        """
        try:
            await airtable_client.update_record(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                record_id=user_id,
                fields={FIELD_MAP["activo"]: False},
            )
            logger.info(f"Usuario {user_id} desactivado")
            return True
        except Exception as e:
            logger.error(f"Error desactivando usuario {user_id}: {e}")
            return False

    async def activate(self, user_id: str) -> bool:
        """
        Reactiva un usuario desactivado.

        Args:
            user_id: ID del usuario a reactivar

        Returns:
            True si se reactivó correctamente
        """
        try:
            await airtable_client.update_record(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                record_id=user_id,
                fields={FIELD_MAP["activo"]: True},
            )
            logger.info(f"Usuario {user_id} reactivado")
            return True
        except Exception as e:
            logger.error(f"Error reactivando usuario {user_id}: {e}")
            return False

    async def list_all(
        self,
        rol: Optional[str] = None,
        activo: Optional[bool] = None,
    ) -> List[User]:
        """
        Lista todos los usuarios con filtros opcionales.

        Args:
            rol: Filtrar por rol (opcional)
            activo: Filtrar por estado activo (opcional)

        Returns:
            Lista de usuarios
        """
        try:
            # Construir filtro
            filters = []

            if rol:
                filters.append(f"{{{FIELD_MAP['rol']}}} = '{rol}'")

            if activo is not None:
                # Airtable usa 1/0 para checkbox
                activo_val = "TRUE()" if activo else "FALSE()"
                filters.append(f"{{{FIELD_MAP['activo']}}} = {activo_val}")

            filter_formula = " AND ".join(filters) if filters else None

            result = await airtable_client.list_records(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                filterByFormula=filter_formula,
                max_records=500,
            )

            records = result.get("records", [])
            users = [User.from_airtable(record) for record in records]

            logger.info(f"Listados {len(users)} usuarios")
            return users

        except Exception as e:
            logger.error(f"Error listando usuarios: {e}")
            return []

    async def count_admins(self) -> int:
        """
        Cuenta cuántos administradores activos hay.

        Returns:
            Número de administradoras activas
        """
        try:
            formula = f"AND({{{FIELD_MAP['rol']}}} = 'administradora', {{{FIELD_MAP['activo']}}} = TRUE())"
            result = await airtable_client.list_records(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                filterByFormula=formula,
                max_records=100,
            )

            return len(result.get("records", []))

        except Exception as e:
            logger.error(f"Error contando administradores: {e}")
            return 0


# Instancia singleton
user_repository = UserRepository()
