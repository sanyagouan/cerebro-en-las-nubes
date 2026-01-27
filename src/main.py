from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import API Routers
from src.api.vapi_router import router as vapi_router
from src.api.whatsapp_router import router as whatsapp_router
from src.api.metrics_router import router as metrics_router

# Static files for dashboard
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Configuración de Logs (Standard Output only for Docker)
logger.info("Cerebro starts on STDOUT")

app = FastAPI(
    title="Cerebro En Las Nubes",
    description="AI Booking Agent Core & Multi-Agent Orchestrator",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(vapi_router)
app.include_router(whatsapp_router)
app.include_router(metrics_router)

# Mount static files for dashboard
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

@app.get("/health")
async def health_check():
    """Endpoint para verificar que el cerebro está vivo."""
    return {"status": "healthy", "service": "Cerebro En Las Nubes"}

@app.get("/")
async def root():
    return {
        "message": "Cerebro Logic is Running. Agents are standing by.",
        "endpoints": {
            "vapi": "/vapi/assistant",
            "whatsapp": "/whatsapp/webhook",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
