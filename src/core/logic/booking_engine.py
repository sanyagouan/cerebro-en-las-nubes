from datetime import datetime, timedelta
from typing import List, Optional
from src.core.entities.booking import Booking, BookingStatus
from src.core.entities.table import Table, TableStatus
from src.core.ports.booking_repository import BookingRepository

class BookingEngine:
    def __init__(self, repository: BookingRepository):
        self.repo = repository

    def find_best_table(self, booking_request: Booking) -> Optional[Table]:
        """
        Algoritmo 'Tetris': Encuentra la mejor mesa para una reserva.
        Reglas:
        1. Capacidad suficiente (pax <= capacity_max).
        2. No desperdiciar espacio (pax >= capacity_min).
        3. Mesa no ocupada en ese horario (check overlap).
        """
        all_tables = self.repo.get_all_tables()
        existing_bookings = self.repo.get_bookings_for_date(booking_request.date_time)
        
        # 1. Filtrar por Capacidad
        candidates = [
            t for t in all_tables 
            if t.capacity_min <= booking_request.pax <= t.capacity_max
        ]
        
        # 2. Filtrar por Disponibilidad (Time Overlap)
        available_candidates = []
        for table in candidates:
            if self.is_table_free(table.id, booking_request.date_time, existing_bookings):
                available_candidates.append(table)
        
        # 3. Ordenar por "Mejor Ajuste" (Menor desperdicio de sillas)
        # Priorizamos las que 'clavan' la capacidad (capacity_max - pax es menor)
        available_candidates.sort(key=lambda t: (t.capacity_max - booking_request.pax, t.priority_score))
        
        if available_candidates:
            return available_candidates[0]
        return None

    def is_table_free(self, table_id: str, time_check: datetime, bookings: List[Booking]) -> bool:
        """Comprueba si una mesa está libre +- 2 horas de la hora deseada"""
        DURATION_HOURS = 2
        
        for b in bookings:
            if b.assigned_table_id != table_id:
                continue
            if b.status == BookingStatus.CANCELLED:
                continue
                
            # Overlap Logic
            # B_start < new_end AND B_end > new_start
            b_start = b.date_time
            b_end = b.date_time + timedelta(hours=DURATION_HOURS)
            
            new_start = time_check
            new_end = time_check + timedelta(hours=DURATION_HOURS)
            
            if b_start < new_end and b_end > new_start:
                return False # Conflicto detectado
                
        return True
