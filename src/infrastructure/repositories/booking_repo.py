import os
from typing import List, Dict, Any, Optional
from datetime import datetime, date, time as time_type
from pyairtable import Api
from src.core.ports.booking_repository import BookingRepository
from src.core.entities.booking import Booking, BookingStatus, BookingChannel
from src.core.entities.table import Table, TableStatus, normalize_zone
from src.core.config.airtable_ids import TABLES, BASE_ID
from loguru import logger


class AirtableBookingRepository(BookingRepository):
    def __init__(self):
        self.api_key = os.getenv("AIRTABLE_API_KEY")
        if not self.api_key:
            logger.warning("AIRTABLE_API_KEY not found in env")
        self.api = Api(self.api_key)
        self.base_id = BASE_ID

    # --- MAPPING HELPERS ---

    def _map_booking_to_fields(self, booking: Booking) -> Dict[str, Any]:
        """Convert domain Booking v2 to Airtable fields (Spanish Schema)"""
        # Booking v2 uses fecha (date) and hora (time) separately

        # 'Fecha de Reserva' (Date) -> "YYYY-MM-DD"
        date_str = (
            booking.fecha.isoformat()
            if booking.fecha
            else datetime.now().strftime("%Y-%m-%d")
        )

        # 'Hora' (DateTime) -> ISO String
        # Combine fecha + hora for Airtable DateTime field
        if booking.fecha and booking.hora:
            dt = datetime.combine(booking.fecha, booking.hora)
            time_str = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        else:
            time_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")

        fields = {
            "Nombre del Cliente": booking.nombre,
            "Teléfono": booking.telefono,
            "Fecha de Reserva": date_str,
            "Hora": time_str,
            "Cantidad de Personas": booking.pax,
            "Estado de Reserva": booking.estado.value
            if hasattr(booking.estado, "value")
            else booking.estado,
        }

        # Optional fields
        if booking.notas:
            fields["Notas"] = booking.notas

        if booking.mesa_asignada:
            # Linked records require an array of IDs
            fields["Mesa"] = [booking.mesa_asignada]

        return fields

    def _map_record_to_booking(self, record: Dict[str, Any]) -> Optional[Booking]:
        """Convert Airtable record to domain Booking v2"""
        fields = record.get("fields", {})

        try:
            # Parse datetime from Airtable
            dt_str = fields.get("Hora")
            if dt_str:
                # ISO Format from Airtable usually ends in Z
                booking_dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            else:
                # Fallback: Date + Time components if separate
                date_str = fields.get("Fecha de Reserva")
                if date_str:
                    booking_dt = datetime.fromisoformat(f"{date_str}T12:00:00")
                else:
                    booking_dt = datetime.now()

            # Map Status
            status_str = fields.get("Estado de Reserva", "Pendiente")
            try:
                status = BookingStatus(status_str)
            except ValueError:
                status = BookingStatus.PENDING

            # Create Booking v2 with correct field names
            return Booking(
                id=record.get("id"),
                nombre=fields.get("Nombre del Cliente", "Anónimo"),
                telefono=fields.get("Teléfono", ""),
                fecha=booking_dt.date(),
                hora=booking_dt.time(),
                pax=fields.get("Cantidad de Personas", 0),
                notas=fields.get("Notas"),
                estado=status,
                mesa_asignada=fields.get("Mesa", [None])[0]
                if fields.get("Mesa")
                else None,
                canal=BookingChannel.WHATSAPP,  # Default channel
            )
        except Exception as e:
            logger.error(f"Error mapping record {record.get('id')}: {e}")
            return None

    # --- PUBLIC METHODS ---

    def get_all_tables(self) -> List[Table]:
        try:
            table_api = self.api.table(self.base_id, TABLES["MESAS"])
            records = table_api.all()
            tables = []

            for r in records:
                fields = r["fields"]

                # Mapear campos de Airtable a entidad Table (nombres correctos)
                capacidad_base = fields.get("Capacidad", 2)
                capacidad_ampliada = fields.get("Capacidad Ampliada") or capacidad_base

                # Disponible: True si el checkbox está marcado o si el campo no existe (default True)
                disponible = fields.get("Disponible", True)

                table = Table(
                    id=r["id"],
                    nombre=fields.get("Nombre de Mesa", "Unknown"),
                    capacidad_min=1,  # Mínimo 1 persona
                    capacidad_max=capacidad_ampliada,
                    zona=normalize_zone(fields.get("Ubicación", "Interior")),
                    prioridad=fields.get("Prioridad", 5),
                    status=TableStatus.AVAILABLE if disponible else TableStatus.BLOCKED,
                )
                tables.append(table)

            logger.info(f"Cargadas {len(tables)} mesas desde Airtable")
            return tables
        except Exception as e:
            logger.exception(f"Error fetching tables: {e}")
            return []

    def get_bookings_for_date(self, date: datetime) -> List[Booking]:
        """Obtiene reservas para una fecha específica."""
        try:
            table_api = self.api.table(self.base_id, TABLES["RESERVAS"])

            # Format date for Airtable formula
            date_str = date.strftime("%Y-%m-%d")
            # Formula checks if 'Fecha de Reserva' matches the requested date
            formula = f"IS_SAME({{Fecha de Reserva}}, '{date_str}', 'day')"

            records = table_api.all(formula=formula)
            bookings = []

            for r in records:
                booking = self._map_record_to_booking(r)
                if booking:
                    bookings.append(booking)

            return bookings
        except Exception as e:
            logger.error(f"Error fetching bookings: {e}")
            return []

    def create_booking(self, booking: Booking) -> Booking:
        """Crea una nueva reserva en Airtable usando el mapeo correcto."""
        try:
            table_api = self.api.table(self.base_id, TABLES["RESERVAS"])

            # Use the single source of truth for mapping
            fields = self._map_booking_to_fields(booking)

            # Create
            record = table_api.create(fields)

            # Update ID and return
            booking.id = record["id"]
            logger.info(f"Reserva creada: {booking.id}")
            return booking

        except Exception as e:
            logger.error(f"Error creando reserva: {e}")
            raise e

    def update_booking_status(
        self, booking_id: str, status: str, table_id: str = None
    ) -> bool:
        """Actualiza el estado de una reserva existente."""
        try:
            table_api = self.api.table(self.base_id, TABLES["RESERVAS"])

            fields = {"Estado de Reserva": status}
            if table_id:
                fields["Mesa"] = [table_id]

            table_api.update(booking_id, fields)
            logger.info(f"Reserva {booking_id} actualizada a {status}")
            return True

        except Exception as e:
            logger.error(f"Error actualizando reserva: {e}")
            return False

    def find_pending_booking_by_phone(self, phone: str) -> Optional[Booking]:
        """Busca una reserva pendiente para este teléfono (HOY o FUTURO)."""
        try:
            table_api = self.api.table(self.base_id, TABLES["RESERVAS"])

            # Simple exact match first. Ideally should handle format diffs.
            # We filter by Status='Pendiente' AND Phone match
            # Note: Phone formatting is tricky. We'll try to match exact first.
            formula = (
                f"AND({{Teléfono}} = '{phone}', {{Estado de Reserva}} = 'Pendiente')"
            )

            records = table_api.all(formula=formula)

            # If multiple, take the most recent one (createdTime) or closest execution date?
            # Let's take the one closest to future.
            if not records:
                return None

            # Convert all to bookings
            bookings = []
            for r in records:
                b = self._map_record_to_booking(r)
                if b:
                    bookings.append(b)

            # Sort by date (nearest first)
            bookings.sort(key=lambda x: x.datetime_completo)

            # Return the first one that is active (not in past, though 'Pendiente' implied future usually)
            return bookings[0] if bookings else None

        except Exception as e:
            logger.error(f"Error finding booking by phone: {e}")
            return None

    def update_booking_notes(self, booking_id: str, new_note: str) -> bool:
        """Añade una nota a la reserva."""
        try:
            table_api = self.api.table(self.base_id, TABLES["RESERVAS"])
            # First get current notes to append? Or just overwrite?
            # Append is safer.
            record = table_api.get(booking_id)
            current_notes = record["fields"].get("Notas", "")

            updated_note = f"{current_notes}\n[WhatsApp]: {new_note}".strip()

            table_api.update(booking_id, {"Notas": updated_note})
            logger.info(f"Notas actualizadas para {booking_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating notes: {e}")
            return False

    def list_by_date(self, fecha: datetime.date) -> List[Booking]:
        """
        Obtiene todas las reservas para una fecha específica.
        Usado por scheduler para enviar recordatorios 24h antes.

        Args:
            fecha: Fecha para filtrar reservas (datetime.date object)

        Returns:
            Lista de reservas para esa fecha
        """
        try:
            table_api = self.api.table(self.base_id, TABLES["RESERVAS"])

            # Format date for Airtable formula
            date_str = fecha.strftime("%Y-%m-%d")

            # Formula: buscar reservas de esta fecha que NO estén canceladas
            formula = f"AND(IS_SAME({{Fecha de Reserva}}, '{date_str}', 'day'), {{Estado de Reserva}} != 'Cancelada')"

            records = table_api.all(formula=formula)
            bookings = []

            for r in records:
                booking = self._map_record_to_booking(r)
                if booking:
                    bookings.append(booking)

            logger.info(f"Found {len(bookings)} bookings for {date_str}")
            return bookings

        except Exception as e:
            logger.error(f"Error listing bookings by date: {e}")
            return []

    def update_booking_reminder_sent(self, booking_id: str) -> bool:
        """
        Marca una reserva como que ya recibió recordatorio 24h.

        Args:
            booking_id: ID de la reserva en Airtable

        Returns:
            True si se actualizó correctamente
        """
        try:
            table_api = self.api.table(self.base_id, TABLES["RESERVAS"])

            # Update only the checkbox field that exists in Airtable
            # "Recordatorio Enviado At" field doesn't exist - removed
            fields = {
                "Recordatorio Enviado": True,
            }

            table_api.update(booking_id, fields)
            logger.info(f"Recordatorio marcado como enviado para {booking_id}")
            return True

        except Exception as e:
            logger.error(f"Error marking reminder as sent: {e}")
            return False

    def modify_booking(
        self,
        booking_id: str,
        new_date: str = None,
        new_time: str = None,
        new_pax: int = None,
    ) -> bool:
        """
        Modifica fecha, hora y/o número de personas de una reserva existente.

        Args:
            booking_id: ID de la reserva en Airtable
            new_date: Nueva fecha en formato YYYY-MM-DD (opcional)
            new_time: Nueva hora en formato HH:MM (opcional)
            new_pax: Nuevo número de personas (opcional)

        Returns:
            True si se modificó correctamente
        """
        try:
            table_api = self.api.table(self.base_id, TABLES["RESERVAS"])

            fields = {}

            if new_date:
                # Update 'Fecha de Reserva' (Date field)
                fields["Fecha de Reserva"] = new_date

            if new_time:
                # Update 'Hora' (DateTime field) - needs ISO format
                # Get current booking to preserve date if only time changed
                current = table_api.get(booking_id)
                current_date = current["fields"].get(
                    "Fecha de Reserva", datetime.now().strftime("%Y-%m-%d")
                )

                # Build new datetime
                dt_str = f"{new_date or current_date}T{new_time}:00.000Z"
                fields["Hora"] = dt_str

            if new_pax:
                fields["Cantidad de Personas"] = new_pax

            if not fields:
                logger.warning("No hay campos para modificar")
                return False

            table_api.update(booking_id, fields)
            logger.info(f"Reserva {booking_id} modificada: {fields}")
            return True

        except Exception as e:
            logger.error(f"Error modificando reserva: {e}")
            return False

    def find_any_booking_by_phone(
        self, phone: str, include_past: bool = False
    ) -> Optional[Booking]:
        """
        Busca CUALQUIER reserva para este teléfono (no solo pendientes).

        Args:
            phone: Número de teléfono
            include_past: Si True, incluye reservas pasadas

        Returns:
            La reserva más próxima encontrada o None
        """
        try:
            table_api = self.api.table(self.base_id, TABLES["RESERVAS"])

            # Buscar por teléfono, excluyendo canceladas
            formula = (
                f"AND({{Teléfono}} = '{phone}', {{Estado de Reserva}} != 'Cancelada')"
            )

            records = table_api.all(formula=formula)

            if not records:
                return None

            # Convertir a bookings
            bookings = []
            for r in records:
                b = self._map_record_to_booking(r)
                if b:
                    bookings.append(b)

            # Filtrar pasadas si no se incluyen
            if not include_past:
                now = datetime.now()
                bookings = [b for b in bookings if b.datetime_completo >= now]

            # Ordenar por fecha (más próxima primero)
            bookings.sort(key=lambda x: x.datetime_completo)

            return bookings[0] if bookings else None

        except Exception as e:
            logger.error(f"Error finding any booking by phone: {e}")
            return None
