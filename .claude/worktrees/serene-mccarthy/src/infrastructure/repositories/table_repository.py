"""
TableRepository - Gestión de mesas con Airtable.
Migración de datos hardcoded a base de datos permanente.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from src.core.entities.table import Table, TableZone, TableStatus
from src.infrastructure.mcp.airtable_client import airtable_client

logger = logging.getLogger(__name__)

# Configuración Airtable
BASE_ID = "appQ2ZXAR68cqDmJt"
TABLE_NAME = "MESAS"


class TableRepository:
    """Repository para gestionar mesas en Airtable."""

    # ========== MAPEO PYTHON ↔ AIRTABLE ==========

    @staticmethod
    def _table_to_airtable_fields(table: Table) -> Dict[str, Any]:
        """Convierte objeto Table a campos Airtable.

        Mapeo:
        - table.id → "ID Mesa" (nuevo campo, único)
        - table.nombre → "Nombre de Mesa"
        - table.zona → "Ubicación" ("Terraza" | "Interior")
        - table.capacidad_max → "Capacidad"
        - table.capacidad_min → "Capacidad Minima" (nuevo campo)
        - table.ampliable → "Tipo" ("Ampliable" si True, "Fija" si False)
        - table.capacidad_ampliada → "Capacidad Ampliada"
        - table.auxiliar_requerida → "Mesa Auxiliar Requerida" (nuevo campo)
        - table.notas → "Notas"
        - table.requiere_aviso → "Requiere Aviso" (nuevo campo checkbox)
        - table.prioridad → "Prioridad" (nuevo campo number)
        - table.status → "Estado" (nuevo campo: "Libre"|"Ocupada"|"Reservada"|"Bloqueada")
        """
        fields = {
            "ID Mesa": table.id,
            "Nombre de Mesa": table.nombre,
            "Ubicación": table.zona.value if isinstance(table.zona, TableZone) else table.zona,
            "Capacidad": table.capacidad_max,
            "Capacidad Minima": table.capacidad_min,
            "Tipo": "Ampliable" if table.ampliable else "Fija",
            "Prioridad": table.prioridad,
            "Estado": table.status.value if isinstance(table.status, TableStatus) else table.status,
            "Disponible": table.status == TableStatus.AVAILABLE  # Checkbox legacy
        }

        # Campos opcionales
        if table.capacidad_ampliada:
            fields["Capacidad Ampliada"] = table.capacidad_ampliada
        if table.auxiliar_requerida:
            fields["Mesa Auxiliar Requerida"] = table.auxiliar_requerida
        if table.notas:
            fields["Notas"] = table.notas

        return fields

    @staticmethod
    def _airtable_to_table(record: Dict[str, Any]) -> Table:
        """Convierte record de Airtable a objeto Table."""
        fields = record.get("fields", {})

        # Campos requeridos
        table_id = fields.get("ID Mesa", fields.get("Nombre de Mesa", "UNKNOWN"))
        nombre = fields.get("Nombre de Mesa", "Sin nombre")
        zona_str = fields.get("Ubicación", "Interior")
        capacidad_max = fields.get("Capacidad", 2)
        capacidad_min = fields.get("Capacidad Minima", 0)

        # Tipo y ampliación
        tipo = fields.get("Tipo", "Fija")
        ampliable = tipo == "Ampliable"
        capacidad_ampliada = fields.get("Capacidad Ampliada")
        auxiliar_requerida = fields.get("Mesa Auxiliar Requerida")

        # Estado
        estado_str = fields.get("Estado")
        if not estado_str:
            # Fallback: usar campo legacy "Disponible"
            disponible = fields.get("Disponible", True)
            estado_str = "Libre" if disponible else "Ocupada"

        # Otros campos
        notas = fields.get("Notas")
        requiere_aviso = False  # Campo aún no existe en Airtable, hardcoded a False
        prioridad = fields.get("Prioridad", 5)

        return Table(
            id=table_id,
            nombre=nombre,
            zona=TableZone(zona_str),
            capacidad_min=capacidad_min,
            capacidad_max=capacidad_max,
            ampliable=ampliable,
            auxiliar_requerida=auxiliar_requerida,
            capacidad_ampliada=capacidad_ampliada,
            notas=notas,
            requiere_aviso=requiere_aviso,
            prioridad=prioridad,
            status=TableStatus(estado_str)
        )

    # ========== CRUD OPERATIONS ==========

    async def list_all(self, zona: Optional[TableZone] = None) -> List[Table]:
        """Lista todas las mesas, opcionalmente filtradas por zona."""
        try:
            # Construir filtro Airtable
            filter_formula = None
            if zona:
                filter_formula = f"{{Ubicación}} = '{zona.value}'"

            # Obtener records de Airtable
            result = await airtable_client.list_records(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                filterByFormula=filter_formula,
                sort=[{"field": "Prioridad", "direction": "asc"}]
            )

            records = result.get("records", [])
            tables = [self._airtable_to_table(r) for r in records]

            logger.info(f"Retrieved {len(tables)} tables from Airtable (zona filter: {zona.value if zona else 'all'})")
            return tables

        except Exception as e:
            logger.error(f"Error listing tables from Airtable: {e}", exc_info=True)
            raise

    async def get_by_id(self, table_id: str) -> Optional[Table]:
        """Obtiene una mesa por su ID único."""
        try:
            # Buscar por ID Mesa
            result = await airtable_client.list_records(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                filterByFormula=f"{{ID Mesa}} = '{table_id}'",
                max_records=1
            )

            records = result.get("records", [])
            if not records:
                logger.warning(f"Table {table_id} not found in Airtable")
                return None

            table = self._airtable_to_table(records[0])
            logger.debug(f"Retrieved table {table_id} from Airtable")
            return table

        except Exception as e:
            logger.error(f"Error getting table {table_id} from Airtable: {e}", exc_info=True)
            raise

    async def create(self, table: Table) -> Table:
        """Crea una nueva mesa en Airtable."""
        try:
            # Verificar que ID no exista
            existing = await self.get_by_id(table.id)
            if existing:
                raise ValueError(f"Table with ID {table.id} already exists")

            # Crear record
            fields = self._table_to_airtable_fields(table)
            result = await airtable_client.create_record(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                fields=fields
            )

            created_table = self._airtable_to_table(result)
            logger.info(f"Created table {table.id} in Airtable (record: {result.get('id')})")
            return created_table

        except Exception as e:
            logger.error(f"Error creating table {table.id} in Airtable: {e}", exc_info=True)
            raise

    async def update(self, table_id: str, updates: Dict[str, Any]) -> Table:
        """Actualiza una mesa existente.

        Args:
            table_id: ID de la mesa (ID Mesa)
            updates: Dict con campos a actualizar (usa nombres Python, no Airtable)
        """
        try:
            # Obtener record actual
            result = await airtable_client.list_records(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                filterByFormula=f"{{ID Mesa}} = '{table_id}'",
                max_records=1
            )

            records = result.get("records", [])
            if not records:
                raise ValueError(f"Table {table_id} not found")

            record_id = records[0]["id"]

            # Mapear updates a campos Airtable
            airtable_updates = {}

            if "nombre" in updates:
                airtable_updates["Nombre de Mesa"] = updates["nombre"]
            if "zona" in updates:
                airtable_updates["Ubicación"] = updates["zona"]
            if "capacidad_max" in updates:
                airtable_updates["Capacidad"] = updates["capacidad_max"]
            if "capacidad_min" in updates:
                airtable_updates["Capacidad Minima"] = updates["capacidad_min"]
            if "ampliable" in updates:
                airtable_updates["Tipo"] = "Ampliable" if updates["ampliable"] else "Fija"
            if "capacidad_ampliada" in updates:
                airtable_updates["Capacidad Ampliada"] = updates["capacidad_ampliada"]
            if "auxiliar_requerida" in updates:
                airtable_updates["Mesa Auxiliar Requerida"] = updates["auxiliar_requerida"]
            if "notas" in updates:
                airtable_updates["Notas"] = updates["notas"]
            if "requiere_aviso" in updates:
                airtable_updates["Requiere Aviso"] = updates["requiere_aviso"]
            if "prioridad" in updates:
                airtable_updates["Prioridad"] = updates["prioridad"]
            if "status" in updates:
                status_value = updates["status"]
                airtable_updates["Estado"] = status_value
                airtable_updates["Disponible"] = status_value == "Libre"

            # Actualizar en Airtable
            updated_record = await airtable_client.update_record(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                record_id=record_id,
                fields=airtable_updates
            )

            updated_table = self._airtable_to_table(updated_record)
            logger.info(f"Updated table {table_id} in Airtable")
            return updated_table

        except Exception as e:
            logger.error(f"Error updating table {table_id} in Airtable: {e}", exc_info=True)
            raise

    async def delete(self, table_id: str) -> bool:
        """Elimina una mesa de Airtable."""
        try:
            # Obtener record ID
            result = await airtable_client.list_records(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                filterByFormula=f"{{ID Mesa}} = '{table_id}'",
                max_records=1
            )

            records = result.get("records", [])
            if not records:
                logger.warning(f"Table {table_id} not found for deletion")
                return False

            record_id = records[0]["id"]

            # Eliminar
            await airtable_client.delete_record(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                record_id=record_id
            )

            logger.info(f"Deleted table {table_id} from Airtable")
            return True

        except Exception as e:
            logger.error(f"Error deleting table {table_id} from Airtable: {e}", exc_info=True)
            raise

    async def update_status(self, table_id: str, new_status: TableStatus) -> Table:
        """Actualiza solo el estado de una mesa."""
        return await self.update(
            table_id=table_id,
            updates={"status": new_status.value}
        )


# Singleton instance
table_repository = TableRepository()
