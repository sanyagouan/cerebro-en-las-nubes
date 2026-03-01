from typing import Optional
import logging
from twilio.rest import Client
import os

logger = logging.getLogger(__name__)

class TwilioService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_from = os.getenv("TWILIO_WHATSAPP_NUMBER")  # whatsapp:+14155238886
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            logger.warning("Twilio credentials not found. WhatsApp will not work.")

    def send_whatsapp(self, to_number: str, message_body: str) -> Optional[str]:
        """
        Envía un mensaje de WhatsApp a través de Twilio.
        
        Args:
            to_number: Número del destinatario en formato E.164 (ej: +34666123456)
            message_body: Contenido del mensaje
            
        Returns:
            SID del mensaje si se envió correctamente, None si falló
        """
        if not self.client:
            logger.warning(f"Mocking WhatsApp to {to_number}: {message_body}")
            return "MOCK_WHATSAPP_SID_12345"

        try:
            # Twilio WhatsApp requiere el prefijo whatsapp: en ambos números
            from_whatsapp = self.whatsapp_from if self.whatsapp_from.startswith('whatsapp:') else f'whatsapp:{self.whatsapp_from}'
            to_whatsapp = to_number if to_number.startswith('whatsapp:') else f'whatsapp:{to_number}'
            
            message = self.client.messages.create(
                body=message_body,
                from_=from_whatsapp,
                to=to_whatsapp
            )
            logger.info(f"WhatsApp enviado a {to_number}: SID {message.sid}")
            return message.sid
        except Exception as e:
            logger.error(f"Error enviando WhatsApp via Twilio: {e}")
            return None
    
    def send_sms(self, to_number: str, message_body: str) -> Optional[str]:
        """
        DEPRECADO: Usar send_whatsapp() en su lugar.
        Método mantenido solo para compatibilidad con código legacy.
        """
        logger.warning("send_sms() está deprecado. Usa send_whatsapp() en su lugar.")
        return self.send_whatsapp(to_number, message_body)
