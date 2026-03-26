"""
Test de validacion de horarios para martes y miercoles.
Verifica que los dias sin servicio de cena funcionen correctamente.

Escenarios:
1. Martes 14:00 - Debe ser VALIDO (Comida)
2. Martes 21:00 - Debe ser INVALIDO (Cena cerrada)
3. Miercoles 15:00 - Debe ser VALIDO (Comida)
4. Miercoles 22:00 - Debe ser INVALIDO (Cena cerrada)
"""

import asyncio
import json
import sys
from datetime import date, datetime
from unittest.mock import AsyncMock, patch, MagicMock

# Configurar encoding para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Importar Request de FastAPI para el mock
from fastapi import Request

# Importar las funciones a probar
from src.api.vapi_tools_router import tool_check_availability, tool_create_reservation
from src.core.config.restaurant import BUSINESS_HOURS


def create_mock_request(tool_call_id: str, arguments: dict) -> AsyncMock:
    """
    Crea un mock de Request con el formato que espera parse_vapi_request.
    
    El router espera el formato VAPI:
    {
        "message": {
            "toolCalls": [{
                "id": "call_xxx",
                "function": {
                    "arguments": {...}  # dict o string JSON
                }
            }]
        }
    }
    """
    mock_request = AsyncMock(spec=Request)
    
    # Crear el payload en formato VAPI
    payload = {
        "message": {
            "toolCalls": [{
                "id": tool_call_id,
                "function": {
                    "arguments": arguments  # dict directo
                }
            }]
        }
    }
    
    # Configurar el metodo json() para retornar el payload
    mock_request.json = AsyncMock(return_value=payload)
    
    return mock_request


def print_header(text: str):
    """Imprime un encabezado con formato."""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)


def print_result(test_name: str, expected: str, actual: str, passed: bool):
    """Imprime el resultado de un test."""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"\n{status} {test_name}")
    print(f"  Esperado: {expected}")
    print(f"  Obtenido: {actual[:200]}..." if len(actual) > 200 else f"  Obtenido: {actual}")


async def test_martes_comida_valido():
    """
    TEST 1: Martes 14:00 (Comida)
    Debe ser VALIDO - El martes abre para comida
    """
    print_header("TEST 1: Martes 14:00 (Comida)")
    
    # Crear mock request con formato VAPI correcto
    mock_request = create_mock_request(
        tool_call_id="test_call_1",
        arguments={
            "date": "2026-03-24",  # Martes
            "time": "14:00",
            "pax": 4
        }
    )
    
    # Ejecutar
    result = await tool_check_availability(mock_request)
    
    # Verificar resultado
    result_text = result["results"][0]["result"]
    
    # Debe indicar que hay sitio disponible
    is_valid = "sitio libre" in result_text.lower() or "queda sitio" in result_text.lower()
    
    print_result(
        "Martes 14:00 - Comida",
        "Debe indicar disponibilidad",
        result_text,
        is_valid
    )
    
    return is_valid


async def test_martes_cena_invalido():
    """
    TEST 2: Martes 21:00 (Cena)
    Debe ser INVALIDO - El martes NO tiene servicio de cena
    """
    print_header("TEST 2: Martes 21:00 (Cena)")
    
    mock_request = create_mock_request(
        tool_call_id="test_call_2",
        arguments={
            "date": "2026-03-24",  # Martes
            "time": "21:00",
            "pax": 4
        }
    )
    
    result = await tool_check_availability(mock_request)
    result_text = result["results"][0]["result"]
    
    # Debe indicar que no abre para cenar los martes
    is_valid = "no abrimos para cenar" in result_text.lower() or "no hay servicio de cena" in result_text.lower()
    
    print_result(
        "Martes 21:00 - Cena",
        "Debe indicar que no abre para cenar los martes",
        result_text,
        is_valid
    )
    
    return is_valid


async def test_miercoles_comida_valido():
    """
    TEST 3: Miercoles 15:00 (Comida)
    Debe ser VALIDO - El miercoles abre para comida
    """
    print_header("TEST 3: Miercoles 15:00 (Comida)")
    
    mock_request = create_mock_request(
        tool_call_id="test_call_3",
        arguments={
            "date": "2026-03-25",  # Miercoles
            "time": "15:00",
            "pax": 4
        }
    )
    
    result = await tool_check_availability(mock_request)
    result_text = result["results"][0]["result"]
    
    # Debe indicar que hay sitio disponible
    is_valid = "sitio libre" in result_text.lower() or "queda sitio" in result_text.lower()
    
    print_result(
        "Miercoles 15:00 - Comida",
        "Debe indicar disponibilidad",
        result_text,
        is_valid
    )
    
    return is_valid


async def test_miercoles_cena_invalido():
    """
    TEST 4: Miercoles 22:00 (Cena)
    Debe ser INVALIDO - El miercoles NO tiene servicio de cena
    """
    print_header("TEST 4: Miercoles 22:00 (Cena)")
    
    mock_request = create_mock_request(
        tool_call_id="test_call_4",
        arguments={
            "date": "2026-03-25",  # Miercoles
            "time": "22:00",
            "pax": 4
        }
    )
    
    result = await tool_check_availability(mock_request)
    result_text = result["results"][0]["result"]
    
    # Debe indicar que no abre para cenar los miercoles
    is_valid = "no abrimos para cenar" in result_text.lower() or "no hay servicio de cena" in result_text.lower()
    
    print_result(
        "Miercoles 22:00 - Cena",
        "Debe indicar que no abre para cenar los miercoles",
        result_text,
        is_valid
    )
    
    return is_valid


def print_config():
    """Imprime la configuracion de horarios."""
    print_header("CONFIGURACION DE HORARIOS")
    
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    days_es = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
    
    for day, day_es in zip(days, days_es):
        hours = BUSINESS_HOURS.get(day) or {}
        lunch = hours.get("lunch")
        dinner = hours.get("dinner")
        
        print(f"\n{day_es.upper()}:")
        if lunch:
            print(f"  Comida: {lunch.get('open', 'N/A')} - {lunch.get('close', 'N/A')}")
        else:
            print("  Comida: CERRADO")
        
        if dinner:
            print(f"  Cena: {dinner.get('open', 'N/A')} - {dinner.get('close', 'N/A')}")
        else:
            print("  Cena: CERRADO")


async def run_all_tests():
    """Ejecuta todos los tests y reporta resultados."""
    print_header("INICIANDO TESTS DE VALIDACION DE HORARIOS")
    print("Para martes y miercoles (dias sin servicio de cena)")
    
    # Mostrar configuracion
    print_config()
    
    # Ejecutar tests
    results = []
    
    try:
        results.append(("Martes 14:00 (Comida)", await test_martes_comida_valido()))
    except Exception as e:
        print(f"\n[ERROR] Test 1 fallo con excepcion: {e}")
        results.append(("Martes 14:00 (Comida)", False))
    
    try:
        results.append(("Martes 21:00 (Cena)", await test_martes_cena_invalido()))
    except Exception as e:
        print(f"\n[ERROR] Test 2 fallo con excepcion: {e}")
        results.append(("Martes 21:00 (Cena)", False))
    
    try:
        results.append(("Miercoles 15:00 (Comida)", await test_miercoles_comida_valido()))
    except Exception as e:
        print(f"\n[ERROR] Test 3 fallo con excepcion: {e}")
        results.append(("Miercoles 15:00 (Comida)", False))
    
    try:
        results.append(("Miercoles 22:00 (Cena)", await test_miercoles_cena_invalido()))
    except Exception as e:
        print(f"\n[ERROR] Test 4 fallo con excepcion: {e}")
        results.append(("Miercoles 22:00 (Cena)", False))
    
    # Resumen final
    print_header("RESUMEN DE RESULTADOS")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\nTotal: {passed}/{total} tests pasados")
    
    if passed == total:
        print("\n[EXITO] Todos los tests pasaron correctamente!")
        return True
    else:
        print(f"\n[ERROR] {total - passed} tests fallaron")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
