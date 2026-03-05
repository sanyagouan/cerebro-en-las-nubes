from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from src.application.services.auth_service import TokenData, require_role
from src.infrastructure.repositories.user_repository import user_repository
from src.infrastructure.repositories.shift_repository import shift_repository
from src.infrastructure.repositories.holiday_repository import holiday_repository
from src.infrastructure.repositories.config_repository import config_repository
from src.application.services.auth_service import auth_service

router = APIRouter(prefix="/api/config", tags=["config"])

# Roles permitidos para lectura general
READ_ROLES = ["administradora", "encargada", "tecnico"]
# Roles permitidos para escritura
WRITE_ROLES = ["administradora", "tecnico"]

# Mapeo de roles Dashboard UI -> Airtable DB
ROLE_MAP_UI_TO_DB = {
    "Admin": "administradora",
    "Manager": "encargada",
    "Waiter": "camarero",
    "Cook": "cocina",
    "Technician": "tecnico"
}

# Mapeo de roles Airtable DB -> Dashboard UI
ROLE_MAP_DB_TO_UI = {v: k for k, v in ROLE_MAP_UI_TO_DB.items()}

@router.get("/schedule")
async def get_schedule(user: TokenData = Depends(require_role(READ_ROLES))):
    """Horario semanal basado en la configuración real de Airtable."""
    schedule = await config_repository.get_param("schedule", default=[])
    if not schedule:
        # Fallback inicial si la tabla está vacía
        days = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        schedule = [
            {"day": d, "is_open": d != "lunes", "lunch_start": "13:30", "lunch_end": "16:00", 
             "dinner_start": "20:30", "dinner_end": "23:30"} for d in days
        ]
    return {"schedule": schedule}

@router.put("/schedule")
async def update_schedule(data: dict, user: TokenData = Depends(require_role(WRITE_ROLES))):
    """Actualiza el horario semanal en Airtable."""
    success = await config_repository.set_param("schedule", data.get("schedule", []), "JSON")
    return {"updated": success}

@router.get("/holidays")
async def get_holidays(user: TokenData = Depends(require_role(READ_ROLES))):
    """Festivos reales desde la tabla 'Días Especiales' de Airtable."""
    holidays = await holiday_repository.list_all()
    return {"holidays": holidays}

@router.post("/holidays")
async def create_holiday(data: dict, user: TokenData = Depends(require_role(WRITE_ROLES))):
    """Crea un nuevo festivo en Airtable."""
    new_id = await holiday_repository.create(data)
    return {"id": new_id, **data}

@router.put("/holidays/{holiday_id}")
async def update_holiday(holiday_id: str, data: dict, user: TokenData = Depends(require_role(WRITE_ROLES))):
    """Actualiza un festivo existente."""
    success = await holiday_repository.update(holiday_id, data)
    return {"id": holiday_id, "updated": success}

@router.delete("/holidays/{holiday_id}")
async def delete_holiday(holiday_id: str, user: TokenData = Depends(require_role(WRITE_ROLES))):
    """Elimina un festivo de Airtable."""
    success = await holiday_repository.delete(holiday_id)
    return {"deleted": success}

@router.get("/shifts")
async def get_shifts(user: TokenData = Depends(require_role(READ_ROLES))):
    """Turnos reales desde la tabla 'Turnos' de Airtable."""
    shifts = await shift_repository.list_all()
    return {"shifts": shifts}

@router.put("/shifts/{shift_id}")
async def update_shift(shift_id: str, data: dict, user: TokenData = Depends(require_role(WRITE_ROLES))):
    """Actualiza la configuración de un turno en Airtable."""
    success = await shift_repository.update(shift_id, data)
    return {"id": shift_id, "updated": success}

@router.get("/capacity")
async def get_capacity(user: TokenData = Depends(require_role(READ_ROLES))):
    """Configuración de capacidad persistente en Airtable."""
    capacity = await config_repository.get_param("capacity", default={
        "max_simultaneous_reservations": 20,
        "max_party_size": 12,
        "min_party_size": 1,
        "overbooking_percentage": 0,
    })
    return capacity

@router.put("/capacity")
async def update_capacity(data: dict, user: TokenData = Depends(require_role(WRITE_ROLES))):
    """Actualiza los límites de capacidad en Airtable."""
    success = await config_repository.set_param("capacity", data, "JSON")
    return {**data, "updated": success}

@router.get("/timings")
async def get_timings(user: TokenData = Depends(require_role(READ_ROLES))):
    """Tiempos de ocupación de mesa persistentes en Airtable."""
    timings = await config_repository.get_param("timings", default=[
        {"party_size_min": 1, "party_size_max": 2, "duration_minutes": 90},
        {"party_size_min": 3, "party_size_max": 4, "duration_minutes": 105},
        {"party_size_min": 5, "party_size_max": 6, "duration_minutes": 120},
        {"party_size_min": 7, "party_size_max": 12, "duration_minutes": 150},
    ])
    return {"timings": timings}

@router.put("/timings")
async def update_timings(data: dict, user: TokenData = Depends(require_role(WRITE_ROLES))):
    """Actualiza los rangos de tiempo en Airtable."""
    success = await config_repository.set_param("timings", data.get("timings", []), "JSON")
    return {"timings": data.get("timings", []), "updated": success}

@router.get("/users")
async def get_users(user: TokenData = Depends(require_role(["administradora", "tecnico"]))):
    """Usuarios reales desde la tabla 'Usuarios' de Airtable."""
    db_users = await user_repository.list_all()
    users_mapped = []
    # Mapeo de roles usando el mapa global
    for u in db_users:
        users_mapped.append({
            "id": u.id,
            "name": u.nombre,
            "email": u.usuario,
            "phone": u.telefono or "",
            "role": ROLE_MAP_DB_TO_UI.get(u.rol.value, "Waiter"),
            "is_active": u.activo
        })
    return {"users": users_mapped}

@router.post("/users")
async def create_user(data: dict, user: TokenData = Depends(require_role(["administradora", "tecnico"]))):
    """Crea un nuevo usuario en Airtable con contraseña hasheada."""
    raw_password = data.get("password") or "admin123"
    password_hash = await auth_service.hash_password(raw_password)
    
    # Mapeo de roles UI -> Airtable
    db_role = ROLE_MAP_UI_TO_DB.get(data.get("role"), "camarero")

    nuevo = await user_repository.create(
        usuario=data.get("email"),
        nombre=data.get("name"),
        password_hash=password_hash,
        rol=db_role,
        telefono=data.get("phone")
    )
    return {"id": nuevo.id, "success": True}

@router.put("/users/{user_id}")
async def update_user(user_id: str, data: dict, user: TokenData = Depends(require_role(["administradora", "tecnico"]))):
    """Actualiza datos de un usuario en Airtable."""
    updates = {}
    if data.get("email"): updates["usuario"] = data.get("email")
    if data.get("name"): updates["nombre"] = data.get("name")
    if data.get("role"): updates["rol"] = ROLE_MAP_UI_TO_DB.get(data.get("role"))
    if data.get("phone"): updates["telefono"] = data.get("phone")
    if "is_active" in data: updates["activo"] = data.get("is_active")

    await user_repository.update(user_id, **updates)
    
    # Actualizar contraseña si se proporciona una nueva
    pwd = data.get("password")
    if pwd and pwd.strip():
        new_hash = await auth_service.hash_password(pwd.strip())
        await user_repository.update_password(user_id, new_hash)

    return {"id": user_id, "updated": True}

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, user: TokenData = Depends(require_role(["administradora", "tecnico"]))):
    """Desactiva un usuario en Airtable."""
    await user_repository.deactivate(user_id)
    return {"deleted": True}
