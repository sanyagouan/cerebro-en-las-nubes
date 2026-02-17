"""
Mesas Router - API endpoints for table assignment.
"""

from datetime import date
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from src.core.logic.table_tetris_engine import (
    ZonePreference,
    AssignmentResult,
)
from src.application.services.table_tetris_service import (
    TableTetrisService,
    get_tetris_service,
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
