#!/usr/bin/env python3
"""
Integration Tests - Automated API Testing
Tests backend API endpoints without requiring browser/frontend
"""
import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✅ PASSED{Colors.RESET}" if passed else f"{Colors.RED}❌ FAILED{Colors.RESET}"
    print(f"\n{status} - {name}")
    if details:
        print(f"  {details}")

def test_backend_health():
    """Test 1: Backend Health Check"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        passed = response.status_code == 200
        details = f"Status: {response.status_code}, Response: {response.json()}"
        print_test("Backend Health Check", passed, details)
        return passed
    except Exception as e:
        print_test("Backend Health Check", False, f"Error: {str(e)}")
        return False

def test_auth_login():
    """Test 2: Authentication - Login"""
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=5
        )
        passed = response.status_code == 200
        data = response.json() if passed else {}
        token = data.get("access_token", "")
        
        details = f"Status: {response.status_code}"
        if passed and token:
            details += f", Token received: {token[:20]}..."
        elif passed:
            details += ", WARNING: No token in response"
        
        print_test("Authentication - Login", passed, details)
        return passed, token if passed else None
    except Exception as e:
        print_test("Authentication - Login", False, f"Error: {str(e)}")
        return False, None

def test_list_reservations(token):
    """Test 3: List Reservations"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/reservas", headers=headers, timeout=5)
        passed = response.status_code == 200
        
        if passed:
            data = response.json()
            count = len(data) if isinstance(data, list) else "N/A"
            details = f"Status: {response.status_code}, Reservations: {count}"
        else:
            details = f"Status: {response.status_code}, Error: {response.text[:100]}"
        
        print_test("List Reservations", passed, details)
        return passed, data if passed else None
    except Exception as e:
        print_test("List Reservations", False, f"Error: {str(e)}")
        return False, None

def test_create_reservation(token):
    """Test 4: Create Reservation"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        payload = {
            "nombre": "Test Integration",
            "telefono": "612345678",
            "fecha": tomorrow,
            "hora": "20:00",
            "personas": 4,
            "zona": "interior",
            "solicitudes_especiales": "Test automatizado"
        }
        
        response = requests.post(
            f"{API_BASE}/reservas",
            json=payload,
            headers=headers,
            timeout=5
        )
        
        passed = response.status_code in [200, 201]
        
        if passed:
            data = response.json()
            reservation_id = data.get("id", "N/A")
            details = f"Status: {response.status_code}, Created ID: {reservation_id}"
        else:
            details = f"Status: {response.status_code}, Error: {response.text[:200]}"
        
        print_test("Create Reservation", passed, details)
        return passed, data.get("id") if passed else None
    except Exception as e:
        print_test("Create Reservation", False, f"Error: {str(e)}")
        return False, None

def test_update_reservation(token, reservation_id):
    """Test 5: Update Reservation"""
    if not reservation_id:
        print_test("Update Reservation", False, "No reservation ID (skipped)")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"personas": 6}
        
        response = requests.put(
            f"{API_BASE}/reservas/{reservation_id}",
            json=payload,
            headers=headers,
            timeout=5
        )
        
        passed = response.status_code == 200
        details = f"Status: {response.status_code}, Updated personas to 6"
        if not passed:
            details = f"Status: {response.status_code}, Error: {response.text[:100]}"
        
        print_test("Update Reservation", passed, details)
        return passed
    except Exception as e:
        print_test("Update Reservation", False, f"Error: {str(e)}")
        return False

def test_cancel_reservation(token, reservation_id):
    """Test 6: Cancel Reservation"""
    if not reservation_id:
        print_test("Cancel Reservation", False, "No reservation ID (skipped)")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{API_BASE}/reservas/{reservation_id}/cancel",
            headers=headers,
            timeout=5
        )
        
        passed = response.status_code == 200
        details = f"Status: {response.status_code}"
        if not passed:
            details = f"Status: {response.status_code}, Error: {response.text[:100]}"
        
        print_test("Cancel Reservation", passed, details)
        return passed
    except Exception as e:
        print_test("Cancel Reservation", False, f"Error: {str(e)}")
        return False

def test_list_tables(token):
    """Test 7: List Tables"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/mesas", headers=headers, timeout=5)
        passed = response.status_code == 200
        
        if passed:
            data = response.json()
            count = len(data) if isinstance(data, list) else "N/A"
            details = f"Status: {response.status_code}, Tables: {count}"
        else:
            details = f"Status: {response.status_code}, Error: {response.text[:100]}"
        
        print_test("List Tables", passed, details)
        return passed
    except Exception as e:
        print_test("List Tables", False, f"Error: {str(e)}")
        return False

def test_dashboard_stats(token):
    """Test 8: Dashboard Stats"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/stats", headers=headers, timeout=5)
        passed = response.status_code == 200
        
        if passed:
            data = response.json()
            details = f"Status: {response.status_code}, Stats keys: {list(data.keys())}"
        else:
            details = f"Status: {response.status_code}, Error: {response.text[:100]}"
        
        print_test("Dashboard Stats", passed, details)
        return passed
    except Exception as e:
        print_test("Dashboard Stats", False, f"Error: {str(e)}")
        return False

def run_all_tests():
    """Run all integration tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}Integration Tests - Automated API Testing{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"Backend: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test 1: Health Check
    results.append(("Backend Health", test_backend_health()))
    
    # Test 2: Login
    login_passed, token = test_auth_login()
    results.append(("Authentication", login_passed))
    
    if not token:
        print(f"\n{Colors.RED}⚠️  Cannot continue without authentication token{Colors.RESET}")
        print_summary(results)
        return
    
    # Test 3: List Reservations
    list_passed, reservations = test_list_reservations(token)
    results.append(("List Reservations", list_passed))
    
    # Test 4: Create Reservation
    create_passed, new_id = test_create_reservation(token)
    results.append(("Create Reservation", create_passed))
    
    # Test 5: Update Reservation
    results.append(("Update Reservation", test_update_reservation(token, new_id)))
    
    # Test 6: Cancel Reservation
    results.append(("Cancel Reservation", test_cancel_reservation(token, new_id)))
    
    # Test 7: List Tables
    results.append(("List Tables", test_list_tables(token)))
    
    # Test 8: Dashboard Stats
    results.append(("Dashboard Stats", test_dashboard_stats(token)))
    
    # Summary
    print_summary(results)

def print_summary(results):
    """Print test summary"""
    total = len(results)
    passed = sum(1 for _, result in results if result)
    failed = total - passed
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}Test Summary{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"Total: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if failed > 0:
        print(f"\n{Colors.RED}Failed Tests:{Colors.RESET}")
        for name, result in results:
            if not result:
                print(f"  - {name}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    if passed >= total * 0.85:
        print(f"{Colors.GREEN}✅ Integration tests PASSED (≥85% success){Colors.RESET}")
    else:
        print(f"{Colors.RED}❌ Integration tests FAILED (<85% success){Colors.RESET}")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {str(e)}{Colors.RESET}")
