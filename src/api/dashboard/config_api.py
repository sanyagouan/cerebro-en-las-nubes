"""
API endpoints para Configuración del Dashboard.
Provee datos mock del horario, turnos, festivos y usuarios del restaurante.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from src.application.services.auth_service import TokenData, require_role

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("/schedule")
async def get_schedule(user: TokenData = Depends(require_role(["administradora", "encargada"]))):
    """Horario semanal del restaurante."""
    days = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    return {
        "schedule": [
            {
                "day": day,
                "is_open": day not in ["lunes"],
                "lunch_start": "13:30",
                "lunch_end": "16:00",
                "dinner_start": "20:30",
                "dinner_end": "23:30",
            }
            for day in days
        ]
    }


@router.put("/schedule")
async def update_schedule(data: dict, user: TokenData = Depends(require_role(["administradora"]))):
    return {"updated": True, "schedule": data.get("schedule", [])}


@router.get("/holidays")
async def get_holidays(user: TokenData = Depends(require_role(["administradora", "encargada"]))):
    """Festivos y días especiales."""
    return {
        "holidays": [
            {
                "id": "hol-1",
                "date": f"{datetime.now().year}-12-25",
                "name": "Navidad",
                "is_closed": True,
            },
            {
                "id": "hol-2",
                "date": f"{datetime.now().year}-01-01",
                "name": "Año Nuevo",
                "is_closed": True,
            },
            {
                "id": "hol-3",
                "date": f"{datetime.now().year}-08-15",
                "name": "Asunción",
                "is_closed": False,
                "special_hours": {
                    "dinner_start": "21:00",
                    "dinner_end": "23:00",
                },
            },
        ]
    }


@router.post("/holidays")
async def create_holiday(data: dict, user: TokenData = Depends(require_role(["administradora"]))):
    return {"id": f"hol-{datetime.now().timestamp()}", **data}


@router.put("/holidays/{holiday_id}")
async def update_holiday(holiday_id: str, data: dict, user: TokenData = Depends(require_role(["administradora"]))):
    return {"id": holiday_id, **data, "updated": True}


@router.delete("/holidays/{holiday_id}")
async def delete_holiday(holiday_id: str, user: TokenData = Depends(require_role(["administradora"]))):
    return {"deleted": True}


@router.get("/shifts")
async def get_shifts(user: TokenData = Depends(require_role(["administradora", "encargada"]))):
    """Turnos del restaurante."""
    return {
        "shifts": [
            {
                "id": "shift-almuerzo",
                "name": "almuerzo",
                "default_start": "13:30",
                "default_end": "16:00",
                "max_capacity": 60,
                "is_active": True,
            },
            {
                "id": "shift-cena",
                "name": "cena",
                "default_start": "20:30",
                "default_end": "23:30",
                "max_capacity": 80,
                "is_active": True,
            },
        ]
    }


@router.put("/shifts/{shift_id}")
async def update_shift(shift_id: str, data: dict, user: TokenData = Depends(require_role(["administradora"]))):
    return {"id": shift_id, **data, "updated": True}


@router.get("/capacity")
async def get_capacity(user: TokenData = Depends(require_role(["administradora", "encargada"]))):
    """Configuración de capacidad."""
    return {
        "max_simultaneous_reservations": 20,
        "max_party_size": 12,
        "min_party_size": 1,
        "overbooking_percentage": 0,
    }


@router.put("/capacity")
async def update_capacity(data: dict, user: TokenData = Depends(require_role(["administradora"]))):
    return {**data, "updated": True}


@router.get("/timings")
async def get_timings(user: TokenData = Depends(require_role(["administradora", "encargada"]))):
    """Tiempos de ocupación de mesa por tamaño de grupo."""
    return {
        "timings": [
            {"party_size_min": 1, "party_size_max": 2, "duration_minutes": 90},
            {"party_size_min": 3, "party_size_max": 4, "duration_minutes": 105},
            {"party_size_min": 5, "party_size_max": 6, "duration_minutes": 120},
            {"party_size_min": 7, "party_size_max": 12, "duration_minutes": 150},
        ]
    }


@router.put("/timings")
async def update_timings(data: dict, user: TokenData = Depends(require_role(["administradora"]))):
    return {"timings": data.get("timings", []), "updated": True}


from src.infrastructure.repositories.user_repository import user_repository
from src.application.services.auth_service import auth_service

@router.get("/users")
async def get_users(user: TokenData = Depends(require_role(["administradora"]))):
    """Usuarios reales del sistema desde Airtable."""
    db_users = await user_repository.list_all()
    # Mapeo a frontend: usuario -> email, nombre -> name, etc.
    users_mapped = []
    for u in db_users:
        users_mapped.append({
            "id": u.id,
            "name": u.nombre,
            "email": u.usuario,
            "phone": u.telefono or "",
            "role": u.rol.value,
            "is_active": u.activo,
            "created_at": "2026-01-01T00:00:00"  # Opcional, db no lo expone siempre
        })
    return {"users": users_mapped}


@router.post("/users")
async def create_user(data: dict, user: TokenData = Depends(require_role(["administradora"]))):
    # Generar hash de la contraseña (si viene vacía, por defecto 'admin123')
    raw_password = data.get("password") or "admin123"
    password_hash = await auth_service.hash_password(raw_password)
    
    nuevo = await user_repository.create(
        usuario=data.get("email"),
        nombre=data.get("name"),
        password_hash=password_hash,
        rol=data.get("role", "camarero").lower(),
        telefono=data.get("phone")
    )
    if data.get("is_active") is False:
        await user_repository.deactivate(nuevo.id)
    
    return {
        "id": nuevo.id,
        "name": nuevo.nombre,
        "email": nuevo.usuario,
        "phone": nuevo.telefono,
        "role": nuevo.rol.value,
        "is_active": data.get("is_active", True)
    }


@router.put("/users/{user_id}")
async def update_user(user_id: str, data: dict, user: TokenData = Depends(require_role(["administradora"]))):
    updates = {
        "usuario": data.get("email"),
        "nombre": data.get("name"),
        "rol": data.get("role", "").lower(),
        "telefono": data.get("phone"),
        "activo": data.get("is_active")
    }
    # Filtrar None values
    updates = {k: v for k, v in updates.items() if v is not None}
    
    updated_user = await user_repository.update(user_id, **updates)
    
    # Si viene password e input no esta vacio, actualizamos hash
    pwd = data.get("password")
    if pwd and pwd.strip():
        new_hash = await auth_service.hash_password(pwd.strip())
        await user_repository.update_password(user_id, new_hash)

    return {"id": user_id, "updated": True}


@router.delete("/users/{user_id}")
async def delete_user(user_id: str, user: TokenData = Depends(require_role(["administradora"]))):
    # En Airtable lo marcamos como inactivo (soft delete)
    await user_repository.deactivate(user_id)
    return {"deleted": True}
