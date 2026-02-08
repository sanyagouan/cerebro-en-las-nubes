import logging
from typing import Dict, Any, Optional, List  # FIXED: added List
import os
from pyairtable import Api

from src.infrastructure.cache.redis_cache import get_cache
from src.core.logging import logger
from src.core.utils.sanitization import sanitize_reservation_data  # SECURITY: Import sanitization


class AirtableService:
    def __init__(self):
        self.api_key = os.getenv("AIRTABLE_API_KEY")
        self.base_id = os.getenv("AIRTABLE_BASE_ID")
        self.table_name = "Reservas"  # Default
        self.cache = get_cache(
            max_connections=5, compress_threshold=2048
        )  # Initialize optimized cache

        if self.api_key:
            self.api = Api(self.api_key)
        else:
            self.api = None
            logger.warning("Airtable credentials not found.")

        # Log cache health on initialization
        if self.cache.enabled:
            cache_health = self.cache.health_check()
            logger.info(f"AirtableService initialized - Cache: {cache_health}")
        else:
            logger.warning("AirtableService initialized - Cache disabled")

    async def create_record(
        self, fields: Dict[str, Any], table_name: Optional[str] = None
    ) -> Optional[Dict]:
        # SECURITY: Sanitize fields to prevent formula injection
        sanitized_fields = sanitize_reservation_data(fields)
        
        if not self.api or not self.base_id:
            logger.warning(f"Mocking Airtable create record: {sanitized_fields}")
            return {"id": "recMOCK12345", "fields": sanitized_fields}

        target_table = table_name or self.table_name
        try:
            table = self.api.table(self.base_id, target_table)
            record = table.create(sanitized_fields)

            # Invalidate cache for this table
            cache_key = f"airtable:{target_table}:*"
            self.cache.delete_pattern(cache_key)
            logger.info(f"Invalidated cache for table '{target_table}' after create")

            return record
        except Exception as e:
            logger.error(f"Error creating record in Airtable: {e}")
            return None

    async def get_record(
        self, record_id: str, table_name: Optional[str] = None
    ) -> Optional[Dict]:
        if not self.api or not self.base_id:
            logger.warning(f"Mocking Airtable get record: {record_id}")
            return {"id": record_id, "fields": {}}

        target_table = table_name or self.table_name
        cache_key = f"airtable:{target_table}:{record_id}"

        # Try cache first
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug(
                f"Cache hit for record '{record_id}' in table '{target_table}'"
            )
            return cached

        # Fetch from Airtable
        try:
            table = self.api.table(self.base_id, target_table)
            record = table.get(record_id)

            # Cache for 1 hour
            self.cache.set(cache_key, record, ttl=3600)
            logger.debug(f"Cached record '{record_id}' from table '{target_table}'")

            return record
        except Exception as e:
            logger.error(f"Error getting record from Airtable: {e}")
            return None

    async def get_all_records(
        self, table_name: Optional[str] = None, max_records: int = 100
    ) -> List[Dict]:
        if not self.api or not self.base_id:
            logger.warning(f"Mocking Airtable get all records")
            return []

        target_table = table_name or self.table_name
        cache_key = f"airtable:{target_table}:all"

        # Try cache first
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug(f"Cache hit for all records in table '{target_table}'")
            return cached

        # Fetch from Airtable
        try:
            table = self.api.table(self.base_id, target_table)
            records = table.all(max_records=max_records)

            # Cache for 10 minutes (fresher data than individual records)
            self.cache.set(cache_key, records, ttl=600)
            logger.debug(f"Cached {len(records)} records from table '{target_table}'")

            return records
        except Exception as e:
            logger.error(f"Error getting all records from Airtable: {e}")
            return []

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics for Airtable operations.
        """
        return self.cache.get_stats()

    def get_cache_health(self) -> Dict[str, Any]:
        """
        Get cache health status.
        """
        return self.cache.health_check()
