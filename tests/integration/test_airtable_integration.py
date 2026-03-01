"""
Quick integration test to verify Airtable+BookingEngine works end-to-end.
Run this ONLY when you expect real Airtable to be available.
"""
import os
import sys
from datetime import datetime

# Ensure src is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.infrastructure.repositories.booking_repo import AirtableBookingRepository
from src.core.logic.booking_engine import BookingEngine
from src.core.entities.booking import Booking

def test_airtable_connection():
    print("\n🔗 TEST: Conectando con Airtable real...")
    repo = AirtableBookingRepository()
    
    # 1. Fetch Tables
    print("   Obteniendo mesas...")
    tables = repo.get_all_tables()
    
    if tables:
        print(f"   ✅ {len(tables)} mesas obtenidas:")
        for t in tables[:3]:
            print(f"      - {t.name} (Capacidad {t.capacity_min}-{t.capacity_max})")
    else:
        print("   ❌ No se obtuvieron mesas")
        return False
        
    # 2. Test BookingEngine with real data
    print("\n🧠 TEST: Probando Booking Engine con datos reales...")
    engine = BookingEngine(repo)
    
    test_booking = Booking(
        client_name="Test Integration",
        client_phone="+34600000000",
        date_time=datetime.now().replace(hour=14, minute=0),
        pax=4
    )
    
    result = engine.find_best_table(test_booking)
    
    if result:
        print(f"   ✅ Mesa asignada: {result.name} (perfecto para 4 pax)")
    else:
        print("   ⚠️ No se encontró mesa disponible (puede ser normal si está lleno)")
        
    return True

if __name__ == "__main__":
    success = test_airtable_connection()
    print(f"\n{'✅ Integración OK' if success else '❌ Fallo de integración'}\n")
