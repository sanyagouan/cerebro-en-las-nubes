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
from src.api.mobile.models import (
    CreateReservationRequest,
    UpdateReservationRequest,
    CancelReservationRequest,
    ReservationResponse,
    PaginatedReservationsResponse,
    CreateTableRequest,
    UpdateTableRequest,
    TableResponse
)
from src.api.mobile.airtable_helpers import (
    airtable_to_reservation_response,
    reservation_request_to_airtable_fields,
    build_airtable_filter,
    AIRTABLE_FIELD_MAP
)
from src.application.services.waitlist_service import WaitlistService
from src.core.entities.waitlist import WaitlistEntry, WaitlistStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/mobile", tags=["mobile"])
security = HTTPBearer()

# Airtable configuration
AIRTABLE_BASE_ID = "appQ2ZXAR68cqDmJt"
RESERVATIONS_TABLE_NAME = "Reservas"


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
    
    # Registrar device token si se proporciona (para push notifications)
    if request.device_token:
        await auth_service.register_device_token(user["id"], request.device_token)
    
    logger.info(f"User logged in: {user['email']} (role: {user['role']})")
    
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

@router.get("/reservations", response_model=PaginatedReservationsResponse)
async def get_reservations(
    fecha: Optional[date] = None,
    estado: Optional[str] = None,
    mesa: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
    user: TokenData = Depends(get_current_user)
):
    """
    Obtiene lista de reservas con filtros y paginación.

    Args:
        fecha: Filtrar por fecha de reserva (ISO format YYYY-MM-DD)
        estado: Filtrar por estado (Pendiente, Confirmada, Sentada, etc.)
        mesa: Filtrar por mesa asignada (ID de mesa)
        offset: Número de registros a saltar (default: 0)
        limit: Máximo de registros a retornar (default: 100, max: 100)

    Returns:
        PaginatedReservationsResponse con lista de reservas, total, y metadata de paginación
    """
    check_permission(user, "reservations.view")

    try:
        # Construir filtro de Airtable
        filter_formula = build_airtable_filter(fecha=fecha, estado=estado, mesa=mesa)

        # Llamar a Airtable MCP para obtener records
        from src.infrastructure.mcp.airtable_client import airtable_client

        list_params = {
            "base_id": AIRTABLE_BASE_ID,
            "table_name": RESERVATIONS_TABLE_NAME,
            "max_records": limit
        }

        if filter_formula:
            list_params["filterByFormula"] = filter_formula

        # Sort por fecha descendente (más recientes primero)
        list_params["sort"] = [{"field": AIRTABLE_FIELD_MAP["fecha"], "direction": "desc"}]

        records_response = await airtable_client.list_records(**list_params)

        # Extraer records
        all_records = records_response.get("records", [])
        total = len(all_records)

        # Aplicar paginación manual (Airtable MCP puede no soportar offset nativo)
        paginated_records = all_records[offset:offset + limit]

        # Convertir a ReservationResponse
        reservations = [
            airtable_to_reservation_response(record)
            for record in paginated_records
        ]

        return PaginatedReservationsResponse(
            reservations=reservations,
            total=total,
            offset=offset,
            limit=limit,
            has_more=(offset + limit) < total
        )

    except Exception as e:
        logger.error(f"Error fetching reservations from Airtable: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving reservations: {str(e)}"
        )


@router.get("/reservations/{reservation_id}", response_model=ReservationResponse)
async def get_reservation(
    reservation_id: str,
    user: TokenData = Depends(get_current_user)
):
    """
    Obtiene detalle completo de una reserva específica.

    Args:
        reservation_id: Airtable record ID de la reserva

    Returns:
        ReservationResponse con todos los datos de la reserva
    """
    check_permission(user, "reservations.view")

    try:
        from src.infrastructure.mcp.airtable_client import airtable_client

        # Obtener record específico de Airtable
        record = await airtable_client.get_record(
            base_id=AIRTABLE_BASE_ID,
            table_name=RESERVATIONS_TABLE_NAME,
            record_id=reservation_id
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reservation {reservation_id} not found"
            )

        # Convertir a response model
        reservation = airtable_to_reservation_response(record)
        return reservation

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching reservation {reservation_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving reservation: {str(e)}"
        )


@router.put("/reservations/{reservation_id}", response_model=ReservationResponse)
async def update_reservation(
    reservation_id: str,
    reservation: UpdateReservationRequest,
    user: TokenData = Depends(get_current_user)
):
    """
    Actualiza una reserva existente (edición parcial).

    Args:
        reservation_id: Airtable record ID de la reserva
        reservation: Datos a actualizar (todos opcionales para edición parcial)

    Returns:
        ReservationResponse con la reserva actualizada
    """
    check_permission(user, "reservations.update")

    try:
        from src.infrastructure.mcp.airtable_client import airtable_client

        # Verificar que la reserva existe
        existing_record = await airtable_client.get_record(
            base_id=AIRTABLE_BASE_ID,
            table_name=RESERVATIONS_TABLE_NAME,
            record_id=reservation_id
        )

        if not existing_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reservation {reservation_id} not found"
            )

        # Convertir solo campos que no son None (partial update)
        update_data = reservation.model_dump(exclude_none=True)
        airtable_fields = reservation_request_to_airtable_fields(update_data)

        # Actualizar en Airtable
        updated_record = await airtable_client.update_record(
            base_id=AIRTABLE_BASE_ID,
            table_name=RESERVATIONS_TABLE_NAME,
            record_id=reservation_id,
            fields=airtable_fields
        )

        if not updated_record:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update reservation in Airtable"
            )

        # Convertir a response model
        reservation_response = airtable_to_reservation_response(updated_record)

        # Notificar a clientes WebSocket
        await manager.broadcast_reservation_update(
            reservation_response.model_dump(),
            event_type="updated"
        )

        logger.info(f"Reservation updated: {reservation_id} by user {user.user_id}")
        return reservation_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating reservation {reservation_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating reservation: {str(e)}"
        )


@router.put("/reservations/{reservation_id}/status")
async def update_reservation_status(
    reservation_id: str,
    request: UpdateStatusRequest,
    user: TokenData = Depends(get_current_user)
):
    """
    Actualiza estado de reserva (Pendiente, Confirmada, Sentada, Completada, Cancelada, NoShow).

    Args:
        reservation_id: Airtable record ID de la reserva
        request: Objeto con status y notas opcionales

    Returns:
        Dict con mensaje de éxito y datos de la reserva actualizada
    """
    check_permission(user, "reservations.update_status")

    try:
        from src.infrastructure.mcp.airtable_client import airtable_client

        # Verificar que la reserva existe
        existing_record = await airtable_client.get_record(
            base_id=AIRTABLE_BASE_ID,
            table_name=RESERVATIONS_TABLE_NAME,
            record_id=reservation_id
        )

        if not existing_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reservation {reservation_id} not found"
            )

        # Preparar campos para actualizar
        update_fields = {
            AIRTABLE_FIELD_MAP["estado"]: request.status
        }

        if request.notes:
            update_fields[AIRTABLE_FIELD_MAP["notas"]] = request.notes

        # Actualizar en Airtable
        updated_record = await airtable_client.update_record(
            base_id=AIRTABLE_BASE_ID,
            table_name=RESERVATIONS_TABLE_NAME,
            record_id=reservation_id,
            fields=update_fields
        )

        if not updated_record:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update reservation status in Airtable"
            )

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

        logger.info(f"Reservation status updated: {reservation_id} -> {request.status} by user {user.user_id}")
        return {
            "message": "Status updated successfully",
            "reservation_id": reservation_id,
            "status": request.status
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating reservation status {reservation_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating reservation status: {str(e)}"
        )


@router.post("/reservations", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    reservation: CreateReservationRequest,
    user: TokenData = Depends(get_current_user)
):
    """
    Crea una nueva reserva manual (dashboard o app móvil).

    Args:
        reservation: Datos de la nueva reserva

    Returns:
        ReservationResponse con la reserva creada (incluye ID de Airtable)
    """
    check_permission(user, "reservations.create")

    try:
        from src.infrastructure.mcp.airtable_client import airtable_client

        # Convertir request a fields de Airtable
        airtable_fields = reservation_request_to_airtable_fields(reservation.model_dump())

        # Crear record en Airtable
        created_record = await airtable_client.create_record(
            base_id=AIRTABLE_BASE_ID,
            table_name=RESERVATIONS_TABLE_NAME,
            fields=airtable_fields
        )

        if not created_record:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create reservation in Airtable"
            )

        # Convertir a response model
        reservation_response = airtable_to_reservation_response(created_record)

        # Notificar a clientes WebSocket
        await manager.broadcast_reservation_update(
            reservation_response.model_dump(),
            event_type="created"
        )

        logger.info(f"Reservation created: {created_record['id']} by user {user.user_id}")
        return reservation_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating reservation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating reservation: {str(e)}"
        )


@router.post("/reservations/{reservation_id}/cancel")
async def cancel_reservation(
    reservation_id: str,
    request: CancelReservationRequest,
    user: TokenData = Depends(get_current_user)
):
    """
    Cancela una reserva existente.

    - Actualiza estado a "Cancelada"
    - Libera mesa asignada automáticamente
    - Envía notificación SMS/WhatsApp al cliente (si notificar_cliente=True)
    - Notifica al staff vía push notification
    - Broadcast WebSocket a todos los clientes conectados

    Args:
        reservation_id: Airtable record ID de la reserva
        request: Datos de cancelación (motivo opcional, notificar_cliente flag)

    Returns:
        Confirmación de cancelación con detalles
    """
    check_permission(user, "reservations.cancel")

    try:
        from src.infrastructure.mcp.airtable_client import airtable_client

        # 1. Verificar que la reserva existe
        existing_record = await airtable_client.get_record(
            base_id=AIRTABLE_BASE_ID,
            table_name=RESERVATIONS_TABLE_NAME,
            record_id=reservation_id
        )

        if not existing_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reservation {reservation_id} not found"
            )

        existing_fields = existing_record.get("fields", {})

        # 2. Verificar que la reserva no esté ya cancelada o completada
        current_estado = existing_fields.get(AIRTABLE_FIELD_MAP["estado"], "")
        if current_estado in ["Cancelada", "Completada"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel reservation with status '{current_estado}'"
            )

        # 3. Preparar campos de actualización
        update_fields = {
            AIRTABLE_FIELD_MAP["estado"]: "Cancelada",
            AIRTABLE_FIELD_MAP["mesa_asignada"]: []  # Liberar mesa (linked record vacío)
        }

        # Agregar motivo de cancelación en notas
        if request.motivo:
            notas_actuales = existing_fields.get(AIRTABLE_FIELD_MAP["notas"], "")
            motivo_texto = f"\n[CANCELACIÓN] {request.motivo}"
            update_fields[AIRTABLE_FIELD_MAP["notas"]] = notas_actuales + motivo_texto

        # 4. Actualizar en Airtable
        updated_record = await airtable_client.update_record(
            base_id=AIRTABLE_BASE_ID,
            table_name=RESERVATIONS_TABLE_NAME,
            record_id=reservation_id,
            fields=update_fields
        )

        # 5. Obtener datos del cliente para notificación
        cliente_telefono = existing_fields.get(AIRTABLE_FIELD_MAP["telefono"], "")
        cliente_nombre = existing_fields.get(AIRTABLE_FIELD_MAP["nombre"], "")
        fecha_reserva = existing_fields.get(AIRTABLE_FIELD_MAP["fecha"], "")
        hora_reserva = existing_fields.get(AIRTABLE_FIELD_MAP["hora"], "")

        # 6. Enviar notificación SMS/WhatsApp al cliente (si aplica)
        sms_sent = False
        if request.notificar_cliente and cliente_telefono:
            try:
                from src.infrastructure.services.twilio_service import twilio_service

                mensaje = (
                    f"Hola {cliente_nombre}, tu reserva para {fecha_reserva} a las {hora_reserva} "
                    f"ha sido cancelada. "
                    f"Si tienes dudas, contáctanos. - En Las Nubes Resto Bar"
                )

                await twilio_service.send_whatsapp(
                    to=cliente_telefono,
                    message=mensaje
                )
                sms_sent = True
                logger.info(f"WhatsApp sent to {cliente_telefono} for cancellation {reservation_id}")
            except Exception as e:
                logger.error(f"Error sending WhatsApp notification: {e}", exc_info=True)
                # No fallar todo el proceso si falla notificación

        # 7. Enviar push notification al staff
        try:
            from src.infrastructure.services.fcm_service import fcm_service

            await fcm_service.send_notification_to_role(
                role="waiter",
                title="🚫 Reserva Cancelada",
                body=f"{cliente_nombre} - {fecha_reserva} {hora_reserva} ({existing_fields.get(AIRTABLE_FIELD_MAP['pax'], '')} pax)",
                data={
                    "type": "reservation_cancelled",
                    "reservation_id": reservation_id,
                    "motivo": request.motivo or ""
                }
            )
            logger.info(f"Push notification sent to staff for cancellation {reservation_id}")
        except Exception as e:
            logger.error(f"Error sending push notification: {e}", exc_info=True)

        # 8. Broadcast WebSocket a todos los clientes
        await manager.broadcast_reservation_update(
            {
                "id": reservation_id,
                "estado": "Cancelada",
                "mesa_asignada": None,
                "cancelled_by": user.user_id,
                "motivo": request.motivo,
                "fecha": fecha_reserva,
                "hora": hora_reserva
            },
            event_type="cancelled"
        )

        logger.info(
            f"Reservation cancelled: {reservation_id} by {user.user_id} "
            f"(motivo: {request.motivo or 'N/A'}, SMS sent: {sms_sent})"
        )

        return {
            "message": "Reservation cancelled successfully",
            "reservation_id": reservation_id,
            "mesa_liberada": len(existing_fields.get(AIRTABLE_FIELD_MAP["mesa_asignada"], [])) > 0,
            "notificacion_enviada": sms_sent,
            "motivo": request.motivo
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling reservation {reservation_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelling reservation: {str(e)}"
        )


# ============ TABLES ENDPOINTS ============
# MIGRADO A AIRTABLE: Todos los endpoints ahora usan TableRepository
# Tabla MESAS en Airtable (Base ID: appQ2ZXAR68cqDmJt)

@router.get("/tables", response_model=List[TableResponse])
async def get_tables(
    zona: Optional[str] = None,
    user: TokenData = Depends(get_current_user)
):
    """
    Lista todas las mesas del restaurante con su estado actual.

    Parámetros:
        - zona: Filtrar por zona (Terraza, Interior) - opcional

    Returns:
        Lista de mesas con su configuración y estado actual
    """
    check_permission(user, "tables.view")

    try:
        from src.infrastructure.repositories.table_repository import table_repository
        from src.core.entities.table import TableZone

        # Validar zona si se proporciona
        zona_enum = None
        if zona:
            if zona not in ["Terraza", "Interior"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid zona. Must be 'Terraza' or 'Interior'"
                )
            zona_enum = TableZone(zona)

        # Obtener todas las mesas desde Airtable (con filtro opcional por zona)
        all_tables = await table_repository.list_all(zona=zona_enum)

        # Convertir a TableResponse
        tables_response = []
        for table in all_tables:
            tables_response.append(
                TableResponse(
                    id=table.id,
                    nombre=table.nombre,
                    zona=table.zona.value,
                    capacidad_min=table.capacidad_min,
                    capacidad_max=table.capacidad_max,
                    ampliable=table.ampliable,
                    auxiliar_requerida=table.auxiliar_requerida,
                    capacidad_ampliada=table.capacidad_ampliada,
                    notas=table.notas,
                    requiere_aviso=table.requiere_aviso,
                    prioridad=table.prioridad,
                    status=table.status.value
                )
            )

        logger.info(f"Listed {len(tables_response)} tables from Airtable (zona filter: {zona or 'all'})")
        return tables_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing tables: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving tables: {str(e)}"
        )


@router.get("/tables/{table_id}", response_model=TableResponse)
async def get_table(
    table_id: str,
    user: TokenData = Depends(get_current_user)
):
    """
    Obtiene detalle de una mesa específica por su ID.

    Args:
        table_id: ID de la mesa (T1, S2, SOFA1, etc.) - Airtable record ID

    Returns:
        Datos completos de la mesa
    """
    check_permission(user, "tables.view")

    try:
        from src.infrastructure.repositories.table_repository import table_repository

        # Obtener mesa desde Airtable
        table = await table_repository.get_by_id(table_id)

        if not table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table {table_id} not found"
            )

        return TableResponse(
            id=table.id,
            nombre=table.nombre,
            zona=table.zona.value,
            capacidad_min=table.capacidad_min,
            capacidad_max=table.capacidad_max,
            ampliable=table.ampliable,
            auxiliar_requerida=table.auxiliar_requerida,
            capacidad_ampliada=table.capacidad_ampliada,
            notas=table.notas,
            requiere_aviso=table.requiere_aviso,
            prioridad=table.prioridad,
            status=table.status.value
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting table {table_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving table: {str(e)}"
        )


@router.post("/tables", response_model=TableResponse, status_code=status.HTTP_201_CREATED)
async def create_table(
    request: CreateTableRequest,
    user: TokenData = Depends(get_current_user)
):
    """
    Crea una nueva mesa en el sistema.

    Args:
        request: Datos de la nueva mesa

    Returns:
        Mesa creada
    """
    check_permission(user, "tables.create")

    try:
        from src.infrastructure.repositories.table_repository import table_repository
        from src.core.entities.table import Table, TableZone, TableStatus

        # Crear objeto Table
        table = Table(
            id=request.id,
            nombre=request.nombre,
            zona=TableZone(request.zona),
            capacidad_min=request.capacidad_min,
            capacidad_max=request.capacidad_max,
            ampliable=request.ampliable,
            auxiliar_requerida=request.auxiliar_requerida,
            capacidad_ampliada=request.capacidad_ampliada,
            notas=request.notas,
            requiere_aviso=request.requiere_aviso,
            prioridad=request.prioridad,
            status=TableStatus.AVAILABLE  # Nuevas mesas siempre empiezan disponibles
        )

        # Crear en Airtable
        created_table = await table_repository.create(table)

        return TableResponse(
            id=created_table.id,
            nombre=created_table.nombre,
            zona=created_table.zona.value,
            capacidad_min=created_table.capacidad_min,
            capacidad_max=created_table.capacidad_max,
            ampliable=created_table.ampliable,
            auxiliar_requerida=created_table.auxiliar_requerida,
            capacidad_ampliada=created_table.capacidad_ampliada,
            notas=created_table.notas,
            requiere_aviso=created_table.requiere_aviso,
            prioridad=created_table.prioridad,
            status=created_table.status.value
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating table: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating table: {str(e)}"
        )


@router.put("/tables/{table_id}", response_model=TableResponse)
async def update_table(
    table_id: str,
    request: UpdateTableRequest,
    user: TokenData = Depends(get_current_user)
):
    """
    Actualiza configuración de una mesa existente.

    Args:
        table_id: ID de la mesa a actualizar
        request: Campos a actualizar (partial update)

    Returns:
        Mesa actualizada
    """
    check_permission(user, "tables.update")

    try:
        from src.infrastructure.repositories.table_repository import table_repository

        # Construir dict de updates solo con campos proporcionados
        updates = {}
        if request.nombre is not None:
            updates["nombre"] = request.nombre
        if request.zona is not None:
            updates["zona"] = request.zona
        if request.capacidad_min is not None:
            updates["capacidad_min"] = request.capacidad_min
        if request.capacidad_max is not None:
            updates["capacidad_max"] = request.capacidad_max
        if request.ampliable is not None:
            updates["ampliable"] = request.ampliable
        if request.auxiliar_requerida is not None:
            updates["auxiliar_requerida"] = request.auxiliar_requerida
        if request.capacidad_ampliada is not None:
            updates["capacidad_ampliada"] = request.capacidad_ampliada
        if request.notas is not None:
            updates["notas"] = request.notas
        if request.requiere_aviso is not None:
            updates["requiere_aviso"] = request.requiere_aviso
        if request.prioridad is not None:
            updates["prioridad"] = request.prioridad
        if request.status is not None:
            updates["status"] = request.status

        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update provided"
            )

        # Actualizar en Airtable
        updated_table = await table_repository.update(table_id, updates)

        return TableResponse(
            id=updated_table.id,
            nombre=updated_table.nombre,
            zona=updated_table.zona.value,
            capacidad_min=updated_table.capacidad_min,
            capacidad_max=updated_table.capacidad_max,
            ampliable=updated_table.ampliable,
            auxiliar_requerida=updated_table.auxiliar_requerida,
            capacidad_ampliada=updated_table.capacidad_ampliada,
            notas=updated_table.notas,
            requiere_aviso=updated_table.requiere_aviso,
            prioridad=updated_table.prioridad,
            status=updated_table.status.value
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating table {table_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating table: {str(e)}"
        )


@router.delete("/tables/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_table(
    table_id: str,
    user: TokenData = Depends(get_current_user)
):
    """
    Elimina una mesa del sistema.

    Args:
        table_id: ID de la mesa a eliminar
    """
    check_permission(user, "tables.delete")

    try:
        from src.infrastructure.repositories.table_repository import table_repository

        success = await table_repository.delete(table_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table {table_id} not found"
            )

        return None  # 204 No Content

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting table {table_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting table: {str(e)}"
        )


@router.put("/tables/{table_id}/status", response_model=TableResponse)
async def update_table_status(
    table_id: str,
    status_update: str,
    user: TokenData = Depends(get_current_user)
):
    """
    Actualiza el estado de una mesa (Libre, Ocupada, Reservada, Bloqueada).

    **IMPORTANTE**: Este endpoint cambia SOLO el estado, no otros atributos.

    Args:
        table_id: ID de la mesa
        status_update: Nuevo estado ("Libre", "Ocupada", "Reservada", "Bloqueada")

    Returns:
        Mesa actualizada con nuevo estado
    """
    check_permission(user, "tables.update_status")

    # Validar estado
    valid_statuses = ["Libre", "Ocupada", "Reservada", "Bloqueada"]
    if status_update not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    try:
        from src.infrastructure.repositories.table_repository import table_repository
        from src.core.entities.table import TableStatus

        # Convertir string a TableStatus enum
        new_status = TableStatus(status_update)

        # Actualizar estado
        updated_table = await table_repository.update_status(table_id, new_status)

        # TODO: Broadcast WebSocket para actualizar dashboards en tiempo real
        # await websocket_manager.broadcast_table_status_change(table_id, status_update)

        return TableResponse(
            id=updated_table.id,
            nombre=updated_table.nombre,
            zona=updated_table.zona.value,
            capacidad_min=updated_table.capacidad_min,
            capacidad_max=updated_table.capacidad_max,
            ampliable=updated_table.ampliable,
            auxiliar_requerida=updated_table.auxiliar_requerida,
            capacidad_ampliada=updated_table.capacidad_ampliada,
            notas=updated_table.notas,
            requiere_aviso=updated_table.requiere_aviso,
            prioridad=updated_table.prioridad,
            status=updated_table.status.value
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating table status {table_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating table status: {str(e)}"
        )


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


# ============ WAITLIST ENDPOINTS ============

# Instanciar servicio de waitlist
waitlist_service = WaitlistService()


class WaitlistCreateRequest(BaseModel):
    """Request para añadir cliente a lista de espera."""
    nombre_cliente: str
    telefono_cliente: str
    fecha: date
    hora: str  # HH:MM format
    num_personas: int
    zona_preferida: Optional[str] = None
    notas: Optional[str] = None


class WaitlistResponse(BaseModel):
    """Response de entrada en waitlist."""
    id: str
    nombre_cliente: str
    telefono_cliente: str
    fecha: str
    hora: str
    num_personas: int
    zona_preferida: Optional[str]
    estado: str
    posicion: Optional[int]
    created_at: str
    notified_at: Optional[str]
    notas: Optional[str]


def waitlist_entry_to_response(entry: WaitlistEntry) -> WaitlistResponse:
    """Convierte WaitlistEntry a WaitlistResponse."""
    return WaitlistResponse(
        id=entry.airtable_id or entry.id or "",
        nombre_cliente=entry.nombre_cliente,
        telefono_cliente=entry.telefono_cliente,
        fecha=entry.fecha.isoformat(),
        hora=entry.hora.strftime("%H:%M"),
        num_personas=entry.num_personas,
        zona_preferida=entry.zona_preferida,
        estado=entry.estado.value,
        posicion=entry.posicion,
        created_at=entry.created_at.isoformat(),
        notified_at=entry.notified_at.isoformat() if entry.notified_at else None,
        notas=entry.notas
    )


@router.get("/waitlist", response_model=List[WaitlistResponse])
async def list_waitlist(
    fecha: Optional[date] = None,
    estado: Optional[str] = None,
    user: TokenData = Depends(get_current_user)
):
    """
    Lista entradas en la lista de espera.

    Query params:
    - fecha: Filtrar por fecha (YYYY-MM-DD)
    - estado: Filtrar por estado (waiting, notified, confirmed, expired, cancelled)

    Permisos: reservations.view
    """
    check_permission(user, "reservations.view")

    try:
        if estado:
            try:
                status_filter = WaitlistStatus(estado)
                entries = await waitlist_service.waitlist_repository.list_by_status(
                    status=status_filter,
                    fecha=fecha
                )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estado inválido: {estado}. Valores válidos: waiting, notified, confirmed, expired, cancelled"
                )
        else:
            # Sin filtro específico, traer todas las WAITING del día (o fecha especificada)
            entries = await waitlist_service.waitlist_repository.list_by_status(
                status=WaitlistStatus.WAITING,
                fecha=fecha or date.today()
            )

        return [waitlist_entry_to_response(entry) for entry in entries]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing waitlist: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing waitlist: {str(e)}"
        )


@router.post("/waitlist", response_model=WaitlistResponse, status_code=status.HTTP_201_CREATED)
async def create_waitlist_entry(
    request: WaitlistCreateRequest,
    user: TokenData = Depends(get_current_user)
):
    """
    Añade un cliente a la lista de espera.

    Permisos: reservations.create
    """
    check_permission(user, "reservations.create")

    try:
        from datetime import datetime as dt
        hora_time = dt.strptime(request.hora, "%H:%M").time()

        entry = await waitlist_service.add_to_waitlist(
            nombre=request.nombre_cliente,
            telefono=request.telefono_cliente,
            fecha=request.fecha,
            hora=hora_time,
            pax=request.num_personas,
            zona_preferida=request.zona_preferida,
            notas=request.notas
        )

        logger.info(f"Cliente {request.nombre_cliente} añadido a waitlist por {user.username}")

        return waitlist_entry_to_response(entry)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating waitlist entry: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating waitlist entry: {str(e)}"
        )


@router.post("/waitlist/{entry_id}/notify", response_model=WaitlistResponse)
async def notify_waitlist_entry(
    entry_id: str,
    user: TokenData = Depends(get_current_user)
):
    """
    Notifica manualmente al próximo cliente en waitlist.

    Nota: Normalmente esto es automático cuando se libera una mesa,
    pero este endpoint permite notificación manual.

    Permisos: reservations.create
    """
    check_permission(user, "reservations.create")

    try:
        # Obtener entrada
        entry = await waitlist_service.waitlist_repository.get_by_id(entry_id)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Waitlist entry {entry_id} not found"
            )

        # Verificar estado
        if entry.estado != WaitlistStatus.WAITING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Entry is not in WAITING state (current: {entry.estado.value})"
            )

        # Notificar
        notified_entry = await waitlist_service.notify_availability(
            fecha=entry.fecha,
            hora=entry.hora,
            pax=entry.num_personas
        )

        if not notified_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No matching waitlist entry found to notify"
            )

        logger.info(f"Waitlist entry {entry_id} notified manually by {user.username}")

        return waitlist_entry_to_response(notified_entry)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error notifying waitlist entry {entry_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error notifying waitlist entry: {str(e)}"
        )


@router.delete("/waitlist/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_waitlist_entry(
    entry_id: str,
    user: TokenData = Depends(get_current_user)
):
    """
    Elimina una entrada de la waitlist.

    Permisos: reservations.cancel
    """
    check_permission(user, "reservations.cancel")

    try:
        # Primero verificar que existe
        entry = await waitlist_service.waitlist_repository.get_by_id(entry_id)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Waitlist entry {entry_id} not found"
            )

        # Cancelar
        await waitlist_service.cancel_from_waitlist(entry_id)

        logger.info(f"Waitlist entry {entry_id} cancelled by {user.username}")

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting waitlist entry {entry_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting waitlist entry: {str(e)}"
        )
