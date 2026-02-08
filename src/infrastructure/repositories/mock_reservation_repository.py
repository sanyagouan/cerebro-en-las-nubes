from typing import Optional, List
from datetime import date, time
from src.domain.models.reservation import Reservation
import uuid

class MockReservationRepository:
    def __init__(self):
        self.reservations = []

    def check_availability(self, fecha: date, hora: time, personas: int) -> bool:
        # Mock logic: Always yes for now unless overridden
        return True

    def create_reservation(self, reservation: Reservation) -> str:
        reservation.id = str(uuid.uuid4())
        self.reservations.append(reservation)
        return reservation.id
