"""
Servicio de notificaciones push Firebase Cloud Messaging (FCM).
Envía notificaciones a dispositivos Android de camareros, cocineros, etc.
"""
import logging
from typing import List, Optional
from datetime import datetime
import httpx

from src.core.config import settings

logger = logging.getLogger(__name__)


class PushNotificationService:
    """Servicio para enviar notificaciones push vía Firebase Cloud Messaging."""
    
    # Eventos que disparan notificaciones push (según configuración aprobada)
    EVENTS = {
        "reservation_created": {
            "title": "Nueva Reserva",
            "body": "Nueva reserva para {pax} personas a las {time}",
            "roles": ["waiter", "manager", "admin"],
            "priority": "high"
        },
        "reservation_confirmed": {
            "title": "Reserva Confirmada",
            "body": "{customer_name} confirmó su reserva",
            "roles": ["waiter", "manager", "admin"],
            "priority": "normal"
        },
        "reservation_cancelled": {
            "title": "Reserva Cancelada",
            "body": "{customer_name} canceló su reserva",
            "roles": ["waiter", "manager", "admin"],
            "priority": "high"
        },
        "customer_seated": {
            "title": "Cliente Sentado",
            "body": "Mesa {table_name} ocupada - {pax} personas",
            "roles": ["waiter", "cook", "manager", "admin"],
            "priority": "high"
        },
        "table_freed": {
            "title": "Mesa Liberada",
            "body": "Mesa {table_name} ahora disponible",
            "roles": ["waiter", "cook", "manager", "admin"],
            "priority": "normal"
        },
        "no_show": {
            "title": "No-Show",
            "body": "{customer_name} no apareció",
            "roles": ["waiter", "manager", "admin"],
            "priority": "normal"
        },
        "large_group": {
            "title": "Grupo Grande",
            "body": "Reserva de {pax} personas requiere atención",
            "roles": ["manager", "admin"],
            "priority": "high"
        },
        "kitchen_alert": {
            "title": "Alerta Cocina",
            "body": "Mesa {table_name} - Entrada lista",
            "roles": ["waiter", "cook", "manager", "admin"],
            "priority": "high"
        },
        "incident": {
            "title": "Incidencia",
            "body": "{message}",
            "roles": ["manager", "admin"],
            "priority": "high"
        },
        "overbooking": {
            "title": "Overbooking",
            "body": "Alerta de sobre-reserva",
            "roles": ["manager", "admin"],
            "priority": "high"
        }
    }
    
    def __init__(self):
        self.fcm_server_key = getattr(settings, 'FCM_SERVER_KEY', None)
        self.fcm_url = "https://fcm.googleapis.com/fcm/send"
    
    async def send_to_device(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[dict] = None,
        priority: str = "normal"
    ) -> bool:
        """Envía notificación push a un dispositivo específico."""
        if not self.fcm_server_key:
            logger.warning("FCM_SERVER_KEY not configured")
            return False
        
        payload = {
            "to": device_token,
            "notification": {
                "title": title,
                "body": body,
                "sound": "default",
                "badge": "1"
            },
            "data": data or {},
            "priority": priority
        }
        
        headers = {
            "Authorization": f"key={self.fcm_server_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.fcm_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success") == 1:
                        logger.info(f"Push notification sent to {device_token[:20]}...")
                        return True
                    else:
                        logger.error(f"FCM error: {result}")
                        return False
                else:
                    logger.error(f"FCM HTTP error {response.status_code}: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
            return False
    
    async def send_to_role(
        self,
        role: str,
        title: str,
        body: str,
        data: Optional[dict] = None,
        priority: str = "normal"
    ):
        """Envía notificación a todos los dispositivos de un rol."""
        # TODO: Obtener device tokens de usuarios con este rol desde base de datos
        # Por ahora, solo logueamos
        logger.info(f"Would send push to role '{role}': {title}")
    
    async def send_event_notification(
        self,
        event_type: str,
        context: dict
    ):
        """
        Envía notificación basada en tipo de evento.
        
        Args:
            event_type: Tipo de evento (reservation_created, customer_seated, etc.)
            context: Variables para formatear el mensaje (pax, time, customer_name, etc.)
        """
        if event_type not in self.EVENTS:
            logger.warning(f"Unknown event type: {event_type}")
            return
        
        event_config = self.EVENTS[event_type]
        
        # Formatear mensaje
        title = event_config["title"]
        try:
            body = event_config["body"].format(**context)
        except KeyError as e:
            logger.error(f"Missing context variable {e} for event {event_type}")
            body = event_config["body"]
        
        # Preparar data payload
        data = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            **context
        }
        
        # Enviar a cada rol configurado
        for role in event_config["roles"]:
            await self.send_to_role(
                role=role,
                title=title,
                body=body,
                data=data,
                priority=event_config.get("priority", "normal")
            )
    
    async def notify_new_reservation(self, reservation: dict):
        """Notifica nueva reserva."""
        await self.send_event_notification("reservation_created", {
            "reservation_id": reservation.get("id"),
            "customer_name": reservation.get("customer_name", "Cliente"),
            "pax": reservation.get("pax", 0),
            "time": reservation.get("time", ""),
            "date": reservation.get("date", ""),
            "table_name": reservation.get("table_name", "")
        })
    
    async def notify_customer_seated(self, reservation: dict, table_name: str):
        """Notifica cliente sentado."""
        await self.send_event_notification("customer_seated", {
            "reservation_id": reservation.get("id"),
            "customer_name": reservation.get("customer_name", "Cliente"),
            "pax": reservation.get("pax", 0),
            "table_name": table_name
        })
    
    async def notify_large_group(self, reservation: dict):
        """Notifica grupo grande (>10 pax)."""
        await self.send_event_notification("large_group", {
            "reservation_id": reservation.get("id"),
            "customer_name": reservation.get("customer_name", "Cliente"),
            "pax": reservation.get("pax", 0),
            "time": reservation.get("time", "")
        })


# Instancia singleton
push_service = PushNotificationService()
