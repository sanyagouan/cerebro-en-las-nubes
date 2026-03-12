import os
from twilio.rest import Client
from src.core.entities.booking import Booking
from src.infrastructure.templates.whatsapp_messages import confirmacion_reserva_template
from src.infrastructure.templates.content_sids import (
    RESERVA_CONFIRMACION_NUBES_SID,
    RESERVA_RECORDATORIO_NUBES_SID,
    RESERVA_CANCELADA_NUBES_SID,
    MESA_DISPONIBLE_NUBES_SID
)


class WhatsAppService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        raw_from = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
        self.from_number = (
            f"whatsapp:{raw_from}" if not raw_from.startswith("whatsapp:") else raw_from
        )

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
                from_=self.from_number, body=body, to=to_number
            )
            print(f"✅ WhatsApp sent to {to_number}: {message.sid}")
            return True
        except Exception as e:
            print(f"❌ Error sending WhatsApp: {e}")
            return False

    def send_premium_confirmation(
        self, booking: Booking, restaurant_name="En Las Nubes"
    ):
        """Sends the polished Initial Confirmation message using unified template."""
        # Booking v2 uses 'telefono' instead of 'client_phone'
        if not booking.telefono:
            return False

        # Use unified template from whatsapp_messages.py
        # This ensures same format for both immediate confirmation and 24h reminders
        msg = confirmacion_reserva_template(
            nombre_cliente=booking.nombre,
            fecha=booking.fecha,
            hora=booking.hora,
            num_personas=booking.pax,
            mesa_asignada=booking.mesa_asignada,  # Can be None
            zona="Terraza"
            if booking.mesa_asignada and "T" in str(booking.mesa_asignada)
            else "Interior"
            if booking.mesa_asignada
            else None,
        )

        text_sent = self.send_message(booking.telefono, msg)

        # 2. Enviar ubicación (Mapa)
        loc_sent = self.send_location(
            booking.telefono, lat=42.4636, lon=-2.4474, label="En Las Nubes Restobar"
        )

        return text_sent and loc_sent

    def send_location(self, to_number: str, lat: float, lon: float, label: str) -> bool:
        """Sends a location message via WhatsApp."""
        if not self.client:
            return False
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
                persistent_action=[f"geo:{lat},{lon}|{label}"],
            )
            print(f"✅ Location sent to {to_number}")
            return True
        except Exception as e:
            print(f"⚠️ Error sending location (native): {e}")
            # Fallback: Enviar Link de Google Maps
            try:
                link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
                self.client.messages.create(
                    from_=self.from_number, to=to_number, body=f"📍 Cómo llegar: {link}"
                )
                return True
            except:
                return False

    def send_reconfirmation_success(self, client_phone: str):
        msg = "✅ *Reserva Confirmada*.\n\n¡Gracias! Su mesa está asegurada. Nos vemos pronto. 🥂"
        return self.send_message(client_phone, msg)

    def send_template_confirmation(
        self, telefono: str, nombre_cliente: str, fecha: str, hora: str
    ) -> bool:
        """Sends a template-based confirmation message using Content API."""
        if not self.client:
            print("❌ WhatsAppService not initialized (missing creds)")
            return False

        try:
            if not telefono.startswith("whatsapp:"):
                telefono = f"whatsapp:{telefono}"

            # Prepare variables for the template
            variables = {
                "1": nombre_cliente,
                "2": fecha,
                "3": hora
            }

            # Send using Content API
            message = self.client.messages.create(
                from_=self.from_number,
                content_sid=RESERVA_CONFIRMACION_NUBES_SID,
                content_variables=variables,
                to=telefono
            )
            print(f"✅ WhatsApp template confirmation sent to {telefono}: {message.sid}")
            return True
        except Exception as e:
            print(f"❌ Error sending WhatsApp template confirmation: {e}")
            return False

    def send_template_reminder(
        self, telefono: str, nombre_cliente: str, fecha: str, hora: str, num_personas: str
    ) -> bool:
        """Sends a template-based reminder message using Content API."""
        if not self.client:
            print("❌ WhatsAppService not initialized (missing creds)")
            return False

        try:
            if not telefono.startswith("whatsapp:"):
                telefono = f"whatsapp:{telefono}"

            # Prepare variables for the template
            variables = {
                "1": nombre_cliente,
                "2": fecha,
                "3": hora,
                "4": num_personas
            }

            # Send using Content API
            message = self.client.messages.create(
                from_=self.from_number,
                content_sid=RESERVA_RECORDATORIO_NUBES_SID,
                content_variables=variables,
                to=telefono
            )
            print(f"✅ WhatsApp template reminder sent to {telefono}: {message.sid}")
            return True
        except Exception as e:
            print(f"❌ Error sending WhatsApp template reminder: {e}")
            return False

    def send_template_cancellation(
        self, telefono: str, nombre_cliente: str, fecha: str, hora: str
    ) -> bool:
        """Sends a template-based cancellation message using Content API."""
        if not self.client:
            print("❌ WhatsAppService not initialized (missing creds)")
            return False

        try:
            if not telefono.startswith("whatsapp:"):
                telefono = f"whatsapp:{telefono}"

            # Prepare variables for the template
            variables = {
                "1": nombre_cliente,
                "2": fecha,
                "3": hora
            }

            # Send using Content API
            message = self.client.messages.create(
                from_=self.from_number,
                content_sid=RESERVA_CANCELADA_NUBES_SID,
                content_variables=variables,
                to=telefono
            )
            print(f"✅ WhatsApp template cancellation sent to {telefono}: {message.sid}")
            return True
        except Exception as e:
            print(f"❌ Error sending WhatsApp template cancellation: {e}")
            return False

    def send_template_mesa_disponible(
        self, telefono: str, nombre_cliente: str, num_personas: str, fecha: str, hora: str
    ) -> bool:
        """Sends a template-based available table notification using Content API."""
        if not self.client:
            print("❌ WhatsAppService not initialized (missing creds)")
            return False

        try:
            if not telefono.startswith("whatsapp:"):
                telefono = f"whatsapp:{telefono}"

            # Prepare variables for the template
            variables = {
                "1": nombre_cliente,
                "2": num_personas,
                "3": fecha,
                "4": hora
            }

            # Send using Content API
            message = self.client.messages.create(
                from_=self.from_number,
                content_sid=MESA_DISPONIBLE_NUBES_SID,
                content_variables=variables,
                to=telefono
            )
            print(f"✅ WhatsApp template mesa disponible sent to {telefono}: {message.sid}")
            return True
        except Exception as e:
            print(f"❌ Error sending WhatsApp template mesa disponible: {e}")
            return False

    def send_cancellation_success(self, client_phone: str):
        msg = "👋 *Reserva Cancelada*.\n\nEntendido. Esperamos poder recibirle en otra ocasión. ¡Gracias por avisar!"
        return self.send_message(client_phone, msg)

    def send_notes_update_success(self, client_phone: str):
        msg = "📝 *Nota Registrada*.\n\nHemos actualizado su reserva con esta información. ¡Gracias!"
        return self.send_message(client_phone, msg)
