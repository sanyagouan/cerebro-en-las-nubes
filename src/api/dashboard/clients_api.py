"""
API de Clientes para Dashboard.

Gestiona clientes utilizando las 3 tablas dedicadas en Airtable:
- Clientes (tblPcVRnFTKDu7Z9t)
- ClientePreferencias (tbl6xjlRuyJZMmzOV)
- ClienteNotas (tbl5RZ31kxSOkGe0U)

Base Airtable: appQ2ZXAR68cqDmJt
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from src.core.entities.cliente import Cliente, ClientePreferencia, ClienteNota
from src.application.services.cliente_service import ClienteService
from src.application.services.auth_service import TokenData, require_role
from pydantic import BaseModel

router = APIRouter(prefix="/clients", tags=["Clientes"])

# Roles permitidos (siguiendo convenciones del sistema)
READ_ROLES = ["administradora", "encargada", "tecnico"]  # Lectura
WRITE_ROLES = ["administradora", "tecnico"]  # Escritura

# ========== DEPENDENCY INJECTION ==========

def get_cliente_service():
    """Retorna instancia del servicio de clientes."""
    return ClienteService()

# ========== SCHEMAS DE REQUEST ==========

class ClienteCreate(BaseModel):
    """Schema para crear cliente."""
    nombre: str
    telefono: str
    email: Optional[str] = None
    notas_generales: Optional[str] = None

class ClienteUpdate(BaseModel):
    """Schema para actualizar cliente."""
    nombre: Optional[str] = None
    email: Optional[str] = None
    total_visitas: Optional[int] = None
    notas_generales: Optional[str] = None

class PreferenciaCreate(BaseModel):
    """Schema para crear preferencia.
    
    Note:
        ⚠️ La tabla ClientePreferencias NO tiene campo Es_Importante.
        Ese campo solo existe en la tabla ClienteNotas.
    """
    tipo: str
    descripcion: str

class NotaCreate(BaseModel):
    """Schema para crear nota."""
    contenido: str
    staff_nombre: str = "Sistema"

# ========== ENDPOINTS CLIENTES ==========

@router.get("", response_model=List[Cliente])
async def list_clientes(
    include_relations: bool = Query(False, description="Incluir preferencias y notas"),
    current_user: TokenData = Depends(require_role(READ_ROLES)),
    service: ClienteService = Depends(get_cliente_service)
):
    """Lista todos los clientes.
    
    Query Params:
        include_relations: Si true, incluye preferencias y notas (más lento)
    
    Returns:
        Lista de clientes
    
    Ejemplo:
        GET /dashboard/clients
        GET /dashboard/clients?include_relations=true
    """
    try:
        return await service.list_all(include_relations=include_relations)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listando clientes: {str(e)}"
        )

@router.get("/{phone}", response_model=Cliente)
async def get_cliente(
    phone: str,
    current_user: TokenData = Depends(require_role(READ_ROLES)),
    service: ClienteService = Depends(get_cliente_service)
):
    """Obtiene un cliente por teléfono.
    
    Path Params:
        phone: Teléfono en formato +34XXXXXXXXX
    
    Returns:
        Cliente con preferencias y notas incluidas
    
    Ejemplo:
        GET /dashboard/clients/+34600000000
    """
    try:
        cliente = await service.get_by_phone(phone, include_relations=True)
        
        if not cliente:
            raise HTTPException(
                status_code=404,
                detail=f"Cliente con teléfono {phone} no encontrado"
            )
        
        return cliente
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo cliente: {str(e)}"
        )

@router.post("", response_model=Cliente, status_code=201)
async def create_cliente(
    data: ClienteCreate,
    current_user: TokenData = Depends(require_role(WRITE_ROLES)),
    service: ClienteService = Depends(get_cliente_service)
):
    """Crea un nuevo cliente.
    
    Body:
        nombre: Nombre completo
        telefono: Teléfono E.164 (+34XXXXXXXXX)
        email: Email (opcional)
        notas_generales: Notas (opcional)
    
    Returns:
        Cliente creado
    
    Ejemplo Body:
        {
            "nombre": "Juan Pérez",
            "telefono": "+34600123456",
            "email": "juan@example.com",
            "notas_generales": "Cliente VIP"
        }
    """
    try:
        cliente_data = data.dict()
        return await service.create(cliente_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creando cliente: {str(e)}"
        )

@router.put("/{phone}", response_model=Cliente)
async def update_cliente(
    phone: str,
    updates: ClienteUpdate,
    current_user: TokenData = Depends(require_role(WRITE_ROLES)),
    service: ClienteService = Depends(get_cliente_service)
):
    """Actualiza un cliente existente.
    
    Path Params:
        phone: Teléfono del cliente
    
    Body:
        Campos a actualizar (solo los proporcionados se actualizarán)
    
    Returns:
        Cliente actualizado
    
    Ejemplo Body:
        {
            "email": "nuevo@example.com",
            "notas_generales": "Actualización de notas"
        }
    """
    try:
        # Buscar cliente por teléfono
        cliente = await service.get_by_phone(phone, include_relations=False)
        
        if not cliente:
            raise HTTPException(
                status_code=404,
                detail=f"Cliente {phone} no encontrado"
            )
        
        # Actualizar solo campos proporcionados
        updates_dict = {k: v for k, v in updates.dict().items() if v is not None}
        return await service.update(cliente.id, updates_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error actualizando cliente: {str(e)}"
        )

# ========== ENDPOINTS PREFERENCIAS ==========

@router.post("/{phone}/preferencias", response_model=ClientePreferencia, status_code=201)
async def add_preferencia(
    phone: str,
    data: PreferenciaCreate,
    current_user: TokenData = Depends(require_role(WRITE_ROLES)),
    service: ClienteService = Depends(get_cliente_service)
):
    """Añade preferencia a un cliente.
    
    Path Params:
        phone: Teléfono del cliente
    
    Body:
        tipo_preferencia: Mesa, Comida, Alergias, Ubicación, Otros
        descripcion: Descripción de la preferencia
        es_importante: True si es crítica (ej: alergia grave)
    
    Returns:
        Preferencia creada
    
    Ejemplo Body:
        {
            "tipo_preferencia": "Alergias",
            "descripcion": "Intolerancia al gluten",
            "es_importante": true
        }
    
    Nota: es_importante se convierte a "Sí"/"No" en Airtable
    """
    try:
        # Buscar cliente
        cliente = await service.get_by_phone(phone, include_relations=False)
        
        if not cliente:
            raise HTTPException(
                status_code=404,
                detail=f"Cliente {phone} no encontrado"
            )
        
        # Añadir preferencia
        return await service.add_preferencia(cliente.id, data.dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error añadiendo preferencia: {str(e)}"
        )

# ========== ENDPOINTS NOTAS ==========

@router.post("/{phone}/notas", response_model=ClienteNota, status_code=201)
async def add_nota(
    phone: str,
    data: NotaCreate,
    current_user: TokenData = Depends(require_role(WRITE_ROLES)),
    service: ClienteService = Depends(get_cliente_service)
):
    """Añade nota a un cliente.
    
    Path Params:
        phone: Teléfono del cliente
    
    Body:
        nota: Texto de la nota
        autor: Usuario que creó la nota (default: Sistema)
    
    Returns:
        Nota creada
    
    Ejemplo Body:
        {
            "nota": "Cliente prefiere mesa en la terraza",
            "autor": "Alba"
        }
    """
    try:
        # Buscar cliente
        cliente = await service.get_by_phone(phone, include_relations=False)
        
        if not cliente:
            raise HTTPException(
                status_code=404,
                detail=f"Cliente {phone} no encontrado"
            )
        
        # Añadir nota
        return await service.add_nota(cliente.id, data.dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error añadiendo nota: {str(e)}"
        )
