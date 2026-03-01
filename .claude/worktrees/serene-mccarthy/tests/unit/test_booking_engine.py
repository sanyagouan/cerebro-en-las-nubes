import pytest
from datetime import datetime
from unittest.mock import MagicMock
from src.core.logic.booking_engine import BookingEngine
from src.core.entities.booking import Booking, BookingStatus
from src.core.entities.table import Table, TableStatus

@pytest.fixture
def mock_repository():
    """Crea un repositorio falso para testing"""
    repo = MagicMock()
    
    # Mesas de prueba (Simula tablas reales de Airtable)
    repo.get_all_tables.return_value = [
        Table(id="t1", name="T1", capacity_min=2, capacity_max=4, zone="Interior", status=TableStatus.AVAILABLE),
        Table(id="t2", name="T2", capacity_min=2, capacity_max=6, zone="Interior", status=TableStatus.AVAILABLE), # Changed min to 2
        Table(id="t3", name="T3", capacity_min=6, capacity_max=10, zone="Terraza", status=TableStatus.AVAILABLE),
    ]
    
    # Sin reservas existentes por defecto
    repo.get_bookings_for_date.return_value = []
    
    return repo


class TestBookingEngine:
    def test_find_best_table_for_2_pax(self, mock_repository):
        """Para 2 personas, debe asignar T1 (capacidad 2-4)"""
        engine = BookingEngine(mock_repository)
        
        request = Booking(
            client_name="Test User",
            client_phone="+34600000001",
            date_time=datetime(2026, 1, 25, 14, 0),
            pax=2
        )
        
        result = engine.find_best_table(request)
        
        assert result is not None
        assert result.name == "T1"  # Mesa más ajustada para 2 pax

    def test_find_best_table_for_5_pax(self, mock_repository):
        """Para 5 personas, debe asignar T2 (capacidad 4-6)"""
        engine = BookingEngine(mock_repository)
        
        request = Booking(
            client_name="Test User",
            client_phone="+34600000002",
            date_time=datetime(2026, 1, 25, 14, 0),
            pax=5
        )
        
        result = engine.find_best_table(request)
        
        assert result is not None
        assert result.name == "T2"

    def test_find_best_table_for_8_pax(self, mock_repository):
        """Para 8 personas, debe asignar T3 (capacidad 6-10)"""
        engine = BookingEngine(mock_repository)
        
        request = Booking(
            client_name="Test User",
            client_phone="+34600000003",
            date_time=datetime(2026, 1, 25, 14, 0),
            pax=8
        )
        
        result = engine.find_best_table(request)
        
        assert result is not None
        assert result.name == "T3"

    def test_no_table_for_excessive_pax(self, mock_repository):
        """Para 15 personas, no debería encontrar mesa"""
        engine = BookingEngine(mock_repository)
        
        request = Booking(
            client_name="Test User",
            client_phone="+34600000004",
            date_time=datetime(2026, 1, 25, 14, 0),
            pax=15
        )
        
        result = engine.find_best_table(request)
        
        assert result is None

    def test_table_blocked_by_overlap(self, mock_repository):
        """Si T1 está ocupada a las 14:00, debe elegir otra"""
        # Simular reserva existente en T1
        mock_repository.get_bookings_for_date.return_value = [
            Booking(
                id="existing",
                client_name="Existing Client",
                client_phone="+34600000000",
                date_time=datetime(2026, 1, 25, 14, 30),
                pax=2,
                status=BookingStatus.CONFIRMED,
                assigned_table_id="t1"
            )
        ]
        
        engine = BookingEngine(mock_repository)
        
        request = Booking(
            client_name="New Client",
            client_phone="+34600000005",
            date_time=datetime(2026, 1, 25, 14, 0),
            pax=2
        )
        
        result = engine.find_best_table(request)
        
        # Debería elegir T2 porque T1 tiene conflicto de tiempo
        assert result is not None
        assert result.name == "T2"
