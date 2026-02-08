"""
Configuración centralizada de la aplicación.
Lee variables de entorno y proporciona configuración tipada.
"""
import os
from typing import Optional

class Settings:
    """Configuración de la aplicación."""
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # FCM Push Notifications
    FCM_SERVER_KEY: Optional[str] = os.getenv("FCM_SERVER_KEY")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # API Configuration
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"
    
    # WebSocket Configuration
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    
    # Cache Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    CACHE_TTL: int = 300  # 5 minutes
    
    # Airtable
    AIRTABLE_API_KEY: Optional[str] = os.getenv("AIRTABLE_API_KEY")
    AIRTABLE_BASE_ID: Optional[str] = os.getenv("AIRTABLE_BASE_ID")
    
    # Twilio
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_FROM_NUMBER: Optional[str] = os.getenv("TWILIO_FROM_NUMBER")
    
    # VAPI
    VAPI_API_KEY: Optional[str] = os.getenv("VAPI_API_KEY")
    
    # Supabase (NUEVO: para sincronización)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "your-supabase-anon-key")
    
    @property
    def is_production(self) -> bool:
        """Retorna True si estamos en producción."""
        return self.ENVIRONMENT == "production"
    
    def validate(self) -> list:
        """Valida configuración crítica y retorna lista de errores."""
        errors = []
        
        if self.is_production:
            if self.JWT_SECRET_KEY == "your-secret-key-change-in-production":
                errors.append("JWT_SECRET_KEY must be changed in production")
            
            if self.AIRTABLE_API_KEY is None:
                errors.append("AIRTABLE_API_KEY is required")
            
            if self.AIRTABLE_BASE_ID is None:
                errors.append("AIRTABLE_BASE_ID is required")
            
            if self.SUPABASE_SERVICE_KEY == "your-supabase-anon-key":
                errors.append("SUPABASE_SERVICE_KEY must be changed in production")
        
        return errors


# Instancia global de settings
settings = Settings()
