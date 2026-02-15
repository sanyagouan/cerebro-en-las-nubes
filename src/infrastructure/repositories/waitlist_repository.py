"""
Repository para gestionar la Waitlist en Airtable.
Tabla: WAITLIST en Base appQ2ZXAR68cqDmJt
"""

from typing import List, Optional
from datetime import datetime, date, time
import logging

from src.core.entities.waitlist import WaitlistEntry, WaitlistStatus
from src.infrastructure.mcp.airtable_client import airtable_client

logger = logging.getLogger(__name__)

# Configuración Airtable
BASE_ID = "appQ2ZXAR68cqDmJt"
TABLE_NAME = "WAITLIST"

# Mapeo de campos Airtable ↔ Modelo
FIELD_MAP = {
    "nombre": "Nombre",
    "telefono": "Teléfono",
    "fecha": "Fecha",
    "hora": "Hora",
    "pax": "PAX",
    "zona_preferida": "Zona Preferida",
    "estado": "Estado",
    "posicion": "Posición",
    "created_at": "Creado",
    "notified_at": "Notificado",
    "confirmed_at": "Confirmado",
    "expired_at": "Expirado",
    "cancelled_at": "Cancelado",
    "notas": "Notas",
    "origen": "Origen",
    "notificacion_sid": "SID WhatsApp"
}


class WaitlistRepository:
    """Repository para operaciones CRUD en la tabla WAITLIST de Airtable."""
    
    def __init__(self):
        self.client = airtable_client
    
    def _to_airtable_fields(self, entry: WaitlistEntry) -> dict:
        """Convierte WaitlistEntry a formato Airtable."""
        fields = {
            FIELD_MAP["nombre"]: entry.nombre_cliente,
            FIELD_MAP["telefono"]: entry.telefono_cliente,
            FIELD_MAP["fecha"]: entry.fecha.isoformat(),
            FIELD_MAP["hora"]: entry.hora.strftime("%H:%M"),
            FIELD_MAP["pax"]: entry.num_personas,
            FIELD_MAP["estado"]: entry.estado.value,
            FIELD_MAP["created_at"]: entry.created_at.isoformat(),
            FIELD_MAP["origen"]: entry.origen,
        }
        
        # Campos opcionales
        if entry.zona_preferida:
            fields[FIELD_MAP["zona_preferida"]] = entry.zona_preferida
        if entry.posicion:
            fields[FIELD_MAP["posicion"]] = entry.posicion
        if entry.notified_at:
            fields[FIELD_MAP["notified_at"]] = entry.notified_at.isoformat()
        if entry.confirmed_at:
            fields[FIELD_MAP["confirmed_at"]] = entry.confirmed_at.isoformat()
        if entry.expired_at:
            fields[FIELD_MAP["expired_at"]] = entry.expired_at.isoformat()
        if entry.cancelled_at:
            fields[FIELD_MAP["cancelled_at"]] = entry.cancelled_at.isoformat()
        if entry.notas:
            fields[FIELD_MAP["notas"]] = entry.notas
        if entry.notificacion_sid:
            fields[FIELD_MAP["notificacion_sid"]] = entry.notificacion_sid
        
        return fields
    
    def _from_airtable_record(self, record: dict) -> WaitlistEntry:
        """Convierte registro de Airtable a WaitlistEntry."""
        fields = record.get("fields", {})
        
        # Parsear fecha y hora
        fecha_str = fields.get(FIELD_MAP["fecha"])
        hora_str = fields.get(FIELD_MAP["hora"])
        
        fecha = datetime.fromisoformat(fecha_str).date() if fecha_str else date.today()
        hora = datetime.strptime(hora_str, "%H:%M").time() if hora_str else time(20, 0)
        
        # Parsear timestamps opcionales
        def parse_datetime(field_name: str) -> Optional[datetime]:
            value = fields.get(FIELD_MAP[field_name])
            return datetime.fromisoformat(value) if value else None
        
        return WaitlistEntry(
            id=record["id"],
            airtable_id=record["id"],
            nombre_cliente=fields.get(FIELD_MAP["nombre"], ""),
            telefono_cliente=fields.get(FIELD_MAP["telefono"], ""),
            fecha=fecha,
            hora=hora,
            num_personas=int(fields.get(FIELD_MAP["pax"], 2)),
            zona_preferida=fields.get(FIELD_MAP["zona_preferida"]),
            estado=WaitlistStatus(fields.get(FIELD_MAP["estado"], "waiting")),
            posicion=fields.get(FIELD_MAP["posicion"]),
            created_at=parse_datetime("created_at") or datetime.now(),
            notified_at=parse_datetime("notified_at"),
            confirmed_at=parse_datetime("confirmed_at"),
            expired_at=parse_datetime("expired_at"),
            cancelled_at=parse_datetime("cancelled_at"),
            notas=fields.get(FIELD_MAP["notas"]),
            origen=fields.get(FIELD_MAP["origen"], "VAPI_VOICE"),
            notificacion_sid=fields.get(FIELD_MAP["notificacion_sid"])
        )
    
    async def create(self, entry: WaitlistEntry) -> WaitlistEntry:
        """Crea una nueva entrada en la waitlist."""
        try:
            fields = self._to_airtable_fields(entry)
            
            result = await self.client.create_record(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                fields=fields
            )
            
            entry.id = result["id"]
            entry.airtable_id = result["id"]
            
            logger.info(f"Waitlist entry creada: {entry.id} - {entry.nombre_cliente}")
            return entry
            
        except Exception as e:
            logger.error(f"Error creando waitlist entry: {e}")
            raise
    
    async def update(self, entry_id: str, updates: dict) -> WaitlistEntry:
        """
        Actualiza una entrada de la waitlist.
        
        Args:
            entry_id: ID de Airtable
            updates: Dict con campos a actualizar (usar nombres de FIELD_MAP)
        """
        try:
            # Mapear campos del modelo a Airtable
            airtable_updates = {}
            for key, value in updates.items():
                if key in FIELD_MAP:
                    airtable_field = FIELD_MAP[key]
                    
                    # Convertir tipos especiales
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    elif isinstance(value, date):
                        value = value.isoformat()
                    elif isinstance(value, time):
                        value = value.strftime("%H:%M")
                    elif isinstance(value, WaitlistStatus):
                        value = value.value
                    
                    airtable_updates[airtable_field] = value
            
            result = await self.client.update_record(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                record_id=entry_id,
                fields=airtable_updates
            )
            
            updated_entry = self._from_airtable_record(result)
            logger.info(f"Waitlist entry actualizada: {entry_id}")
            return updated_entry
            
        except Exception as e:
            logger.error(f"Error actualizando waitlist entry {entry_id}: {e}")
            raise
    
    async def get_by_id(self, entry_id: str) -> Optional[WaitlistEntry]:
        """Obtiene una entrada por su ID de Airtable."""
        try:
            record = await self.client.get_record(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                record_id=entry_id
            )
            
            return self._from_airtable_record(record)
            
        except Exception as e:
            logger.error(f"Error obteniendo waitlist entry {entry_id}: {e}")
            return None
    
    async def list_by_status(
        self, 
        status: WaitlistStatus, 
        fecha: Optional[date] = None
    ) -> List[WaitlistEntry]:
        """
        Lista entradas por estado y opcionalmente por fecha.
        Ordenadas por posición (ascendente) y created_at.
        """
        try:
            # Construir filtro
            filter_parts = [f"{{{FIELD_MAP['estado']}}}='{status.value}'"]
            
            if fecha:
                filter_parts.append(f"{{{FIELD_MAP['fecha']}}}='{fecha.isoformat()}'")
            
            filter_formula = f"AND({','.join(filter_parts)})" if len(filter_parts) > 1 else filter_parts[0]
            
            result = await self.client.list_records(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                filterByFormula=filter_formula,
                sort=[
                    {"field": FIELD_MAP["posicion"], "direction": "asc"},
                    {"field": FIELD_MAP["created_at"], "direction": "asc"}
                ]
            )
            
            entries = [self._from_airtable_record(r) for r in result.get("records", [])]
            logger.info(f"Encontradas {len(entries)} entradas con estado {status.value}")
            return entries
            
        except Exception as e:
            logger.error(f"Error listando waitlist por estado: {e}")
            return []
    
    async def get_next_waiting(self, fecha: date, hora: time, pax: int) -> Optional[WaitlistEntry]:
        """
        Obtiene la siguiente entrada WAITING que coincida con fecha/hora/pax.
        Devuelve la de mayor posición (primero en cola).
        """
        try:
            filter_formula = f"""AND(
                {{{FIELD_MAP['estado']}}}='waiting',
                {{{FIELD_MAP['fecha']}}}='{fecha.isoformat()}',
                {{{FIELD_MAP['pax']}}}<={pax}
            )"""
            
            result = await self.client.list_records(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                filterByFormula=filter_formula,
                sort=[{"field": FIELD_MAP["posicion"], "direction": "asc"}],
                max_records=1
            )
            
            records = result.get("records", [])
            if records:
                return self._from_airtable_record(records[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo próximo waiting: {e}")
            return None
    
    async def delete(self, entry_id: str) -> bool:
        """Elimina una entrada de la waitlist."""
        try:
            await self.client.delete_record(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                record_id=entry_id
            )
            
            logger.info(f"Waitlist entry eliminada: {entry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando waitlist entry {entry_id}: {e}")
            return False


# Instancia global del repositorio
waitlist_repository = WaitlistRepository()
