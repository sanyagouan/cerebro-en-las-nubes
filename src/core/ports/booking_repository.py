from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from src.core.entities.booking import Booking
from src.core.entities.table import Table

class BookingRepository(ABC):
    @abstractmethod
    def get_bookings_for_date(self, date: datetime) -> List[Booking]:
        pass

    @abstractmethod
    def create_booking(self, booking: Booking) -> Booking:
        pass
    
    @abstractmethod
    def get_all_tables(self) -> List[Table]:
        pass
