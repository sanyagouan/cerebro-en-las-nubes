"""
ConfigRepository - Repositorio para gestión de parámetros generales en Airtable (Tabla CONFIGURACIÓN).
"""

import logging
import json
from typing import Optional, Dict, Any
from src.infrastructure.mcp.airtable_client import airtable_client

logger = logging.getLogger(__name__)

# Constantes de Airtable
BASE_ID = "appQ2ZXAR68cqDmJt"
TABLE_NAME = "CONFIGURACIÓN"

# Mapeo de campos Python -> Airtable
FIELD_MAP = {
    "parametro": "Parámetro",
    "valor": "Valor",
    "tipo": "Tipo",
}

class ConfigRepository:
    """Repositorio para parámetros de configuración en Airtable."""

    async def get_param(self, name: str, default: Any = None) -> Any:
        """Obtiene un parámetro por nombre."""
        try:
            formula = f"{{{FIELD_MAP['parametro']}}} = '{name}'"
            result = await airtable_client.list_records(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                filterByFormula=formula,
                max_records=1
            )
            records = result.get("records", [])
            if not records:
                return default
            
            field_data = records[0].get("fields", {})
            value_str = field_data.get(FIELD_MAP["valor"], "")
            value_type = field_data.get(FIELD_MAP["tipo"], "Texto")

            if value_type == "JSON":
                try:
                    return json.loads(value_str)
                except:
                    return default
            elif value_type == "Número":
                try:
                    return float(value_str)
                except:
                    return default
            elif value_type == "Booleano":
                return value_str.lower() in ("true", "1", "yes")
            
            return value_str

        except Exception as e:
            logger.error(f"Error obteniendo parámetro {name}: {e}")
            return default

    async def set_param(self, name: str, value: Any, value_type: str = "Texto") -> bool:
        """Guarda un parámetro."""
        try:
            # Buscar si existe
            formula = f"{{{FIELD_MAP['parametro']}}} = '{name}'"
            result = await airtable_client.list_records(
                base_id=BASE_ID,
                table_name=TABLE_NAME,
                filterByFormula=formula,
                max_records=1
            )
            
            val_str = json.dumps(value) if value_type == "JSON" else str(value)
            
            fields = {
                FIELD_MAP["parametro"]: name,
                FIELD_MAP["valor"]: val_str,
                FIELD_MAP["tipo"]: value_type
            }

            records = result.get("records", [])
            if records:
                await airtable_client.update_record(
                    base_id=BASE_ID,
                    table_name=TABLE_NAME,
                    record_id=records[0].get("id"),
                    fields=fields
                )
            else:
                await airtable_client.create_record(
                    base_id=BASE_ID,
                    table_name=TABLE_NAME,
                    fields=fields
                )
            return True
        except Exception as e:
            logger.error(f"Error guardando parámetro {name}: {e}")
            return False

config_repository = ConfigRepository()
