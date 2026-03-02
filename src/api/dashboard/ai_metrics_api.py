import psutil
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from src.application.services.auth_service import AuthService, TokenData, require_role

router = APIRouter(prefix="/api", tags=["ai-metrics"])
auth_service = AuthService()

# ========== SYSTEM HEALTH ==========

@router.get("/system/health")
async def get_system_health(user: TokenData = Depends(require_role(["administradora", "encargada", "admin", "manager"]))):
    return {
        "overall_status": "healthy",
        "services": {
            "backend": {"status": "healthy", "service": "Backend Core API", "timestamp": datetime.now().isoformat()},
            "redis": {"status": "healthy", "service": "Redis Cache", "timestamp": datetime.now().isoformat()},
            "airtable": {"status": "healthy", "service": "Airtable DB", "timestamp": datetime.now().isoformat()},
            "vapi": {"status": "healthy", "service": "VAPI Voice Agent", "timestamp": datetime.now().isoformat()},
            "twilio": {"status": "healthy", "service": "Twilio Communications", "timestamp": datetime.now().isoformat()}
        },
        "timestamp": datetime.now().isoformat()
    }

@router.get("/system/metrics")
async def get_system_metrics(user: TokenData = Depends(require_role(["administradora", "encargada", "admin", "manager"]))):
    cpu_usage = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    return {
        "cpu_usage_percent": cpu_usage,
        "memory_usage_mb": mem.used // (1024*1024),
        "memory_total_mb": mem.total // (1024*1024),
        "memory_percent": mem.percent,
        "requests_per_minute": 134, # mock
        "avg_response_time_ms": 42, # mock
        "active_websocket_connections": 5, # mock
        "cache_hit_rate_percent": 96.5, # mock
        "uptime_seconds": 86400 * 3 + 3600, # mock 3d 1h
        "timestamp": datetime.now().isoformat()
    }

@router.get("/system/uptime")
async def get_system_uptime(user: TokenData = Depends(require_role(["administradora", "encargada", "admin", "manager"]))):
    uptime_seconds = 86400 * 3 + 3600
    started_at = (datetime.now() - timedelta(seconds=uptime_seconds)).isoformat()
    return {
        "uptime_seconds": uptime_seconds,
        "uptime_formatted": "3d 1h 0m",
        "started_at": started_at,
        "current_time": datetime.now().isoformat(),
        "healthy_since": started_at
    }

@router.get("/system/logs")
async def get_system_error_logs(limit: int = 50, user: TokenData = Depends(require_role(["administradora", "encargada", "admin", "manager"]))):
    return {
        "logs": [
            {
                "id": f"log-{i}",
                "level": "warning",
                "message": "High latency detected from Airtable API" if i % 2 == 0 else "Retrying Twilio webhook connection",
                "timestamp": (datetime.now() - timedelta(minutes=i*25)).isoformat(),
                "service": "airtable" if i % 2 == 0 else "twilio",
            } for i in range(5)
        ],
        "total": 5
    }

# ========== VAPI LOGS ==========

@router.get("/vapi/logs")
async def get_vapi_logs(limit: int = 100, user: TokenData = Depends(require_role(["administradora", "encargada", "admin", "manager"]))):
    calls = []
    statuses = ['completed', 'completed', 'completed', 'failed', 'busy']
    for i in range(15):
        duration = 45 + i*15
        started = datetime.now() - timedelta(minutes=i*55)
        calls.append({
            "id": f"call-{i}",
            "call_id": f"vapi-sid-{i}",
            "phone_number": f"+346001234{i:02d}",
            "direction": "inbound",
            "status": statuses[i % len(statuses)],
            "duration_seconds": duration,
            "started_at": started.isoformat(),
            "ended_at": (started + timedelta(seconds=duration)).isoformat(),
            "transcript": "Hola buenas, quer\u00eda reservar una mesa para el martes...",
            "summary": "El cliente reserv\u00f3 una mesa para 4 personas.",
            "reservation_created": i % 3 != 0,
            "cost": round(duration * 0.05, 2)
        })
    return {"calls": calls, "total": 15}

@router.get("/vapi/analytics")
async def get_vapi_analytics(user: TokenData = Depends(require_role(["administradora", "encargada", "admin", "manager"]))):
    return {
        "total_calls": 342,
        "completed_calls": 310,
        "failed_calls": 12,
        "avg_duration_seconds": 65,
        "total_cost": 45.60,
        "conversion_rate": 68.5,
        "reservations_created": 210,
        "calls_by_status": {"completed": 310, "failed": 12, "no_answer": 15, "busy": 5},
        "calls_by_hour": [{"hour": h, "count": 10 + (h%5)*5} for h in range(12, 24)]
    }

# ========== WHATSAPP LOGS ==========

@router.get("/whatsapp/logs")
async def get_whatsapp_logs(user: TokenData = Depends(require_role(["administradora", "encargada", "admin", "manager"]))):
    messages = []
    types = ['confirmation', 'reminder', 'cancellation', 'waitlist']
    for i in range(20):
        sent = datetime.now() - timedelta(minutes=i*30)
        messages.append({
            "id": f"msg-{i}",
            "message_id": f"tw-msg-{i}",
            "phone_number": f"+346001235{i:02d}",
            "message_type": types[i % 4],
            "content": f"Hola, confirmamos tu reserva en En Las Nubes para el {sent.strftime('%d/%m')}...",
            "status": "read" if i % 2 == 0 else "delivered",
            "sent_at": sent.isoformat(),
            "delivered_at": (sent + timedelta(seconds=2)).isoformat(),
            "read_at": (sent + timedelta(minutes=5)).isoformat() if i % 2 == 0 else None,
            "cost": 0.04
        })
    # FIXED: Wrap in object so frontend `logs?.messages` works correctly
    return {"messages": messages, "total": len(messages)}

@router.get("/whatsapp/analytics")
async def get_whatsapp_analytics(user: TokenData = Depends(require_role(["administradora", "encargada", "admin", "manager"]))):
    return {
        "total_messages": 1250,
        "sent_messages": 1250,
        "delivered_messages": 1245,
        "read_messages": 1100,
        "failed_messages": 5,
        "delivery_rate": 99.6,
        "read_rate": 88.0,
        "total_cost": 50.0,
        "messages_by_type": {"confirmation": 600, "reminder": 500, "cancellation": 50, "waitlist": 100},
        "messages_by_status": {"sent": 1250, "delivered": 145, "read": 1100, "failed": 5}
    }

# ========== WHATSAPP TEMPLATES ==========

@router.get("/whatsapp/templates")
async def get_whatsapp_templates(user: TokenData = Depends(require_role(["administradora", "encargada", "admin", "manager"]))):
    """Plantillas de mensajes de WhatsApp."""
    return [
        {
            "id": "tpl-confirmacion",
            "nombre": "Confirmación de Reserva",
            "contenido": "Hola {{nombre}}, confirmamos tu reserva para {{pax}} personas el {{fecha}} a las {{hora}} en En Las Nubes.",
            "tipo": "confirmation",
            "activo": True,
            "variables": ["nombre", "pax", "fecha", "hora"]
        },
        {
            "id": "tpl-recordatorio",
            "nombre": "Recordatorio 24h",
            "contenido": "Hola {{nombre}}, te recordamos tu reserva mañana {{fecha}} a las {{hora}}. ¡Te esperamos!",
            "tipo": "reminder",
            "activo": True,
            "variables": ["nombre", "fecha", "hora"]
        },
        {
            "id": "tpl-cancelacion",
            "nombre": "Cancelación",
            "contenido": "Hola {{nombre}}, tu reserva para el {{fecha}} ha sido cancelada. Disculpa las molestias.",
            "tipo": "cancellation",
            "activo": True,
            "variables": ["nombre", "fecha"]
        },
        {
            "id": "tpl-lista-espera",
            "nombre": "Notificación Lista de Espera",
            "contenido": "Buenas noticias {{nombre}}, tenemos mesa disponible ahora mismo. ¿Vienes en los próximos 15 minutos?",
            "tipo": "waitlist",
            "activo": True,
            "variables": ["nombre"]
        }
    ]

@router.put("/whatsapp/templates/{template_id}")
async def update_whatsapp_template(
    template_id: str,
    data: dict,
    user: TokenData = Depends(require_role(["administradora", "admin"]))
):
    """Actualiza una plantilla de WhatsApp (mock)."""
    return {"id": template_id, **data, "updated": True}

@router.post("/whatsapp/messages/{message_id}/resend")
async def resend_whatsapp_message(
    message_id: str,
    user: TokenData = Depends(require_role(["administradora", "encargada", "admin", "manager"]))
):
    """Reenvía un mensaje de WhatsApp (mock)."""
    return {"id": message_id, "status": "queued", "message": "Mensaje reenviado correctamente"}

@router.get("/whatsapp/messages/{message_id}")
async def get_whatsapp_message(
    message_id: str,
    user: TokenData = Depends(require_role(["administradora", "encargada", "admin", "manager"]))
):
    """Obtiene detalle de un mensaje de WhatsApp (mock)."""
    return {
        "id": message_id,
        "phone_number": "+34600123456",
        "content": "Hola, confirmamos tu reserva en En Las Nubes...",
        "status": "delivered",
        "sent_at": datetime.now().isoformat(),
        "cost": 0.04
    }

# ========== VAPI LOGS DETAIL ==========

@router.get("/vapi/logs/{call_id}")
async def get_vapi_call_detail(
    call_id: str,
    user: TokenData = Depends(require_role(["administradora", "encargada", "admin", "manager"]))
):
    """Detalle de una llamada VAPI específica (mock)."""
    return {
        "id": call_id,
        "call_id": f"vapi-{call_id}",
        "phone_number": "+34600123456",
        "direction": "inbound",
        "status": "completed",
        "duration_seconds": 120,
        "started_at": (datetime.now() - timedelta(hours=2)).isoformat(),
        "ended_at": (datetime.now() - timedelta(hours=2) + timedelta(seconds=120)).isoformat(),
        "transcript": "Cliente: Hola, quería reservar una mesa...\nAsistente: Claro, ¿para cuántas personas?",
        "summary": "El cliente reservó una mesa para 4 personas el sábado.",
        "reservation_created": True,
        "cost": 0.60
    }

# ========== MOBILE ACTIVITY ==========

@router.get("/mobile/activity")
async def get_mobile_activity(
    limit: int = 50,
    tipo: str = None,
    desde: str = None,
    user: TokenData = Depends(require_role(["administradora", "encargada", "admin", "manager", "camarero"]))
):
    """Actividad reciente del sistema (eventos de reservas, mesas, etc.)."""
    event_types = ['reserva_creada', 'reserva_editada', 'mesa_asignada', 'cliente_sentado', 'reserva_completada']
    descriptions = [
        'Nueva reserva creada por VAPI para 4 personas',
        'Reserva modificada: mesa cambiada a terraza',
        'Mesa 5 asignada a reserva de García',
        'Cliente sentado en mesa 3 (2 personas)',
        'Reserva completada satisfactoriamente'
    ]
    events = []
    for i in range(min(limit, 20)):
        events.append({
            "id": f"evt-{i}",
            "tipo": event_types[i % len(event_types)],
            "descripcion": descriptions[i % len(descriptions)],
            "usuario": "Sistema" if i % 3 == 0 else "Recepción",
            "timestamp": (datetime.now() - timedelta(minutes=i*15)).isoformat(),
            "metadata": {
                "reserva_id": f"res-{i}" if 'reserva' in event_types[i % len(event_types)] else None,
                "mesa_id": f"mesa-{(i % 10) + 1}",
            }
        })
    return {"events": events, "total": len(events)}

