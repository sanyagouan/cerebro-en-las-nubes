import os
from twilio.rest import Client
from src.core.entities.booking import Booking

class WhatsAppService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886") # Default sandbox
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            print("⚠️ Twilio credentials missing in env")

    def send_message(self, to_number: str, body: str) -> bool:
        """Sends a generic WhatsApp message."""
        if not self.client:
            print("❌ WhatsAppService not initialized (missing creds)")
            return False

        try:
            # Ensure number has whatsapp prefix
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"
            
            message = self.client.messages.create(
                from_=self.from_number,
                body=body,
                to=to_number
            )
            print(f"✅ WhatsApp sent to {to_number}: {message.sid}")
            return True
        except Exception as e:
            print(f"❌ Error sending WhatsApp: {e}")
            return False

    def send_premium_confirmation(self, booking: Booking, restaurant_name="En las Nubes"):
        """Sends the polished Initial Confirmation message."""
        if not booking.client_phone:
            return False
            
        # Format nice date/time
        date_nice = booking.date_time.strftime("%d/%m")
        time_nice = booking.date_time.strftime("%H:%M")
        
        # Link to Google Maps (Real address)
        maps_link = "https://maps.app.goo.gl/7XYxPxMHr6dHxKbZ9"  # En las Nubes, Logroño
        
        msg = (
            f"🌟 *{restaurant_name.upper()}* 🌟\n\n"
            f"Hola *{booking.client_name}* 👋,\n"
            f"Hemos recibido su solicitud de reserva:\n\n"
            f"📅 *{date_nice}* a las *{time_nice}*\n"
            f"👥 *{booking.pax} personas*\n"
            f"📍 {maps_link}\n\n"
            f"Por favor, complete su reserva:\n"
            f"✅ Responda *SÍ* para confirmar.\n"
            f"📝 Responda con cualquier *alergia* o petición especial.\n"
            f"❌ Responda *CANCELAR* si no puede asistir.\n\n"
            f"¡Esperamos verle pronto! 🍷"
        )
        
        return self.send_message(booking.client_phone, msg)

    def send_reconfirmation_success(self, client_phone: str):
        msg = "✅ *Reserva Confirmada*.\n\n¡Gracias! Su mesa está asegurada. Nos vemos pronto. 🥂"
        return self.send_message(client_phone, msg)

    def send_cancellation_success(self, client_phone: str):
        msg = "👋 *Reserva Cancelada*.\n\nEntendido. Esperamos poder recibirle en otra ocasión. ¡Gracias por avisar!"
        return self.send_message(client_phone, msg)

    def send_notes_update_success(self, client_phone: str):
        msg = "📝 *Nota Registrada*.\n\nHemos actualizado su reserva con esta información. ¡Gracias!"
        return self.send_message(client_phone, msg)
