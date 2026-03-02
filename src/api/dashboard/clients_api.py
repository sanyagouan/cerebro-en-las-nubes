"""
API endpoints para Clientes (CRM) del Dashboard.
Provee datos mock hasta integración completa con Airtable.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from src.application.services.auth_service import TokenData, require_role

router = APIRouter(prefix="/api/clients", tags=["clients"])

ALLOWED_ROLES = ["administradora", "encargada", "admin", "manager"]


def mock_customer(i: int) -> dict:
    tiers = ["Regular", "Frecuente", "VIP", "Premium"]
    nombres = ["García López", "Martínez Ruiz", "Fernández Sanz", "González Pérez", "Rodríguez Díaz"]
    return {
        "id": f"cli-{i}",
        "nombre": nombres[i % len(nombres)],
        "telefono": f"+346001{i:05d}",
        "email": f"cliente{i}@email.com",
        "tier": tiers[i % len(tiers)],
        "total_reservas": 5 + i,
        "reservas_completadas": 4 + (i % 3),
        "reservas_canceladas": i % 2,
        "no_shows": 0,
        "primera_reserva": (datetime.now() - timedelta(days=200 + i * 10)).strftime("%Y-%m-%d"),
        "ultima_reserva": (datetime.now() - timedelta(days=i * 5)).strftime("%Y-%m-%d"),
        "notas_staff": "Cliente habitual, prefiere terraza." if i % 3 == 0 else None,
        "preferencias": [],
        "created_at": (datetime.now() - timedelta(days=200 + i * 10)).isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


@router.get("")
async def list_clients(
    query: str = None,
    tier: str = None,
    limit: int = 50,
    offset: int = 0,
    user: TokenData = Depends(require_role(ALLOWED_ROLES))
):
    """Lista clientes del CRM."""
    customers = [mock_customer(i) for i in range(20)]
    if query:
        customers = [c for c in customers if query.lower() in c["nombre"].lower()]
    if tier:
        customers = [c for c in customers if c["tier"] == tier]
    return {"customers": customers[offset:offset + limit], "total": len(customers)}


@router.get("/stats")
async def get_client_stats(user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    """Estadísticas globales de clientes."""
    return {
        "total_clientes": 142,
        "clientes_vip": 12,
        "clientes_premium": 5,
        "clientes_frecuentes": 35,
        "clientes_regulares": 90,
        "tasa_no_show_promedio": 3.2,
        "reservas_mes_actual": 48,
    }


@router.get("/search")
async def search_clients(q: str = "", user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    """Búsqueda rápida de clientes."""
    if len(q) < 2:
        return []
    customers = [mock_customer(i) for i in range(20)]
    return [c for c in customers if q.lower() in c["nombre"].lower() or q in c["telefono"]]


@router.get("/export")
async def export_clients(user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    """Exporta clientes en CSV (mock)."""
    from fastapi.responses import PlainTextResponse
    csv = "nombre,telefono,tier,total_reservas\n"
    for i in range(20):
        c = mock_customer(i)
        csv += f"{c['nombre']},{c['telefono']},{c['tier']},{c['total_reservas']}\n"
    return PlainTextResponse(csv, media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=clientes.csv"})


@router.get("/{customer_id}")
async def get_client(customer_id: str, user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    idx = int(customer_id.replace("cli-", "")) if customer_id.startswith("cli-") else 0
    return mock_customer(idx % 20)


@router.put("/{customer_id}")
async def update_client(customer_id: str, data: dict, user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    c = mock_customer(0)
    return {**c, **data, "id": customer_id}


@router.put("/{customer_id}/tier")
async def update_client_tier(customer_id: str, data: dict, user: TokenData = Depends(require_role(["administradora", "admin"]))):
    return {"id": customer_id, "tier": data.get("tier"), "updated": True}


@router.get("/{customer_id}/reservations")
async def get_client_reservations(customer_id: str, limit: int = 20, user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    reservations = [
        {
            "id": f"res-{customer_id}-{i}",
            "customer_id": customer_id,
            "fecha": (datetime.now() - timedelta(days=i * 15)).strftime("%Y-%m-%d"),
            "hora": "21:00" if i % 2 == 0 else "14:00",
            "pax": 2 + (i % 4),
            "estado": "Completada" if i > 0 else "Confirmada",
            "canal": "VAPI" if i % 2 == 0 else "WhatsApp",
            "created_at": (datetime.now() - timedelta(days=i * 15 + 2)).isoformat(),
        }
        for i in range(min(limit, 8))
    ]
    return {"reservations": reservations, "total": len(reservations)}


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
    return {"id": f"note-{datetime.now().timestamp()}", "customer_id": customer_id, "staff_user_id": user.user_id,
            "staff_user_name": user.nombre, **data, "created_at": datetime.now().isoformat()}


@router.put("/{customer_id}/notes/{note_id}")
async def update_client_note(customer_id: str, note_id: str, data: dict, user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    return {"id": note_id, "customer_id": customer_id, **data}


@router.delete("/{customer_id}/notes/{note_id}")
async def delete_client_note(customer_id: str, note_id: str, user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    return {"deleted": True}
