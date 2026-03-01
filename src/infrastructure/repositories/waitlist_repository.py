"""
Repository para gestionar la Waitlist en Airtable.
Tabla: Lista de Espera en Base appQ2ZXAR68cqDmJt
"""

from typing import List, Optional
from datetime import datetime, date, time
import logging

from src.core.entities.waitlist import WaitlistEntry, WaitlistStatus
from src.infrastructure.mcp.airtable_client import airtable_client

logger = logging.getLogger(__name__)

# Configuración Airtable - CAMPOS REALES DE LA TABLA
BASE_ID = "appQ2ZXAR68cqDmJt"
TABLE_NAME = "Lista de Espera"

# Estados reales en Airtable: Esperando, Notificado, Convertida, Cancelada
STATUS_MAP = {
    WaitlistStatus.WAITING: "Esperando",
    WaitlistStatus.NOTIFIED: "Notificado",
    WaitlistStatus.CONFIRMED: "Convertida",
    WaitlistStatus.CANCELLED: "Cancelada",
    WaitlistStatus.EXPIRED: "Cancelada",  # No hay estado Expired, usamos Cancelada
}


class WaitlistRepository:
    """Repository para operaciones CRUD en la tabla Lista de Espera de Airtable."""

    def __init__(self):
        self.client = airtable_client

    async def create(self, entry: WaitlistEntry) -> WaitlistEntry:
        """Crea una nueva entrada en la waitlist."""
        try:
            fields = {
                "Nombre del Cliente": entry.nombre_cliente,
                "Teléfono": entry.telefono_cliente,
                "Número de Personas": entry.num_personas,
                "Estado": STATUS_MAP.get(entry.estado, "Esperando"),
                "Fecha Solicitada": entry.fecha.isoformat() if entry.fecha else None,
                "Notas": entry.notas or f"Origen: {entry.origen or 'VAPI_VOICE'}",
            }

            # Hora solicitada
            if entry.hora:
                fields["Hora Solicitada"] = (
                    f"2025-01-01T{entry.hora.strftime('%H:%M:%S')}.000Z"
                )

            result = await self.client.create_record(
                base_id=BASE_ID, table_name=TABLE_NAME, fields=fields
            )

            entry.id = result["id"]
            entry.airtable_id = result["id"]

            logger.info(f"Waitlist entry creada: {entry.id} - {entry.nombre_cliente}")
            return entry

        except Exception as e:
            logger.error(f"Error creando waitlist entry: {e}")
            raise

    async def update(self, entry_id: str, updates: dict) -> WaitlistEntry:
        """Actualiza una entrada de la waitlist."""
        try:
            airtable_updates = {}

            for key, value in updates.items():
                if key == "estado" and isinstance(value, WaitlistStatus):
                    airtable_updates["Estado"] = STATUS_MAP.get(value, "Esperando")
                elif key == "notified_at" and value:
                    airtable_updates["Fecha Notificación"] = value.isoformat()
                    airtable_updates["Notificado"] = True
                elif key == "notas":
                    airtable_updates["Notas"] = value

            result = await self.client.update_record(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                record_id=entry_id,
                fields=airtable_updates,
            )

            logger.info(f"Waitlist entry actualizada: {entry_id}")
            return await self.get_by_id(entry_id)

        except Exception as e:
            logger.error(f"Error actualizando waitlist entry {entry_id}: {e}")
            raise

    async def get_by_id(self, entry_id: str) -> Optional[WaitlistEntry]:
        """Obtiene una entrada por su ID de Airtable."""
        try:
            record = await self.client.get_record(
                base_id=BASE_ID, table_name=TABLE_NAME, record_id=entry_id
            )
            return self._from_airtable_record(record)

        except Exception as e:
            logger.error(f"Error obteniendo waitlist entry {entry_id}: {e}")
            return None

    async def list_by_status(
        self, status: WaitlistStatus, fecha: Optional[date] = None
    ) -> List[WaitlistEntry]:
        """Lista entradas por estado."""
        try:
            status_value = STATUS_MAP.get(status, "Esperando")
            filter_formula = f"{{Estado}}='{status_value}'"

            result = await self.client.list_records(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                filterByFormula=filter_formula,
                sort=[{"field": "Fecha Entrada Lista", "direction": "asc"}],
            )

            entries = [self._from_airtable_record(r) for r in result.get("records", [])]
            logger.info(
                f"Encontradas {len(entries)} entradas con estado {status_value}"
            )
            return entries

        except Exception as e:
            logger.error(f"Error listando waitlist por estado: {e}")
            return []

    async def get_next_waiting(
        self, fecha: date, hora: time, pax: int
    ) -> Optional[WaitlistEntry]:
        """Obtiene la siguiente entrada WAITING."""
        try:
            entries = await self.list_by_status(WaitlistStatus.WAITING)
            # Filtrar por fecha y pax
            for entry in entries:
                if entry.fecha == fecha and entry.num_personas <= pax:
                    return entry
            return None

        except Exception as e:
            logger.error(f"Error obteniendo próximo waiting: {e}")
            return None

    async def delete(self, entry_id: str) -> bool:
        """Elimina una entrada de la waitlist."""
        try:
            await self.client.delete_record(
                base_id=BASE_ID, table_name=TABLE_NAME, record_id=entry_id
            )
            logger.info(f"Waitlist entry eliminada: {entry_id}")
            return True

        except Exception as e:
            logger.error(f"Error eliminando waitlist entry {entry_id}: {e}")
            return False

    def _from_airtable_record(self, record: dict) -> WaitlistEntry:
        """Convierte registro de Airtable a WaitlistEntry."""
        fields = record.get("fields", {})

        # Parsear estado
        estado_str = fields.get("Estado", "Esperando")
        estado_map_reverse = {
            "Esperando": WaitlistStatus.WAITING,
            "Notificado": WaitlistStatus.NOTIFIED,
            "Convertida": WaitlistStatus.CONFIRMED,
            "Cancelada": WaitlistStatus.CANCELLED,
        }
        estado = estado_map_reverse.get(estado_str, WaitlistStatus.WAITING)

        # Parsear fecha
        fecha_str = fields.get("Fecha Solicitada")
        if fecha_str:
            try:
                fecha = (
                    datetime.fromisoformat(fecha_str.replace("Z", "")).date()
                    if "T" in fecha_str
                    else date.fromisoformat(fecha_str)
                )
            except:
                fecha = date.today()
        else:
            fecha = date.today()

        # Parsear hora
        hora_str = fields.get("Hora Solicitada")
        if hora_str:
            try:
                hora = (
                    datetime.fromisoformat(hora_str.replace("Z", "")).time()
                    if "T" in hora_str
                    else time(20, 0)
                )
            except:
                hora = time(20, 0)
        else:
            hora = time(20, 0)

        return WaitlistEntry(
            id=record["id"],
            airtable_id=record["id"],
            nombre_cliente=fields.get("Nombre del Cliente", ""),
            telefono_cliente=fields.get("Teléfono", ""),
            fecha=fecha,
            hora=hora,
            num_personas=int(fields.get("Número de Personas", 2)),
            zona_preferida=None,
            estado=estado,
            posicion=None,
            created_at=datetime.now(),
            notified_at=None,
            confirmed_at=None,
            expired_at=None,
            cancelled_at=None,
            notas=fields.get("Notas", ""),
            origen="AIRTABLE",
            notificacion_sid=None,
        )


# Instancia global del repositorio
waitlist_repository = WaitlistRepository()
