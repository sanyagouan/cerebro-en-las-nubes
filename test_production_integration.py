#!/usr/bin/env python3
"""
Integration Tests - Production Environment
Ejecuta tests contra el backend desplegado en Coolify
Backend URL: https://go84sgscs4ckcs08wog84o0o.app.generaia.site
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import sys

# Configuration
BACKEND_URL = "https://go84sgscs4ckcs08wog84o0o.app.generaia.site"
FRONTEND_URL = "https://y08s40o0sgco88g0ook4gk48.app.generaia.site"

# Test credentials (from frontend demo users)
TEST_USERS = {
    "waiter": {"username": "waiter", "password": "waiter123"},
    "manager": {"username": "manager", "password": "manager123"},
    "admin": {"username": "admin", "password": "admin123"}
}

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_test(name: str):
    """Print test header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}▶ {name}{Colors.END}")

def print_success(message: str):
    """Print success message"""
    print(f"  {Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message: str):
    """Print error message"""
    print(f"  {Colors.RED}✗ {message}{Colors.END}")

def print_warning(message: str):
    """Print warning message"""
    print(f"  {Colors.YELLOW}⚠ {message}{Colors.END}")

def print_info(message: str):
    """Print info message"""
    print(f"  {Colors.BLUE}ℹ {message}{Colors.END}")


# ==================== TEST 1: Backend Health ====================
def test_backend_health() -> bool:
    """Test 1: Verificar que el backend está accesible"""
    print_test("Test 1: Backend Health Check")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend healthy: {data}")
            return True
        else:
            print_error(f"Backend unhealthy: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Connection failed: {e}")
        return False


# ==================== TEST 2: Authentication ====================
def test_auth_login() -> Optional[str]:
    """Test 2: Autenticación con usuario demo"""
    print_test("Test 2: Authentication (Login)")
    
    try:
        credentials = TEST_USERS["waiter"]
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json=credentials,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                print_success(f"Login successful. Token: {token[:20]}...")
                print_info(f"User role: {data.get('role', 'unknown')}")
                return token
            else:
                print_error("No token in response")
                return None
        else:
            print_error(f"Login failed: {response.status_code}")
            print_info(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return None


# ==================== TEST 3: List Reservations ====================
def test_list_reservations(token: str) -> bool:
    """Test 3: Listar reservas"""
    print_test("Test 3: List Reservations")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BACKEND_URL}/api/mobile/reservations",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get("count", 0)
            print_success(f"Retrieved {count} reservations")
            
            # Show first reservation as sample
            if data and isinstance(data, list) and len(data) > 0:
                print_info(f"Sample: {data[0].get('customer_name', 'N/A')} - {data[0].get('date', 'N/A')}")
            
            return True
        elif response.status_code == 404:
            print_warning("Endpoint not implemented yet (404)")
            return False
        else:
            print_error(f"Failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False


# ==================== TEST 4: Create Reservation ====================
def test_create_reservation(token: str) -> Optional[str]:
    """Test 4: Crear nueva reserva"""
    print_test("Test 4: Create Reservation")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create test reservation for tomorrow
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        new_reservation = {
            "customer_name": "Test Integration",
            "customer_phone": "+1234567890",
            "date": tomorrow,
            "time": "19:00",
            "party_size": 4,
            "zone": "Interior",
            "special_requests": "Integration test - can be deleted"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/mobile/reservations",
            headers=headers,
            json=new_reservation,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            reservation_id = data.get("id") or data.get("reservation_id")
            print_success(f"Reservation created: ID {reservation_id}")
            print_info(f"Customer: {new_reservation['customer_name']}")
            print_info(f"Date/Time: {tomorrow} at {new_reservation['time']}")
            return reservation_id
        elif response.status_code == 404:
            print_warning("Endpoint not implemented yet (404)")
            return None
        else:
            print_error(f"Failed: {response.status_code}")
            print_info(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return None


# ==================== TEST 5: Update Reservation ====================
def test_update_reservation(token: str, reservation_id: str) -> bool:
    """Test 5: Actualizar reserva existente"""
    print_test("Test 5: Update Reservation")
    
    if not reservation_id:
        print_warning("Skipped: No reservation ID available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        updates = {
            "party_size": 6,
            "special_requests": "Updated during integration test"
        }
        
        response = requests.put(
            f"{BACKEND_URL}/api/mobile/reservations/{reservation_id}",
            headers=headers,
            json=updates,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Reservation updated: ID {reservation_id}")
            print_info(f"New party size: {updates['party_size']}")
            return True
        elif response.status_code == 404:
            print_warning("Endpoint not implemented yet (404)")
            return False
        else:
            print_error(f"Failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False


# ==================== TEST 6: Cancel Reservation ====================
def test_cancel_reservation(token: str, reservation_id: str) -> bool:
    """Test 6: Cancelar reserva"""
    print_test("Test 6: Cancel Reservation")
    
    if not reservation_id:
        print_warning("Skipped: No reservation ID available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.post(
            f"{BACKEND_URL}/api/mobile/reservations/{reservation_id}/cancel",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print_success(f"Reservation cancelled: ID {reservation_id}")
            return True
        elif response.status_code == 404:
            print_warning("Endpoint not implemented yet (404)")
            return False
        else:
            print_error(f"Failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False


# ==================== TEST 7: List Tables ====================
def test_list_tables(token: str) -> bool:
    """Test 7: Listar mesas"""
    print_test("Test 7: List Tables")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BACKEND_URL}/api/mobile/tables",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get("count", 0)
            print_success(f"Retrieved {count} tables")
            
            # Show first table as sample
            if data and isinstance(data, list) and len(data) > 0:
                table = data[0]
                print_info(f"Sample: Table {table.get('number', 'N/A')} - Capacity: {table.get('capacity', 'N/A')}")
            
            return True
        elif response.status_code == 404:
            print_warning("Endpoint not implemented yet (404)")
            return False
        else:
            print_error(f"Failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False


# ==================== TEST 8: Dashboard Stats ====================
def test_dashboard_stats(token: str) -> bool:
    """Test 8: Obtener estadísticas del dashboard"""
    print_test("Test 8: Dashboard Statistics")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BACKEND_URL}/api/dashboard/stats",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Dashboard stats retrieved")
            print_info(f"Today reservations: {data.get('today_reservations', 'N/A')}")
            print_info(f"Pending: {data.get('pending', 'N/A')}")
            print_info(f"Confirmed: {data.get('confirmed', 'N/A')}")
            return True
        elif response.status_code == 404:
            print_warning("Endpoint not implemented yet (404)")
            return False
        else:
            print_error(f"Failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False


# ==================== TEST 9: Frontend Accessibility ====================
def test_frontend_access() -> bool:
    """Test 9: Verificar que el frontend está accesible"""
    print_test("Test 9: Frontend Accessibility")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        
        if response.status_code == 200:
            print_success(f"Frontend accessible")
            print_info(f"Content length: {len(response.content)} bytes")
            
            # Check if it's actually HTML
            if "<!DOCTYPE html>" in response.text or "<html" in response.text:
                print_success("Valid HTML response")
                return True
            else:
                print_warning("Response is not HTML")
                return False
        else:
            print_error(f"Failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Connection failed: {e}")
        return False


# ==================== Main Test Runner ====================
def run_all_tests():
    """Execute all integration tests"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("INTEGRATION TESTS - PRODUCTION ENVIRONMENT")
    print(f"{'='*60}{Colors.END}\n")
    
    print(f"{Colors.BOLD}Configuration:{Colors.END}")
    print(f"  Backend:  {BACKEND_URL}")
    print(f"  Frontend: {FRONTEND_URL}")
    print(f"  Time:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test 1: Backend Health
    results['backend_health'] = test_backend_health()
    
    if not results['backend_health']:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Backend is not accessible. Stopping tests.{Colors.END}")
        return results
    
    # Test 2: Authentication
    token = test_auth_login()
    results['auth'] = token is not None
    
    if not token:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Authentication failed. Stopping tests.{Colors.END}")
        return results
    
    # Test 3-8: API Endpoints (require authentication)
    results['list_reservations'] = test_list_reservations(token)
    
    reservation_id = test_create_reservation(token)
    results['create_reservation'] = reservation_id is not None
    
    results['update_reservation'] = test_update_reservation(token, reservation_id)
    results['cancel_reservation'] = test_cancel_reservation(token, reservation_id)
    results['list_tables'] = test_list_tables(token)
    results['dashboard_stats'] = test_dashboard_stats(token)
    
    # Test 9: Frontend
    results['frontend_access'] = test_frontend_access()
    
    # Print Summary
    print_summary(results)
    
    return results


def print_summary(results: Dict[str, bool]):
    """Print test summary"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}{Colors.END}\n")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {test_name:25} {status}")
    
    print(f"\n{Colors.BOLD}Results:{Colors.END}")
    print(f"  Total:  {total}")
    print(f"  {Colors.GREEN}Passed: {passed}{Colors.END}")
    print(f"  {Colors.RED}Failed: {failed}{Colors.END}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"  {Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.END}\n")
    
    if success_rate == 100:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.END}\n")
    elif success_rate >= 70:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ PARTIAL SUCCESS{Colors.END}\n")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ TESTS FAILED{Colors.END}\n")


if __name__ == "__main__":
    try:
        results = run_all_tests()
        
        # Exit with appropriate code
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        if passed == total:
            sys.exit(0)  # Success
        elif passed >= total * 0.7:
            sys.exit(1)  # Partial success
        else:
            sys.exit(2)  # Failure
            
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.END}\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}{Colors.BOLD}Fatal error: {e}{Colors.END}\n")
        sys.exit(3)
