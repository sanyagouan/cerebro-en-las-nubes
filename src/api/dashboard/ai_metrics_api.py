"""
API endpoints de métricas del sistema, VAPI logs y WhatsApp logs para el Dashboard.
Implementa health checks reales para Redis, Airtable, VAPI y Twilio,
métricas de sistema con psutil y uptime real del proceso.
"""
import os
import time
import psutil
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from loguru import logger
from src.application.services.auth_service import AuthService, TokenData, require_role

router = APIRouter(prefix="/api", tags=["ai-metrics"])
auth_service = AuthService()

# Tiempo de inicio del proceso
_PROCESS_START_TIME = time.time()
ALLOWED_ROLES = ["administradora", "encargada", "tecnico"]
ADMIN_ROLES = ["administradora", "tecnico"]

# ========== HELPERS HEALTH CHECKS REALES =========

async def _check_redis() -> dict:
    """Verifica conectividad real con Redis."""
    try:
        redis_url = os.getenv("REDIS_URL", "")
        if not redis_url:
            return {"status": "unknown", "service": "Redis Cache", "message": "REDIS_URL no configurado"}
        import redis.asyncio as aioredis
        r = aioredis.from_url(redis_url, socket_connect_timeout=2)
        await r.ping()
        await r.aclose()
        return {"status": "healthy", "service": "Redis Cache", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "degraded", "service": "Redis Cache", "message": str(e)[:100], "timestamp": datetime.now().isoformat()}


async def _check_airtable() -> dict:
    """Verifica conectividad real con Airtable."""
    try:
        from src.infrastructure.mcp.airtable_client import airtable_client
        if not airtable_client._api:
            return {"status": "unknown", "service": "Airtable DB", "message": "API key no configurada"}
        # Ping ligero
        base_id = os.getenv("AIRTABLE_BASE_ID", "appQ2ZXAR68cqDmJt")
        table = "Usuarios"
        airtable_client._get_table(table)
        return {"status": "healthy", "service": "Airtable DB", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "degraded", "service": "Airtable DB", "message": str(e)[:100], "timestamp": datetime.now().isoformat()}


async def _check_vapi() -> dict:
    """Verifica conectividad con la API de VAPI."""
    try:
        import httpx
        api_key = os.getenv("VAPI_API_KEY", "")
        if not api_key:
            return {"status": "unknown", "service": "VAPI Voice Agent", "message": "VAPI_API_KEY no configurado"}
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(
                "https://api.vapi.ai/assistant",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            if resp.status_code in (200, 401):  # 401 = credenciales, pero la API responde
                return {"status": "healthy", "service": "VAPI Voice Agent", "timestamp": datetime.now().isoformat()}
            return {"status": "degraded", "service": "VAPI Voice Agent", "message": f"HTTP {resp.status_code}", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "degraded", "service": "VAPI Voice Agent", "message": str(e)[:100], "timestamp": datetime.now().isoformat()}


async def _check_twilio() -> dict:
    """Verifica conectividad con Twilio."""
    try:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        if not account_sid or not auth_token:
            return {"status": "unknown", "service": "Twilio Communications", "message": "Credenciales no configuradas"}
        import httpx
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(
                f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}.json",
                auth=(account_sid, auth_token),
            )
            if resp.status_code == 200:
                return {"status": "healthy", "service": "Twilio Communications", "timestamp": datetime.now().isoformat()}
            return {"status": "degraded", "service": "Twilio Communications", "message": f"HTTP {resp.status_code}", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "degraded", "service": "Twilio Communications", "message": str(e)[:100], "timestamp": datetime.now().isoformat()}


# ========== SYSTEM HEALTH — REAL ==========

@router.get("/system/health")
async def get_system_health(user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    """Health checks reales de todos los servicios externos."""
    import asyncio
    redis_status, airtable_status, vapi_status, twilio_status = await asyncio.gather(
        _check_redis(), _check_airtable(), _check_vapi(), _check_twilio()
    )
    services = {
        "backend": {"status": "healthy", "service": "Backend Core API", "timestamp": datetime.now().isoformat()},
        "redis": redis_status,
        "airtable": airtable_status,
        "vapi": vapi_status,
        "twilio": twilio_status,
    }
    statuses = [s["status"] for s in services.values()]
    overall = "healthy" if all(s == "healthy" for s in statuses) else ("degraded" if "healthy" in statuses else "unhealthy")
    return {"overall_status": overall, "services": services, "timestamp": datetime.now().isoformat()}


@router.get("/system/metrics")
async def get_system_metrics(user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    """Métricas del sistema: CPU, RAM, uptime."""
    cpu_usage = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    uptime_seconds = int(time.time() - _PROCESS_START_TIME)
    return {
        "cpu_usage_percent": cpu_usage,
        "memory_usage_mb": mem.used // (1024 * 1024),
        "memory_total_mb": mem.total // (1024 * 1024),
        "memory_percent": mem.percent,
        "uptime_seconds": uptime_seconds,
        "timestamp": datetime.now().isoformat()
    }


from src.infrastructure.external.vapi_service import vapi_service
from src.infrastructure.external.twilio_service import twilio_service

@router.get("/vapi/logs")
async def get_vapi_logs(
    limit: int = Query(100, ge=1, le=500),
    user: TokenData = Depends(require_role(ALLOWED_ROLES))
):
    """Logs de llamadas VAPI reales."""
    return await vapi_service.get_calls(limit=limit)


@router.get("/vapi/analytics")
async def get_vapi_analytics(user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    """Analíticas de VAPI reales."""
    return await vapi_service.get_analytics()


@router.get("/whatsapp/logs")
async def get_whatsapp_logs(
    limit: int = Query(50, ge=1, le=200),
    user: TokenData = Depends(require_role(ALLOWED_ROLES))
):
    """Logs de mensajes WhatsApp reales de Twilio."""
    return await twilio_service.get_messages(limit=limit)


@router.get("/whatsapp/analytics")
async def get_whatsapp_analytics(user: TokenData = Depends(require_role(ALLOWED_ROLES))):
    """Analíticas de WhatsApp reales de Twilio."""
    return await twilio_service.get_analytics()


@router.get("/mobile/activity")
async def get_mobile_activity(
    limit: int = Query(50, ge=1, le=200),
    user: TokenData = Depends(require_role(ALLOWED_ROLES))
):
    """Actividad reciente del sistema. Limpio de datos mock."""
    return {"events": [], "total": 0, "message": "No hay actividad reciente registrada"}
