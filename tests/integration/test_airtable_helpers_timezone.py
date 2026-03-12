"""
Tests de integración para validar el manejo de timezone en airtable_helpers.

Valida que el round-trip de lectura/escritura del campo Hora funcione correctamente:
1. Escribir hora local (21:00 Spain) → Guardar como UTC (20:00Z)
2. Leer UTC (20:00Z) → Convertir a hora local (21:00 Spain)
3. El resultado debe ser idéntico al original
"""
import pytest
from datetime import date, time, datetime
from zoneinfo import ZoneInfo

from src.api.mobile.airtable_helpers import (
    airtable_to_reservation_response,
    reservation_request_to_airtable_fields,
)


class TestTimezoneRoundTrip:
    """Tests para validar el round-trip de timezone en el campo Hora."""

    def test_write_21h_spain_converts_to_20h_utc_in_winter(self):
        """
        Test: 21:00 hora España (invierno, UTC+1) debe guardarse como 20:00 UTC.
        
        En invierno (sin horario de verano), España está en UTC+1.
        Por tanto, 21:00 Spain = 20:00 UTC.
        """
        # Arrange: Datos de reserva con hora 21:00
        data = {
            "nombre": "Test Cliente",
            "telefono": "+34600000000",
            "fecha": date(2026, 1, 15),  # 15 enero = horario invierno
            "hora": time(21, 0),  # 21:00
            "pax": 4,
        }
        
        # Act: Convertir a campos de Airtable
        fields = reservation_request_to_airtable_fields(data)
        
        # Assert: La hora debe estar en formato ISO con Z (UTC)
        hora_guardada = fields["Hora"]
        assert "T" in hora_guardada, "Debe ser formato ISO DateTime"
        assert hora_guardada.endswith("Z"), "Debe terminar en Z (UTC)"
        
        # Assert: La hora UTC debe ser 20:00 (21:00 - 1h)
        assert "T20:00:00.000Z" in hora_guardada, f"Esperado 20:00 UTC, got {hora_guardada}"

    def test_write_21h_spain_converts_to_19h_utc_in_summer(self):
        """
        Test: 21:00 hora España (verano, UTC+2) debe guardarse como 19:00 UTC.
        
        En verano (con horario de verano), España está en UTC+2.
        Por tanto, 21:00 Spain = 19:00 UTC.
        """
        # Arrange: Datos de reserva con hora 21:00 en julio
        data = {
            "nombre": "Test Cliente",
            "telefono": "+34600000000",
            "fecha": date(2026, 7, 15),  # 15 julio = horario verano
            "hora": time(21, 0),  # 21:00
            "pax": 4,
        }
        
        # Act: Convertir a campos de Airtable
        fields = reservation_request_to_airtable_fields(data)
        
        # Assert: La hora UTC debe ser 19:00 (21:00 - 2h)
        hora_guardada = fields["Hora"]
        assert "T19:00:00.000Z" in hora_guardada, f"Esperado 19:00 UTC, got {hora_guardada}"

    def test_read_20h_utc_converts_to_21h_spain_in_winter(self):
        """
        Test: 20:00 UTC debe leerse como 21:00 España (invierno).
        
        Validación inversa: Al leer de Airtable, convertir UTC a hora local.
        """
        # Arrange: Record de Airtable con hora en formato ISO UTC
        record = {
            "id": "recTest123",
            "createdTime": "2026-01-15T10:00:00.000Z",
            "fields": {
                "Nombre del Cliente": "Test Cliente",
                "Teléfono": "+34600000000",
                "Fecha de Reserva": "2026-01-15",
                "Hora": "2026-01-15T20:00:00.000Z",  # 20:00 UTC
                "Cantidad de Personas": 4,
                "Estado": "Pendiente",
            }
        }
        
        # Act: Convertir a ReservationResponse
        response = airtable_to_reservation_response(record)
        
        # Assert: La hora debe ser 21:00 (20:00 + 1h)
        assert response.hora == time(21, 0), f"Esperado 21:00, got {response.hora}"

    def test_read_19h_utc_converts_to_21h_spain_in_summer(self):
        """
        Test: 19:00 UTC debe leerse como 21:00 España (verano).
        
        En verano, España está en UTC+2.
        """
        # Arrange: Record de Airtable con hora en formato ISO UTC
        record = {
            "id": "recTest123",
            "createdTime": "2026-07-15T10:00:00.000Z",
            "fields": {
                "Nombre del Cliente": "Test Cliente",
                "Teléfono": "+34600000000",
                "Fecha de Reserva": "2026-07-15",
                "Hora": "2026-07-15T19:00:00.000Z",  # 19:00 UTC
                "Cantidad de Personas": 4,
                "Estado": "Pendiente",
            }
        }
        
        # Act: Convertir a ReservationResponse
        response = airtable_to_reservation_response(record)
        
        # Assert: La hora debe ser 21:00 (19:00 + 2h)
        assert response.hora == time(21, 0), f"Esperado 21:00, got {response.hora}"

    def test_round_trip_winter_time(self):
        """
        Test de round-trip completo en horario de invierno.
        
        Flujo:
        1. Escribir 21:00 Spain → Guardar como 20:00 UTC
        2. Simular lectura de Airtable con 20:00 UTC
        3. Verificar que se lee como 21:00 Spain
        """
        # Arrange: Hora original
        hora_original = time(21, 0)
        fecha = date(2026, 1, 15)  # Invierno
        
        # Step 1: Escribir
        data_write = {
            "nombre": "Test Round Trip",
            "telefono": "+34600000000",
            "fecha": fecha,
            "hora": hora_original,
            "pax": 2,
        }
        fields = reservation_request_to_airtable_fields(data_write)
        hora_en_airtable = fields["Hora"]
        
        # Step 2: Simular lectura (crear record con la hora guardada)
        record = {
            "id": "recTestRT",
            "createdTime": "2026-01-15T10:00:00.000Z",
            "fields": {
                "Nombre del Cliente": "Test Round Trip",
                "Teléfono": "+34600000000",
                "Fecha de Reserva": fecha.isoformat(),
                "Hora": hora_en_airtable,
                "Cantidad de Personas": 2,
                "Estado": "Pendiente",
            }
        }
        
        # Step 3: Leer
        response = airtable_to_reservation_response(record)
        
        # Assert: La hora debe ser idéntica a la original
        assert response.hora == hora_original, (
            f"Round-trip falló: {hora_original} → {hora_en_airtable} → {response.hora}"
        )

    def test_round_trip_summer_time(self):
        """
        Test de round-trip completo en horario de verano.
        
        Flujo:
        1. Escribir 21:00 Spain → Guardar como 19:00 UTC
        2. Simular lectura de Airtable con 19:00 UTC
        3. Verificar que se lee como 21:00 Spain
        """
        # Arrange: Hora original
        hora_original = time(21, 0)
        fecha = date(2026, 7, 15)  # Verano
        
        # Step 1: Escribir
        data_write = {
            "nombre": "Test Round Trip Summer",
            "telefono": "+34600000000",
            "fecha": fecha,
            "hora": hora_original,
            "pax": 2,
        }
        fields = reservation_request_to_airtable_fields(data_write)
        hora_en_airtable = fields["Hora"]
        
        # Step 2: Simular lectura
        record = {
            "id": "recTestRTSummer",
            "createdTime": "2026-07-15T10:00:00.000Z",
            "fields": {
                "Nombre del Cliente": "Test Round Trip Summer",
                "Teléfono": "+34600000000",
                "Fecha de Reserva": fecha.isoformat(),
                "Hora": hora_en_airtable,
                "Cantidad de Personas": 2,
                "Estado": "Pendiente",
            }
        }
        
        # Step 3: Leer
        response = airtable_to_reservation_response(record)
        
        # Assert: La hora debe ser idéntica a la original
        assert response.hora == hora_original, (
            f"Round-trip falló: {hora_original} → {hora_en_airtable} → {response.hora}"
        )

    def test_round_trip_multiple_hours(self):
        """
        Test de round-trip para múltiples horas del día.
        
        Valida que diferentes horas funcionen correctamente.
        """
        test_cases = [
            (time(13, 0), date(2026, 1, 15)),  # 13:00 invierno
            (time(14, 30), date(2026, 1, 15)),  # 14:30 invierno
            (time(20, 0), date(2026, 1, 15)),   # 20:00 invierno
            (time(22, 0), date(2026, 1, 15)),   # 22:00 invierno
            (time(13, 0), date(2026, 7, 15)),   # 13:00 verano
            (time(21, 0), date(2026, 7, 15)),   # 21:00 verano
            (time(23, 0), date(2026, 7, 15)),   # 23:00 verano
        ]
        
        for hora_original, fecha in test_cases:
            # Write
            data_write = {
                "nombre": f"Test {hora_original}",
                "telefono": "+34600000000",
                "fecha": fecha,
                "hora": hora_original,
                "pax": 2,
            }
            fields = reservation_request_to_airtable_fields(data_write)
            hora_en_airtable = fields["Hora"]
            
            # Read
            record = {
                "id": f"recTest{hora_original.hour}",
                "createdTime": "2026-01-15T10:00:00.000Z",
                "fields": {
                    "Nombre del Cliente": f"Test {hora_original}",
                    "Teléfono": "+34600000000",
                    "Fecha de Reserva": fecha.isoformat(),
                    "Hora": hora_en_airtable,
                    "Cantidad de Personas": 2,
                    "Estado": "Pendiente",
                }
            }
            response = airtable_to_reservation_response(record)
            
            # Assert
            assert response.hora == hora_original, (
                f"Round-trip falló para {hora_original} en {fecha}: "
                f"{hora_original} → {hora_en_airtable} → {response.hora}"
            )


class TestLegacyFormatCompatibility:
    """Tests para validar compatibilidad con formato legacy (HH:MM)."""

    def test_read_legacy_format_hh_mm(self):
        """
        Test: El formato legacy "21:00" debe seguir funcionando.
        
        Esto asegura que registros antiguos en Airtable sigan siendo legibles.
        """
        # Arrange: Record con formato legacy
        record = {
            "id": "recLegacy123",
            "createdTime": "2026-01-15T10:00:00.000Z",
            "fields": {
                "Nombre del Cliente": "Test Legacy",
                "Teléfono": "+34600000000",
                "Fecha de Reserva": "2026-01-15",
                "Hora": "21:00",  # Formato legacy
                "Cantidad de Personas": 4,
                "Estado": "Pendiente",
            }
        }
        
        # Act: Convertir a ReservationResponse
        response = airtable_to_reservation_response(record)
        
        # Assert: La hora debe ser 21:00
        assert response.hora == time(21, 0), f"Esperado 21:00, got {response.hora}"

    def test_read_legacy_format_hh_mm_ss(self):
        """
        Test: El formato legacy "21:00:00" debe seguir funcionando.
        
        Algunos registros pueden tener segundos incluidos.
        """
        # Arrange: Record con formato legacy con segundos
        record = {
            "id": "recLegacySS",
            "createdTime": "2026-01-15T10:00:00.000Z",
            "fields": {
                "Nombre del Cliente": "Test Legacy SS",
                "Teléfono": "+34600000000",
                "Fecha de Reserva": "2026-01-15",
                "Hora": "21:00:00",  # Formato legacy con segundos
                "Cantidad de Personas": 4,
                "Estado": "Pendiente",
            }
        }
        
        # Act: Convertir a ReservationResponse
        response = airtable_to_reservation_response(record)
        
        # Assert: La hora debe ser 21:00:00
        assert response.hora == time(21, 0, 0), f"Esperado 21:00:00, got {response.hora}"

    def test_read_legacy_format_with_milliseconds(self):
        """
        Test: El formato legacy "21:00:00.000" debe funcionar.
        
        Algunos registros pueden tener milisegundos.
        """
        # Arrange: Record con formato legacy con milisegundos
        record = {
            "id": "recLegacyMS",
            "createdTime": "2026-01-15T10:00:00.000Z",
            "fields": {
                "Nombre del Cliente": "Test Legacy MS",
                "Teléfono": "+34600000000",
                "Fecha de Reserva": "2026-01-15",
                "Hora": "21:00:00.000",  # Formato legacy con milisegundos
                "Cantidad de Personas": 4,
                "Estado": "Pendiente",
            }
        }
        
        # Act: Convertir a ReservationResponse
        response = airtable_to_reservation_response(record)
        
        # Assert: La hora debe ser 21:00:00
        assert response.hora == time(21, 0, 0), f"Esperado 21:00:00, got {response.hora}"


class TestEdgeCases:
    """Tests para casos edge y manejo de errores."""

    def test_read_null_hora_returns_default(self):
        """
        Test: Si la hora es null, debe retornar hora por defecto (12:00).
        """
        # Arrange: Record sin hora
        record = {
            "id": "recNullHora",
            "createdTime": "2026-01-15T10:00:00.000Z",
            "fields": {
                "Nombre del Cliente": "Test Null Hora",
                "Teléfono": "+34600000000",
                "Fecha de Reserva": "2026-01-15",
                "Hora": None,  # Sin hora
                "Cantidad de Personas": 4,
                "Estado": "Pendiente",
            }
        }
        
        # Act: Convertir a ReservationResponse
        response = airtable_to_reservation_response(record)
        
        # Assert: La hora debe ser 12:00 (default)
        assert response.hora == time(12, 0), f"Esperado 12:00 default, got {response.hora}"

    def test_read_invalid_hora_returns_default(self):
        """
        Test: Si la hora tiene formato inválido, debe retornar hora por defecto.
        """
        # Arrange: Record con hora inválida
        record = {
            "id": "recInvalidHora",
            "createdTime": "2026-01-15T10:00:00.000Z",
            "fields": {
                "Nombre del Cliente": "Test Invalid Hora",
                "Teléfono": "+34600000000",
                "Fecha de Reserva": "2026-01-15",
                "Hora": "invalid-time",  # Formato inválido
                "Cantidad de Personas": 4,
                "Estado": "Pendiente",
            }
        }
        
        # Act: Convertir a ReservationResponse
        response = airtable_to_reservation_response(record)
        
        # Assert: La hora debe ser 12:00 (default)
        assert response.hora == time(12, 0), f"Esperado 12:00 default, got {response.hora}"

    def test_write_hora_as_string(self):
        """
        Test: La hora puede venir como string "21:00" y debe procesarse correctamente.
        """
        # Arrange: Datos con hora como string
        data = {
            "nombre": "Test String Hora",
            "telefono": "+34600000000",
            "fecha": date(2026, 1, 15),
            "hora": "21:00",  # String en lugar de time object
            "pax": 4,
        }
        
        # Act: Convertir a campos de Airtable
        fields = reservation_request_to_airtable_fields(data)
        
        # Assert: Debe generar formato ISO válido
        hora_guardada = fields["Hora"]
        assert "T" in hora_guardada, "Debe ser formato ISO DateTime"
        assert hora_guardada.endswith("Z"), "Debe terminar en Z (UTC)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
