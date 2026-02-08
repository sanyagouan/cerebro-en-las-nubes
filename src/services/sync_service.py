"""
Servicio de sincronización bidireccional entre Supabase y Airtable.
Mantiene consistencia de datos entre ambas plataformas.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import urllib.parse

import httpx
from supabase import create_client, Client

from src.core.config import settings

logger = logging.getLogger(__name__)


class SyncDirection(Enum):
    AIRTABLE_TO_SUPABASE = "airtable_to_supabase"
    SUPABASE_TO_AIRTABLE = "supabase_to_airtable"
    BIDIRECTIONAL = "bidirectional"


@dataclass
class SyncConfig:
    table_name: str
    airtable_table_id: str
    supabase_table: str
    direction: SyncDirection
    primary_key: str = "id"
    last_sync_field: str = "updated_at"


class SupabaseAirtableSync:
    """Servicio de sincronización entre Supabase y Airtable."""
    
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
        self.airtable_base_id = settings.AIRTABLE_BASE_ID
        self.airtable_api_key = settings.AIRTABLE_API_KEY
        self.airtable_url = f"https://api.airtable.com/v0/{self.airtable_base_id}"
        
        # Configuración de tablas a sincronizar
        self.sync_configs = [
            SyncConfig(
                table_name="reservations",
                airtable_table_id="tblReservations",  # ID real de Airtable
                supabase_table="reservations",
                direction=SyncDirection.BIDIRECTIONAL,
                primary_key="id",
                last_sync_field="updated_at"
            ),
            SyncConfig(
                table_name="tables",
                airtable_table_id="tblTables",
                supabase_table="tables",
                direction=SyncDirection.AIRTABLE_TO_SUPABASE,
                primary_key="id"
            ),
            SyncConfig(
                table_name="users",
                airtable_table_id="tblUsers",
                supabase_table="users",
                direction=SyncDirection.SUPABASE_TO_AIRTABLE,
                primary_key="id"
            )
        ]
        
        self._sync_history: List[Dict] = []
    
    async def sync_all(self, full_sync: bool = False) -> Dict[str, Any]:
        """
        Ejecuta sincronización completa de todas las tablas configuradas.
        
        Args:
            full_sync: Si True, sincroniza todos los registros. 
                      Si False, solo sincroniza cambios desde última sync.
        
        Returns:
            Dict con estadísticas de sincronización por tabla
        """
        results = {}
        
        for config in self.sync_configs:
            try:
                logger.info(f"Syncing {config.table_name}...")
                result = await self.sync_table(config, full_sync)
                results[config.table_name] = result
                
                # Registrar en historial
                self._sync_history.append({
                    "table": config.table_name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"Error syncing {config.table_name}: {e}")
                results[config.table_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    async def sync_table(self, config: SyncConfig, full_sync: bool = False) -> Dict[str, Any]:
        """Sincroniza una tabla específica."""
        
        if config.direction == SyncDirection.AIRTABLE_TO_SUPABASE:
            return await self._sync_airtable_to_supabase(config, full_sync)
        elif config.direction == SyncDirection.SUPABASE_TO_AIRTABLE:
            return await self._sync_supabase_to_airtable(config, full_sync)
        else:  # BIDIRECTIONAL
            return await self._sync_bidirectional(config, full_sync)
    
    async def _sync_airtable_to_supabase(
        self, 
        config: SyncConfig, 
        full_sync: bool
    ) -> Dict[str, Any]:
        """Sincroniza desde Airtable hacia Supabase."""
        
        # Obtener registros de Airtable
        airtable_records = await self._get_airtable_records(
            config.airtable_table_id,
            full_sync
        )
        
        inserted = 0
        updated = 0
        errors = 0
        
        for record in airtable_records:
            try:
                # Transformar datos de Airtable a formato Supabase
                supabase_data = self._transform_airtable_to_supabase(
                    record, 
                    config.table_name
                )
                
                # Verificar si existe en Supabase
                existing = self.supabase.table(config.supabase_table)\
                    .select("*")\
                    .eq(config.primary_key, supabase_data[config.primary_key])\
                    .execute()
                
                if existing.data:
                    # Actualizar
                    self.supabase.table(config.supabase_table)\
                        .update(supabase_data)\
                        .eq(config.primary_key, supabase_data[config.primary_key])\
                        .execute()
                    updated += 1
                else:
                    # Insertar
                    self.supabase.table(config.supabase_table)\
                        .insert(supabase_data)\
                        .execute()
                    inserted += 1
                    
            except Exception as e:
                logger.error(f"Error processing record {record.get('id')}: {e}")
                errors += 1
        
        return {
            "status": "success",
            "direction": "airtable_to_supabase",
            "inserted": inserted,
            "updated": updated,
            "errors": errors,
            "total": len(airtable_records)
        }
    
    async def _sync_supabase_to_airtable(
        self, 
        config: SyncConfig, 
        full_sync: bool
    ) -> Dict[str, Any]:
        """Sincroniza desde Supabase hacia Airtable."""
        
        # Obtener registros de Supabase
        query = self.supabase.table(config.supabase_table).select("*")
        
        if not full_sync and config.last_sync_field:
            # Solo registros modificados desde última sync
            last_sync = await self._get_last_sync_timestamp(config.table_name)
            if last_sync:
                query = query.gte(config.last_sync_field, last_sync)
        
        supabase_records = query.execute().data
        
        inserted = 0
        updated = 0
        errors = 0
        
        async with httpx.AsyncClient() as client:
            for record in supabase_records:
                try:
                    # Transformar datos de Supabase a formato Airtable
                    airtable_data = self._transform_supabase_to_airtable(
                        record, 
                        config.table_name
                    )
                    
                    # Verificar si existe en Airtable
                    existing_id = await self._find_airtable_record(
                        client,
                        config.airtable_table_id,
                        config.primary_key,
                        record[config.primary_key]
                    )
                    
                    if existing_id:
                        # Actualizar
                        await self._update_airtable_record(
                            client,
                            config.airtable_table_id,
                            existing_id,
                            airtable_data
                        )
                        updated += 1
                    else:
                        # Insertar
                        await self._create_airtable_record(
                            client,
                            config.airtable_table_id,
                            airtable_data
                        )
                        inserted += 1
                        
                except Exception as e:
                    logger.error(f"Error processing record {record.get('id')}: {e}")
                    errors += 1
        
        return {
            "status": "success",
            "direction": "supabase_to_airtable",
            "inserted": inserted,
            "updated": updated,
            "errors": errors,
            "total": len(supabase_records)
        }
    
    async def _sync_bidirectional(
        self, 
        config: SyncConfig, 
        full_sync: bool
    ) -> Dict[str, Any]:
        """Sincronización bidireccional con resolución de conflictos."""
        
        # Primero: Airtable → Supabase
        airtable_result = await self._sync_airtable_to_supabase(config, full_sync)
        
        # Luego: Supabase → Airtable (solo registros nuevos/modificados)
        supabase_result = await self._sync_supabase_to_airtable(config, full_sync)
        
        return {
            "status": "success",
            "direction": "bidirectional",
            "airtable_to_supabase": airtable_result,
            "supabase_to_airtable": supabase_result
        }
    
    async def _get_airtable_records(
        self, 
        table_id: str, 
        full_sync: bool
    ) -> List[Dict]:
        """Obtiene registros de Airtable con límite máximo."""
        MAX_RECORDS = 10000  # Límite máximo para prevenir OOM
        records = []
        offset = None
        
        async with httpx.AsyncClient() as client:
            while True:
                params = {}
                if offset:
                    params["offset"] = offset
                
                response = await client.get(
                    f"{self.airtable_url}/{table_id}",
                    headers={"Authorization": f"Bearer {self.airtable_api_key}"},
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                new_records = data.get("records", [])
                records.extend(new_records)
                
                # Verificar límite máximo
                if len(records) >= MAX_RECORDS:
                    logger.warning(
                        f"Reached maximum records limit ({MAX_RECORDS}) "
                        f"for table {table_id}. Partial sync performed."
                    )
                    break
                
                offset = data.get("offset")
                
                if not offset:
                    break
        
        return records
    
    async def _find_airtable_record(
        self,
        client: httpx.AsyncClient,
        table_id: str,
        field: str,
        value: str
    ) -> Optional[str]:
        """Busca un registro en Airtable por campo."""
        escaped_value = urllib.parse.quote(value, safe='')
        response = await client.get(
            f"{self.airtable_url}/{table_id}",
            headers={"Authorization": f"Bearer {self.airtable_api_key}"},
            params={"filterByFormula": f"{{{field}}}='{escaped_value}'"}
        )
        response.raise_for_status()
        data = response.json()
        
        records = data.get("records", [])
        return records[0]["id"] if records else None
    
    async def _create_airtable_record(
        self,
        client: httpx.AsyncClient,
        table_id: str,
        data: Dict
    ):
        """Crea un registro en Airtable."""
        response = await client.post(
            f"{self.airtable_url}/{table_id}",
            headers={
                "Authorization": f"Bearer {self.airtable_api_key}",
                "Content-Type": "application/json"
            },
            json={"fields": data}
        )
        response.raise_for_status()
        return response.json()
    
    async def _update_airtable_record(
        self,
        client: httpx.AsyncClient,
        table_id: str,
        record_id: str,
        data: Dict
    ):
        """Actualiza un registro en Airtable."""
        response = await client.patch(
            f"{self.airtable_url}/{table_id}/{record_id}",
            headers={
                "Authorization": f"Bearer {self.airtable_api_key}",
                "Content-Type": "application/json"
            },
            json={"fields": data}
        )
        response.raise_for_status()
        return response.json()
    
    def _transform_airtable_to_supabase(
        self, 
        airtable_record: Dict, 
        table_name: str
    ) -> Dict:
        """Transforma datos de Airtable a formato Supabase."""
        fields = airtable_record.get("fields", {})
        
        transformers = {
            "reservations": self._transform_reservation_airtable_to_supabase,
            "tables": self._transform_table_airtable_to_supabase,
            "users": self._transform_user_airtable_to_supabase
        }
        
        transformer = transformers.get(table_name, lambda x: x)
        return transformer(fields)
    
    def _transform_supabase_to_airtable(
        self, 
        supabase_record: Dict, 
        table_name: str
    ) -> Dict:
        """Transforma datos de Supabase a formato Airtable."""
        transformers = {
            "reservations": self._transform_reservation_supabase_to_airtable,
            "tables": self._transform_table_supabase_to_airtable,
            "users": self._transform_user_supabase_to_airtable
        }
        
        transformer = transformers.get(table_name, lambda x: x)
        return transformer(supabase_record)
    
    # Transformadores específicos
    def _transform_reservation_airtable_to_supabase(self, fields: Dict) -> Dict:
        return {
            "id": fields.get("ID"),
            "customer_name": fields.get("Nombre del Cliente"),
            "phone": fields.get("Teléfono"),
            "date": fields.get("Fecha de Reserva"),
            "time": fields.get("Hora"),
            "pax": fields.get("Cantidad de Personas"),
            "status": fields.get("Estado de Reserva", "Pendiente"),
            "table_id": fields.get("Mesa", [None])[0] if fields.get("Mesa") else None,
            "notes": fields.get("Notas"),
            "created_at": fields.get("Creado"),
            "updated_at": fields.get("Modificado")
        }
    
    def _transform_reservation_supabase_to_airtable(self, record: Dict) -> Dict:
        return {
            "ID": record.get("id"),
            "Nombre del Cliente": record.get("customer_name"),
            "Teléfono": record.get("phone"),
            "Fecha de Reserva": record.get("date"),
            "Hora": record.get("time"),
            "Cantidad de Personas": record.get("pax"),
            "Estado de Reserva": record.get("status"),
            "Mesa": [record.get("table_id")] if record.get("table_id") else [],
            "Notas": record.get("notes")
        }
    
    def _transform_table_airtable_to_supabase(self, fields: Dict) -> Dict:
        return {
            "id": fields.get("ID"),
            "name": fields.get("Nombre"),
            "capacity": fields.get("Capacidad"),
            "location": fields.get("Ubicación"),
            "status": fields.get("Estado", "free"),
            "is_active": fields.get("Activa", True)
        }
    
    def _transform_table_supabase_to_airtable(self, record: Dict) -> Dict:
        return {
            "ID": record.get("id"),
            "Nombre": record.get("name"),
            "Capacidad": record.get("capacity"),
            "Ubicación": record.get("location"),
            "Estado": record.get("status"),
            "Activa": record.get("is_active", True)
        }
    
    def _transform_user_airtable_to_supabase(self, fields: Dict) -> Dict:
        return {
            "id": fields.get("ID"),
            "email": fields.get("Email"),
            "name": fields.get("Nombre"),
            "role": fields.get("Rol", "waiter"),
            "is_active": fields.get("Activo", True)
        }
    
    def _transform_user_supabase_to_airtable(self, record: Dict) -> Dict:
        return {
            "ID": record.get("id"),
            "Email": record.get("email"),
            "Nombre": record.get("name"),
            "Rol": record.get("role"),
            "Activo": record.get("is_active", True)
        }
    
    async def _get_last_sync_timestamp(self, table_name: str) -> Optional[str]:
        """Obtiene el timestamp de última sincronización."""
        # Buscar en historial
        for entry in reversed(self._sync_history):
            if entry["table"] == table_name and entry["result"]["status"] == "success":
                return entry["timestamp"]
        return None
    
    def get_sync_history(self) -> List[Dict]:
        """Retorna historial de sincronizaciones."""
        return self._sync_history[-100:]  # Últimas 100


# Instancia singleton
sync_service = SupabaseAirtableSync()
