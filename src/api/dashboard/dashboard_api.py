"""
Dashboard API Router - Endpoints específicos para el dashboard web.
Este router maneja autenticación y operaciones del dashboard sin el prefijo 'mobile'.
"""

from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from loguru import logger

from src.application.services.auth_service import auth_service

# Initialize router sin prefijo para el dashboard
router = APIRouter(prefix="/api", tags=["dashboard"])


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


class RefreshRequest(BaseModel):
    """Request body para refresh token"""

    refresh_token: str


class TokenResponse(BaseModel):
    """Response para refresh token"""

    access_token: str
    token_type: str


# ========== ENDPOINTS ==========


@router.post("/auth/login", response_model=LoginResponse)
async def dashboard_login(request: Request, login_data: LoginRequest):
    """
    Login para dashboard web. Retorna JWT tokens.

    **Usuarios demo:**
    - admin@enlasnubes.com / admin123 (administrador)
    - manager@enlasnubes.com / manager123 (encargado)
    - waiter@enlasnubes.com / waiter123 (camarero)
    """
    # Autenticar usuario
    user = await auth_service.authenticate_user(login_data.email, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )

    # Generar tokens JWT
    access_token = auth_service.create_access_token(
        user_id=user["id"], email=user["email"], role=user["role"]
    )

    refresh_token = auth_service.create_refresh_token(
        user_id=user["id"], email=user["email"], role=user["role"]
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
            "role": user["role"],
        },
    )


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(request: Request, refresh_data: RefreshRequest):
    """
    Refresca el access token usando un refresh token válido.
    """
    payload = auth_service.verify_token(refresh_data.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
        )

    # Generar nuevo access token
    new_access_token = auth_service.create_access_token(
        user_id=payload["sub"],
        email=payload["email"],
        role=payload["role"],
    )

    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
    )


@router.post("/auth/logout")
async def logout(request: Request):
    """
    Logout del usuario. En una implementación completa,
    esto invalidaría el token en una lista negra.
    """
    # TODO: Implementar blacklist de tokens si es necesario
    return {"message": "Logout exitoso"}


@router.get("/auth/me")
async def get_current_user(request: Request):
    """
    Obtiene información del usuario actual basado en el token JWT.
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorización requerido",
        )

    token = auth_header.replace("Bearer ", "")
    payload = auth_service.verify_token(token)

    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )

    return {
        "id": payload["sub"],
        "email": payload["email"],
        "role": payload["role"],
    }
