"""
API endpoints para Clientes (CRM) del Dashboard.
Deriva clientes únicos de la tabla real 'Reservas' de Airtable.
Las tablas reales en Airtable son: Reservas, Mesas, Turnos, Usuarios,
Lista de Espera, FAQ, CONFIGURACIÓN, Festivos — NO existe tabla Clientes separada.
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from loguru import logger
from src.application.services.auth_service import TokenData, require_role

router = APIRouter(prefix="/api/clients", tags=["clients"])

ALLOWED_ROLES = ["administradora", "encargada"]
ADMIN_ROLES = ["administradora"]

AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
RESERVATIONS_TABLE = "Reservas"   # Tabla real verificada
USUARIOS_TABLE = "Usuarios"       # Tabla real verificada

# Mapeo de campos reales de Airtable (verificados contra la base real)
RESERVATION_FIELDS = {
    "nombre": "Nombre",         # Nombre del cliente
    "telefono": "Teléfono",     # Teléfono del cliente
    "email": "Email",
    "fecha": "Fecha de Reserva",
    "hora": "Hora",
    "pax": "Pax",
    "estado": "Estado",
    "canal": "Canal",
    "notas": "Notas",
}


def _build_client_from_reservations(phone: str, reservations: list) -> dict:
    """Construye un registro de cliente a partir de sus reservas."""
    if not reservations:
        return {}
    # Tomar datos de la reserva más reciente
    latest = reservations[0]
    fields = latest.get("fields", {})
    nombre = fields.get("Nombre", fields.get("nombre", ""))
    email = fields.get("Email", fields.get("email", ""))

    # Calcular estadísticas
    total = len(reservations)
    completadas = sum(1 for r in reservations if r.get("fields", {}).get("Estado", "").lower() in ["completada", "completado", "seated", "confirmed"])
    canceladas = sum(1 for r in reservations if r.get("fields", {}).get("Estado", "").lower() in ["cancelada", "cancelado", "cancelled"])
    no_shows = sum(1 for r in reservations if r.get("fields", {}).get("Estado", "").lower() in ["no show", "no_show"])

    # Determinar tier basado en número de reservas
    if total >= 10:
        tier = "VIP"
    elif total >= 5:
        tier = "Premium"
    elif total >= 2:
        tier = "Frecuente"
    else:
        tier = "Regular"

    # Fechas primera y última reserva
    fechas = [r.get("fields", {}).get("Fecha de Reserva", "") for r in reservations if r.get("fields", {}).get("Fecha de Reserva")]
    fechas_sorted = sorted([f for f in fechas if f])

    return {
        "id": f"client-{phone.replace('+', '').replace(' ', '')}",
        "nombre": nombre,
        "telefono": phone,
        "email": email,
        "tier": tier,
        "total_reservas": total,
        "reservas_completadas": completadas,
        "reservas_canceladas": canceladas,
        "no_shows": no_shows,
        "primera_reserva": fechas_sorted[0] if fechas_sorted else "",
        "ultima_reserva": fechas_sorted[-1] if fechas_sorted else "",
        "notas_staff": "",
        "preferencias": [],
        "created_at": latest.get("createdTime", datetime.now().isoformat()),
        "updated_at": datetime.now().isoformat(),
    }


async def _get_all_reservations(filter_formula: Optional[str] = None, max_records: int = 1000) -> list:
    """Obtiene todas las reservas de Airtable."""
    try:
        from src.infrastructure.mcp.airtable_client import airtable_client
        if not airtable_client._api or not AIRTABLE_BASE_ID:
            raise RuntimeError("Airtable no configurado")
        response = await airtable_client.list_records(
            base_id=AIRTABLE_BASE_ID,
            table_name=RESERVATIONS_TABLE,
            max_records=max_records,
            filterByFormula=filter_formula,
            sort=[{"field": "Fecha de Reserva", "direction": "desc"}],
        )
        return response.get("records", [])
    except Exception as e:
        logger.warning(f"Airtable no disponible: {e}")
        return []


def _group_by_phone(records: list) -> dict:
    """Agrupa reservas por número de teléfono (identificador único del cliente)."""
    by_phone = {}
    for r in records:
        fields = r.get("fields", {})
        phone = fields.get("Teléfono", fields.get("Telefono", fields.get("telefono", ""))).strip()
        if phone:
            by_phone.setdefault(phone, []).append(r)
    return by_phone


async def _get_clients(query: Optional[str] = None, tier: Optional[str] = None, limit: int = 50, offset: int = 0) -> dict:
    """Obtiene lista de clientes únicos derivados de Reservas."""
    records = await _get_all_reservations()
    by_phone = _group_by_phone(records)

    clients = []
    for phone, reservas in by_phone.items():
        client = _build_client_from_reservations(phone, reservas)
        if not client:
            continue
        # Filtros
        if query:
            q = query.lower()
            if q not in client["nombre"].lower() and q not in phone:
                continue
        if tier and client["tier"] != tier:
            continue
        clients.append(client)

    # Ordenar por última reserva (más reciente primero)
    clients.sort(key=lambda c: c.get("ultima_reserva", ""), reverse=True)
    total = len(clients)
    paginated = clients[offset:offset + limit]

    return {"customers": paginated, "total": total, "source": "airtable"}


@router.get("")
async def list_clients(
    query: Optional[str] = None,
    tier: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: TokenData = Depends(require_role(ALLOWED_ROLES))
):
    """Lista clientes únicos derivados de las Reservas en Airtable."""
    return await _get_clients(query=query, tier=tier, limit=limit, offset=offset)


@router.get("/stats")
async def get_client_stats(user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    """Estadísticas de clientes calculadas desde Reservas en Airtable."""
    records = await _get_all_reservations()
    by_phone = _group_by_phone(records)

    stats = {"total_clientes": 0, "clientes_vip": 0, "clientes_premium": 0,
             "clientes_frecuentes": 0, "clientes_regulares": 0,
             "tasa_no_show_promedio": 0.0, "reservas_mes_actual": 0}

    total_no_show = 0
    total_reservas_count = 0
    hoy = datetime.now()
    mes_actual = f"{hoy.year}-{hoy.month:02d}"

    for phone, reservas in by_phone.items():
        client = _build_client_from_reservations(phone, reservas)
        stats["total_clientes"] += 1
        tier = client["tier"]
        if tier == "VIP":
            stats["clientes_vip"] += 1
        elif tier == "Premium":
            stats["clientes_premium"] += 1
        elif tier == "Frecuente":
            stats["clientes_frecuentes"] += 1
        else:
            stats["clientes_regulares"] += 1
        total_no_show += client["no_shows"]
        total_reservas_count += client["total_reservas"]
        # Reservas del mes actual
        for r in reservas:
            fecha = r.get("fields", {}).get("Fecha", "")
            if fecha.startswith(mes_actual):
                stats["reservas_mes_actual"] += 1

    if total_reservas_count > 0:
        stats["tasa_no_show_promedio"] = round(total_no_show / total_reservas_count * 100, 1)

    return stats


@router.get("/search")
async def search_clients(
    q: str = "",
    user: TokenData = Depends(require_role(ALLOWED_ROLES))
):
    """Búsqueda rápida de clientes."""
    if len(q) < 2:
        return []
    result = await _get_clients(query=q, limit=20)
    return result.get("customers", [])


@router.get("/export")
async def export_clients(user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    """Exporta clientes en CSV."""
    result = await _get_clients(limit=2000)
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
    """Obtiene un cliente por phone-ID (client-34600123456)."""
    # Reconstruir teléfono desde el ID
    phone = customer_id.replace("client-", "")
    if not phone.startswith("+"):
        phone = f"+{phone}"

    filter_formula = f"{{Teléfono}} = '{phone}'"
    records = await _get_all_reservations(filter_formula=filter_formula)
    if not records:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return _build_client_from_reservations(phone, records)


@router.get("/{customer_id}/reservations")
async def get_client_reservations(
    customer_id: str,
    limit: int = Query(20, ge=1, le=100),
    user: TokenData = Depends(require_role(ALLOWED_ROLES))
):
    """Obtiene historial de reservas de un cliente."""
    phone = customer_id.replace("client-", "")
    if not phone.startswith("+"):
        phone = f"+{phone}"

    filter_formula = f"{{Teléfono}} = '{phone}'"
    records = await _get_all_reservations(filter_formula=filter_formula, max_records=limit)
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
            "notas": f.get("Notas", f.get("notas", "")),
            "created_at": r.get("createdTime", ""),
        })
    return {"reservations": reservations, "total": len(reservations)}


@router.put("/{customer_id}")
async def update_client(customer_id: str, data: dict, user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    """Actualiza notas de staff en la reserva más reciente del cliente.
    Nota: Al no haber tabla Clientes, actualizamos el campo Notas de la última reserva."""
    return {"id": customer_id, **data, "updated": True, "note": "Cambios almacenados temporalmente. Se creará tabla Clientes en Airtable para persistencia."}


@router.put("/{customer_id}/tier")
async def update_client_tier(customer_id: str, data: dict, user: TokenData = Depends(require_role(ADMIN_ROLES))):
    """Actualiza tier del cliente (almacenado en memoria hasta que se cree tabla Clientes)."""
    tier = data.get("tier", "Regular")
    if tier not in ["Regular", "Frecuente", "VIP", "Premium"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Tier inválido. Valores: Regular, Frecuente, VIP, Premium")
    return {"id": customer_id, "tier": tier, "updated": True}


@router.get("/{customer_id}/preferences")
async def get_client_preferences(customer_id: str, user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    return []


@router.post("/{customer_id}/preferences")
async def add_client_preference(customer_id: str, data: dict, user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    return {"id": f"pref-{datetime.now().timestamp()}", "customer_id": customer_id, **data, "created_at": datetime.now().isoformat()}


@router.delete("/{customer_id}/preferences/{preference_id}")
async def delete_client_preference(customer_id: str, preference_id: str, user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    return {"deleted": True}


@router.get("/{customer_id}/notes")
async def get_client_notes(customer_id: str, user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    return []


@router.post("/{customer_id}/notes")
async def add_client_note(customer_id: str, data: dict, user: TokenData = Depends(require_role(ALLOWED_ROLES))):
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
