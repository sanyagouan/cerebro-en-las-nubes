import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from pyairtable import Api
from src.core.ports.booking_repository import BookingRepository
from src.core.entities.booking import Booking, BookingStatus
from src.core.entities.table import Table, TableStatus
from src.core.config.airtable_ids import TABLES, BASE_ID

class AirtableBookingRepository(BookingRepository):
    def __init__(self):
        self.api_key = os.getenv("AIRTABLE_API_KEY")
        if not self.api_key:
            print("❌ WARNING: AIRTABLE_API_KEY not found in env")
        self.api = Api(self.api_key)
        self.base_id = BASE_ID

    # --- MAPPING HELPERS ---

    def _map_booking_to_fields(self, booking: Booking) -> Dict[str, Any]:
        """Convert domain Booking to Airtable fields (Spanish Schema)"""
        # Convert date and time to strings/formats compatible with Airtable
        
        # 'Fecha de Reserva' (Date) -> "YYYY-MM-DD"
        date_str = booking.date_time.strftime("%Y-%m-%d")
        
        # 'Hora' (DateTime) -> ISO String
        # Since 'Hora' is confirmed to be a DateTime field in Airtable, we send the full ISO string.
        time_str = booking.date_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        
        fields = {
            "Nombre del Cliente": booking.client_name,
            "Teléfono": booking.client_phone,
            "Fecha de Reserva": date_str,
            "Hora": time_str,
            "Cantidad de Personas": booking.pax,
            "Estado de Reserva": booking.status.value if hasattr(booking.status, 'value') else booking.status,
            # "Origen": booking.source or "Voice AI" # Comentado por no existir en schema
        }
        
        # Optional fields
        if booking.notes:
            fields["Notas"] = booking.notes
            
        if booking.assigned_table_id:
            # Linked records require an array of IDs
            fields["Mesa"] = [booking.assigned_table_id]
            
        return fields

    def _map_record_to_booking(self, record: Dict[str, Any]) -> Optional[Booking]:
        """Convert Airtable record to domain Booking"""
        fields = record.get("fields", {})
        
        try:
            # Parse datetime
            # Helper to combine Date+Time or use DateTime field
            dt_str = fields.get("Hora")
            if dt_str:
                # ISO Format from Airtable usually ends in Z
                # Python < 3.11 fromisoformat might not like Z, but 3.11 is fine.
                # Safe replace Z -> +00:00
                booking_dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            else:
                # Fallback: Date + Time components if separate
                date_str = fields.get("Fecha de Reserva")
                if date_str:
                     # Default time if missing
                     booking_dt = datetime.fromisoformat(f"{date_str}T12:00:00")
                else:
                    booking_dt = datetime.now()
            
            # Map Status
            status_str = fields.get("Estado de Reserva", "Pendiente")
            try:
                status = BookingStatus(status_str)
            except ValueError:
                status = BookingStatus.PENDING

            return Booking(
                id=record.get("id"),
                client_name=fields.get("Nombre del Cliente", "Anónimo"),
                client_phone=fields.get("Teléfono", ""),
                date_time=booking_dt,
                pax=fields.get("Cantidad de Personas", 0),
                notes=fields.get("Notas"),
                status=status,
                assigned_table_id=fields.get("Mesa", [None])[0] if fields.get("Mesa") else None,
                source=fields.get("Origen", "Voice AI")
            )
        except Exception as e:
            print(f"Error mapping record {record.get('id')}: {e}")
            return None

    # --- PUBLIC METHODS ---

    def get_all_tables(self) -> List[Table]:
        try:
            table_api = self.api.table(self.base_id, TABLES["MESAS"])
            records = table_api.all()
            tables = []
            
            for r in records:
                fields = r["fields"]
                tables.append(Table(
                    id=r["id"],
                    name=fields.get("Nombre de Mesa", "Unknown"),
                    capacity_min=fields.get("Capacidad", 2),
                    capacity_max=fields.get("Capacidad Ampliada") or fields.get("Capacidad", 4),
                    zone=fields.get("Ubicación", "Interior"),
                    # Assuming logic for combinable
                    is_combinable=True if "Combinable" in str(fields.get("Tipo", "")) else False,
                    status=TableStatus.AVAILABLE if fields.get("Disponible") else TableStatus.BLOCKED
                ))
            return tables
        except Exception as e:
            print(f"❌ Error fetching tables: {e}")
            # If failing, return empty list to not crash app, but log it.
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
            print(f"❌ Error fetching bookings: {e}")
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
            print(f"✅ Reserva creada: {booking.id}")
            return booking
            
        except Exception as e:
            print(f"❌ Error creando reserva: {e}")
            raise e

    def update_booking_status(self, booking_id: str, status: str, table_id: str = None) -> bool:
        """Actualiza el estado de una reserva existente."""
        try:
            table_api = self.api.table(self.base_id, TABLES["RESERVAS"])
            
            fields = {"Estado de Reserva": status}
            if table_id:
                fields["Mesa"] = [table_id]
            
            table_api.update(booking_id, fields)
            print(f"✅ Reserva {booking_id} actualizada a {status}")
            return True
            
        except Exception as e:
            print(f"❌ Error actualizando reserva: {e}")
            return False

    def find_pending_booking_by_phone(self, phone: str) -> Optional[Booking]:
        """Busca una reserva pendiente para este teléfono (HOY o FUTURO)."""
        try:
            table_api = self.api.table(self.base_id, TABLES["RESERVAS"])
            
            # Simple exact match first. Ideally should handle format diffs.
            # We filter by Status='Pendiente' AND Phone match
            # Note: Phone formatting is tricky. We'll try to match exact first.
            formula = f"AND({{Teléfono}} = '{phone}', {{Estado de Reserva}} = 'Pendiente')"
            
            records = table_api.all(formula=formula)
            
            # If multiple, take the most recent one (createdTime) or closest execution date?
            # Let's take the one closest to future.
            if not records:
                return None
                
            # Convert all to bookings
            bookings = []
            for r in records:
                b = self._map_record_to_booking(r)
                if b: bookings.append(b)
            
            # Sort by date (nearest first)
            bookings.sort(key=lambda x: x.date_time)
            
            # Return the first one that is active (not in past, though 'Pendiente' implied future usually)
            return bookings[0] if bookings else None
            
        except Exception as e:
            print(f"❌ Error finding booking by phone: {e}")
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
            print(f"✅ Notas actualizadas para {booking_id}")
            return True
        except Exception as e:
            print(f"❌ Error updating notes: {e}")
            return False
