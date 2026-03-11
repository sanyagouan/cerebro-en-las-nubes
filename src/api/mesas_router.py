"""
Mesas Router - API endpoints for table assignment.

Endpoints disponibles:
- POST /asignar - Legacy table assignment (Tetris service)
- POST /asignar-v2 - New 3-phase algorithm assignment
- GET /disponibilidad - Check table availability
"""

from datetime import date
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

# Legacy imports (Tetris service)
from src.core.logic.table_tetris_engine import (
    ZonePreference,
    AssignmentResult,
)
from src.application.services.table_tetris_service import (
    TableTetrisService,
    get_tetris_service,
)

# New imports (3-phase algorithm)
from src.core.entities.mesa import (
    SolicitudAsignacion,
    ResultadoAsignacion,
    Mesa,
    ConfiguracionMesa,
    ZonaMesa,
    EstadoMesa,
)
from src.application.services.table_assignment_service import (
    TableAssignmentService,
    get_table_assignment_service,
)

router = APIRouter(prefix="/api/mesas", tags=["mesas"])


class AsignarMesaRequest(BaseModel):
    """Request body for table assignment."""

    party_size: int = Field(..., ge=1, le=20, description="Numero de comensales")
    fecha: str = Field(..., description="Fecha de la reserva (YYYY-MM-DD)")
    turno: str = Field(..., description="Turno (T1 o T2)")
    zone_preference: str = Field(
        default="Sin preferencia",
        description="Preferencia de zona: Interior, Terraza, Sin preferencia",
    )
    has_pets: bool = Field(default=False, description="Si traen mascota")
    terrace_closed: bool = Field(
        default=False, description="Si la terraza esta cerrada"
    )


class AsignarMesaResponse(BaseModel):
    """Response for table assignment."""

    success: bool
    table_id: Optional[str] = None
    table_name: Optional[str] = None
    tables: List[str] = []
    zone: Optional[str] = None
    uses_combo: bool = False
    uses_aux: bool = False
    score: float = 0.0
    warnings: List[str] = []
    reason: Optional[str] = None
    needs_human: bool = False
    suggest_waitlist: bool = False
    hold_id: Optional[str] = None


def get_service() -> TableTetrisService:
    """Dependency to get the tetris service with Airtable/Redis integration."""
    return get_tetris_service()


@router.post("/asignar", response_model=AsignarMesaResponse)
async def asignar_mesa(
    request: AsignarMesaRequest, service: TableTetrisService = Depends(get_service)
) -> AsignarMesaResponse:
    """
    Asigna la mejor mesa disponible para una reserva.

    Args:
        request: Datos de la reserva (party_size, fecha, turno, etc.)

    Returns:
        Resultado de la asignacion con mesa sugerida o razon de fallo
    """
    # Parse zone preference
    zone_map = {
        "Interior": ZonePreference.INTERIOR,
        "Terraza": ZonePreference.TERRAZA,
        "Sin preferencia": ZonePreference.NO_PREFERENCE,
    }
    zone_pref = zone_map.get(request.zone_preference, ZonePreference.NO_PREFERENCE)

    # Parse fecha
    try:
        fecha = date.fromisoformat(request.fecha)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Formato de fecha invalido. Use YYYY-MM-DD"
        )

    # Get assignment using integrated service
    result: AssignmentResult = await service.assign_table(
        party_size=request.party_size,
        fecha=fecha,
        turno=request.turno,
        zone_preference=zone_pref,
        has_pets=request.has_pets,
        terrace_closed=request.terrace_closed,
    )

    return AsignarMesaResponse(
        success=result.success,
        table_id=result.table_id,
        table_name=result.table_name,
        tables=result.tables,
        zone=result.zone,
        uses_combo=result.uses_combo,
        uses_aux=result.uses_aux,
        score=result.score,
        warnings=result.warnings,
        reason=result.reason,
        needs_human=result.needs_human,
        suggest_waitlist=result.suggest_waitlist,
        hold_id=result.hold_id,
    )


@router.get("/disponibilidad/{fecha}/{turno}")
async def verificar_disponibilidad(
    fecha: str,
    turno: str,
    party_size: int = 4,
    service: TableTetrisService = Depends(get_service),
):
    """
    Verifica disponibilidad para una fecha y turno.

    Returns:
        Lista de mesas disponibles
    """
    try:
        fecha_obj = date.fromisoformat(fecha)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha invalido")

    # Get available tables from service (with Airtable/Redis)
    available = await service.get_available_tables(fecha=fecha_obj, turno=turno)

    return {
        "fecha": fecha,
        "turno": turno,
        "party_size": party_size,
        "available_count": len(available),
        "available_tables": available[:20],  # Top 20
    }


@router.get("/health")
async def mesas_health():
    """Health check for mesas service."""
    return {"status": "ok", "service": "mesas-tetris"}


# =============================================================================
# NUEVOS ENDPOINTS - Algoritmo de 3 Fases
# =============================================================================


@router.post("/asignar-v2", response_model=ResultadoAsignacion)
async def asignar_mesa_v2(
    solicitud: SolicitudAsignacion,
    service: TableAssignmentService = Depends(get_table_assignment_service),
) -> ResultadoAsignacion:
    """
    Asigna mesa automáticamente usando algoritmo de 3 fases.

    **Algoritmo:**
    - FASE 1: Buscar mesa individual con capacidad exacta
    - FASE 2: Buscar mesa individual con capacidad ampliada
    - FASE 3: Buscar configuración de mesas combinadas (terraza)

    **Body:**
    - num_personas: 1-20
    - fecha: YYYY-MM-DD
    - hora: HH:MM
    - preferencia_zona: Sala Exterior, Sala Interior, Sofás, Barra, Terraza (opcional)
    - preferencia_mesa: ID de mesa específica (opcional)
    - requiere_accesibilidad: True si necesita acceso adaptado

    **Returns:**
    - ResultadoAsignacion con mesa asignada o alternativas
    """
    try:
        return await service.asignar_mesa(solicitud)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error asignando mesa: {str(e)}"
        )


@router.get("/disponibilidad")
async def get_disponibilidad(
    fecha: str = Query(..., description="Fecha YYYY-MM-DD"),
    hora: str = Query(..., description="Hora HH:MM"),
    zona: Optional[str] = Query(None, description="Filtrar por zona"),
    service: TableAssignmentService = Depends(get_table_assignment_service),
):
    """
    Obtiene mesas disponibles para una fecha y hora.

    **Query Params:**
    - fecha: Fecha de la reserva (YYYY-MM-DD)
    - hora: Hora de la reserva (HH:MM)
    - zona: Filtrar por zona (opcional)
      - Sala Exterior
      - Sala Interior
      - Sofás
      - Barra
      - Terraza

    **Returns:**
    - Lista de mesas disponibles con detalles
    """
    try:
        # Convertir zona string a enum si se proporciona
        zona_enum = None
        if zona:
            zona_map = {
                "Sala Exterior": ZonaMesa.SALA_EXTERIOR,
                "Sala Interior": ZonaMesa.SALA_INTERIOR,
                "Sofás": ZonaMesa.SOFAS,
                "Barra": ZonaMesa.BARRA,
                "Terraza": ZonaMesa.TERRAZA,
            }
            zona_enum = zona_map.get(zona)

        mesas = await service._get_mesas_disponibles(fecha, hora, zona_enum)

        return {
            "fecha": fecha,
            "hora": hora,
            "zona": zona,
            "mesas_disponibles": len(mesas),
            "mesas": [m.model_dump() for m in mesas],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error obteniendo disponibilidad: {str(e)}"
        )


@router.get("/mesa/{mesa_id}", response_model=Mesa)
async def get_mesa(
    mesa_id: str,
    service: TableAssignmentService = Depends(get_table_assignment_service),
) -> Mesa:
    """
    Obtiene detalles de una mesa específica.

    **Path Params:**
    - mesa_id: ID de la mesa (ej: SE-1, T-1, SI-3)

    **Returns:**
    - Detalles completos de la mesa
    """
    try:
        mesa = await service.get_mesa_by_id(mesa_id)
        if not mesa:
            raise HTTPException(status_code=404, detail=f"Mesa {mesa_id} no encontrada")
        return mesa
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error obteniendo mesa: {str(e)}"
        )


@router.get("/configuraciones")
async def get_configuraciones(
    service: TableAssignmentService = Depends(get_table_assignment_service),
):
    """
    Obtiene todas las configuraciones de mesas combinadas.

    **Returns:**
    - Lista de configuraciones disponibles (principalmente terraza)
    """
    try:
        configs = await service._get_configuraciones_activas()
        return {
            "total": len(configs),
            "configuraciones": [c.model_dump() for c in configs],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error obteniendo configuraciones: {str(e)}"
        )


@router.get("/zonas")
async def get_zonas():
    """
    Obtiene lista de zonas disponibles en el restobar.

    **Returns:**
    - Lista de zonas con descripción
    """
    return {
        "zonas": [
            {
                "id": "sala_exterior",
                "nombre": "Sala Exterior",
                "descripcion": "Zona junto a ventanas, luminosa",
                "mesas": 4,
                "capacidad_total": 20,
            },
            {
                "id": "sala_interior",
                "nombre": "Sala Interior",
                "descripcion": "Zona principal del restaurante",
                "mesas": 4,
                "capacidad_total": 20,
            },
            {
                "id": "sofas",
                "nombre": "Sofás",
                "descripcion": "Zona acogedora con sofás",
                "mesas": 1,
                "capacidad_total": 2,
            },
            {
                "id": "barra",
                "nombre": "Barra",
                "descripcion": "Mesas altas junto a la barra",
                "mesas": 2,
                "capacidad_total": 4,
            },
            {
                "id": "terraza",
                "nombre": "Terraza",
                "descripcion": "Zona exterior con vistas",
                "mesas": 25,
                "capacidad_total": 50,
                "notas": "Mesas combinables para grupos grandes",
            },
        ]
    }


@router.get("/horarios")
async def get_horarios(
    fecha: str = Query(..., description="Fecha YYYY-MM-DD"),
    service: TableAssignmentService = Depends(get_table_assignment_service),
):
    """
    Verifica si el restobar está abierto en una fecha específica.

    **Query Params:**
    - fecha: Fecha a verificar (YYYY-MM-DD)

    **Returns:**
    - Estado de apertura y horarios disponibles
    """
    from datetime import datetime

    try:
        dt = datetime.strptime(fecha, "%Y-%m-%d")
        dia_semana = dt.weekday()  # 0=Lunes, 6=Domingo

        dias = [
            "Lunes",
            "Martes",
            "Miércoles",
            "Jueves",
            "Viernes",
            "Sábado",
            "Domingo",
        ]

        # Lunes cerrado
        if dia_semana == 0:
            return {
                "fecha": fecha,
                "dia": dias[dia_semana],
                "abierto": False,
                "motivo": "Lunes cerrado",
                "horarios": [],
            }

        # Horarios según día
        if dia_semana == 5:  # Sábado
            horarios = [
                {"turno": "comidas", "inicio": "13:00", "fin": "17:00"},
                {"turno": "cenas", "inicio": "20:00", "fin": "00:00"},
            ]
        else:  # Martes a Domingo
            horarios = [
                {"turno": "comidas", "inicio": "13:00", "fin": "17:00"},
                {"turno": "cenas", "inicio": "20:00", "fin": "23:00"},
            ]

        return {
            "fecha": fecha,
            "dia": dias[dia_semana],
            "abierto": True,
            "horarios": horarios,
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido")
