"""
HolidayRepository - Repositorio para gestión de festivos en Airtable.
"""

import logging
from typing import Optional, List, Dict, Any
from src.infrastructure.mcp.airtable_client import airtable_client

logger = logging.getLogger(__name__)

# Constantes de Airtable
BASE_ID = "appQ2ZXAR68cqDmJt"
TABLE_NAME = "Días Especiales"

# Mapeo de campos Python -> Airtable
FIELD_MAP = {
    "nombre": "Nombre del Día Especial",
    "fecha": "Fecha",
    "notas": "Notas",
    "tipo": "Tipo",
    "abierto": "Abierto",
    "turnos": "Turnos Activos",
    "desviar_humano": "Desviar a Humano",
}

class HolidayRepository:
    """Repositorio para operaciones CRUD de festivos en Airtable."""

    async def list_all(self) -> List[Dict[str, Any]]:
        """Lista todos los festivos."""
        try:
            result = await airtable_client.list_records(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
            )
            records = result.get("records", [])
            holidays = []
            for r in records:
                fields = r.get("fields", {})
                holidays.append({
                    "id": r.get("id"),
                    "name": fields.get(FIELD_MAP["nombre"]),
                    "date": fields.get(FIELD_MAP["fecha"]),
                    "is_closed": not fields.get(FIELD_MAP["abierto"], False),
                    "notes": fields.get(FIELD_MAP["notas"]),
                    "type": fields.get(FIELD_MAP["tipo"]),
                    "active_shifts": fields.get(FIELD_MAP["turnos"], []),
                    "forward_to_human": fields.get(FIELD_MAP["desviar_humano"], False)
                })
            return holidays
        except Exception as e:
            logger.error(f"Error listando festivos: {e}")
            return []

    async def create(self, data: Dict[str, Any]) -> str:
        """Crea un nuevo festivo."""
        fields = {
            FIELD_MAP["nombre"]: data.get("name"),
            FIELD_MAP["fecha"]: data.get("date"),
            FIELD_MAP["abierto"]: not data.get("is_closed", False),
            FIELD_MAP["tipo"]: "Festivo"
        }
        result = await airtable_client.create_record(
            base_id=BASE_ID,
            table_name=TABLE_NAME,
            fields=fields
        )
        return result.get("id")

    async def update(self, holiday_id: str, data: Dict[str, Any]) -> bool:
        """Actualiza un festivo."""
        fields = {}
        if "name" in data: fields[FIELD_MAP["nombre"]] = data["name"]
        if "date" in data: fields[FIELD_MAP["fecha"]] = data["date"]
        if "is_closed" in data: fields[FIELD_MAP["abierto"]] = not data["is_closed"]

        await airtable_client.update_record(
            base_id=BASE_ID,
            table_name=TABLE_NAME,
            record_id=holiday_id,
            fields=fields
        )
        return True

    async def delete(self, holiday_id: str) -> bool:
        """Elimina un festivo."""
        return await airtable_client.delete_record(
            base_id=BASE_ID,
            table_name=TABLE_NAME,
            record_id=holiday_id
        )

holiday_repository = HolidayRepository()
