"""
Airtable Client - Wrapper para interactuar con Airtable via pyairtable.
Proporciona una interfaz async para operaciones CRUD en Airtable.
"""

from typing import Dict, Any, List, Optional
import os
import logging

from pyairtable import Api

logger = logging.getLogger(__name__)


class AirtableMCPClient:
    """Cliente para interactuar con Airtable a través de pyairtable."""

    def __init__(self):
        """Inicializa el cliente Airtable."""
        self.api_key = os.getenv("AIRTABLE_API_KEY")
        self.base_id = os.getenv("AIRTABLE_BASE_ID")
        self._api = None

        if self.api_key:
            try:
                self._api = Api(self.api_key)
                logger.info("AirtableMCPClient initialized with pyairtable")
            except Exception as e:
                logger.error(f"Failed to initialize Airtable API: {e}")
        else:
            logger.warning("AIRTABLE_API_KEY not found - Airtable client disabled")

    def _get_table(self, table_name: str):
        """Obtiene una tabla de Airtable."""
        if not self._api or not self.base_id:
            raise RuntimeError("Airtable not configured")
        return self._api.table(self.base_id, table_name)

    async def list_records(
        self,
        base_id: str,
        table_name: str,
        max_records: Optional[int] = None,
        filterByFormula: Optional[str] = None,
        sort: Optional[List[Dict[str, str]]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Lista records de una tabla de Airtable.
        """
        try:
            table = self._get_table(table_name)

            kwargs_list = {}
            if max_records:
                kwargs_list["max_records"] = max_records
            if filterByFormula:
                kwargs_list["formula"] = filterByFormula
            if sort:
                # Convertir formato [{field, direction}] a ["field"] o ["-field"]
                sort_fields = []
                for s in sort:
                    field = s.get("field", "")
                    direction = s.get("direction", "asc")
                    if direction.lower() == "desc":
                        sort_fields.append(f"-{field}")
                    else:
                        sort_fields.append(field)
                kwargs_list["sort"] = sort_fields

            records = table.all(**kwargs_list)
            result = {"records": records}
            logger.debug(f"Listed {len(records)} records from {table_name}")
            return result

        except Exception as e:
            logger.error(f"Error listing Airtable records: {e}", exc_info=True)
            raise

    async def get_record(
        self, base_id: str, table_name: str, record_id: str
    ) -> Optional[Dict[str, Any]]:
        """Obtiene un record específico de Airtable."""
        try:
            table = self._get_table(table_name)
            record = table.get(record_id)
            logger.debug(f"Retrieved record {record_id} from {table_name}")
            return record
        except Exception as e:
            logger.error(f"Error getting Airtable record {record_id}: {e}")
            if "404" in str(e) or "not found" in str(e).lower():
                return None
            raise

    async def create_record(
        self, base_id: str, table_name: str, fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Crea un nuevo record en Airtable."""
        try:
            table = self._get_table(table_name)
            result = table.create(fields)
            logger.info(f"Created record {result.get('id')} in {table_name}")
            return result
        except Exception as e:
            logger.error(f"Error creating Airtable record: {e}")
            raise

    async def update_record(
        self, base_id: str, table_name: str, record_id: str, fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Actualiza un record existente en Airtable."""
        try:
            table = self._get_table(table_name)
            result = table.update(record_id, fields)
            logger.info(f"Updated record {record_id} in {table_name}")
            return result
        except Exception as e:
            logger.error(f"Error updating Airtable record {record_id}: {e}")
            raise

    async def delete_record(
        self, base_id: str, table_name: str, record_id: str
    ) -> bool:
        """Elimina un record de Airtable."""
        try:
            table = self._get_table(table_name)
            table.delete(record_id)
            logger.info(f"Deleted record {record_id} from {table_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting Airtable record {record_id}: {e}")
            raise


# Singleton instance
airtable_client = AirtableMCPClient()


def get_airtable_client() -> AirtableMCPClient:
    """Retorna la instancia singleton del cliente Airtable."""
    return airtable_client
