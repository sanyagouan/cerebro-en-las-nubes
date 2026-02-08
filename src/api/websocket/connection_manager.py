"""
WebSocket Manager para tiempo real en app móvil.
Maneja conexiones de camareros, cocineros, encargados y admin.
"""
import asyncio
import json
from typing import Dict, List, Set
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Gestiona conexiones WebSocket por rol y sala."""
    
    def __init__(self):
        # Conexiones activas: {websocket: {"user_id": str, "role": str, "tables": List[str]}}
        self.active_connections: Dict[WebSocket, dict] = {}
        
        # Salas por tipo: {"reservations": {websocket1, websocket2}, "kitchen": {...}}
        self.rooms: Dict[str, Set[WebSocket]] = {
            "reservations": set(),
            "kitchen": set(),
            "admin": set(),
            "all": set()
        }
        
        # Tracking de mesas asignadas por conexión
        self.table_assignments: Dict[WebSocket, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, role: str):
        """Acepta nueva conexión WebSocket."""
        await websocket.accept()
        
        self.active_connections[websocket] = {
            "user_id": user_id,
            "role": role,
            "connected_at": datetime.utcnow().isoformat()
        }
        
        # Asignar a salas según rol
        self.rooms["all"].add(websocket)
        
        if role in ["waiter", "camarero"]:
            self.rooms["reservations"].add(websocket)
        elif role in ["cook", "cocinero"]:
            self.rooms["kitchen"].add(websocket)
        elif role in ["manager", "encargada", "admin"]:
            self.rooms["reservations"].add(websocket)
            self.rooms["kitchen"].add(websocket)
            self.rooms["admin"].add(websocket)
        
        self.table_assignments[websocket] = set()
        
        logger.info(f"WebSocket connected: {user_id} ({role})")
        
        # Enviar confirmación
        await self.send_personal_message({
            "type": "connection",
            "status": "connected",
            "role": role,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Desconecta cliente y limpia recursos."""
        if websocket in self.active_connections:
            user_info = self.active_connections[websocket]
            logger.info(f"WebSocket disconnected: {user_info.get('user_id')}")
            
            del self.active_connections[websocket]
            
            # Remover de todas las salas
            for room in self.rooms.values():
                room.discard(websocket)
            
            # Limpiar asignaciones de mesa
            if websocket in self.table_assignments:
                del self.table_assignments[websocket]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Envía mensaje a cliente específico."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_room(self, room: str, message: dict):
        """Envía mensaje a todos en una sala."""
        if room not in self.rooms:
            return
        
        disconnected = []
        for websocket in self.rooms[room]:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception:
                disconnected.append(websocket)
        
        # Limpiar conexiones fallidas
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def broadcast_to_role(self, role: str, message: dict):
        """Envía mensaje a usuarios con rol específico."""
        disconnected = []
        
        for websocket, info in self.active_connections.items():
            if info.get("role") == role:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception:
                    disconnected.append(websocket)
        
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def broadcast_reservation_update(self, reservation_data: dict, event_type: str):
        """Notifica actualización de reserva a clientes relevantes."""
        message = {
            "type": "reservation_update",
            "event": event_type,  # created, updated, cancelled, seated
            "data": reservation_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Enviar a sala de reservas
        await self.broadcast_to_room("reservations", message)
        
        # Si es alerta de cocina, también a cocineros
        if event_type in ["seated", "kitchen_alert"]:
            await self.broadcast_to_room("kitchen", message)
    
    async def broadcast_table_status(self, table_id: str, status: str, reservation_id: str = None):
        """Notifica cambio de estado de mesa."""
        message = {
            "type": "table_update",
            "table_id": table_id,
            "status": status,  # free, occupied, reserved, maintenance
            "reservation_id": reservation_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.broadcast_to_room("reservations", message)
    
    def get_connection_stats(self) -> dict:
        """Retorna estadísticas de conexiones."""
        role_counts = {}
        for info in self.active_connections.values():
            role = info.get("role", "unknown")
            role_counts[role] = role_counts.get(role, 0) + 1
        
        return {
            "total_connections": len(self.active_connections),
            "by_role": role_counts,
            "rooms": {name: len(conns) for name, conns in self.rooms.items()}
        }


# Instancia singleton del manager
manager = ConnectionManager()
