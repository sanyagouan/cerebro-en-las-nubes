"""
API endpoints para app móvil.
Autenticación, reservas, mesas y notificaciones.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
import logging

from src.services.auth_service import auth_service, UserLogin, TokenData
from src.api.websocket.connection_manager import manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/mobile", tags=["mobile"])
security = HTTPBearer()


# ============ MODELOS ============

class LoginRequest(BaseModel):
    email: str
    password: str
    device_token: Optional[str] = None  # FCM token


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshRequest(BaseModel):
    refresh_token: str


class ReservationResponse(BaseModel):
    id: str
    customer_name: str
    phone: str
    date: date
    time: str
    pax: int
    status: str  # pending, confirmed, seated, cancelled, no_show
    table_id: Optional[str] = None
    table_name: Optional[str] = None
    location: Optional[str] = None  # interior, terrace
    notes: Optional[str] = None
    special_requests: List[str] = []
    created_at: datetime


class TableResponse(BaseModel):
    id: str
    name: str
    capacity: int
    max_capacity: int
    location: str  # interior, terrace
    status: str  # free, occupied, reserved, maintenance
    current_reservation: Optional[dict] = None


class UpdateStatusRequest(BaseModel):
    reservation_id: Optional[str] = None
    table_id: Optional[str] = None
    status: str
    notes: Optional[str] = None


class DashboardStats(BaseModel):
    total_reservations: int
    confirmed: int
    pending: int
    seated: int
    cancelled: int
    occupancy_rate: float
    pax_total: int


# ============ DEPENDENCIAS ============

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """Dependency para verificar JWT token."""
    token = credentials.credentials
    payload = auth_service.decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    return TokenData(
        user_id=payload["sub"],
        email=payload["email"],
        role=payload["role"],
        permissions=payload.get("permissions", [])
    )


def check_permission(user: TokenData, permission: str):
    """Verifica si usuario tiene permiso."""
    if not auth_service.verify_role_permission(user.role, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {permission}"
        )


# ============ AUTH ENDPOINTS ============

@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login de usuario móvil. Retorna JWT tokens."""
    # TODO: Implementar autenticación real contra Supabase Auth
    # Por ahora, este endpoint está deshabilitado hasta conectar con Supabase
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not implemented yet. Please configure Supabase Auth."
    )


@router.post("/auth/refresh")
async def refresh_token(request: RefreshRequest):
    """Refresca access token usando refresh token."""
    payload = auth_service.decode_token(request.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload["sub"]
    
    # TODO: Verificar que usuario existe y está activo
    
    # TODO: Obtener usuario real desde base de datos
    # Por ahora, usar datos del token si existen
    email = payload.get("email", "")
    role = payload.get("role", "")
    if not email or not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing user data for token refresh"
        )

    new_access_token = auth_service.create_access_token(
        user_id=user_id,
        email=email,
        role=role
    )
    
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/auth/logout")
async def logout(
    request: Request,
    user: TokenData = Depends(get_current_user)
):
    """
    Logout de usuario (invalida tokens).
    
    Agrega el token actual a la blacklist en Redis para invalidarlo
    antes de su expiración natural.
    """
    # Obtener el token del header Authorization
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        # Invalidar el token en Redis
        await auth_service.invalidate_token(token)
    
    return {"message": "Logged out successfully"}


# ============ RESERVATIONS ENDPOINTS ============

@router.get("/reservations", response_model=List[ReservationResponse])
async def get_reservations(
    date: Optional[date] = None,
    status: Optional[str] = None,
    user: TokenData = Depends(get_current_user)
):
    """Obtiene lista de reservas filtradas."""
    check_permission(user, "reservations.view")
    
    # TODO: Implementar consulta real a Airtable/Supabase
    # Por ahora, retornamos estructura vacía
    return []


@router.get("/reservations/{reservation_id}", response_model=ReservationResponse)
async def get_reservation(
    reservation_id: str,
    user: TokenData = Depends(get_current_user)
):
    """Obtiene detalle de una reserva."""
    check_permission(user, "reservations.view")
    
    # TODO: Implementar consulta real
    raise HTTPException(status_code=404, detail="Reservation not found")


@router.put("/reservations/{reservation_id}/status")
async def update_reservation_status(
    reservation_id: str,
    request: UpdateStatusRequest,
    user: TokenData = Depends(get_current_user)
):
    """Actualiza estado de reserva (seated, paying, cancelled, etc)."""
    check_permission(user, "reservations.update_status")
    
    # TODO: Actualizar en base de datos
    
    # Notificar a clientes vía WebSocket
    await manager.broadcast_reservation_update(
        {
            "id": reservation_id,
            "status": request.status,
            "updated_by": user.user_id,
            "notes": request.notes
        },
        event_type=request.status
    )
    
    return {"message": "Status updated", "reservation_id": reservation_id, "status": request.status}


@router.post("/reservations")
async def create_reservation(
    reservation: dict,
    user: TokenData = Depends(get_current_user)
):
    """Crea nueva reserva (solo encargada/admin)."""
    check_permission(user, "reservations.create")
    
    # TODO: Crear en base de datos
    
    # Notificar a todos los conectados
    await manager.broadcast_reservation_update(
        reservation,
        event_type="created"
    )
    
    return {"message": "Reservation created", "id": "new_id"}


# ============ TABLES ENDPOINTS ============

@router.get("/tables", response_model=List[TableResponse])
async def get_tables(
    location: Optional[str] = None,
    user: TokenData = Depends(get_current_user)
):
    """Obtiene estado de todas las mesas."""
    check_permission(user, "tables.view")
    
    # TODO: Implementar consulta real
    return []


@router.get("/tables/{table_id}", response_model=TableResponse)
async def get_table(
    table_id: str,
    user: TokenData = Depends(get_current_user)
):
    """Obtiene detalle de una mesa."""
    check_permission(user, "tables.view")
    
    # TODO: Implementar consulta real
    raise HTTPException(status_code=404, detail="Table not found")


@router.put("/tables/{table_id}/status")
async def update_table_status(
    table_id: str,
    request: UpdateStatusRequest,
    user: TokenData = Depends(get_current_user)
):
    """Actualiza estado de mesa (free, occupied, maintenance)."""
    check_permission(user, "tables.update_status")
    
    # TODO: Actualizar en base de datos
    
    # Notificar vía WebSocket
    await manager.broadcast_table_status(
        table_id=table_id,
        status=request.status,
        reservation_id=request.reservation_id
    )
    
    return {"message": "Table status updated", "table_id": table_id, "status": request.status}


# ============ DASHBOARD ENDPOINTS ============

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    date: Optional[date] = None,
    user: TokenData = Depends(get_current_user)
):
    """Estadísticas del día para dashboard."""
    check_permission(user, "reports.view")
    
    # TODO: Calcular estadísticas reales
    return DashboardStats(
        total_reservations=0,
        confirmed=0,
        pending=0,
        seated=0,
        cancelled=0,
        occupancy_rate=0.0,
        pax_total=0
    )


# ============ NOTIFICATIONS ENDPOINTS ============

class DeviceTokenRequest(BaseModel):
    device_token: str


@router.post("/notifications/register")
async def register_device_token(
    request: DeviceTokenRequest,
    user: TokenData = Depends(get_current_user)
):
    """Registra token FCM para push notifications."""
    await auth_service.register_device_token(user.user_id, request.device_token)
    return {"message": "Device token registered"}


@router.post("/notifications/test")
async def test_push_notification(
    user: TokenData = Depends(get_current_user)
):
    """Envía notificación de prueba al usuario actual."""
    # TODO: Implementar envío FCM
    return {"message": "Test notification sent"}
