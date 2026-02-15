"""
Airtable MCP Client - Wrapper para interactuar con Airtable via MCP.
Proporciona una interfaz async para operaciones CRUD en Airtable.
"""
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class AirtableMCPClient:
    """Cliente para interactuar con Airtable a través del MCP server."""

    def __init__(self):
        """Inicializa el cliente Airtable MCP."""
        self._mcp_available = True
        logger.info("AirtableMCPClient initialized")

    async def list_records(
        self,
        base_id: str,
        table_name: str,
        max_records: Optional[int] = None,
        filterByFormula: Optional[str] = None,
        sort: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Lista records de una tabla de Airtable.

        Args:
            base_id: ID de la base de Airtable
            table_name: Nombre de la tabla
            max_records: Máximo de records a retornar
            filterByFormula: Fórmula de filtro de Airtable
            sort: Lista de objetos {field, direction} para ordenar

        Returns:
            Dict con estructura: {"records": [...], "offset": "..."}
        """
        try:
            # Importar MCP tool dinámicamente para evitar errores si no está disponible
            from mcp__airtable__list_records import list_records as mcp_list_records

            params = {
                "base_id": base_id,
                "table_name": table_name
            }

            if max_records:
                params["max_records"] = max_records
            if filterByFormula:
                params["filterByFormula"] = filterByFormula
            if sort:
                params["sort"] = sort

            result = await mcp_list_records(**params)
            logger.debug(f"Listed {len(result.get('records', []))} records from {table_name}")
            return result

        except ImportError:
            logger.error("Airtable MCP not available - check MCP server configuration")
            raise RuntimeError("Airtable MCP server not configured")
        except Exception as e:
            logger.error(f"Error listing Airtable records: {e}", exc_info=True)
            raise

    async def get_record(
        self,
        base_id: str,
        table_name: str,
        record_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene un record específico de Airtable.

        Args:
            base_id: ID de la base de Airtable
            table_name: Nombre de la tabla
            record_id: ID del record (empieza con "rec")

        Returns:
            Dict con estructura: {"id": "...", "fields": {...}, "createdTime": "..."}
            o None si no se encuentra
        """
        try:
            from mcp__airtable__get_record import get_record as mcp_get_record

            result = await mcp_get_record(
                base_id=base_id,
                table_name=table_name,
                record_id=record_id
            )

            logger.debug(f"Retrieved record {record_id} from {table_name}")
            return result

        except ImportError:
            logger.error("Airtable MCP not available")
            raise RuntimeError("Airtable MCP server not configured")
        except Exception as e:
            logger.error(f"Error getting Airtable record {record_id}: {e}", exc_info=True)
            # Si es 404, retornar None en vez de exception
            if "404" in str(e) or "not found" in str(e).lower():
                return None
            raise

    async def create_record(
        self,
        base_id: str,
        table_name: str,
        fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crea un nuevo record en Airtable.

        Args:
            base_id: ID de la base de Airtable
            table_name: Nombre de la tabla
            fields: Dict con los campos del record

        Returns:
            Dict con el record creado: {"id": "...", "fields": {...}, "createdTime": "..."}
        """
        try:
            from mcp__airtable__create_record import create_record as mcp_create_record

            result = await mcp_create_record(
                base_id=base_id,
                table_name=table_name,
                fields=fields
            )

            logger.info(f"Created record {result.get('id')} in {table_name}")
            return result

        except ImportError:
            logger.error("Airtable MCP not available")
            raise RuntimeError("Airtable MCP server not configured")
        except Exception as e:
            logger.error(f"Error creating Airtable record: {e}", exc_info=True)
            raise

    async def update_record(
        self,
        base_id: str,
        table_name: str,
        record_id: str,
        fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Actualiza un record existente en Airtable.

        Args:
            base_id: ID de la base de Airtable
            table_name: Nombre de la tabla
            record_id: ID del record a actualizar
            fields: Dict con los campos a actualizar (partial update)

        Returns:
            Dict con el record actualizado: {"id": "...", "fields": {...}}
        """
        try:
            from mcp__airtable__update_record import update_record as mcp_update_record

            result = await mcp_update_record(
                base_id=base_id,
                table_name=table_name,
                record_id=record_id,
                fields=fields
            )

            logger.info(f"Updated record {record_id} in {table_name}")
            return result

        except ImportError:
            logger.error("Airtable MCP not available")
            raise RuntimeError("Airtable MCP server not configured")
        except Exception as e:
            logger.error(f"Error updating Airtable record {record_id}: {e}", exc_info=True)
            raise

    async def delete_record(
        self,
        base_id: str,
        table_name: str,
        record_id: str
    ) -> bool:
        """
        Elimina un record de Airtable.

        Args:
            base_id: ID de la base de Airtable
            table_name: Nombre de la tabla
            record_id: ID del record a eliminar

        Returns:
            True si se eliminó correctamente
        """
        try:
            from mcp__airtable__delete_record import delete_record as mcp_delete_record

            await mcp_delete_record(
                base_id=base_id,
                table_name=table_name,
                record_id=record_id
            )

            logger.info(f"Deleted record {record_id} from {table_name}")
            return True

        except ImportError:
            logger.error("Airtable MCP not available")
            raise RuntimeError("Airtable MCP server not configured")
        except Exception as e:
            logger.error(f"Error deleting Airtable record {record_id}: {e}", exc_info=True)
            raise


# Singleton instance
airtable_client = AirtableMCPClient()
