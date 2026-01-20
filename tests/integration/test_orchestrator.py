"""
Integration test for the Multi-Agent Orchestrator.
Tests the full pipeline: Router -> Logic -> Human.
"""
import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.application.orchestrator import Orchestrator

async def test_orchestrator():
    print("\n🧪 TEST: Multi-Agent Orchestrator\n")
    
    orchestrator = Orchestrator()
    
    # Test 1: Reservation Intent
    print("📞 Test 1: Mensaje de reserva...")
    result = await orchestrator.process_message(
        "Hola, quiero reservar mesa para 4 personas",
        metadata={
            "date": "2026-01-25",
            "time": "14:00",
            "pax": 4,
            "client_name": "Test User",
            "client_phone": "+34600000000"
        }
    )
    print(f"   Intent: {result.get('intent')}")
    print(f"   Booking: {result.get('booking_result', {}).get('available')}")
    print(f"   Response: {result.get('response', '')[:100]}...")
    
    # Test 2: FAQ Intent
    print("\n❓ Test 2: Pregunta FAQ...")
    result2 = await orchestrator.process_message("¿Cuál es vuestro horario?")
    print(f"   Intent: {result2.get('intent')}")
    print(f"   Response: {result2.get('response', '')[:100]}...")
    
    # Test 3: Human Handoff
    print("\n👤 Test 3: Pedir hablar con humano...")
    result3 = await orchestrator.process_message("Quiero hablar con una persona")
    print(f"   Intent: {result3.get('intent')}")
    print(f"   Handoff: {result3.get('needs_human_handoff', False)}")
    
    print("\n✅ Tests completados.")

if __name__ == "__main__":
    asyncio.run(test_orchestrator())
