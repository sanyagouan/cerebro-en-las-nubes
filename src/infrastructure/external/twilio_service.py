from typing import Optional
import logging
from twilio.rest import Client
import os

logger = logging.getLogger(__name__)

class TwilioService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            logger.warning("Twilio credentials not found. SMS/WhatsApp will not work.")

    def send_sms(self, to_number: str, message_body: str) -> Optional[str]:
        if not self.client:
            logger.warning(f"Mocking SMS to {to_number}: {message_body}")
            return "MOCK_SID_12345"

        try:
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=to_number
            )
            return message.sid
        except Exception as e:
            logger.error(f"Error sending SMS via Twilio: {e}")
            return None
