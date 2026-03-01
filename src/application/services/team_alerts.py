"""
Team Alert Service: Sends WhatsApp notifications to restaurant staff via Twilio.
Used for escalations (large groups, special requests, etc.)
"""
import os
from twilio.rest import Client

class TeamAlertService:
    """Sends alerts to restaurant team via WhatsApp."""
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        
        # Team members to notify (could be loaded from config)
        self.team_numbers = [
            "+34XXXXXXXXX"  # Replace with real team numbers
        ]
        
        self.client = Client(self.account_sid, self.auth_token) if self.account_sid else None

    def send_alert(self, message: str, priority: str = "normal") -> bool:
        """
        Send WhatsApp alert to team.
        
        Args:
            message: Alert content
            priority: "normal", "high", "urgent"
            
        Returns:
            True if sent successfully
        """
        if not self.client:
            print("⚠️ Twilio not configured. Alert not sent.")
            return False
            
        prefix = {
            "urgent": "🚨 URGENTE:",
            "high": "⚠️ ATENCIÓN:",
            "normal": "📢"
        }.get(priority, "📢")
        
        full_message = f"{prefix} {message}"
        
        try:
            for number in self.team_numbers:
                self.client.messages.create(
                    body=full_message,
                    from_=f"whatsapp:{self.from_number}",
                    to=f"whatsapp:{number}"
                )
            return True
        except Exception as e:
            print(f"❌ Error sending WhatsApp alert: {e}")
            return False

    def alert_large_group(self, pax: int, date: str, client_name: str):
        """Alert for groups larger than 10."""
        message = f"Solicitud de reserva para {pax} personas el {date}. Cliente: {client_name}. Requiere aprobación."
        return self.send_alert(message, priority="high")

    def alert_special_request(self, request: str, client_name: str):
        """Alert for special requests."""
        message = f"Solicitud especial de {client_name}: {request}"
        return self.send_alert(message, priority="normal")
