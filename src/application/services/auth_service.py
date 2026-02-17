"""
Authentication Service - Manejo de JWT y autenticación de usuarios.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
from loguru import logger


# ========== MODELS ==========


class TokenData(BaseModel):
    """Datos extraídos del token JWT."""

    user_id: str
    email: str
    role: str


# ========== SECURITY ==========

security = HTTPBearer()


# ========== SERVICE ==========


class AuthService:
    """Servicio de autenticación con JWT."""

    def __init__(self):
        self.secret_key = os.getenv(
            "JWT_SECRET_KEY", "dev-secret-key-change-in-production"
        )
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60  # 1 hora
        self.refresh_token_expire_days = 7  # 7 días

        # Usuarios demo para desarrollo (en producción usar base de datos)
        self._demo_users = {
            "admin@enlasnubes.com": {
                "id": "user_admin_001",
                "email": "admin@enlasnubes.com",
                "password": "admin123",
                "name": "Administrador",
                "role": "admin",
            },
            "manager@enlasnubes.com": {
                "id": "user_manager_001",
                "email": "manager@enlasnubes.com",
                "password": "manager123",
                "name": "Encargada",
                "role": "manager",
            },
            "waiter@enlasnubes.com": {
                "id": "user_waiter_001",
                "email": "waiter@enlasnubes.com",
                "password": "waiter123",
                "name": "Camarero",
                "role": "waiter",
            },
        }

    def create_access_token(self, user_id: str, email: str, role: str) -> str:
        """Crea un JWT access token."""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: str, email: str, role: str) -> str:
        """Crea un JWT refresh token."""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
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

    async def authenticate_user(
        self, email: str, password: str
    ) -> Optional[Dict[str, Any]]:
        """
        Autentica un usuario por email y password.
        Retorna los datos del usuario si es exitoso, None si no.
        """
        user = self._demo_users.get(email)
        if not user:
            return None

        if password != user["password"]:
            return None

        return {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
        }

    async def create_user(
        self, email: str, password: str, name: str, role: str = "staff"
    ) -> Dict[str, Any]:
        """Crea un nuevo usuario (solo para desarrollo)."""
        user_id = f"user_{email.split('@')[0]}_{len(self._demo_users) + 1}"
        new_user = {
            "id": user_id,
            "email": email,
            "password": password,
            "name": name,
            "role": role,
        }
        self._demo_users[email] = new_user
        logger.info(f"Created new user: {email} (role: {role})")

        return {
            "id": user_id,
            "email": email,
            "name": name,
            "role": role,
        }


# Instancia singleton
auth_service = AuthService()


# ========== DEPENDENCIES ==========


def require_role(allowed_roles: List[str]):
    """
    FastAPI dependency que verifica que el usuario tenga uno de los roles permitidos.

    Uso:
        @router.get("/admin-only")
        async def admin_endpoint(user: TokenData = Depends(require_role(["admin"]))):
            return {"message": f"Hello admin {user.email}"}
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

        user_role = payload.get("role", "guest")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Roles requeridos: {allowed_roles}",
            )

        return TokenData(
            user_id=payload["sub"],
            email=payload["email"],
            role=user_role,
        )

    return _require_role
