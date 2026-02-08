import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import structured logging
from src.core.logging import logger

# Import API Routers
from src.api.vapi_router import router as vapi_router
from src.api.whatsapp_router import router as whatsapp_router

# Get CORS origins from environment
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
if os.getenv("ENVIRONMENT") == "production":
    # In production, deny wildcard origins for security
    if "*" in allowed_origins:
        logger.warning("Wildard CORS (*) detected in production - this is insecure!")
        allowed_origins = []  # Deny all if misconfigured

app = FastAPI(
    title="Cerebro En Las Nubes",
    description="AI Booking Agent Core & Multi-Agent Orchestrator",
    version="1.0.0",
)

# CORS - Restricted to specific origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
)

# Include API Routers
app.include_router(vapi_router)
app.include_router(whatsapp_router)

logger.info(
    f"Cerebro starting - Environment: {os.getenv('ENVIRONMENT', 'development')}"
)


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
            "health": "/health",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
