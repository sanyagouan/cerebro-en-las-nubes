"""Reservation model - alias to Booking for backward compatibility."""
from src.core.entities.booking import Booking as Reservation

__all__ = ["Reservation"]
