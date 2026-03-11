import os
from typing import Optional, Dict, Any, List
from twilio.rest import Client
from loguru import logger

class TwilioService:
    """
    Servicio de Twilio para enviar notificaciones por WhatsApp y SMS.
    """

    def __init__(self):
        self.sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.token = os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_from = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
        logger.info(f"WhatsApp From Number configurado: {self.whatsapp_from}")
        
        if self.sid and self.token:
            self.client = Client(self.sid, self.token)
        else:
            self.client = None
            logger.warning("Twilio SID o Token no configurados. Las notificaciones estarán desactivadas.")

    def send_whatsapp(self, to_number: str, message_body: str, reservation_data: Optional[Dict] = None) -> Optional[str]:
        """
        Envía un mensaje de texto por WhatsApp.
        Solo envía a números móviles - filtra teléfonos fijos.
        """
        if not self.client:
            logger.error("Cliente de Twilio no inicializado.")
            return None

        # Filtrar teléfonos no móviles
        if reservation_data:
            tipo_telefono = reservation_data.get("Tipo_Telefono", "desconocido")
            if tipo_telefono != "movil":
                logger.info(f"Omitiendo WhatsApp para {to_number} (tipo: {tipo_telefono})")
                return None

        # Asegurar formato whatsapp:+
        if not to_number.startswith("whatsapp:"):
            to_formatted = f"whatsapp:{to_number}"
        else:
            to_formatted = to_number

        try:
            message = self.client.messages.create(
                body=message_body, from_=self.whatsapp_from, to=to_formatted
            )
            logger.info(f"WhatsApp enviado a {to_number}: SID {message.sid}")
            return message.sid
        except Exception as ex:
            logger.error(f"Error enviando WhatsApp: {ex}")
            return None

    def send_whatsapp_template(
        self, to_number: str, template_sid: str, variables: Dict[str, str]
    ) -> Optional[str]:
        """
        Envía una plantilla de WhatsApp pre-aprobada.
        Variables: Diccionario con los valores para la plantilla.
        """
        if not self.client:
            return None

        if not to_number.startswith("whatsapp:"):
            to_formatted = f"whatsapp:{to_number}"
        else:
            to_formatted = to_number

        try:
            # Twilio templates se envían de forma distinta según la API usada. 
            # Aquí usamos el enfoque estándar de Content SID si está disponible, 
            # o enviamos el body completo si es una plantilla de texto simple.
            # Por ahora, implementamos envío de mensaje con parámetros.
            
            message = self.client.messages.create(
                from_=self.whatsapp_from,
                body=self._format_template_body(template_sid, variables),
                to=to_formatted
            )
            logger.info(f"Plantilla WhatsApp enviada a {to_number}: SID {message.sid}")
            return message.sid
        except Exception as ex:
            logger.error(f"Error enviando plantilla WhatsApp: {ex}")
            return None

    def _format_template_body(self, template_sid: str, variables: Dict[str, str]) -> str:
        """
        Mapeo temporal de plantillas hasta que se integre Twilio Content API.
        """
        templates = {
            "confirmacion_reserva": "¡Hola {nombre}! Tu reserva en Restobar En Las Nubes para el {fecha} a las {hora} ha sido confirmada. ¡Te esperamos!",
            "recordatorio_reserva": "Recordatorio: Tienes una reserva hoy en Restobar En Las Nubes a las {hora}. Si no puedes asistir, por favor avísanos.",
            "cancelacion_reserva": "Hola {nombre}, tu reserva para el {fecha} ha sido cancelada correctamente."
        }
        
        base_text = templates.get(template_sid, "Mensaje de Restobar En Las Nubes")
        try:
            return base_text.format(**variables)
        except Exception:
            return base_text

    def send_sms_contingency(self, to_number: str, message_body: str) -> Optional[str]:
        """
        Envía un SMS tradicional como respaldo.
        """
        if not self.client:
            return None

        fallback_from = os.getenv("TWILIO_FROM_NUMBER")
        if not fallback_from:
            logger.error("TWILIO_FROM_NUMBER no está configurado para SMS.")
            return None

        try:
            message = self.client.messages.create(
                body=message_body, from_=fallback_from, to=to_number
            )
            logger.info(f"SMS enviado a {to_number}: SID {message.sid}")
            return message.sid
        except Exception as ex:
            logger.error(f"Error enviando SMS de contingencia: {ex}")
            return None

    def send_sms(self, to_number: str, message_body: str) -> Optional[str]:
        """
        DEPRECADO: Usar send_whatsapp() en su lugar.
        Método mantenido solo para compatibilidad con código legacy.
        """
        logger.warning("send_sms() está deprecado. Usa send_whatsapp() en su lugar.")
        return self.send_whatsapp(to_number, message_body)

    async def get_messages(self, limit: int = 50) -> Dict[str, Any]:
        """
        Recupera el historial de mensajes enviados por WhatsApp.
        """
        if not self.sid or not self.token:
            logger.warning("Credenciales de Twilio no configuradas")
            return {"messages": [], "total": 0}

        try:
            import httpx
            auth = (self.sid, self.token)
            async with httpx.AsyncClient() as client:
                url = f"https://api.twilio.com/2010-04-01/Accounts/{self.sid}/Messages.json"
                response = await client.get(url, auth=auth, params={"PageSize": limit})
                response.raise_for_status()
                data = response.json()
                
                messages = data.get("messages", [])
                formatted_messages = []
                
                for msg in messages:
                    to_val = msg.get("to", "") or ""
                    if not to_val.startswith("whatsapp:"):
                        continue
                        
                    formatted_messages.append({
                        "id": msg.get("sid"),
                        "message_id": msg.get("sid"),
                        "phone_number": to_val.replace("whatsapp:", ""),
                        "message_type": self._infer_message_type(msg.get("body", "") or ""),
                        "content": msg.get("body", ""),
                        "status": self._map_status(msg.get("status", "")),
                        "sent_at": msg.get("date_sent") or msg.get("date_created"),
                        "delivered_at": msg.get("date_sent") if msg.get("status") == "delivered" else None,
                        "read_at": msg.get("date_sent") if msg.get("status") == "read" else None,
                        "cost": abs(float(msg.get("price") or 0)),
                        "error_message": msg.get("error_message"),
                        "retry_count": 0
                    })
                
                return {
                    "messages": formatted_messages,
                    "total": len(formatted_messages)
                }
        except Exception as e:
            logger.error(f"Error recuperando mensajes de Twilio: {e}")
            return {"messages": [], "total": 0, "error": str(e)}

    async def get_analytics(self) -> Dict[str, Any]:
        """
        Calcula analíticas agregadas de los mensajes de WhatsApp.
        """
        res = await self.get_messages(limit=100)
        messages = res.get("messages", [])
        
        if not messages:
            return self._empty_analytics()

        total = len(messages)
        sent = [m for m in messages if m["status"] in ("sent", "delivered", "read")]
        delivered = [m for m in messages if m["status"] in ("delivered", "read")]
        read = [m for m in messages if m["status"] == "read"]
        failed = [m for m in messages if m["status"] == "failed"]
        
        total_cost = sum(m.get("cost", 0) or 0 for m in messages)

        conf = len([m for m in messages if m["message_type"] == "confirmation"])
        rem = len([m for m in messages if m["message_type"] == "reminder"])

        return {
            "total_messages": total,
            "sent_messages": len(sent),
            "delivered_messages": len(delivered),
            "read_messages": len(read),
            "failed_messages": len(failed),
            "delivery_rate": (len(delivered) / len(sent) * 100) if len(sent) > 0 else 0,
            "read_rate": (len(read) / len(delivered) * 100) if len(delivered) > 0 else 0,
            "total_cost": total_cost,
            "messages_by_type": {
                "confirmation": conf,
                "reminder": rem,
                "cancellation": 0,
                "waitlist": 0
            },
            "messages_by_status": {
                "sent": len(sent),
                "delivered": len(delivered),
                "read": len(read),
                "failed": len(failed)
            }
        }

    def _infer_message_type(self, body: str) -> str:
        body_lower = body.lower()
        if "confirmada" in body_lower or "reserva" in body_lower:
            return "confirmation"
        if "recordatorio" in body_lower:
            return "reminder"
        return "confirmation"

    def _map_status(self, twilio_status: str) -> str:
        if twilio_status in ("delivered", "read"):
            return twilio_status
        if twilio_status in ("sent", "queued", "sending"):
            return "sent"
        return "failed"

    def _empty_analytics(self) -> Dict[str, Any]:
        return {
            "total_messages": 0,
            "sent_messages": 0,
            "delivered_messages": 0,
            "read_messages": 0,
            "failed_messages": 0,
            "delivery_rate": 0,
            "read_rate": 0,
            "total_cost": 0,
            "messages_by_type": {
                "confirmation": 0,
                "reminder": 0,
                "cancellation": 0,
                "waitlist": 0
            },
            "messages_by_status": {
                "sent": 0,
                "delivered": 0,
                "read": 0,
                "failed": 0
            }
        }

twilio_service = TwilioService()
