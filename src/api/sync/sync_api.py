"""
Endpoints para sincronización de datos.
"""
import os
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status, Request, Header
from pydantic import BaseModel
from typing import Optional, List
import logging
import hmac
import hashlib

from src.services.sync_service import sync_service, SupabaseAirtableSync
from src.api.mobile.mobile_api import get_current_user, TokenData
from src.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sync", tags=["sync"])


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verifica la firma HMAC de un webhook de Airtable.
    
    Airtable envía la firma en el header 'X-Airtable-Signature'.
    """
    if not signature or not secret:
        return False
    
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)


class SyncRequest(BaseModel):
    table: Optional[str] = None  # Si None, sincroniza todas
    full_sync: bool = False


class SyncResponse(BaseModel):
    status: str
    results: dict
    timestamp: str


class SyncHistoryResponse(BaseModel):
    history: List[dict]


@router.post("/run", response_model=SyncResponse)
async def run_sync(
    request: SyncRequest,
    background_tasks: BackgroundTasks,
    user: TokenData = Depends(get_current_user)
):
    """
    Ejecuta sincronización entre Supabase y Airtable.
    
    - **table**: Nombre de tabla específica o null para todas
    - **full_sync**: True para sincronización completa, False para incremental
    
    Requiere rol admin.
    """
    # Verificar permisos
    if user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or manager can run sync"
        )
    
    try:
        if request.table:
            # Buscar config para tabla específica
            config = next(
                (c for c in sync_service.sync_configs if c.table_name == request.table),
                None
            )
            if not config:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Table {request.table} not configured for sync"
                )
            
            result = await sync_service.sync_table(config, request.full_sync)
            results = {request.table: result}
        else:
            # Sincronizar todas
            results = await sync_service.sync_all(request.full_sync)
        
        return SyncResponse(
            status="success",
            results=results,
            timestamp=__import__("datetime").datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Sync error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}"
        )


@router.get("/history", response_model=SyncHistoryResponse)
async def get_sync_history(
    user: TokenData = Depends(get_current_user)
):
    """Obtiene historial de sincronizaciones."""
    if user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or manager can view sync history"
        )
    
    return SyncHistoryResponse(history=sync_service.get_sync_history())


@router.get("/status")
async def get_sync_status(
    user: TokenData = Depends(get_current_user)
):
    """Obtiene estado actual de sincronización."""
    if user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or manager can view sync status"
        )
    
    return {
        "configured_tables": [
            {
                "name": c.table_name,
                "direction": c.direction.value,
                "airtable_table": c.airtable_table_id,
                "supabase_table": c.supabase_table
            }
            for c in sync_service.sync_configs
        ],
        "last_syncs": sync_service.get_sync_history()[-5:]
    }


@router.post("/webhook/airtable")
async def airtable_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_airtable_signature: Optional[str] = Header(None)
):
    """
    Webhook para recibir notificaciones de cambios en Airtable.
    
    Este endpoint debe ser configurado en Airtable como webhook
    para sincronización en tiempo real.
    """
    # Obtener el secreto de webhook desde configuración
    webhook_secret = os.getenv("AIRTABLE_WEBHOOK_SECRET")
    
    # Verificar firma si está configurado el secreto
    if webhook_secret:
        payload = await request.body()
        if not verify_webhook_signature(payload, x_airtable_signature, webhook_secret):
            logger.warning("Invalid webhook signature from Airtable")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            )
    
    try:
        # Parsear payload después de verificación
        payload_data = await request.json()
        
        table_id = payload_data.get("table_id")
        changed_records = payload_data.get("changed_records", [])
        
        logger.info(f"Airtable webhook received for table {table_id}")
        
        # Buscar config por table_id
        config = next(
            (c for c in sync_service.sync_configs if c.airtable_table_id == table_id),
            None
        )
        
        if config:
            # Sincronizar tabla específica
            background_tasks.add_task(
                sync_service.sync_table,
                config,
                full_sync=False
            )
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
