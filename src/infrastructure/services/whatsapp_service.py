import os
from twilio.rest import Client
from src.core.entities.booking import Booking

class WhatsAppService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        raw_from = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
        self.from_number = f"whatsapp:{raw_from}" if not raw_from.startswith("whatsapp:") else raw_from
        
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
        
        
        # 1. Enviar mensaje de texto profesional
        msg = (
            f"🌟 *RESERVA CONFIRMADA - EN LAS NUBES* 🌟\n\n"
            f"¡Hola *{booking.client_name}*! 👋\n"
            f"Gracias por elegirnos. Aquí tienes los detalles:\n\n"
            f"🗓️ *{date_nice}*\n"
            f"⏰ *{time_nice}*\n"
            f"👥 *{booking.pax} personas*\n"
            f"📍 *C/ María Teresa Gil de Gárate 16*\n\n"
            f"👇 *ACCIONES DISPONIBLES:*\n"
            f"Para finalizar, si necesitas algo especial:\n"
            f"🔹 Escribe *ALERGIAS* para indicar intolerancias\n"
            f"🔹 Escribe *TRONA* o *CARRO* si vienes con peques\n"
            f"🔹 Escribe *MASCOTA* si vienes con tu perro (Terraza)\n\n"
            f"❓ ¿Cambios? Escríbenos por aquí.\n"
            f"¡Nos vemos pronto! 🍷"
        )
        
        text_sent = self.send_message(booking.client_phone, msg)
        
        # 2. Enviar ubicación (Mapa)
        loc_sent = self.send_location(
            booking.client_phone, 
            lat=42.4636, 
            lon=-2.4474, 
            label="En Las Nubes Restobar"
        )
        
        return text_sent and loc_sent

    def send_location(self, to_number: str, lat: float, lon: float, label: str) -> bool:
        """Sends a location message via WhatsApp."""
        if not self.client: return False
        try:
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"
            
            # Twilio format for location: persistent_action parameter (geo:lat,lon)
            # Nota: WhatsApp Location Messages se envían pasando persistent_action=[f"geo:{lat},{lon}|{label}"]
            # Pero en la librería python de Twilio se hace pasando 'persistent_action'
            # OJO: En modo Sandbox puede estar limitado. Usamos fallback link si falla.
            
            self.client.messages.create(
                from_=self.from_number,
                to=to_number,
                body=label,
                persistent_action=[f"geo:{lat},{lon}|{label}"]
            )
            print(f"✅ Location sent to {to_number}")
            return True
        except Exception as e:
            print(f"⚠️ Error sending location (native): {e}")
            # Fallback: Enviar Link de Google Maps
            try:
                link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
                self.client.messages.create(
                    from_=self.from_number,
                    to=to_number,
                    body=f"📍 Cómo llegar: {link}"
                )
                return True
            except:
                return False

    def send_reconfirmation_success(self, client_phone: str):
        msg = "✅ *Reserva Confirmada*.\n\n¡Gracias! Su mesa está asegurada. Nos vemos pronto. 🥂"
        return self.send_message(client_phone, msg)

    def send_cancellation_success(self, client_phone: str):
        msg = "👋 *Reserva Cancelada*.\n\nEntendido. Esperamos poder recibirle en otra ocasión. ¡Gracias por avisar!"
        return self.send_message(client_phone, msg)

    def send_notes_update_success(self, client_phone: str):
        msg = "📝 *Nota Registrada*.\n\nHemos actualizado su reserva con esta información. ¡Gracias!"
        return self.send_message(client_phone, msg)
