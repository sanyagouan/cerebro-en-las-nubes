import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Add src to path
sys.path.append(os.getcwd())

from src.core.entities.booking import Booking, BookingStatus
from src.infrastructure.repositories.booking_repo import AirtableBookingRepository

def test_repo():
    print("Initializing repo...")
    api_key = os.getenv("AIRTABLE_API_KEY")
    if not api_key:
        print("❌ API KEY NOT FOUND IN ENV")
        return

    repo = AirtableBookingRepository()
    
    # Create Booking Object
    test_booking = Booking(
        client_name="TEST_VERIFIED_NAME",
        client_phone="123456789",
        date_time=datetime.now() + timedelta(days=5),
        pax=4,
        source="Test Script",
        status=BookingStatus.CONFIRMED
    )
    
    print(f"Creating booking for {test_booking.client_name}...")
    try:
        saved_booking = repo.create_booking(test_booking)
        if saved_booking:
            print(f"✅ Booking Created with ID: {saved_booking.id}")
            
            # Verify fields were mapped back correctly
            if saved_booking.client_name == "TEST_VERIFIED_NAME":
                print("✅ Client Name OK")
            else:
                print(f"❌ Client Name Mismatch: {saved_booking.client_name}")
            return True
        else:
            print("❌ Booking Creation returned None")
            return False
    except Exception as e:
        print(f"❌ Error creating booking: {e}")
        return False

if __name__ == "__main__":
    test_repo()
