"""
Tests unitarios para las funciones de seguridad.

Cubre:
- Sanitización para Airtable (formula injection prevention)
- Validación de inputs (teléfonos, emails, fechas, etc.)
- Detección de patrones maliciosos

Ejecutar con:
    pytest tests/unit/test_security.py -v
"""

import pytest
from datetime import date, timedelta

# Import functions to test
from src.core.utils.sanitization import (
    sanitize_for_airtable,
    sanitize_phone_number,
    sanitize_email,
    sanitize_name,
    sanitize_notes,
    sanitize_reservation_data,
    sanitize_all_fields,
    validate_guest_count,
    validate_date_format,
    validate_time_format,
    is_potentially_malicious,
    DANGEROUS_PREFIXES,
    MALICIOUS_PATTERNS,
)


class TestSanitizeForAirtable:
    """Tests para la función sanitize_for_airtable."""
    
    def test_normal_text_unchanged(self):
        """Texto normal no debe modificarse."""
        assert sanitize_for_airtable("Hola mundo") == "Hola mundo"
        assert sanitize_for_airtable("Juan García") == "Juan García"
        assert sanitize_for_airtable("Mesa para 4") == "Mesa para 4"
    
    def test_formula_injection_equals(self):
        """Fórmulas con = deben neutralizarse."""
        assert sanitize_for_airtable("=SUM(1+1)").startswith("'")
        assert sanitize_for_airtable("=IMPORTXML()").startswith("'")
        assert sanitize_for_airtable("=CMD|calc").startswith("'")
    
    def test_formula_injection_plus(self):
        """Fórmulas con + deben neutralizarse."""
        assert sanitize_for_airtable("+SUM(1)").startswith("'")
    
    def test_formula_injection_minus(self):
        """Fórmulas con - deben neutralizarse."""
        assert sanitize_for_airtable("-1+1").startswith("'")
    
    def test_formula_injection_at(self):
        """Valores con @ deben neutralizarse."""
        assert sanitize_for_airtable("@SUM(1)").startswith("'")
    
    def test_dde_injection_pipe(self):
        """DDE con | debe escaparse."""
        result = sanitize_for_airtable("|calc.exe!A0")
        # Debe tener el pipe escapado o prefijo de apóstrofo
        assert "'" in result or "｜" in result
    
    def test_dde_injection_backslash(self):
        """DDE con \\ debe escaparse."""
        result = sanitize_for_airtable("\\cmd")
        # Debe tener el backslash escapado o prefijo de apóstrofo
        assert "'" in result or "＼" in result
    
    def test_pipe_in_middle_escaped(self):
        """Pipe en medio del texto debe escaparse."""
        result = sanitize_for_airtable("test|value|here")
        # El pipe debe ser reemplazado por fullwidth pipe
        assert "|" not in result
        assert "｜" in result
    
    def test_empty_string(self):
        """String vacío debe retornar vacío."""
        assert sanitize_for_airtable("") == ""
        assert sanitize_for_airtable("   ") == ""
    
    def test_none_value(self):
        """None debe retornar string vacío."""
        assert sanitize_for_airtable(None) == ""
    
    def test_non_string_value(self):
        """Valores no-string deben convertirse a string."""
        assert sanitize_for_airtable(123) == "123"
        assert sanitize_for_airtable(45.67) == "45.67"
    
    def test_max_length_text(self):
        """Texto largo debe truncarse."""
        long_text = "a" * 15000
        result = sanitize_for_airtable(long_text, 'text')
        assert len(result) <= 10000
    
    def test_max_length_name(self):
        """Nombre largo debe truncarse."""
        long_name = "a" * 500
        result = sanitize_for_airtable(long_name, 'name')
        assert len(result) <= 200
    
    def test_control_characters_removed(self):
        """Caracteres de control deben eliminarse."""
        # Null byte
        result = sanitize_for_airtable("test\x00value")
        assert "\x00" not in result
        
        # Bell character
        result = sanitize_for_airtable("test\x07value")
        assert "\x07" not in result


class TestSanitizePhoneNumber:
    """Tests para la función sanitize_phone_number."""
    
    def test_valid_spanish_phone(self):
        """Teléfonos españoles válidos."""
        result = sanitize_phone_number("+34600123456")
        # Debe tener apóstrofo por el +
        assert result.startswith("'") or result.startswith("+")
        assert "34600123456" in result
    
    def test_phone_without_country_code(self):
        """Teléfono sin código de país asume España."""
        result = sanitize_phone_number("600123456")
        assert "34" in result
    
    def test_phone_with_spaces(self):
        """Teléfono con espacios debe limpiarse."""
        result = sanitize_phone_number("+34 600 123 456")
        # No debe tener espacios en el número y debe contener los dígitos correctos
        clean_digits = "".join(c for c in result if c.isdigit())
        assert "600123456" in clean_digits
    
    def test_phone_with_dashes(self):
        """Teléfono con guiones debe limpiarse."""
        result = sanitize_phone_number("+34-600-123-456")
        assert "-" not in result
    
    def test_invalid_phone_too_short(self):
        """Teléfono muy corto debe fallar."""
        with pytest.raises(ValueError):
            sanitize_phone_number("123")
    
    def test_invalid_phone_letters(self):
        """Teléfono con letras debe fallar."""
        with pytest.raises(ValueError):
            sanitize_phone_number("abc123def")
    
    def test_empty_phone(self):
        """Teléfono vacío debe retornar vacío."""
        assert sanitize_phone_number("") == ""
        assert sanitize_phone_number(None) == ""


class TestSanitizeEmail:
    """Tests para la función sanitize_email."""
    
    def test_valid_email(self):
        """Emails válidos."""
        assert sanitize_email("test@example.com") == "test@example.com"
        assert sanitize_email("user.name@domain.es") == "user.name@domain.es"
    
    def test_email_uppercase_normalized(self):
        """Email en mayúsculas debe normalizarse."""
        assert sanitize_email("TEST@EXAMPLE.COM") == "test@example.com"
    
    def test_email_with_spaces(self):
        """Email con espacios debe limpiarse."""
        assert sanitize_email("  test@example.com  ") == "test@example.com"
    
    def test_invalid_email_no_at(self):
        """Email sin @ debe fallar."""
        with pytest.raises(ValueError):
            sanitize_email("invalid-email.com")
    
    def test_invalid_email_no_domain(self):
        """Email sin dominio debe fallar."""
        with pytest.raises(ValueError):
            sanitize_email("test@")
    
    def test_empty_email(self):
        """Email vacío debe retornar vacío."""
        assert sanitize_email("") == ""


class TestSanitizeName:
    """Tests para la función sanitize_name."""
    
    def test_valid_name(self):
        """Nombres válidos."""
        assert "Juan" in sanitize_name("Juan")
        assert "García" in sanitize_name("García")
    
    def test_name_capitalization(self):
        """Nombres deben capitalizarse."""
        result = sanitize_name("juan garcía")
        assert result == "'Juan García" or result == "Juan García"
    
    def test_name_extra_spaces(self):
        """Espacios extra deben eliminarse."""
        result = sanitize_name("  Juan   García  ")
        # No debe tener espacios dobles
        assert "  " not in result
    
    def test_name_special_chars_removed(self):
        """Caracteres especiales deben eliminarse."""
        result = sanitize_name("Juan123")
        assert "123" not in result
    
    def test_empty_name(self):
        """Nombre vacío debe fallar."""
        with pytest.raises(ValueError):
            sanitize_name("")
    
    def test_name_only_numbers(self):
        """Nombre solo números debe fallar."""
        with pytest.raises(ValueError):
            sanitize_name("12345")


class TestValidateGuestCount:
    """Tests para la función validate_guest_count."""
    
    def test_valid_guest_counts(self):
        """Números válidos de comensales."""
        assert validate_guest_count(1) == 1
        assert validate_guest_count(4) == 4
        assert validate_guest_count(10) == 10
        assert validate_guest_count(20) == 20
    
    def test_string_number(self):
        """String numérico debe convertirse."""
        assert validate_guest_count("4") == 4
        assert validate_guest_count("10") == 10
    
    def test_zero_guests(self):
        """Cero comensales debe fallar."""
        with pytest.raises(ValueError):
            validate_guest_count(0)
    
    def test_negative_guests(self):
        """Número negativo debe fallar."""
        with pytest.raises(ValueError):
            validate_guest_count(-1)
    
    def test_too_many_guests(self):
        """Más de 20 comensales debe fallar."""
        with pytest.raises(ValueError):
            validate_guest_count(21)
    
    def test_invalid_string(self):
        """String no numérico debe fallar."""
        with pytest.raises(ValueError):
            validate_guest_count("cuatro")


class TestValidateDateFormat:
    """Tests para la función validate_date_format."""
    
    def test_valid_iso_date(self):
        """Fecha ISO válida."""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        result = validate_date_format(tomorrow)
        assert result == tomorrow
    
    def test_spanish_format(self):
        """Formato español (DD/MM/YYYY)."""
        tomorrow = date.today() + timedelta(days=1)
        spanish = tomorrow.strftime("%d/%m/%Y")
        result = validate_date_format(spanish)
        assert result == tomorrow.isoformat()
    
    def test_past_date(self):
        """Fecha pasada debe fallar."""
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        with pytest.raises(ValueError):
            validate_date_format(yesterday)
    
    def test_too_far_future(self):
        """Fecha muy lejana debe fallar."""
        far_future = (date.today() + timedelta(days=100)).isoformat()
        with pytest.raises(ValueError):
            validate_date_format(far_future)
    
    def test_invalid_format(self):
        """Formato inválido debe fallar."""
        with pytest.raises(ValueError):
            validate_date_format("not-a-date")


class TestValidateTimeFormat:
    """Tests para la función validate_time_format."""
    
    def test_valid_dinner_time(self):
        """Hora de cena válida."""
        assert validate_time_format("21:00") == "21:00"
        assert validate_time_format("20:30") == "20:30"
        assert validate_time_format("22:00") == "22:00"
    
    def test_valid_lunch_time(self):
        """Hora de comida válida."""
        assert validate_time_format("13:00") == "13:00"
        assert validate_time_format("14:30") == "14:30"
        assert validate_time_format("16:00") == "16:00"
    
    def test_outside_service_hours(self):
        """Hora fuera de servicio debe fallar."""
        with pytest.raises(ValueError):
            validate_time_format("10:00")  # Muy temprano
        with pytest.raises(ValueError):
            validate_time_format("18:00")  # Entre turnos
        with pytest.raises(ValueError):
            validate_time_format("03:00")  # Muy tarde
    
    def test_invalid_format(self):
        """Formato inválido debe fallar."""
        with pytest.raises(ValueError):
            validate_time_format("not-a-time")


class TestIsPotentiallyMalicious:
    """Tests para la función is_potentially_malicious."""
    
    def test_normal_text_not_malicious(self):
        """Texto normal no es malicioso."""
        assert is_potentially_malicious("Hola mundo") is False
        assert is_potentially_malicious("Juan García") is False
        assert is_potentially_malicious("Mesa para 4") is False
    
    def test_formula_is_malicious(self):
        """Fórmulas son maliciosas."""
        assert is_potentially_malicious("=SUM(1+1)") is True
        assert is_potentially_malicious("=IMPORTXML()") is True
        assert is_potentially_malicious("=CMD|calc") is True
    
    def test_at_mention_is_malicious(self):
        """@ al inicio es malicioso."""
        assert is_potentially_malicious("@SUM(1)") is True
    
    def test_dde_is_malicious(self):
        """DDE es malicioso."""
        assert is_potentially_malicious("|calc.exe!A0") is True
    
    def test_empty_not_malicious(self):
        """String vacío no es malicioso."""
        assert is_potentially_malicious("") is False
        assert is_potentially_malicious(None) is False


class TestSanitizeReservationData:
    """Tests para la función sanitize_reservation_data."""
    
    def test_sanitize_all_fields(self):
        """Todos los campos deben sanitizarse."""
        data = {
            "nombre": "Juan García",
            "telefono": "+34600123456",
            "email": "juan@example.com",
            "notas": "Mesa cerca de ventana",
        }
        result = sanitize_reservation_data(data)
        
        assert "nombre" in result
        assert "telefono" in result
        assert "email" in result
        assert "notas" in result
    
    def test_sanitize_malicious_notes(self):
        """Notas maliciosas deben sanitizarse."""
        data = {
            "notas": "=CMD|calc.exe",
        }
        result = sanitize_reservation_data(data)
        
        # Debe estar sanitizado (con apóstrofo o pipe escapado)
        assert "'" in result["notas"] or "｜" in result["notas"]


class TestSanitizeAllFields:
    """Tests para la función sanitize_all_fields."""
    
    def test_complete_reservation(self):
        """Reserva completa debe sanitizarse."""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        data = {
            "nombre": "Juan García",
            "telefono": "+34600123456",
            "personas": 4,
            "fecha": tomorrow,
            "hora": "21:00",
            "notas": "Trona para bebé",
        }
        result = sanitize_all_fields(data)
        
        assert "nombre" in result
        assert "telefono" in result
        assert result["personas"] == 4
        assert result["fecha"] == tomorrow
        assert result["hora"] == "21:00"
    
    def test_unknown_fields_sanitized_generically(self):
        """Campos desconocidos deben sanitizarse genéricamente."""
        data = {
            "campo_custom": "=MALICIOUS()",
        }
        result = sanitize_all_fields(data)
        
        # Debe estar sanitizado
        assert result["campo_custom"].startswith("'")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
