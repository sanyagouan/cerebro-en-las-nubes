from datetime import datetime, timedelta, date, time as time_type
from typing import List, Optional
import logging
from src.core.entities.booking import Booking, BookingStatus
from src.core.entities.table import Table, TableStatus
from src.core.ports.booking_repository import BookingRepository

logger = logging.getLogger(__name__)


class BookingEngine:
    def __init__(self, repository: BookingRepository):
        self.repo = repository

    def find_best_table(self, booking_request: Booking) -> Optional[Table]:
        """
        Algoritmo 'Tetris': Encuentra la mejor mesa para una reserva.
        Reglas:
        1. Capacidad suficiente (pax <= capacidad_max).
        2. No desperdiciar espacio (pax >= capacidad_min).
        3. Mesa no ocupada en ese horario (check overlap).
        """
        all_tables = self.repo.get_all_tables()

        # Booking v2 uses fecha + hora, combine for datetime
        booking_datetime = booking_request.datetime_completo
        existing_bookings = self.repo.get_bookings_for_date(booking_request.fecha)

        logger.info(
            f"🔍 [DEBUG] Total mesas: {len(all_tables)}, Reservas existentes: {len(existing_bookings)}"
        )

        # 1. Filtrar por Capacidad (usando nombres correctos de entidad Table)
        candidates = [
            t
            for t in all_tables
            if t.capacidad_min <= booking_request.pax <= t.capacidad_max
        ]
        logger.info(
            f"🔍 [DEBUG] Candidatos por capacidad para {booking_request.pax} pax: {len(candidates)}"
        )

        # Log de cada candidato
        for t in candidates:
            logger.info(
                f"   - {t.nombre}: min={t.capacidad_min}, max={t.capacidad_max}, status={t.status}"
            )

        # 2. Filtrar por Disponibilidad (Time Overlap)
        available_candidates = []
        for table in candidates:
            if self.is_table_free(table.id, booking_datetime, existing_bookings):
                available_candidates.append(table)
                logger.info(f"   ✅ {table.nombre} disponible")
            else:
                logger.info(f"   ❌ {table.nombre} ocupada")

        logger.info(f"🔍 [DEBUG] Mesas disponibles: {len(available_candidates)}")

        # 3. Ordenar por "Mejor Ajuste" (Menor desperdicio de sillas)
        # Priorizamos las que 'clavan' la capacidad (capacidad_max - pax es menor)
        # Usamos prioridad como desempate (menor prioridad = mejor)
        available_candidates.sort(
            key=lambda t: (t.capacidad_max - booking_request.pax, t.prioridad)
        )

        if available_candidates:
            best = available_candidates[0]
            logger.info(
                f"✅ [DEBUG] Mejor mesa: {best.nombre} (capacidad {best.capacidad_max})"
            )
            return best

        logger.info(f"❌ [DEBUG] No hay mesas disponibles")
        return None

    def is_table_free(
        self, table_id: str, time_check: datetime, bookings: List[Booking]
    ) -> bool:
        """Comprueba si una mesa está libre +- 2 horas de la hora deseada"""
        DURATION_HOURS = 2

        for b in bookings:
            # Booking v2 uses mesa_asignada instead of assigned_table_id
            if b.mesa_asignada != table_id:
                continue
            # Booking v2 uses estado instead of status
            if b.estado == BookingStatus.CANCELLED:
                continue

            # Overlap Logic
            # B_start < new_end AND B_end > new_start
            # Booking v2 uses datetime_completo property to combine fecha + hora
            b_start = b.datetime_completo
            b_end = b.datetime_completo + timedelta(hours=DURATION_HOURS)

            new_start = time_check
            new_end = time_check + timedelta(hours=DURATION_HOURS)

            if b_start < new_end and b_end > new_start:
                return False  # Conflicto detectado

        return True
