"""
WebSocket endpoint para app móvil.
Autenticación JWT + manejo de eventos en tiempo real.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from jose import JWTError, jwt
import json
import logging
from datetime import datetime

from src.api.websocket.connection_manager import manager
from src.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ws", tags=["websocket"])


async def verify_websocket_token(websocket: WebSocket) -> dict:
    """Verifica token JWT en query params de WebSocket."""
    try:
        # Token debe venir en query param: ?token=xxx
        token = websocket.query_params.get("token")
        
        if not token:
            await websocket.close(code=4001, reason="Missing authentication token")
            return None
        
        # Verificar JWT
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id = payload.get("sub")
        role = payload.get("role")
        
        if not user_id or not role:
            await websocket.close(code=4002, reason="Invalid token payload")
            return None
        
        return {"user_id": user_id, "role": role}
        
    except JWTError as e:
        logger.warning(f"Invalid JWT token: {e}")
        await websocket.close(code=4003, reason="Invalid authentication token")
        return None
    except Exception as e:
        logger.error(f"Error verifying WebSocket token: {e}")
        await websocket.close(code=4004, reason="Authentication error")
        return None


@router.websocket("/reservations")
async def websocket_reservations(websocket: WebSocket):
    """
    WebSocket principal para notificaciones de reservas.
    Requiere token JWT en query params.
    
    URL: ws://api.example.com/ws/reservations?token=JWT_TOKEN
    """
    # Verificar autenticación
    auth_data = await verify_websocket_token(websocket)
    if not auth_data:
        return
    
    user_id = auth_data["user_id"]
    role = auth_data["role"]
    
    # Conectar al manager
    await manager.connect(websocket, user_id, role)
    
    try:
        while True:
            # Esperar mensajes del cliente
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                
                if msg_type == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }, websocket)
                
                elif msg_type == "subscribe_table":
                    # Cliente quiere seguir una mesa específica
                    table_id = message.get("table_id")
                    if table_id:
                        manager.table_assignments[websocket].add(table_id)
                        await manager.send_personal_message({
                            "type": "subscribed",
                            "table_id": table_id
                        }, websocket)
                
                elif msg_type == "unsubscribe_table":
                    table_id = message.get("table_id")
                    if table_id and table_id in manager.table_assignments[websocket]:
                        manager.table_assignments[websocket].discard(table_id)
                
                elif msg_type == "status_update":
                    # Cliente actualiza estado (ej: marca mesa como ocupada)
                    await handle_status_update(websocket, role, message)
                
                else:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"Unknown message type: {msg_type}"
                    }, websocket)
                    
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON"
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket)


async def handle_status_update(websocket: WebSocket, role: str, message: dict):
    """Procesa actualización de estado desde cliente móvil."""
    entity_type = message.get("entity_type")  # reservation, table
    entity_id = message.get("entity_id")
    new_status = message.get("status")
    
    # Validar permisos según rol
    allowed_updates = {
        "waiter": ["seated", "paying", "free"],
        "camarero": ["seated", "paying", "free"],
        "cook": ["ready", "preparing"],
        "cocinero": ["ready", "preparing"],
        "manager": ["seated", "paying", "free", "cancelled", "confirmed"],
        "encargada": ["seated", "paying", "free", "cancelled", "confirmed"],
        "admin": ["seated", "paying", "free", "cancelled", "confirmed", "no_show"]
    }
    
    allowed = allowed_updates.get(role, [])
    
    if new_status not in allowed:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Role '{role}' cannot set status to '{new_status}'"
        }, websocket)
        return
    
    # Aquí se actualizaría en base de datos
    # Por ahora solo broadcasteamos el cambio
    if entity_type == "reservation":
        await manager.broadcast_reservation_update(
            {"id": entity_id, "status": new_status},
            event_type=new_status
        )
    elif entity_type == "table":
        await manager.broadcast_table_status(entity_id, new_status)
    
    # Confirmar al emisor
    await manager.send_personal_message({
        "type": "status_updated",
        "entity_type": entity_type,
        "entity_id": entity_id,
        "status": new_status
    }, websocket)


@router.get("/stats")
async def get_websocket_stats():
    """Endpoint HTTP para ver estadísticas de conexiones WebSocket."""
    return manager.get_connection_stats()
