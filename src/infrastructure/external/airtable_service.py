import logging
from typing import Dict, Any, Optional
import os
from pyairtable import Api

logger = logging.getLogger(__name__)

class AirtableService:
    def __init__(self):
        self.api_key = os.getenv("AIRTABLE_API_KEY")
        self.base_id = os.getenv("AIRTABLE_BASE_ID")
        self.table_name = "Reservas" # Default
        
        if self.api_key:
            self.api = Api(self.api_key)
        else:
            self.api = None
            logger.warning("Airtable credentials not found.")

    async def create_record(self, fields: Dict[str, Any], table_name: Optional[str] = None) -> Optional[Dict]:
        if not self.api or not self.base_id:
            logger.warning(f"Mocking Airtable create record: {fields}")
            return {"id": "recMOCK12345", "fields": fields}

        target_table = table_name or self.table_name
        try:
            table = self.api.table(self.base_id, target_table)
            # PyAirtable is synchronous currently usually, but we wrap for future async
            record = table.create(fields)
            return record
        except Exception as e:
            logger.error(f"Error creating record in Airtable: {e}")
            # Don't raise, just log
            return None
