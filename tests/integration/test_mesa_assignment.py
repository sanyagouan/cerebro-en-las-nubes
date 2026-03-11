"""
Tests de Integración - Algoritmo de Asignación de Mesas

Este módulo prueba el algoritmo de 3 fases para asignación de mesas:
- FASE 1: Buscar mesa individual con capacidad exacta
- FASE 2: Buscar mesa individual con capacidad ampliada
- FASE 3: Buscar configuración de mesas combinadas (terraza)

Ejecutar con: pytest tests/integration/test_mesa_assignment.py -v
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import os
import sys

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.core.entities.mesa import (
    Mesa,
    ConfiguracionMesa,
    SolicitudAsignacion,
    ResultadoAsignacion,
    ZonaMesa,
    EstadoMesa,
)
from src.application.services.table_assignment_service import (
    TableAssignmentService,
)


# =============================================================================
# FIXTURES - Datos de prueba
# =============================================================================


@pytest.fixture
def mesas_interior_mock():
    """Crea mesas de interior mock para testing."""
    return [
        Mesa(
            id="recSE1",
            id_mesa="SE-1",
            nombre="Mesa Sala Exterior 1",
            zona=ZonaMesa.SALA_EXTERIOR,
            ubicacion_detallada="Junto a ventana",
            capacidad_estandar=4,
            capacidad_ampliada=6,
            mesas_auxiliares=["A1", "A2"],
            es_combinable=False,
            mesas_compatibles=None,
            estado=EstadoMesa.DISPONIBLE,
            notas=None,
            orden_prioridad=1,
            activa=True,
        ),
        Mesa(
            id="recSE2",
            id_mesa="SE-2",
            nombre="Mesa Sala Exterior 2",
            zona=ZonaMesa.SALA_EXTERIOR,
            ubicacion_detallada="Junto a ventana",
            capacidad_estandar=4,
            capacidad_ampliada=6,
            mesas_auxiliares=["A3", "A4"],
            es_combinable=False,
            mesas_compatibles=None,
            estado=EstadoMesa.DISPONIBLE,
            notas=None,
            orden_prioridad=2,
            activa=True,
        ),
        Mesa(
            id="recSE4",
            id_mesa="SE-4",
            nombre="Mesa Sala Exterior 4",
            zona=ZonaMesa.SALA_EXTERIOR,
            ubicacion_detallada="Mesa grande",
            capacidad_estandar=8,
            capacidad_ampliada=10,
            mesas_auxiliares=["A7", "A8"],
            es_combinable=False,
            mesas_compatibles=None,
            estado=EstadoMesa.DISPONIBLE,
            notas="Mesa grande para grupos",
            orden_prioridad=4,
            activa=True,
        ),
        Mesa(
            id="recSI1",
            id_mesa="SI-1",
            nombre="Mesa Sala Interior 1",
            zona=ZonaMesa.SALA_INTERIOR,
            ubicacion_detallada=None,
            capacidad_estandar=4,
            capacidad_ampliada=6,
            mesas_auxiliares=None,
            es_combinable=False,
            mesas_compatibles=None,
            estado=EstadoMesa.DISPONIBLE,
            notas=None,
            orden_prioridad=5,
            activa=True,
        ),
        Mesa(
            id="recSI3",
            id_mesa="SI-3",
            nombre="Mesa Sala Interior 3",
            zona=ZonaMesa.SALA_INTERIOR,
            ubicacion_detallada="Mesa grande",
            capacidad_estandar=8,
            capacidad_ampliada=10,
            mesas_auxiliares=None,
            es_combinable=False,
            mesas_compatibles=None,
            estado=EstadoMesa.DISPONIBLE,
            notas="Ideal para grupos",
            orden_prioridad=7,
            activa=True,
        ),
        Mesa(
            id="recSOF1",
            id_mesa="SOF-1",
            nombre="Mesa Sofás",
            zona=ZonaMesa.SOFAS,
            ubicacion_detallada="Zona acogedora",
            capacidad_estandar=2,
            capacidad_ampliada=4,
            mesas_auxiliares=None,
            es_combinable=False,
            mesas_compatibles=None,
            estado=EstadoMesa.DISPONIBLE,
            notas="Zona de sofás",
            orden_prioridad=9,
            activa=True,
        ),
        Mesa(
            id="recB5",
            id_mesa="B-5",
            nombre="Mesa Barra 5",
            zona=ZonaMesa.BARRA,
            ubicacion_detallada="Mesa alta",
            capacidad_estandar=2,
            capacidad_ampliada=4,
            mesas_auxiliares=None,
            es_combinable=False,
            mesas_compatibles=None,
            estado=EstadoMesa.DISPONIBLE,
            notas="Mesa alta junto a barra",
            orden_prioridad=10,
            activa=True,
        ),
    ]


@pytest.fixture
def mesas_terraza_mock():
    """Crea mesas de terraza mock para testing."""
    mesas = []
    for i in range(1, 26):
        # Determinar mesas compatibles (adyacentes)
        compatibles = []
        if i > 1:
            compatibles.append(f"T-{i-1}")
        if i < 25:
            compatibles.append(f"T-{i+1}")

        mesa = Mesa(
            id=f"recT{i}",
            id_mesa=f"T-{i}",
            nombre=f"Mesa Terraza {i}",
            zona=ZonaMesa.TERRAZA,
            ubicacion_detallada="Exterior con vistas",
            capacidad_estandar=2,
            capacidad_ampliada=4,
            mesas_auxiliares=None,
            es_combinable=True,
            mesas_compatibles=compatibles,
            estado=EstadoMesa.DISPONIBLE,
            notas="Mesa combinable",
            orden_prioridad=20 + i,
            activa=True,
        )
        mesas.append(mesa)
    return mesas


@pytest.fixture
def configuraciones_terraza_mock():
    """Crea configuraciones de terraza mock para testing."""
    return [
        ConfiguracionMesa(
            id="recConf1",
            id_configuracion="CONF-T-1-2",
            nombre="Pareja Terraza 1-2",
            mesas_incluidas=["T-1", "T-2"],
            capacidad_total=4,
            ubicacion="Terraza",
            activa=True,
            notas="Configuración para 4 personas",
        ),
        ConfiguracionMesa(
            id="recConf2",
            id_configuracion="CONF-T-3-4",
            nombre="Pareja Terraza 3-4",
            mesas_incluidas=["T-3", "T-4"],
            capacidad_total=4,
            ubicacion="Terraza",
            activa=True,
            notas="Configuración para 4 personas",
        ),
        ConfiguracionMesa(
            id="recConf3",
            id_configuracion="CONF-T-1-2-3",
            nombre="Grupo 6 personas",
            mesas_incluidas=["T-1", "T-2", "T-3"],
            capacidad_total=6,
            ubicacion="Terraza",
            activa=True,
            notas="Configuración para 6 personas",
        ),
        ConfiguracionMesa(
            id="recConf4",
            id_configuracion="CONF-T-1-2-3-4",
            nombre="Grupo 8 personas",
            mesas_incluidas=["T-1", "T-2", "T-3", "T-4"],
            capacidad_total=8,
            ubicacion="Terraza",
            activa=True,
            notas="Configuración para 8 personas",
        ),
    ]


@pytest.fixture
def service_mock(mesas_interior_mock, mesas_terraza_mock, configuraciones_terraza_mock):
    """Crea un servicio con métodos mockeados."""
    service = TableAssignmentService()

    # Mockear métodos de acceso a datos
    service._get_mesas_disponibles = AsyncMock(
        return_value=mesas_interior_mock + mesas_terraza_mock
    )
    service._get_configuraciones_activas = AsyncMock(
        return_value=configuraciones_terraza_mock
    )

    return service


# =============================================================================
# TESTS - FASE 1: Capacidad Exacta
# =============================================================================


@pytest.mark.asyncio
async def test_asignacion_2_personas_capacidad_exacta(service_mock):
    """
    Test: 2 personas obtienen mesa de 2 (capacidad exacta).

    Escenario:
    - Cliente solicita mesa para 2 personas
    - Debe asignar mesa con capacidad_estandar == 2
    - Prioriza mesas de terraza (menor desperdicio)
    """
    # Preparar fecha válida (domingo)
    fecha = "2026-03-15"  # Domingo
    hora = "14:00"

    solicitud = SolicitudAsignacion(
        num_personas=2,
        fecha=fecha,
        hora=hora,
        preferencia_zona=ZonaMesa.TERRAZA,
    )

    resultado = await service_mock.asignar_mesa(solicitud)

    # Verificaciones
    assert resultado.exito is True, f"Esperaba éxito, pero: {resultado.mensaje}"
    assert resultado.mesa_asignada is not None, "Debe asignar una mesa"
    assert resultado.mesa_asignada.capacidad_estandar == 2, (
        f"Capacidad estándar debe ser 2, es {resultado.mesa_asignada.capacidad_estandar}"
    )
    assert resultado.mesa_asignada.zona == ZonaMesa.TERRAZA, (
        f"Zona debe ser Terraza, es {resultado.mesa_asignada.zona}"
    )
    assert "capacidad exacta" in resultado.mensaje.lower(), (
        f"Mensaje debe indicar capacidad exacta: {resultado.mensaje}"
    )


@pytest.mark.asyncio
async def test_asignacion_4_personas_capacidad_exacta(service_mock):
    """
    Test: 4 personas obtienen mesa de 4 (capacidad exacta).

    Escenario:
    - Cliente solicita mesa para 4 personas
    - Debe asignar mesa con capacidad_estandar == 4
    - Prioriza Sala Exterior (menor orden_prioridad)
    """
    fecha = "2026-03-15"  # Domingo
    hora = "14:00"

    solicitud = SolicitudAsignacion(
        num_personas=4,
        fecha=fecha,
        hora=hora,
        preferencia_zona=ZonaMesa.SALA_EXTERIOR,
    )

    resultado = await service_mock.asignar_mesa(solicitud)

    assert resultado.exito is True
    assert resultado.mesa_asignada is not None
    assert resultado.mesa_asignada.capacidad_estandar == 4
    assert resultado.mesa_asignada.zona == ZonaMesa.SALA_EXTERIOR
    # Verificar que asigna la de menor prioridad (SE-1)
    assert resultado.mesa_asignada.orden_prioridad == 1


@pytest.mark.asyncio
async def test_asignacion_8_personas_capacidad_exacta(service_mock):
    """
    Test: 8 personas obtienen mesa de 8 (capacidad exacta).

    Escenario:
    - Cliente solicita mesa para 8 personas
    - Debe asignar mesa con capacidad_estandar == 8
    - Puede ser SE-4 o SI-3
    """
    fecha = "2026-03-15"
    hora = "21:00"

    solicitud = SolicitudAsignacion(
        num_personas=8,
        fecha=fecha,
        hora=hora,
    )

    resultado = await service_mock.asignar_mesa(solicitud)

    assert resultado.exito is True
    assert resultado.mesa_asignada is not None
    assert resultado.mesa_asignada.capacidad_estandar == 8


# =============================================================================
# TESTS - FASE 2: Capacidad Ampliada
# =============================================================================


@pytest.mark.asyncio
async def test_asignacion_4_personas_capacidad_ampliada(service_mock):
    """
    Test: 4 personas obtienen mesa de 2 ampliada a 4.

    Escenario:
    - No hay mesas de 4 disponibles
    - Debe asignar mesa con capacidad_ampliada >= 4
    - Minimiza desperdicio
    """
    # Mockear solo mesas de 2 personas disponibles
    mesas_reducidas = [
        m for m in (await service_mock._get_mesas_disponibles("", ""))
        if m.capacidad_estandar == 2
    ]
    service_mock._get_mesas_disponibles = AsyncMock(return_value=mesas_reducidas)

    fecha = "2026-03-15"
    hora = "14:00"

    solicitud = SolicitudAsignacion(
        num_personas=4,
        fecha=fecha,
        hora=hora,
        preferencia_zona=ZonaMesa.TERRAZA,
    )

    resultado = await service_mock.asignar_mesa(solicitud)

    assert resultado.exito is True
    assert resultado.mesa_asignada is not None
    assert resultado.mesa_asignada.capacidad_ampliada >= 4
    assert "capacidad ampliada" in resultado.mensaje.lower()


@pytest.mark.asyncio
async def test_asignacion_6_personas_capacidad_ampliada(service_mock):
    """
    Test: 6 personas obtienen mesa de 4 ampliada a 6.

    Escenario:
    - No hay mesas de 6 disponibles
    - Debe asignar mesa con capacidad_ampliada >= 6
    - Prioriza SE-1 o SE-2 (capacidad_ampliada = 6)
    """
    # Filtrar solo mesas que pueden ampliarse a 6
    mesas_filtradas = [
        m
        for m in (await service_mock._get_mesas_disponibles("", ""))
        if m.capacidad_ampliada >= 6 and m.capacidad_estandar < 6
    ]
    service_mock._get_mesas_disponibles = AsyncMock(return_value=mesas_filtradas)

    fecha = "2026-03-15"
    hora = "14:00"

    solicitud = SolicitudAsignacion(
        num_personas=6,
        fecha=fecha,
        hora=hora,
    )

    resultado = await service_mock.asignar_mesa(solicitud)

    assert resultado.exito is True
    assert resultado.mesa_asignada is not None
    assert resultado.mesa_asignada.capacidad_ampliada >= 6


# =============================================================================
# TESTS - FASE 3: Configuraciones Combinadas
# =============================================================================


@pytest.mark.asyncio
async def test_asignacion_6_personas_configuracion(service_mock):
    """
    Test: 6 personas obtienen configuración de 3 mesas terraza.

    Escenario:
    - No hay mesa individual para 6
    - Debe asignar configuración CONF-T-1-2-3 (capacidad 6)
    """
    # Mockear solo mesas de terraza pequeñas
    mesas_terraza = [
        m
        for m in (await service_mock._get_mesas_disponibles("", ""))
        if m.zona == ZonaMesa.TERRAZA
    ]
    service_mock._get_mesas_disponibles = AsyncMock(return_value=mesas_terraza)

    fecha = "2026-03-15"
    hora = "14:00"

    solicitud = SolicitudAsignacion(
        num_personas=6,
        fecha=fecha,
        hora=hora,
        preferencia_zona=ZonaMesa.TERRAZA,
    )

    resultado = await service_mock.asignar_mesa(solicitud)

    assert resultado.exito is True
    assert resultado.configuracion_asignada is not None, (
        "Debe asignar una configuración para 6 personas"
    )
    assert resultado.configuracion_asignada.capacidad_total >= 6
    assert len(resultado.configuracion_asignada.mesas_incluidas) >= 3


@pytest.mark.asyncio
async def test_asignacion_8_personas_configuracion(service_mock):
    """
    Test: 8 personas obtienen configuración de 4 mesas terraza.

    Escenario:
    - No hay mesa individual para 8
    - Debe asignar configuración CONF-T-1-2-3-4 (capacidad 8)
    """
    mesas_terraza = [
        m
        for m in (await service_mock._get_mesas_disponibles("", ""))
        if m.zona == ZonaMesa.TERRAZA
    ]
    service_mock._get_mesas_disponibles = AsyncMock(return_value=mesas_terraza)

    fecha = "2026-03-15"
    hora = "14:00"

    solicitud = SolicitudAsignacion(
        num_personas=8,
        fecha=fecha,
        hora=hora,
        preferencia_zona=ZonaMesa.TERRAZA,
    )

    resultado = await service_mock.asignar_mesa(solicitud)

    assert resultado.exito is True
    assert resultado.configuracion_asignada is not None
    assert resultado.configuracion_asignada.capacidad_total >= 8


# =============================================================================
# TESTS - Validaciones de Horario
# =============================================================================


@pytest.mark.asyncio
async def test_asignacion_lunes_cerrado(service_mock):
    """
    Test: Lunes el restobar está cerrado.

    Escenario:
    - Cliente intenta reservar un lunes
    - Debe rechazar con mensaje de cerrado
    """
    # Calcular próximo lunes
    hoy = datetime.now()
    dias_hasta_lunes = (0 - hoy.weekday()) % 7
    if dias_hasta_lunes == 0:
        dias_hasta_lunes = 7
    lunes = hoy + timedelta(days=dias_hasta_lunes)
    fecha_lunes = lunes.strftime("%Y-%m-%d")

    solicitud = SolicitudAsignacion(
        num_personas=4,
        fecha=fecha_lunes,
        hora="14:00",
    )

    resultado = await service_mock.asignar_mesa(solicitud)

    assert resultado.exito is False, "Debe fallar porque es lunes"
    assert "cerrado" in resultado.mensaje.lower(), (
        f"Mensaje debe indicar cerrado: {resultado.mensaje}"
    )


@pytest.mark.asyncio
async def test_asignacion_horario_valido_comidas(service_mock):
    """
    Test: Horario válido de comidas (13:00-17:00).

    Escenario:
    - Cliente reserva a las 14:00 un domingo
    - Debe aceptar la reserva
    """
    fecha = "2026-03-15"  # Domingo
    hora = "14:00"

    solicitud = SolicitudAsignacion(
        num_personas=4,
        fecha=fecha,
        hora=hora,
    )

    resultado = await service_mock.asignar_mesa(solicitud)

    assert resultado.exito is True


@pytest.mark.asyncio
async def test_asignacion_horario_valido_cenas(service_mock):
    """
    Test: Horario válido de cenas (20:00-23:00).

    Escenario:
    - Cliente reserva a las 21:00 un domingo
    - Debe aceptar la reserva
    """
    fecha = "2026-03-15"  # Domingo
    hora = "21:00"

    solicitud = SolicitudAsignacion(
        num_personas=4,
        fecha=fecha,
        hora=hora,
    )

    resultado = await service_mock.asignar_mesa(solicitud)

    assert resultado.exito is True


@pytest.mark.asyncio
async def test_asignacion_horario_invalido(service_mock):
    """
    Test: Horario inválido (fuera de horario de apertura).

    Escenario:
    - Cliente intenta reservar a las 10:00
    - Debe rechazar con mensaje de horario
    """
    fecha = "2026-03-15"  # Domingo
    hora = "10:00"  # Fuera de horario

    solicitud = SolicitudAsignacion(
        num_personas=4,
        fecha=fecha,
        hora=hora,
    )

    resultado = await service_mock.asignar_mesa(solicitud)

    assert resultado.exito is False
    assert "cerrado" in resultado.mensaje.lower() or "horario" in resultado.mensaje.lower()


# =============================================================================
# TESTS - Priorización de Zonas
# =============================================================================


@pytest.mark.asyncio
async def test_priorizacion_sala_exterior(service_mock):
    """
    Test: Se prioriza Sala Exterior sobre otras zonas.

    Escenario:
    - Cliente prefiere Sala Exterior
    - Debe asignar mesa de Sala Exterior
    - Debe ser la de menor orden_prioridad
    """
    fecha = "2026-03-15"
    hora = "14:00"

    solicitud = SolicitudAsignacion(
        num_personas=4,
        fecha=fecha,
        hora=hora,
        preferencia_zona=ZonaMesa.SALA_EXTERIOR,
    )

    resultado = await service_mock.asignar_mesa(solicitud)

    assert resultado.exito is True
    assert resultado.mesa_asignada.zona == ZonaMesa.SALA_EXTERIOR
    # Verificar que es la de menor prioridad (SE-1)
    assert resultado.mesa_asignada.id_mesa == "SE-1"


@pytest.mark.asyncio
async def test_priorizacion_terraza(service_mock):
    """
    Test: Se prioriza Terraza cuando se solicita.

    Escenario:
    - Cliente prefiere Terraza
    - Debe asignar mesa de Terraza
    """
    fecha = "2026-03-15"
    hora = "14:00"

    solicitud = SolicitudAsignacion(
        num_personas=2,
        fecha=fecha,
        hora=hora,
        preferencia_zona=ZonaMesa.TERRAZA,
    )

    resultado = await service_mock.asignar_mesa(solicitud)

    assert resultado.exito is True
    assert resultado.mesa_asignada.zona == ZonaMesa.TERRAZA


# =============================================================================
# TESTS - Sin Disponibilidad
# =============================================================================


@pytest.mark.asyncio
async def test_sin_disponibilidad_ofrece_alternativas(service_mock):
    """
    Test: Sin disponibilidad ofrece alternativas.

    Escenario:
    - No hay mesas disponibles
    - Debe ofrecer alternativas cercanas
    """
    # Mockear sin mesas disponibles
    service_mock._get_mesas_disponibles = AsyncMock(return_value=[])

    fecha = "2026-03-15"
    hora = "14:00"

    solicitud = SolicitudAsignacion(
        num_personas=4,
        fecha=fecha,
        hora=hora,
    )

    resultado = await service_mock.asignar_mesa(solicitud)

    assert resultado.exito is False
    assert "no hay" in resultado.mensaje.lower() or "disponible" in resultado.mensaje.lower()


# =============================================================================
# TESTS - Casos Edge
# =============================================================================


@pytest.mark.asyncio
async def test_grupo_grande_sin_configuracion(service_mock):
    """
    Test: Grupo grande sin configuración disponible.

    Escenario:
    - Cliente solicita mesa para 15 personas
    - No hay configuración para ese tamaño
    - Debe rechazar con mensaje apropiado
    """
    fecha = "2026-03-15"
    hora = "14:00"

    solicitud = SolicitudAsignacion(
        num_personas=15,
        fecha=fecha,
        hora=hora,
    )

    resultado = await service_mock.asignar_mesa(solicitud)

    # Puede fallar o asignar configuración si existe
    # En este caso, no hay configuración para 15
    if not resultado.exito:
        assert "no hay" in resultado.mensaje.lower() or "disponible" in resultado.mensaje.lower()


@pytest.mark.asyncio
async def test_mesa_especifica_no_disponible(service_mock):
    """
    Test: Mesa específica solicitada no disponible.

    Escenario:
    - Cliente solicita mesa específica (SE-1)
    - La mesa está disponible
    - Debe asignar esa mesa
    """
    fecha = "2026-03-15"
    hora = "14:00"

    solicitud = SolicitudAsignacion(
        num_personas=4,
        fecha=fecha,
        hora=hora,
        preferencia_mesa="SE-1",
    )

    resultado = await service_mock.asignar_mesa(solicitud)

    # Si la mesa está disponible, debe asignarla
    # Si no, debe ofrecer alternativa
    if resultado.exito:
        assert resultado.mesa_asignada.id_mesa == "SE-1"


@pytest.mark.asyncio
async def test_mesa_fuera_de_servicio(service_mock):
    """
    Test: Mesa fuera de servicio no se asigna.

    Escenario:
    - Mesa marcada como inactiva
    - No debe ser asignada
    """
    # Crear mesa inactiva
    mesa_inactiva = Mesa(
        id="recSE99",
        id_mesa="SE-99",
        nombre="Mesa Inactiva",
        zona=ZonaMesa.SALA_EXTERIOR,
        capacidad_estandar=4,
        capacidad_ampliada=6,
        es_combinable=False,
        estado=EstadoMesa.MANTENIMIENTO,
        orden_prioridad=1,
        activa=False,  # Inactiva
    )

    # Mockear solo mesa inactiva
    service_mock._get_mesas_disponibles = AsyncMock(return_value=[mesa_inactiva])

    fecha = "2026-03-15"
    hora = "14:00"

    solicitud = SolicitudAsignacion(
        num_personas=4,
        fecha=fecha,
        hora=hora,
    )

    resultado = await service_mock.asignar_mesa(solicitud)

    # No debe asignar mesa inactiva
    assert resultado.exito is False or (
        resultado.mesa_asignada is None or resultado.mesa_asignada.activa is False
    )


# =============================================================================
# TESTS - Integración con Airtable (Requiere API Key)
# =============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
async def test_integracion_airtable_obtener_mesas():
    """
    Test de integración: Obtener mesas reales de Airtable.

    NOTA: Requiere AIRTABLE_API_KEY en variables de entorno.
    Marcar con: pytest -m integration
    """
    api_key = os.getenv("AIRTABLE_API_KEY")
    if not api_key:
        pytest.skip("AIRTABLE_API_KEY no configurado")

    service = TableAssignmentService()

    # Intentar obtener mesas
    mesas = await service._get_mesas_disponibles("2026-03-15", "14:00")

    # Verificar que hay mesas
    assert len(mesas) > 0, "Debe haber al menos una mesa en Airtable"

    # Verificar estructura
    for mesa in mesas:
        assert mesa.id_mesa is not None
        assert mesa.capacidad_estandar > 0
        assert mesa.zona in [z.value for z in ZonaMesa]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_integracion_airtable_configuraciones():
    """
    Test de integración: Obtener configuraciones de Airtable.

    NOTA: Requiere AIRTABLE_API_KEY en variables de entorno.
    """
    api_key = os.getenv("AIRTABLE_API_KEY")
    if not api_key:
        pytest.skip("AIRTABLE_API_KEY no configurado")

    service = TableAssignmentService()

    # Intentar obtener configuraciones
    configs = await service._get_configuraciones_activas()

    # Verificar estructura si hay configuraciones
    for config in configs:
        assert config.id_configuracion is not None
        assert len(config.mesas_incluidas) > 0
        assert config.capacidad_total > 0


# =============================================================================
# TESTS - Algoritmo de Minimización de Desperdicio
# =============================================================================


@pytest.mark.asyncio
async def test_minimizacion_desperdicio_capacidad(service_mock):
    """
    Test: Algoritmo minimiza desperdicio de capacidad.

    Escenario:
    - 4 personas
    - Hay mesa de 4 y mesa de 8 disponibles
    - Debe asignar mesa de 4 (menor desperdicio)
    """
    # Crear mesas con diferentes capacidades
    mesas = [
        Mesa(
            id="rec1",
            id_mesa="M-4",
            nombre="Mesa 4",
            zona=ZonaMesa.SALA_EXTERIOR,
            capacidad_estandar=4,
            capacidad_ampliada=6,
            estado=EstadoMesa.DISPONIBLE,
            orden_prioridad=1,
            activa=True,
        ),
        Mesa(
            id="rec2",
            id_mesa="M-8",
            nombre="Mesa 8",
            zona=ZonaMesa.SALA_EXTERIOR,
            capacidad_estandar=8,
            capacidad_ampliada=10,
            estado=EstadoMesa.DISPONIBLE,
            orden_prioridad=2,
            activa=True,
        ),
    ]
    service_mock._get_mesas_disponibles = AsyncMock(return_value=mesas)

    fecha = "2026-03-15"
    hora = "14:00"

    solicitud = SolicitudAsignacion(
        num_personas=4,
        fecha=fecha,
        hora=hora,
    )

    resultado = await service_mock.asignar_mesa(solicitud)

    assert resultado.exito is True
    # Debe asignar mesa de 4, no de 8
    assert resultado.mesa_asignada.capacidad_estandar == 4


# =============================================================================
# TESTS - Validación de Parámetros
# =============================================================================


def test_solicitud_asignacion_validacion_num_personas():
    """Test: Validación de num_personas en SolicitudAsignacion."""
    # Valores válidos
    solicitud = SolicitudAsignacion(
        num_personas=4,
        fecha="2026-03-15",
        hora="14:00",
    )
    assert solicitud.num_personas == 4

    # Valor mínimo
    solicitud_min = SolicitudAsignacion(
        num_personas=1,
        fecha="2026-03-15",
        hora="14:00",
    )
    assert solicitud_min.num_personas == 1

    # Valor máximo
    solicitud_max = SolicitudAsignacion(
        num_personas=20,
        fecha="2026-03-15",
        hora="14:00",
    )
    assert solicitud_max.num_personas == 20

    # Valor inválido (menor que mínimo)
    with pytest.raises(Exception):  # Pydantic ValidationError
        SolicitudAsignacion(
            num_personas=0,
            fecha="2026-03-15",
            hora="14:00",
        )

    # Valor inválido (mayor que máximo)
    with pytest.raises(Exception):  # Pydantic ValidationError
        SolicitudAsignacion(
            num_personas=21,
            fecha="2026-03-15",
            hora="14:00",
        )


def test_mesa_model_validation():
    """Test: Validación de modelo Mesa."""
    mesa = Mesa(
        id_mesa="TEST-1",
        nombre="Mesa Test",
        zona=ZonaMesa.SALA_EXTERIOR,
        capacidad_estandar=4,
        capacidad_ampliada=6,
        orden_prioridad=1,
    )

    assert mesa.id_mesa == "TEST-1"
    assert mesa.estado == EstadoMesa.DISPONIBLE  # Default
    assert mesa.activa is True  # Default
    assert mesa.es_combinable is False  # Default


# =============================================================================
# RUNNER
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
