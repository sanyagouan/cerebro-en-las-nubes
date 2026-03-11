"""
Script rapido para verificar que la entidad Reservation se importa correctamente
despues de corregir el error de Pydantic v2 (regex -> pattern).
"""

print("=" * 60)
print("TEST: Importacion de Reservation (Pydantic v2)")
print("=" * 60)

try:
    from src.core.entities.reservation import (
        Reservation,
        ReservationState,
        TipoTelefono,
        TipoConfirmacion
    )
    print("[OK] Importacion exitosa de todas las clases")
    
    # Verificar que los enums funcionan
    print(f"\n[OK] Estados disponibles: {[e.value for e in ReservationState]}")
    print(f"[OK] Tipos de telefono: {[e.value for e in TipoTelefono]}")
    print(f"[OK] Tipos de confirmacion: {[e.value for e in TipoConfirmacion]}")
    
    # Crear una reserva de prueba para movil
    print("\n" + "-" * 60)
    print("TEST: Creacion de reserva movil")
    print("-" * 60)
    
    reserva_movil = Reservation(
        nombre_cliente="Juan Perez",
        telefono="+34612345678",
        email="juan@example.com",
        fecha_reserva="2026-03-15",
        hora="2026-03-15T21:00:00+01:00",
        cantidad_personas=4,
        estado=ReservationState.PRE_RESERVA,
        tipo_telefono=TipoTelefono.MOVIL,
        tipo_confirmacion=TipoConfirmacion.PENDIENTE
    )
    
    print(f"[OK] Reserva movil creada: {reserva_movil.nombre_cliente}")
    print(f"   - Telefono: {reserva_movil.telefono} (tipo: {reserva_movil.tipo_telefono})")
    print(f"   - Estado: {reserva_movil.estado}")
    print(f"   - Es movil: {reserva_movil.es_movil()}")
    
    # Crear una reserva de prueba para fijo
    print("\n" + "-" * 60)
    print("TEST: Creacion de reserva fijo")
    print("-" * 60)
    
    reserva_fijo = Reservation(
        nombre_cliente="Maria Garcia",
        telefono="+34912345678",
        fecha_reserva="2026-03-16",
        hora="2026-03-16T20:30:00+01:00",
        cantidad_personas=2,
        estado=ReservationState.PRE_RESERVA,
        tipo_telefono=TipoTelefono.FIJO,
        tipo_confirmacion=TipoConfirmacion.PENDIENTE,
        requiere_recordatorio=True
    )
    
    print(f"[OK] Reserva fijo creada: {reserva_fijo.nombre_cliente}")
    print(f"   - Telefono: {reserva_fijo.telefono} (tipo: {reserva_fijo.tipo_telefono})")
    print(f"   - Estado: {reserva_fijo.estado}")
    print(f"   - Es fijo: {reserva_fijo.es_fijo()}")
    print(f"   - Requiere recordatorio: {reserva_fijo.requiere_recordatorio}")
    
    # Probar transiciones de estado
    print("\n" + "-" * 60)
    print("TEST: Transiciones de estado")
    print("-" * 60)
    
    puede_confirmar = reserva_movil.puede_transicionar_a(ReservationState.CONFIRMADA)
    print(f"[OK] Pre-reserva -> Confirmada: {puede_confirmar}")
    
    puede_curso_invalida = reserva_movil.puede_transicionar_a(ReservationState.EN_CURSO)
    print(f"[OK] Pre-reserva -> En curso (invalida): {puede_curso_invalida}")
    
    # Probar conversion a Airtable
    print("\n" + "-" * 60)
    print("TEST: Conversion a formato Airtable")
    print("-" * 60)
    
    airtable_data = reserva_movil.to_airtable_dict()
    print("[OK] Conversion a Airtable exitosa:")
    print(f"   - Estado: {airtable_data.get('Estado')}")
    print(f"   - Tipo_Telefono: {airtable_data.get('Tipo_Telefono')}")
    print(f"   - Tipo_Confirmacion: {airtable_data.get('Tipo_Confirmacion')}")
    
    # Test validacion de phone_utils
    print("\n" + "-" * 60)
    print("TEST: Deteccion automatica tipo telefono")
    print("-" * 60)
    
    from src.core.utils.phone_utils import detectar_tipo_telefono
    
    test_cases = [
        ("+34612345678", "movil"),
        ("+34712345678", "movil"),
        ("+34912345678", "fijo"),
        ("+34918765432", "fijo"),
        ("+34967890123", "fijo"),
        ("+34812345678", "desconocido"),
        ("+1555123456", "desconocido")
    ]
    
    all_passed = True
    for numero, esperado in test_cases:
        resultado = detectar_tipo_telefono(numero)
        if resultado == esperado:
            print(f"[OK] {numero} -> {resultado}")
        else:
            print(f"[ERROR] {numero} -> {resultado} (esperado: {esperado})")
            all_passed = False
    
    if not all_passed:
        raise ValueError("Algunos tests de phone_utils fallaron")
    
    print("\n" + "=" * 60)
    print("[EXITO] TODOS LOS TESTS PASARON")
    print("=" * 60)
    print("\nModelo Pydantic v2 funcional.")
    print("Sistema de estados unificados implementado correctamente.")

except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}")
    print(f"   {str(e)}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 60)
    print("[FALLO] TESTS FALLARON")
    print("=" * 60)
    exit(1)
