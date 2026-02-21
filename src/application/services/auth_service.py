"""
Authentication Service - Manejo de JWT, bcrypt y autenticación de usuarios.
TODO EN ESPAÑOL DE ESPAÑA.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
from loguru import logger
import bcrypt

from src.infrastructure.repositories.user_repository import user_repository


# ========== MODELS ==========


class TokenData(BaseModel):
    """Datos extraídos del token JWT."""

    user_id: str
    usuario: str
    nombre: str
    rol: str


# ========== SECURITY ==========

security = HTTPBearer()

# Configuración bcrypt
BCRYPT_ROUNDS = 12  # Work factor óptimo


# ========== PERMISSIONS (RBAC) ==========

# Matriz de permisos por rol (TODO EN ESPAÑOL)
PERMISSIONS = {
    "administradora": [
        "reservas.ver",
        "reservas.crear",
        "reservas.editar",
        "reservas.actualizar_estado",
        "reservas.cancelar",
        "mesas.ver",
        "mesas.actualizar_estado",
        "mesas.anadir_notas",
        "cocina.ver",
        "cocina.actualizar",
        "cocina.enviar_avisos",
        "usuarios.ver",
        "usuarios.crear",
        "usuarios.editar",
        "usuarios.cambiar_password",
        "usuarios.desactivar",
        "config.ver",
        "config.editar",
        "reportes.ver",
        "notificaciones.enviar",
        "notificaciones.recibir",
    ],
    "encargada": [
        "reservas.ver",
        "reservas.crear",
        "reservas.editar",
        "reservas.actualizar_estado",
        "reservas.cancelar",
        "mesas.ver",
        "mesas.actualizar_estado",
        "mesas.anadir_notas",
        "cocina.ver",
        "cocina.actualizar",
        "cocina.enviar_avisos",
        "reportes.ver",
        "notificaciones.enviar",
        "notificaciones.recibir",
    ],
    "camarero": [
        "reservas.ver",
        "reservas.actualizar_estado",
        "mesas.ver",
        "mesas.actualizar_estado",
        "mesas.anadir_notas",
        "cocina.enviar_avisos",
        "notificaciones.enviar",
        "notificaciones.recibir",
    ],
    "cocina": [
        "cocina.ver",
        "cocina.actualizar",
        "cocina.enviar_avisos",
        "notificaciones.enviar",
        "notificaciones.recibir",
    ],
}


def check_permission(role: str, permission: str) -> bool:
    """
    Verifica si un rol tiene un permiso específico.

    Args:
        role: Rol del usuario (administradora, encargada, camarero, cocina)
        permission: Permiso a verificar (ej: "reservas.ver")

    Returns:
        True si tiene el permiso, False si no
    """
    role_permissions = PERMISSIONS.get(role, [])
    return permission in role_permissions


# ========== SERVICE ==========


class AuthService:
    """Servicio de autenticación con JWT y bcrypt."""

    def __init__(self):
        self.secret_key = os.getenv(
            "JWT_SECRET_KEY", "dev-secret-key-change-in-production"
        )
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60  # 1 hora
        self.refresh_token_expire_days = 7  # 7 días

    def _hash_password(self, password: str) -> str:
        """Hashea una contraseña con bcrypt directamente."""
        salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def _verify_password(self, password: str, hash: str) -> bool:
        """Verifica una contraseña contra su hash."""
        return bcrypt.checkpw(password.encode("utf-8"), hash.encode("utf-8"))

    def create_access_token(
        self, user_id: str, usuario: str, nombre: str, rol: str
    ) -> str:
        """Crea un JWT access token."""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            "sub": user_id,
            "usuario": usuario,
            "nombre": nombre,
            "rol": rol,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(
        self, user_id: str, usuario: str, nombre: str, rol: str
    ) -> str:
        """Crea un JWT refresh token."""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        payload = {
            "sub": user_id,
            "usuario": usuario,
            "nombre": nombre,
            "rol": rol,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifica y decodifica un JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Alias para verify_token (compatibilidad)."""
        return self.verify_token(token)

    async def authenticate_user(
        self, usuario: str, password: str
    ) -> Optional[Dict[str, Any]]:
        """
        Autentica un usuario por nombre de usuario y contraseña.

        Args:
            usuario: Nombre de usuario
            password: Contraseña en texto plano

        Returns:
            Datos del usuario si es exitoso, None si no
        """
        # Buscar usuario en Airtable
        user = await user_repository.get_by_usuario(usuario)

        if not user:
            logger.warning(f"Usuario no encontrado: {usuario}")
            return None

        # Verificar que esté activo
        if not user.activo:
            logger.warning(f"Usuario inactivo: {usuario}")
            return None

        # Verificar contraseña con bcrypt
        if not self._verify_password(password, user.password_hash):
            logger.warning(f"Contraseña incorrecta para: {usuario}")
            return None

        return {
            "id": user.id,
            "usuario": user.usuario,
            "nombre": user.nombre,
            "rol": user.rol.value,
        }

    def verify_role_permission(self, role: str, permission: str) -> bool:
        """Verifica si un rol tiene un permiso específico."""
        return check_permission(role, permission)

    async def hash_password(self, password: str) -> str:
        """Hashea una contraseña (para uso externo)."""
        return self._hash_password(password)

    async def change_user_password(self, user_id: str, new_password: str) -> bool:
        """
        Cambia la contraseña de un usuario.

        Args:
            user_id: ID del usuario
            new_password: Nueva contraseña en texto plano

        Returns:
            True si se cambió correctamente
        """
        password_hash = self._hash_password(new_password)
        return await user_repository.update_password(user_id, password_hash)

    async def register_device_token(self, user_id: str, device_token: str) -> bool:
        """Registra el token FCM del dispositivo del usuario."""
        return await user_repository.update_device_token(user_id, device_token)

    async def invalidate_token(self, token: str) -> bool:
        """
        Invalida un token añadiéndolo a una blacklist en Redis.

        Por ahora, solo retornamos True ya que los tokens
        expiran naturalmente según su tiempo de vida.
        """
        # TODO: Implementar blacklist en Redis si es necesario
        logger.info(f"Token invalidado (logout): {token[:20]}...")
        return True


# Instancia singleton
auth_service = AuthService()


# ========== DEPENDENCIES ==========


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    """Dependency para verificar JWT token y obtener datos del usuario."""
    token = credentials.credentials
    payload = auth_service.verify_token(token)

    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenData(
        user_id=payload["sub"],
        usuario=payload.get("usuario", ""),
        nombre=payload.get("nombre", ""),
        rol=payload.get("rol", ""),
    )


def require_permission(permission: str):
    """
    Dependency que verifica que el usuario tenga un permiso específico.

    Uso:
        @router.get("/admin-only")
        async def admin_endpoint(user: TokenData = Depends(require_permission("usuarios.ver"))):
            return {"message": f"Hola {user.nombre}"}
    """

    async def _require_permission(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> TokenData:
        token = credentials.credentials
        payload = auth_service.verify_token(token)

        if not payload or payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_role = payload.get("rol", "")
        if not check_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso denegado: {permission}",
            )

        return TokenData(
            user_id=payload["sub"],
            usuario=payload.get("usuario", ""),
            nombre=payload.get("nombre", ""),
            rol=user_role,
        )

    return _require_permission


def require_role(allowed_roles: List[str]):
    """
    FastAPI dependency que verifica que el usuario tenga uno de los roles permitidos.

    Uso:
        @router.get("/admin-only")
        async def admin_endpoint(user: TokenData = Depends(require_role(["administradora"]))):
            return {"message": f"Hola administradora {user.nombre}"}
    """

    async def _require_role(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> TokenData:
        token = credentials.credentials
        payload = auth_service.verify_token(token)

        if not payload or payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_role = payload.get("rol", "")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Roles requeridos: {allowed_roles}",
            )

        return TokenData(
            user_id=payload["sub"],
            usuario=payload.get("usuario", ""),
            nombre=payload.get("nombre", ""),
            rol=user_role,
        )

    return _require_role
