"""
Servicio de autenticación JWT para app móvil.
Maneja login, refresh tokens y RBAC (Role-Based Access Control).
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import logging
import redis.asyncio as redis

from src.core.config import settings

logger = logging.getLogger(__name__)

# Configuración de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    """Datos contenidos en el token JWT."""
    user_id: str
    email: str
    role: str
    permissions: list


class UserLogin(BaseModel):
    """Modelo para login de usuario."""
    email: str
    password: str
    device_token: Optional[str] = None  # FCM token para push notifications


class UserCreate(BaseModel):
    """Modelo para crear nuevo usuario."""
    email: str
    password: str
    name: str
    role: str  # waiter, cook, manager, admin
    phone: Optional[str] = None


class AuthService:
    """Servicio de autenticación para usuarios de la app móvil."""
    
    # Definición de roles y permisos
    ROLES = {
        "waiter": {
            "name": "Camarero",
            "permissions": [
                "reservations.view",
                "reservations.update_status",
                "tables.view",
                "tables.update_status",
                "notes.add"
            ]
        },
        "cook": {
            "name": "Cocinero", 
            "permissions": [
                "kitchen.view",
                "kitchen.update_status",
                "reservations.view_limited",
                "alerts.receive"
            ]
        },
        "manager": {
            "name": "Encargada",
            "permissions": [
                "reservations.view",
                "reservations.create",
                "reservations.update",
                "reservations.cancel",
                "tables.manage",
                "waitlist.manage",
                "incidents.manage",
                "reports.view"
            ]
        },
        "admin": {
            "name": "Administrador",
            "permissions": [
                "*"  # Todos los permisos
            ]
        }
    }
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = 15  # Tokens cortos para seguridad
        self.refresh_token_expire_days = 7
        self.redis_client = None
    
    async def get_redis_client(self):
        """Obtiene cliente de Redis de forma lazy."""
        if self.redis_client is None:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        return self.redis_client
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica contraseña contra hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Genera hash de contraseña."""
        return pwd_context.hash(password)
    
    def create_access_token(self, user_id: str, email: str, role: str) -> str:
        """Crea token JWT de acceso."""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "permissions": self.ROLES.get(role, {}).get("permissions", []),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str, email: Optional[str] = None, role: Optional[str] = None) -> str:
        """Crea token de refresco."""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> Optional[Dict]:
        """Decodifica y valida token JWT."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verificar si el token está en blacklist (síncrono, solo si redis está disponible)
            if self.redis_client:
                token_hash = self._get_token_hash(token)
                is_blacklisted = self.redis_client.get(f"blacklist:{token_hash}")
                if is_blacklisted:
                    logger.warning(f"Token is blacklisted: {token_hash}")
                    return None
            
            return payload
        except JWTError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    async def invalidate_token(self, token: str):
        """Agrega token a blacklist en Redis."""
        try:
            client = await self.get_redis_client()
            token_hash = self._get_token_hash(token)
            
            # Decodificar token para obtener expiración
            payload = self.decode_token(token)
            if payload:
                exp = payload.get("exp")
                if exp:
                    # Calcular TTL hasta expiración del token
                    ttl = exp - int(datetime.utcnow().timestamp())
                    if ttl > 0:
                        await client.setex(
                            f"blacklist:{token_hash}",
                            ttl,
                            "1"
                        )
                        logger.info(f"Token blacklisted with TTL {ttl}s")
        except Exception as e:
            logger.error(f"Error invalidating token: {e}")
    
    def _get_token_hash(self, token: str) -> str:
        """Genera hash único del token para blacklist."""
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest()[:32]
    
    def verify_role_permission(self, role: str, permission: str) -> bool:
        """Verifica si un rol tiene un permiso específico."""
        if role not in self.ROLES:
            return False
        
        permissions = self.ROLES[role].get("permissions", [])
        
        # Admin tiene todos los permisos
        if "*" in permissions:
            return True
        
        # Verificar permiso específico o wildcard de categoría
        if permission in permissions:
            return True
        
        # Verificar wildcard (ej: "reservations.*")
        category = permission.split(".")[0]
        if f"{category}.*" in permissions:
            return True
        
        return False
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """
        Autentica usuario contra base de datos.
        En producción, esto consultaría Supabase/Airtable.
        """
        # TODO: Implementar consulta real a base de datos
        # Por ahora, estructura del retorno esperado:
        """
        user = await get_user_by_email(email)
        if not user:
            return None
        
        if not self.verify_password(password, user["password_hash"]):
            return None
        
        return {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "is_active": user["is_active"]
        }
        """
        return None  # Placeholder
    
    async def register_device_token(self, user_id: str, device_token: str):
        """Registra token FCM para push notifications."""
        # TODO: Guardar en base de datos
        logger.info(f"Registering device token for user {user_id}")


# Instancia singleton
auth_service = AuthService()
