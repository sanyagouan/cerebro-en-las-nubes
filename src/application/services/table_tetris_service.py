"""
TableTetrisService - Servicio integrado de asignación de mesas.
Conecta TableTetrisEngine con Airtable y Redis.
"""

from datetime import date, datetime
from typing import Optional, List, Dict, Any
import logging
import json

from src.core.logic.table_tetris_engine import (
    TableTetrisEngine,
    ZonePreference,
    AssignmentResult,
    TableCandidate,
)
from src.core.logic.table_learning_service import (
    TableLearningService,
    get_learning_service,
)
from src.infrastructure.repositories.table_repository import (
    TableRepository,
    table_repository,
)
from src.infrastructure.cache.redis_cache import get_cache
from src.core.entities.table import Table, TableZone, TableStatus

logger = logging.getLogger(__name__)


class TableTetrisService:
    """
    Servicio completo de asignación de mesas.

    INTEGRACIÓN:
    - Airtable: Carga mesas reales desde la base de datos
    - Redis: Cache de disponibilidad en tiempo real
    - Learning: Aprendizaje de duraciones y no-shows
    """

    CACHE_TTL_TABLES = 300  # 5 minutos para lista de mesas
    CACHE_TTL_AVAILABILITY = 60  # 1 minuto para disponibilidad

    def __init__(
        self,
        table_repo: TableRepository = None,
        redis_cache=None,
        learning_service: TableLearningService = None,
    ):
        self.table_repo = table_repo or table_repository
        self.cache = redis_cache or get_cache()
        self.learning = learning_service or get_learning_service()

        # Engine principal
        self.engine = TableTetrisEngine(
            redis_client=self.cache.redis_client if self.cache.enabled else None
        )

        # Cache de mesas cargadas
        self._tables_loaded = False

    async def _load_tables_from_airtable(self) -> Dict[str, Dict]:
        """Carga mesas desde Airtable y las cachea."""
        cache_key = "tetris:tables:all"

        # Intentar cache primero
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug("Tables loaded from cache")
            return cached

        # Cargar desde Airtable
        try:
            tables = await self.table_repo.list_all()
            tables_dict = {}

            for table in tables:
                tables_dict[table.id] = {
                    "id": table.id,
                    "nombre": table.nombre,
                    "zona": table.zona.value,
                    "capacidad_min": table.capacidad_min,
                    "capacidad_max": table.capacidad_max,
                    "ampliable": table.ampliable,
                    "auxiliar_requerida": table.auxiliar_requerida,
                    "capacidad_ampliada": table.capacidad_ampliada,
                    "prioridad": table.prioridad,
                    "notas": table.notas,
                    "status": table.status.value,
                }

            # Cargar en el engine
            self.engine.load_tables_from_dict(list(tables_dict.values()))

            # Cachear
            self.cache.set(cache_key, tables_dict, ttl=self.CACHE_TTL_TABLES)
            self._tables_loaded = True

            logger.info(f"Loaded {len(tables)} tables from Airtable")
            return tables_dict

        except Exception as e:
            logger.error(f"Error loading tables from Airtable: {e}")
            return {}

    async def get_available_tables(
        self, fecha: date, turno: str, zona: Optional[ZonePreference] = None
    ) -> List[str]:
        """
        Obtiene lista de mesas disponibles para una fecha y turno.

        USA REDIS para estado en tiempo real.
        """
        cache_key = f"tetris:availability:{fecha.isoformat()}:{turno}"

        # Intentar cache
        cached = self.cache.get(cache_key)
        if cached:
            available = cached.get("available", [])

            # Filtrar por zona si se especifica
            if zona and zona != ZonePreference.NO_PREFERENCE:
                tables = await self._load_tables_from_airtable()
                available = [
                    t for t in available if tables.get(t, {}).get("zona") == zona.value
                ]

            return available

        # Si no hay cache, asumir todas disponibles
        # (en producción, esto consultaría las reservas existentes)
        tables = await self._load_tables_from_airtable()

        # Filtrar por estado
        available = [
            tid for tid, t in tables.items() if t.get("status") in ["Libre", None]
        ]

        return available

    async def assign_table(
        self,
        party_size: int,
        fecha: date,
        turno: str,
        zone_preference: ZonePreference = ZonePreference.NO_PREFERENCE,
        has_pets: bool = False,
        terrace_closed: bool = False,
    ) -> AssignmentResult:
        """
        Asigna la mejor mesa disponible.

        FLUJO:
        1. Cargar mesas desde Airtable (con cache)
        2. Verificar disponibilidad en Redis
        3. Ejecutar algoritmo de asignación
        4. Crear hold en Redis
        5. Actualizar learning service
        """
        # 1. Asegurar que las mesas están cargadas
        await self._load_tables_from_airtable()

        # 2. Obtener mesas disponibles
        available_tables = await self.get_available_tables(
            fecha=fecha, turno=turno, zona=zone_preference
        )

        # 3. Ejecutar algoritmo
        result = await self.engine.assign_table(
            party_size=party_size,
            fecha=fecha,
            turno=turno,
            zone_preference=zone_preference,
            has_pets=has_pets,
            terrace_closed=terrace_closed,
            available_tables=available_tables,
        )

        # 4. Si exitoso, marcar mesa como reservada en cache
        if result.success and result.hold_id:
            await self._mark_table_as_held(
                table_ids=result.tables,
                fecha=fecha,
                turno=turno,
                hold_id=result.hold_id,
            )

        return result

    async def _mark_table_as_held(
        self, table_ids: List[str], fecha: date, turno: str, hold_id: str
    ):
        """Marca mesas como reservadas temporalmente."""
        if not self.cache.enabled:
            return

        # Invalidar cache de disponibilidad
        cache_key = f"tetris:availability:{fecha.isoformat()}:{turno}"
        self.cache.delete(cache_key)

        logger.info(f"Marked tables {table_ids} as held (hold: {hold_id})")

    async def confirm_reservation(
        self, hold_id: str, fecha: date, turno: str, table_ids: List[str]
    ) -> bool:
        """
        Confirma una reserva y actualiza el estado de las mesas.
        """
        # Confirmar hold en engine
        success = await self.engine.confirm_hold(hold_id, fecha, turno)

        if success:
            # Actualizar estado en Airtable
            for table_id in table_ids:
                try:
                    await self.table_repo.update_status(
                        table_id=table_id, new_status=TableStatus.RESERVED
                    )
                except Exception as e:
                    logger.error(f"Error updating table {table_id} status: {e}")

            # Invalidar caches
            self.cache.delete(f"tetris:availability:{fecha.isoformat()}:{turno}")
            self.cache.delete("tetris:tables:all")

            logger.info(f"Confirmed reservation for tables {table_ids}")

        return success

    async def release_reservation(
        self, hold_id: str, fecha: date, turno: str, table_ids: List[str]
    ) -> bool:
        """
        Libera una reserva y marca las mesas como disponibles.
        """
        # Liberar hold
        success = await self.engine.release_hold(hold_id, fecha, turno)

        if success:
            # Actualizar estado en Airtable
            for table_id in table_ids:
                try:
                    await self.table_repo.update_status(
                        table_id=table_id, new_status=TableStatus.AVAILABLE
                    )
                except Exception as e:
                    logger.error(f"Error releasing table {table_id}: {e}")

            # Invalidar caches
            self.cache.delete(f"tetris:availability:{fecha.isoformat()}:{turno}")

            logger.info(f"Released reservation for tables {table_ids}")

        return success

    async def record_outcome(
        self,
        reservation_id: str,
        party_size: int,
        weekday: int,
        time_slot: str,
        zone: str,
        actual_duration_minutes: int,
        was_no_show: bool = False,
        channel: str = "VAPI",
    ):
        """
        Registra el resultado de una reserva para aprendizaje.

        ACTUALIZA:
        - Expected dining duration
        - No-show rate
        """
        # Actualizar duración
        self.learning.update_from_outcome(
            party_size=party_size,
            weekday=weekday,
            time_slot=time_slot,
            zone=zone,
            actual_duration_minutes=actual_duration_minutes,
        )

        # Actualizar no-show rate
        if was_no_show:
            self.learning.update_no_show_rate(
                channel=channel,
                lead_time_days=1,  # Default
                weekday=weekday,
                was_no_show=True,
            )

        logger.debug(f"Recorded outcome for reservation {reservation_id}")

    def get_expected_duration(
        self, party_size: int, weekday: int, time_slot: str, zone: str
    ) -> int:
        """Obtiene duración esperada basada en datos históricos."""
        return self.learning.get_expected_duration(
            party_size=party_size, weekday=weekday, time_slot=time_slot, zone=zone
        )


# Singleton
_tetris_service: Optional[TableTetrisService] = None


def get_tetris_service() -> TableTetrisService:
    """Obtiene la instancia singleton del servicio."""
    global _tetris_service
    if _tetris_service is None:
        _tetris_service = TableTetrisService()
    return _tetris_service
