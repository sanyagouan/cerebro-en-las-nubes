import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import structured logging
from src.core.logging import logger
from src.core.config import settings

# Import API Routers
from src.api.vapi_router import router as vapi_router
from src.api.whatsapp_router import router as whatsapp_router
from src.api.twilio_webhook_router import router as twilio_router
from src.api.mobile.mobile_api import router as mobile_router
from src.api.dashboard.dashboard_api import router as dashboard_router
from src.api.websocket.reservations_ws import router as websocket_router
from src.api.sync.sync_api import router as sync_router
from src.api.analytics_router import router as analytics_router

# Import Middleware
from src.api.middleware.twilio_validation import TwilioValidationMiddleware
from src.api.middleware.rate_limiting import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Import Services
from src.infrastructure.services.scheduler_service import get_scheduler

# Get CORS origins from environment
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
if os.getenv("ENVIRONMENT") == "production":
    # In production, deny wildcard origins for security
    if "*" in allowed_origins:
        logger.warning("Wildard CORS (*) detected in production - this is insecure!")
        allowed_origins = []  # Deny all if misconfigured

settings_errors = settings.validate()
if settings_errors:
    for err in settings_errors:
        logger.error(f"Config error: {err}")
    raise RuntimeError("Invalid configuration. Fix settings before starting.")

app = FastAPI(
    title="Cerebro En Las Nubes",
    description="AI Booking Agent Core & Multi-Agent Orchestrator",
    version="1.0.0",
)

# Register rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# CORS - Restricted to specific origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
)

# Twilio Signature Validation - Protects webhooks from spoofing
app.add_middleware(TwilioValidationMiddleware)

# Include API Routers
app.include_router(vapi_router)
app.include_router(whatsapp_router)
app.include_router(twilio_router)
app.include_router(mobile_router)
app.include_router(dashboard_router)  # Dashboard web API
app.include_router(websocket_router)
app.include_router(sync_router)
app.include_router(analytics_router)  # Analytics and reporting

logger.info(
    f"Cerebro starting - Environment: {os.getenv('ENVIRONMENT', 'development')}"
)


@app.on_event("startup")
async def startup_event():
    """
    Evento de inicio de la aplicación.
    Inicia servicios en background como el scheduler.
    """
    logger.info("Starting background services...")
    scheduler = get_scheduler()
    await scheduler.start()
    logger.info("Background services started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento de cierre de la aplicación.
    Detiene servicios en background gracefully.
    """
    logger.info("Stopping background services...")
    scheduler = get_scheduler()
    await scheduler.stop()
    logger.info("Background services stopped successfully")


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns service status and environment info.
    """
    return {
        "status": "healthy",
        "service": "Cerebro En Las Nubes",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
    }


@app.get("/cache/stats")
async def cache_stats():
    """
    Get cache performance statistics.
    """
    from src.infrastructure.external.airtable_service import AirtableService

    service = AirtableService()
    stats = service.get_cache_stats()

    return {
        "cache": stats,
        "timestamp": __import__("datetime").datetime.now().isoformat(),
    }


@app.get("/cache/health")
async def cache_health():
    """
    Get cache health status.
    """
    from src.infrastructure.external.airtable_service import AirtableService

    service = AirtableService()
    health = service.get_cache_health()

    return {
        "cache_health": health,
        "timestamp": __import__("datetime").datetime.now().isoformat(),
    }


@app.get("/")
async def root():
    return {
        "message": "Cerebro Logic is Running. Agents are standing by.",
        "endpoints": {
            "vapi": "/vapi/webhook",
            "whatsapp": "/whatsapp/webhook",
            "twilio": "/twilio/whatsapp/incoming",
            "mobile_api": "/api/mobile",
            "websocket": "/ws/reservations",
            "health": "/health",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
