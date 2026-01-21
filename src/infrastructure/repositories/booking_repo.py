import os
from typing import List
from datetime import datetime
from pyairtable import Api
from src.core.ports.booking_repository import BookingRepository
from src.core.entities.booking import Booking, BookingStatus
from src.core.entities.table import Table, TableStatus
from src.core.config.airtable_ids import TABLES, BASE_ID

class AirtableBookingRepository(BookingRepository):
    def __init__(self):
        self.api_key = os.getenv("AIRTABLE_API_KEY")
        self.api = Api(self.api_key)
        self.base_id = BASE_ID

    def get_all_tables(self) -> List[Table]:
        try:
            table_api = self.api.table(self.base_id, TABLES["MESAS"])
            records = table_api.all()
            tables = []
            
            for r in records:
                fields = r["fields"]
                # Airtable Fields Mapping
                tables.append(Table(
                    id=r["id"],
                    name=fields.get("Nombre de Mesa", "Unknown"),
                    capacity_min=fields.get("Capacidad", 2),
                    capacity_max=fields.get("Capacidad Ampliada") or fields.get("Capacidad", 4),
                    zone=fields.get("Ubicación", "Interior"),
                    is_combinable=True if "Combinable" in fields.get("Tipo", []) else False, # Inferido
                    status=TableStatus.AVAILABLE if fields.get("Disponible") else TableStatus.BLOCKED
                ))
            return tables
        except Exception as e:
            print(f"❌ Error fetching tables: {e}")
            return []

    def get_bookings_for_date(self, date: datetime) -> List[Booking]:
        """Obtiene reservas para una fecha específica desde Airtable."""
        try:
            table_api = self.api.table(self.base_id, TABLES["RESERVAS"])
            
            # Airtable date filter format: YYYY-MM-DD
            date_str = date.strftime("%Y-%m-%d")
            formula = f"IS_SAME({{Fecha de Reserva}}, '{date_str}', 'day')"
            
            records = table_api.all(formula=formula)
            bookings = []
            
            for r in records:
                fields = r["fields"]
                # Parse datetime from Airtable (Fecha de Reserva + Hora)
                booking_date_str = fields.get("Fecha de Reserva", "")
                hora_str = fields.get("Hora", "12:00")
                
                try:
                    booking_datetime = datetime.fromisoformat(f"{booking_date_str}T{hora_str}")
                except:
                    booking_datetime = datetime.now()
                
                bookings.append(Booking(
                    id=r["id"],
                    client_name=fields.get("Nombre del Cliente", "Unknown"),
                    client_phone=fields.get("Teléfono", ""),
                    date_time=booking_datetime,
                    pax=fields.get("Cantidad de Personas", 2),
                    notes=fields.get("Notas Especiales"),
                    status=fields.get("Estado", BookingStatus.PENDING),
                    assigned_table_id=fields.get("Mesa", [None])[0] if fields.get("Mesa") else None,
                    source=fields.get("Canal", "Voice AI")
                ))
            return bookings
        except Exception as e:
            print(f"❌ Error fetching bookings: {e}")
            return []

    def create_booking(self, booking: Booking) -> Booking:
        """Crea una nueva reserva en Airtable."""
        try:
            table_api = self.api.table(self.base_id, TABLES["RESERVAS"])
            
            # Preparar datos para Airtable
            fields = {
                "Nombre del Cliente": booking.client_name,
                "Teléfono": booking.client_phone or "",
                "Fecha de Reserva": booking.date_time.strftime("%Y-%m-%d"),
                "Hora": booking.date_time.strftime("%H:%M"),
                "Cantidad de Personas": booking.pax,
                "Estado": str(booking.status) if booking.status else "Pendiente",
                "Canal": booking.source or "Voice AI",
                "Notas Especiales": booking.notes or ""
            }
            
            # Si hay mesa asignada, añadirla (Airtable espera array de IDs)
            if booking.assigned_table_id:
                fields["Mesa"] = [booking.assigned_table_id]
            
            # Crear registro
            record = table_api.create(fields)
            
            # Actualizar ID del booking con el ID de Airtable
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
            
            fields = {"Estado": status}
            if table_id:
                fields["Mesa"] = [table_id]
            
            table_api.update(booking_id, fields)
            print(f"✅ Reserva {booking_id} actualizada a {status}")
            return True
            
        except Exception as e:
            print(f"❌ Error actualizando reserva: {e}")
            return False
