"""
Analytics API Router - Reportes y métricas del sistema.
"""

from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Response, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from loguru import logger
import csv
import io

from src.application.services.auth_service import AuthService, TokenData, require_role
from src.infrastructure.mcp.airtable_client import get_airtable_client
from src.api.middleware.rate_limiting import expensive_limit


router = APIRouter(prefix="/api/analytics", tags=["analytics"])
auth_service = AuthService()


# ========== RESPONSE MODELS ==========


class DailySummary(BaseModel):
    """Resumen de métricas diarias"""

    date: date
    total_reservations: int
    confirmed: int
    cancelled: int
    completed: int
    pending: int
    total_guests: int
    avg_party_size: float
    occupancy_rate: float  # % de mesas ocupadas


class OccupancyStats(BaseModel):
    """Estadísticas de ocupación"""

    period_start: date
    period_end: date
    avg_occupancy: float
    peak_day: str
    peak_occupancy: float
    lowest_day: str
    lowest_occupancy: float
    total_tables: int
    avg_reservations_per_day: float


class RevenueMetrics(BaseModel):
    """Métricas de ingresos (placeholder para futura integración POS)"""

    period_start: date
    period_end: date
    total_revenue: float = 0.0  # Placeholder
    avg_revenue_per_reservation: float = 0.0
    notes: str = "Integración con POS pendiente"


class AnalyticsSummaryResponse(BaseModel):
    """Respuesta completa de analytics"""

    period: str  # "day", "week", "month"
    start_date: date
    end_date: date
    total_reservations: int
    total_guests: int
    avg_party_size: float
    occupancy_rate: float
    status_breakdown: Dict[str, int]
    zone_breakdown: Dict[str, int]
    hourly_distribution: Dict[str, int]


# ========== HELPER FUNCTIONS ==========


async def get_reservations_in_period(
    start_date: date, end_date: date, airtable: Any
) -> List[Dict[str, Any]]:
    """Obtiene todas las reservas en un período"""
    try:
        formula = f"AND(IS_AFTER({{fecha}}, '{start_date}'), IS_BEFORE({{fecha}}, '{end_date}'))"
        result = await airtable.query_data_source(
            data_source_id="appQ2ZXAR68cqDmJt",
            filter={"formula": formula},
            page_size=1000,
        )
        return result.get("records", [])
    except Exception as e:
        logger.error(f"Error fetching reservations for analytics: {e}")
        return []


def calculate_occupancy(
    reservations: List[Dict], total_tables: int, hours_open: int = 12
) -> float:
    """Calcula tasa de ocupación basada en reservas"""
    if not reservations or total_tables == 0:
        return 0.0

    # Contar reservas confirmadas/completadas
    active_reservations = [
        r
        for r in reservations
        if r.get("fields", {}).get("estado") in ["confirmada", "sentada", "completada"]
    ]

    # Cálculo simplificado: (reservas activas / (mesas totales * horas abiertas)) * 100
    # Asume que cada reserva ocupa mesa por ~2 horas
    table_hours_available = total_tables * hours_open
    table_hours_used = len(active_reservations) * 2  # 2 horas promedio por reserva

    occupancy = min((table_hours_used / table_hours_available) * 100, 100.0)
    return round(occupancy, 2)


# ========== ENDPOINTS ==========


@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    period: str = Query("day", regex="^(day|week|month)$"),
    target_date: Optional[date] = None,
    user: TokenData = Depends(require_role(["manager", "admin"])),
):
    """
    Obtiene resumen de métricas para el día/semana/mes.

    **Permisos:** Manager, Admin

    **Parámetros:**
    - period: "day", "week", "month"
    - target_date: Fecha objetivo (default: hoy)
    """
    airtable = get_airtable_client()
    target = target_date or date.today()

    # Calcular rango de fechas
    if period == "day":
        start_date = target
        end_date = target + timedelta(days=1)
    elif period == "week":
        start_date = target - timedelta(days=target.weekday())  # Lunes
        end_date = start_date + timedelta(days=7)
    else:  # month
        start_date = target.replace(day=1)
        next_month = start_date.replace(day=28) + timedelta(days=4)
        end_date = next_month.replace(day=1)

    # Obtener reservas
    reservations = await get_reservations_in_period(start_date, end_date, airtable)

    # Calcular métricas
    total_reservations = len(reservations)
    total_guests = sum(
        r.get("fields", {}).get("numero_personas", 0) for r in reservations
    )
    avg_party_size = (
        round(total_guests / total_reservations, 2) if total_reservations > 0 else 0.0
    )

    # Status breakdown
    status_breakdown = {}
    for r in reservations:
        status = r.get("fields", {}).get("estado", "pendiente")
        status_breakdown[status] = status_breakdown.get(status, 0) + 1

    # Zone breakdown
    zone_breakdown = {}
    for r in reservations:
        zone = r.get("fields", {}).get("zona_preferida", "sin especificar")
        zone_breakdown[zone] = zone_breakdown.get(zone, 0) + 1

    # Hourly distribution (simplificado)
    hourly_distribution = {}
    for r in reservations:
        hora = r.get("fields", {}).get("hora", "")
        if hora:
            hour_key = hora.split(":")[0] if ":" in hora else hora
            hourly_distribution[hour_key] = hourly_distribution.get(hour_key, 0) + 1

    # Calcular ocupación (asume 20 mesas total, placeholder)
    total_tables = 20  # TODO: Obtener de tabla MESAS
    occupancy_rate = calculate_occupancy(reservations, total_tables)

    logger.info(
        f"Analytics summary generated: {period} from {start_date} to {end_date}"
    )

    return AnalyticsSummaryResponse(
        period=period,
        start_date=start_date,
        end_date=end_date,
        total_reservations=total_reservations,
        total_guests=total_guests,
        avg_party_size=avg_party_size,
        occupancy_rate=occupancy_rate,
        status_breakdown=status_breakdown,
        zone_breakdown=zone_breakdown,
        hourly_distribution=hourly_distribution,
    )


@router.get("/occupancy", response_model=OccupancyStats)
async def get_occupancy_stats(
    start_date: date = Query(..., description="Fecha inicio del período"),
    end_date: date = Query(..., description="Fecha fin del período"),
    user: TokenData = Depends(require_role(["manager", "admin"])),
):
    """
    Obtiene estadísticas de ocupación histórica.

    **Permisos:** Manager, Admin
    """
    airtable = get_airtable_client()

    # Validar rango de fechas
    if end_date < start_date:
        raise HTTPException(
            status_code=400, detail="end_date debe ser mayor que start_date"
        )

    days_diff = (end_date - start_date).days
    if days_diff > 90:
        raise HTTPException(
            status_code=400,
            detail="Rango máximo: 90 días. Para períodos más largos, use exportación.",
        )

    # Obtener reservas del período
    reservations = await get_reservations_in_period(start_date, end_date, airtable)

    # Agrupar por día
    daily_occupancy: Dict[str, List[Dict]] = {}
    for r in reservations:
        fecha_str = r.get("fields", {}).get("fecha", "")
        if fecha_str:
            if fecha_str not in daily_occupancy:
                daily_occupancy[fecha_str] = []
            daily_occupancy[fecha_str].append(r)

    # Calcular métricas diarias
    total_tables = 20  # TODO: Obtener de DB
    daily_rates = {}
    for day, day_reservations in daily_occupancy.items():
        daily_rates[day] = calculate_occupancy(day_reservations, total_tables)

    # Encontrar picos
    if daily_rates:
        peak_day = max(daily_rates, key=daily_rates.get)
        peak_occupancy = daily_rates[peak_day]
        lowest_day = min(daily_rates, key=daily_rates.get)
        lowest_occupancy = daily_rates[lowest_day]
        avg_occupancy = round(sum(daily_rates.values()) / len(daily_rates), 2)
    else:
        peak_day = lowest_day = str(start_date)
        peak_occupancy = lowest_occupancy = avg_occupancy = 0.0

    avg_reservations = round(len(reservations) / max(days_diff, 1), 2)

    logger.info(f"Occupancy stats generated: {start_date} to {end_date}")

    return OccupancyStats(
        period_start=start_date,
        period_end=end_date,
        avg_occupancy=avg_occupancy,
        peak_day=peak_day,
        peak_occupancy=peak_occupancy,
        lowest_day=lowest_day,
        lowest_occupancy=lowest_occupancy,
        total_tables=total_tables,
        avg_reservations_per_day=avg_reservations,
    )


@router.get("/export")
@expensive_limit()
async def export_analytics_csv(
    request: Request,
    start_date: date = Query(..., description="Fecha inicio"),
    end_date: date = Query(..., description="Fecha fin"),
    format: str = Query("csv", regex="^(csv)$"),  # Futuro: excel, pdf
    user: TokenData = Depends(require_role(["manager", "admin"])),
):
    """
    Exporta datos de reservas en formato CSV.

    **Permisos:** Manager, Admin

    **Formatos soportados:** csv (futuro: excel, pdf)
    """
    airtable = get_airtable_client()

    # Validar rango
    if end_date < start_date:
        raise HTTPException(
            status_code=400, detail="end_date debe ser mayor que start_date"
        )

    days_diff = (end_date - start_date).days
    if days_diff > 365:
        raise HTTPException(
            status_code=400, detail="Rango máximo para exportación: 365 días"
        )

    # Obtener reservas
    reservations = await get_reservations_in_period(start_date, end_date, airtable)

    # Generar CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Headers
    headers = [
        "ID",
        "Fecha",
        "Hora",
        "Nombre",
        "Teléfono",
        "Email",
        "Num Personas",
        "Estado",
        "Zona",
        "Mesa Asignada",
        "Solicitudes Especiales",
        "Creado en",
        "Actualizado en",
    ]
    writer.writerow(headers)

    # Datos
    for r in reservations:
        fields = r.get("fields", {})
        row = [
            r.get("id", ""),
            fields.get("fecha", ""),
            fields.get("hora", ""),
            fields.get("nombre_cliente", ""),
            fields.get("telefono", ""),
            fields.get("email", ""),
            fields.get("numero_personas", ""),
            fields.get("estado", ""),
            fields.get("zona_preferida", ""),
            fields.get("mesa_asignada", ""),
            fields.get("solicitudes_especiales", ""),
            fields.get("created_at", ""),
            fields.get("updated_at", ""),
        ]
        writer.writerow(row)

    # Preparar respuesta
    output.seek(0)
    filename = f"reservas_{start_date}_{end_date}.csv"

    logger.info(
        f"CSV export generated: {len(reservations)} reservations from {start_date} to {end_date}"
    )

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/dashboard-metrics")
async def get_dashboard_metrics(
    user: TokenData = Depends(require_role(["manager", "admin"])),
):
    """
    Métricas rápidas para el dashboard (hoy + esta semana).

    **Permisos:** Manager, Admin
    """
    airtable = get_airtable_client()
    today = date.today()

    # Métricas de hoy
    today_reservations = await get_reservations_in_period(
        today, today + timedelta(days=1), airtable
    )

    # Métricas de la semana
    week_start = today - timedelta(days=today.weekday())
    week_reservations = await get_reservations_in_period(
        week_start, week_start + timedelta(days=7), airtable
    )

    total_tables = 20  # TODO: Obtener de DB

    return {
        "today": {
            "total": len(today_reservations),
            "confirmed": len(
                [
                    r
                    for r in today_reservations
                    if r.get("fields", {}).get("estado") == "confirmada"
                ]
            ),
            "pending": len(
                [
                    r
                    for r in today_reservations
                    if r.get("fields", {}).get("estado") == "pendiente"
                ]
            ),
            "occupancy": calculate_occupancy(today_reservations, total_tables),
        },
        "this_week": {
            "total": len(week_reservations),
            "avg_per_day": round(len(week_reservations) / 7, 2),
            "occupancy": calculate_occupancy(week_reservations, total_tables),
        },
        "alerts": [],  # Placeholder para alertas futuras
    }
