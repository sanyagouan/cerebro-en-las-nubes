"""
ShiftRepository - Repositorio para gestión de turnos en Airtable.
"""

import logging
from typing import Optional, List, Dict, Any
from src.infrastructure.mcp.airtable_client import airtable_client

logger = logging.getLogger(__name__)

# Constantes de Airtable
BASE_ID = "appQ2ZXAR68cqDmJt"
TABLE_NAME = "Turnos"

# Mapeo de campos Python -> Airtable
FIELD_MAP = {
    "nombre": "Nombre de Turno",
    "servicio": "Servicio",
    "dias": "Día de Semana",
    "numero": "Número de Turno",
    "hora_inicio": "Hora Entrada Inicio",
    "hora_fin": "Hora Entrada Fin",
    "hora_salida": "Hora Salida",
    "activo_demanda": "Activo Solo Alta Demanda",
    "restriccion": "Restricción Capacidad",
}

class ShiftRepository:
    """Repositorio para operaciones CRUD de turnos en Airtable."""

    async def list_all(self) -> List[Dict[str, Any]]:
        """
        Lista todos los turnos configurados.
        """
        try:
            result = await airtable_client.list_records(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
            )
            records = result.get("records", [])
            shifts = []
            for r in records:
                fields = r.get("fields", {})
                shifts.append({
                    "id": r.get("id"),
                    "name": fields.get(FIELD_MAP["nombre"], "").lower(),
                    "service": fields.get(FIELD_MAP["servicio"]),
                    "days": fields.get(FIELD_MAP["dias"], []),
                    "number": fields.get(FIELD_MAP["numero"]),
                    "start": fields.get(FIELD_MAP["hora_inicio"]),
                    "end": fields.get(FIELD_MAP["hora_fin"]),
                    "exit": fields.get(FIELD_MAP["hora_salida"]),
                    "is_active": not fields.get(FIELD_MAP["activo_demanda"], False), # Invertido para lógica simple en dashboard
                    "max_capacity": fields.get(FIELD_MAP["restriccion"], 60)
                })
            return shifts
        except Exception as e:
            logger.error(f"Error listando turnos: {e}")
            return []

    async def update(self, shift_id: str, updates: Dict[str, Any]) -> bool:
        """
        Actualiza un turno específico.
        """
        try:
            airtable_fields = {}
            if "is_active" in updates:
                airtable_fields[FIELD_MAP["activo_demanda"]] = not updates["is_active"]
            if "max_capacity" in updates:
                airtable_fields[FIELD_MAP["restriccion"]] = updates["max_capacity"]
            if "start" in updates:
                airtable_fields[FIELD_MAP["hora_inicio"]] = updates["start"]
            if "end" in updates:
                airtable_fields[FIELD_MAP["hora_fin"]] = updates["end"]

            await airtable_client.update_record(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                record_id=shift_id,
                fields=airtable_fields
            )
            return True
        except Exception as e:
            logger.error(f"Error actualizando turno {shift_id}: {e}")
            return False

shift_repository = ShiftRepository()
