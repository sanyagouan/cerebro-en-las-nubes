"""
Dashboard API Router - Endpoints específicos para el dashboard web.
Este router maneja autenticación y operaciones del dashboard sin el prefijo 'mobile'.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from loguru import logger

from src.application.services.auth_service import AuthService
from src.api.middleware.rate_limiting import auth_limit

# Initialize router sin prefijo para el dashboard
router = APIRouter(prefix="/api", tags=["dashboard"])

# Initialize services
auth_service = AuthService()


# ========== REQUEST/RESPONSE MODELS ==========

class LoginRequest(BaseModel):
    """Request body para login"""
    email: EmailStr
    password: str
    device_token: str | None = None  # Opcional para web


class LoginResponse(BaseModel):
    """Response body para login exitoso"""
    access_token: str
    refresh_token: str
    token_type: str
    user: dict


# ========== ENDPOINTS ==========

@router.post("/auth/login", response_model=LoginResponse)
@auth_limit()
async def dashboard_login(request: LoginRequest):
    """
    Login para dashboard web. Retorna JWT tokens.

    **Usuarios demo:**
    - admin@enlasnubes.com / admin123 (administrador)
    - manager@enlasnubes.com / manager123 (encargado)
    - waiter@enlasnubes.com / waiter123 (camarero)
    """
    # TODO: Implementar autenticación real contra Supabase Auth
    # Por ahora, usuarios hardcodeados para desarrollo

    # Usuarios de prueba
    DEMO_USERS = {
        "admin@enlasnubes.com": {
            "id": "user_admin_001",
            "email": "admin@enlasnubes.com",
            "password": "admin123",  # En producción: hash bcrypt
            "name": "Administrador",
            "role": "admin"
        },
        "manager@enlasnubes.com": {
            "id": "user_manager_001",
            "email": "manager@enlasnubes.com",
            "password": "manager123",
            "name": "Encargada",
            "role": "manager"
        },
        "waiter@enlasnubes.com": {
            "id": "user_waiter_001",
            "email": "waiter@enlasnubes.com",
            "password": "waiter123",
            "name": "Camarero",
            "role": "waiter"
        }
    }

    # Buscar usuario
    user = DEMO_USERS.get(request.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )

    # Verificar contraseña (en desarrollo, comparación simple; en producción: bcrypt)
    if request.password != user["password"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )

    # Generar tokens JWT
    access_token = auth_service.create_access_token(
        user_id=user["id"],
        email=user["email"],
        role=user["role"]
    )

    refresh_token = auth_service.create_refresh_token(
        user_id=user["id"],
        email=user["email"],
        role=user["role"]
    )

    logger.info(f"Dashboard login successful: {user['email']} (role: {user['role']})")

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user={
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"]
        }
    )
