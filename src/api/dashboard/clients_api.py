"""
API endpoints para Clientes (CRM) del Dashboard.
Obtiene datos reales desde Airtable con fallback graceful a registros vacíos.
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from loguru import logger
from src.application.services.auth_service import TokenData, require_role

router = APIRouter(prefix="/api/clients", tags=["clients"])

ALLOWED_ROLES = ["administradora", "encargada", "admin", "manager"]
ADMIN_ROLES = ["administradora", "admin"]

# Airtable config (reutiliza la tabla de reservas para derivar clientes únicos)
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
RESERVATIONS_TABLE = os.getenv("AIRTABLE_RESERVATIONS_TABLE", "Reservas")
CLIENTS_TABLE = os.getenv("AIRTABLE_CLIENTS_TABLE", "Clientes")

# Field mapping — adaptar si los nombres cambian en Airtable
FIELD_MAP = {
    "nombre": "Nombre",
    "telefono": "Teléfono",
    "email": "Email",
    "tier": "Tier",
    "notas": "Notas Staff",
    "total_reservas": "Total Reservas",
    "primera_reserva": "Primera Reserva",
    "ultima_reserva": "Última Reserva",
}


def _record_to_client(record: dict) -> dict:
    """Transforma un record de Airtable al formato del CRM."""
    fields = record.get("fields", {})
    return {
        "id": record.get("id", ""),
        "nombre": fields.get(FIELD_MAP["nombre"], fields.get("Nombre", "")),
        "telefono": fields.get(FIELD_MAP["telefono"], fields.get("Teléfono", fields.get("Telefono", ""))),
        "email": fields.get(FIELD_MAP["email"], fields.get("Email", "")),
        "tier": fields.get(FIELD_MAP["tier"], "Regular"),
        "total_reservas": fields.get(FIELD_MAP["total_reservas"], fields.get("Total Reservas", 0)),
        "reservas_completadas": fields.get("Reservas Completadas", 0),
        "reservas_canceladas": fields.get("Reservas Canceladas", 0),
        "no_shows": fields.get("No Shows", 0),
        "primera_reserva": fields.get(FIELD_MAP["primera_reserva"], fields.get("Primera Reserva", "")),
        "ultima_reserva": fields.get(FIELD_MAP["ultima_reserva"], fields.get("Última Reserva", "")),
        "notas_staff": fields.get(FIELD_MAP["notas"], fields.get("Notas Staff", fields.get("Notas", ""))),
        "preferencias": [],
        "created_at": record.get("createdTime", datetime.now().isoformat()),
        "updated_at": datetime.now().isoformat(),
    }


async def _get_clients_from_airtable(query: Optional[str] = None, tier: Optional[str] = None, limit: int = 50, offset: int = 0) -> dict:
    """Obtiene clientes reales desde Airtable con fallback graceful."""
    try:
        from src.infrastructure.mcp.airtable_client import airtable_client
        if not airtable_client._api or not AIRTABLE_BASE_ID:
            raise RuntimeError("Airtable no configurado")

        filter_parts = []
        if query:
            escaped = query.replace("'", "\\'")
            filter_parts.append(
                f"OR(FIND(LOWER('{escaped}'), LOWER({{{FIELD_MAP['nombre']}}})), "
                f"FIND('{escaped}', {{{FIELD_MAP['telefono']}}}))"
            )
        if tier:
            filter_parts.append(f"{{{FIELD_MAP['tier']}}} = '{tier}'")

        filter_formula = f"AND({', '.join(filter_parts)})" if filter_parts else None

        response = await airtable_client.list_records(
            base_id=AIRTABLE_BASE_ID,
            table_name=CLIENTS_TABLE,
            max_records=500,
            filterByFormula=filter_formula,
            sort=[{"field": FIELD_MAP["ultima_reserva"], "direction": "desc"}],
        )
        all_records = response.get("records", [])
        clients = [_record_to_client(r) for r in all_records]
        paginated = clients[offset:offset + limit]
        return {"customers": paginated, "total": len(clients), "source": "airtable"}

    except Exception as e:
        logger.warning(f"Airtable no disponible para clientes: {e} — devolviendo lista vacía")
        return {"customers": [], "total": 0, "source": "unavailable", "error": str(e)[:100]}


@router.get("")
async def list_clients(
    query: Optional[str] = None,
    tier: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: TokenData = Depends(require_role(ALLOWED_ROLES))
):
    """Lista clientes del CRM desde Airtable."""
    return await _get_clients_from_airtable(query=query, tier=tier, limit=limit, offset=offset)


@router.get("/stats")
async def get_client_stats(user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    """Estadísticas globales de clientes desde Airtable."""
    try:
        from src.infrastructure.mcp.airtable_client import airtable_client
        if not airtable_client._api or not AIRTABLE_BASE_ID:
            raise RuntimeError("Airtable no configurado")

        response = await airtable_client.list_records(
            base_id=AIRTABLE_BASE_ID,
            table_name=CLIENTS_TABLE,
            max_records=1000,
        )
        all_records = response.get("records", [])
        stats = {"total_clientes": len(all_records), "clientes_vip": 0, "clientes_premium": 0,
                 "clientes_frecuentes": 0, "clientes_regulares": 0, "tasa_no_show_promedio": 0.0, "reservas_mes_actual": 0}
        total_no_show = 0
        total_reservas = 0
        for r in all_records:
            f = r.get("fields", {})
            tier = f.get(FIELD_MAP["tier"], "Regular")
            if tier == "VIP":
                stats["clientes_vip"] += 1
            elif tier == "Premium":
                stats["clientes_premium"] += 1
            elif tier == "Frecuente":
                stats["clientes_frecuentes"] += 1
            else:
                stats["clientes_regulares"] += 1
            total_no_show += f.get("No Shows", 0)
            total_reservas += f.get(FIELD_MAP["total_reservas"], 0)
        if total_reservas > 0:
            stats["tasa_no_show_promedio"] = round(total_no_show / total_reservas * 100, 1)
        return stats

    except Exception as e:
        logger.warning(f"Airtable stats no disponible: {e}")
        return {"total_clientes": 0, "clientes_vip": 0, "clientes_premium": 0,
                "clientes_frecuentes": 0, "clientes_regulares": 0,
                "tasa_no_show_promedio": 0.0, "reservas_mes_actual": 0,
                "source": "unavailable"}


@router.get("/search")
async def search_clients(
    q: str = "",
    user: TokenData = Depends(require_role(ALLOWED_ROLES))
):
    """Búsqueda rápida de clientes por nombre o teléfono."""
    if len(q) < 2:
        return []
    result = await _get_clients_from_airtable(query=q, limit=20)
    return result.get("customers", [])


@router.get("/export")
async def export_clients(user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    """Exporta clientes en CSV."""
    result = await _get_clients_from_airtable(limit=1000)
    csv_lines = ["nombre,telefono,email,tier,total_reservas,ultima_reserva"]
    for c in result.get("customers", []):
        csv_lines.append(
            f"{c['nombre']},{c['telefono']},{c.get('email','')},{c['tier']},{c['total_reservas']},{c.get('ultima_reserva','')}"
        )
    return PlainTextResponse(
        "\n".join(csv_lines),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=clientes.csv"}
    )


@router.get("/{customer_id}")
async def get_client(customer_id: str, user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    """Obtiene un cliente específico de Airtable por su record ID."""
    try:
        from src.infrastructure.mcp.airtable_client import airtable_client
        record = await airtable_client.get_record(
            base_id=AIRTABLE_BASE_ID,
            table_name=CLIENTS_TABLE,
            record_id=customer_id,
        )
        if not record:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        return _record_to_client(record)
    except Exception as e:
        logger.warning(f"Error obteniendo cliente {customer_id}: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Cliente no encontrado")


@router.put("/{customer_id}")
async def update_client(customer_id: str, data: dict, user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    """Actualiza un cliente en Airtable."""
    try:
        from src.infrastructure.mcp.airtable_client import airtable_client
        # Construir campos a actualizar (solo los permitidos)
        fields = {}
        if "tier" in data:
            fields[FIELD_MAP["tier"]] = data["tier"]
        if "notas_staff" in data:
            fields[FIELD_MAP["notas"]] = data["notas_staff"]
        if "email" in data:
            fields[FIELD_MAP["email"]] = data["email"]
        updated = await airtable_client.update_record(
            base_id=AIRTABLE_BASE_ID,
            table_name=CLIENTS_TABLE,
            record_id=customer_id,
            fields=fields,
        )
        return _record_to_client(updated)
    except Exception as e:
        logger.error(f"Error actualizando cliente {customer_id}: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Error al actualizar cliente")


@router.put("/{customer_id}/tier")
async def update_client_tier(
    customer_id: str,
    data: dict,
    user: TokenData = Depends(require_role(ADMIN_ROLES))
):
    """Actualiza el tier de un cliente."""
    try:
        from src.infrastructure.mcp.airtable_client import airtable_client
        tier = data.get("tier", "Regular")
        if tier not in ["Regular", "Frecuente", "VIP", "Premium"]:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Tier inválido. Valores: Regular, Frecuente, VIP, Premium")
        await airtable_client.update_record(
            base_id=AIRTABLE_BASE_ID,
            table_name=CLIENTS_TABLE,
            record_id=customer_id,
            fields={FIELD_MAP["tier"]: tier},
        )
        return {"id": customer_id, "tier": tier, "updated": True}
    except Exception as e:
        logger.error(f"Error actualizando tier de {customer_id}: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Error al actualizar tier")


@router.get("/{customer_id}/reservations")
async def get_client_reservations(
    customer_id: str,
    limit: int = Query(20, ge=1, le=100),
    user: TokenData = Depends(require_role(ALLOWED_ROLES))
):
    """Obtiene historial de reservas de un cliente desde Airtable."""
    try:
        from src.infrastructure.mcp.airtable_client import airtable_client
        # Buscar reservas donde el cliente esté vinculado por ID o teléfono
        # Primero obtain the client record to get the phone
        client_record = await airtable_client.get_record(
            base_id=AIRTABLE_BASE_ID,
            table_name=CLIENTS_TABLE,
            record_id=customer_id,
        )
        if not client_record:
            return {"reservations": [], "total": 0}

        phone = client_record.get("fields", {}).get(FIELD_MAP["telefono"], "")
        if phone:
            # Buscar reservas por teléfono
            filter_formula = f"{{Teléfono}} = '{phone}'"
            response = await airtable_client.list_records(
                base_id=AIRTABLE_BASE_ID,
                table_name=RESERVATIONS_TABLE,
                max_records=limit,
                filterByFormula=filter_formula,
                sort=[{"field": "Fecha", "direction": "desc"}],
            )
            records = response.get("records", [])
            reservations = []
            for r in records:
                f = r.get("fields", {})
                reservations.append({
                    "id": r.get("id"),
                    "customer_id": customer_id,
                    "fecha": f.get("Fecha", ""),
                    "hora": f.get("Hora", ""),
                    "pax": f.get("Pax", f.get("Comensales", 0)),
                    "estado": f.get("Estado", ""),
                    "canal": f.get("Canal", ""),
                    "created_at": r.get("createdTime", ""),
                })
            return {"reservations": reservations, "total": len(reservations)}

    except Exception as e:
        logger.warning(f"Error obteniendo reservas de cliente {customer_id}: {e}")

    return {"reservations": [], "total": 0}


@router.get("/{customer_id}/preferences")
async def get_client_preferences(customer_id: str, user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    """Obtiene preferencias de un cliente."""
    return []


@router.post("/{customer_id}/preferences")
async def add_client_preference(customer_id: str, data: dict, user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    """Añade una preferencia a un cliente."""
    return {"id": f"pref-{datetime.now().timestamp()}", "customer_id": customer_id, **data, "created_at": datetime.now().isoformat()}


@router.delete("/{customer_id}/preferences/{preference_id}")
async def delete_client_preference(customer_id: str, preference_id: str, user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    return {"deleted": True}


@router.get("/{customer_id}/notes")
async def get_client_notes(customer_id: str, user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    """Obtiene notas de staff sobre un cliente."""
    return []


@router.post("/{customer_id}/notes")
async def add_client_note(customer_id: str, data: dict, user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    """Añade una nota de staff a un cliente."""
    return {
        "id": f"note-{datetime.now().timestamp()}",
        "customer_id": customer_id,
        "staff_user_id": user.user_id,
        "staff_user_name": user.nombre,
        **data,
        "created_at": datetime.now().isoformat()
    }


@router.put("/{customer_id}/notes/{note_id}")
async def update_client_note(customer_id: str, note_id: str, data: dict, user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    return {"id": note_id, "customer_id": customer_id, **data}


@router.delete("/{customer_id}/notes/{note_id}")
async def delete_client_note(customer_id: str, note_id: str, user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    return {"deleted": True}
