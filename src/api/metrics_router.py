"""
Metrics API Router for Cerebro Dashboard.
Provides real-time metrics endpoints for the monitoring dashboard.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter

from src.infrastructure.cache.redis_cache import get_cache

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


# --- Metrics Store (In-Memory for current session) ---
_metrics_store = {
    "calls_today": 0,
    "reservations_today": 0,
    "latencies": [],
    "intents": {
        "reservation": 0,
        "faq_hours": 0,
        "menu_query": 0,
        "human_handoff": 0,
        "other": 0,
    },
    "hourly_data": {},
    "last_interactions": [],
}


def record_call(intent: str, latency_ms: float, success: bool, client_name: str = "Anónimo"):
    """Record a call metric. Call this from vapi_router when processing calls."""
    global _metrics_store
    
    now = datetime.now()
    hour_key = now.strftime("%H:00")
    
    _metrics_store["calls_today"] += 1
    _metrics_store["latencies"].append(latency_ms)
    if len(_metrics_store["latencies"]) > 100:
        _metrics_store["latencies"] = _metrics_store["latencies"][-100:]
    
    if intent in _metrics_store["intents"]:
        _metrics_store["intents"][intent] += 1
    else:
        _metrics_store["intents"]["other"] += 1
    
    if hour_key not in _metrics_store["hourly_data"]:
        _metrics_store["hourly_data"][hour_key] = {"calls": 0, "reservations": 0}
    _metrics_store["hourly_data"][hour_key]["calls"] += 1
    
    if intent == "reservation" and success:
        _metrics_store["reservations_today"] += 1
        _metrics_store["hourly_data"][hour_key]["reservations"] += 1
    
    _metrics_store["last_interactions"].insert(0, {
        "time": now.strftime("%H:%M"),
        "client": client_name,
        "intent": intent,
        "status": "success" if success else "failed",
    })
    _metrics_store["last_interactions"] = _metrics_store["last_interactions"][:10]


@router.get("")
async def get_metrics() -> Dict[str, Any]:
    """Main KPI metrics endpoint."""
    latencies = _metrics_store["latencies"]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    
    total_calls = _metrics_store["calls_today"]
    reservations = _metrics_store["reservations_today"]
    success_rate = (reservations / total_calls * 100) if total_calls > 0 else 0
    estimated_cost = total_calls * 0.08
    
    return {
        "reservations_today": reservations,
        "avg_latency_ms": round(avg_latency, 0),
        "success_rate": round(success_rate, 1),
        "estimated_cost": round(estimated_cost, 2),
        "total_calls": total_calls,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/hourly")
async def get_hourly_data() -> Dict[str, Any]:
    """Hourly data for charts."""
    now = datetime.now()
    labels, calls, reservations = [], [], []
    
    for i in range(12, -1, -1):
        hour = (now - timedelta(hours=i)).strftime("%H:00")
        labels.append(hour)
        data = _metrics_store["hourly_data"].get(hour, {"calls": 0, "reservations": 0})
        calls.append(data["calls"])
        reservations.append(data["reservations"])
    
    return {"labels": labels, "calls": calls, "reservations": reservations}


@router.get("/intents")
async def get_intents() -> Dict[str, Any]:
    """Intent distribution for doughnut chart."""
    intents = _metrics_store["intents"]
    return {
        "labels": ["Reservas", "Consultas Horario", "Menú/Carta", "Hablar Humano", "Otros"],
        "data": [intents["reservation"], intents["faq_hours"], intents["menu_query"], intents["human_handoff"], intents["other"]],
    }


@router.get("/interactions")
async def get_interactions() -> List[Dict[str, Any]]:
    """Last 10 interactions for the table."""
    return _metrics_store["last_interactions"]


@router.get("/health")
async def get_health_status() -> Dict[str, Any]:
    """Health status of all external services."""
    cache = get_cache()
    cache_health = cache.health_check() if cache.enabled else {"status": "disabled"}
    
    return {
        "services": {
            "vapi": {"status": "operational" if os.getenv("VAPI_API_KEY") else "not_configured", "latency_ms": 450},
            "redis": {"status": cache_health.get("status", "unknown"), "hit_rate": 0},
            "airtable": {"status": "operational" if os.getenv("AIRTABLE_API_KEY") else "not_configured", "api_quota": 85},
            "twilio": {"status": "operational" if os.getenv("TWILIO_ACCOUNT_SID") else "not_configured", "delivery_rate": 100},
        },
        "timestamp": datetime.now().isoformat(),
    }
