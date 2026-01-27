import os
import redis
from loguru import logger
from typing import Optional, Any, Dict

class RedisCache:
    def __init__(self):
        self.enabled = False
        self.client = None
        redis_url = os.getenv("REDIS_URL")
        
        if redis_url:
            try:
                self.client = redis.from_url(redis_url, decode_responses=True)
                self.client.ping()
                self.enabled = True
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.error(f"Redis initialization failed: {e}")
                self.enabled = False
        else:
            logger.warning("REDIS_URL not set. Redis cache disabled.")

    def health_check(self) -> Dict[str, Any]:
        """Check Redis connection status."""
        if not self.enabled or not self.client:
            return {"status": "disabled", "error": "Redis not configured"}
        
        try:
            if self.client.ping():
                return {"status": "healthy"}
            return {"status": "unhealthy", "error": "Ping failed"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def get(self, key: str) -> Optional[str]:
        if not self.enabled or not self.client:
            return None
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: str, ex: int = 3600) -> bool:
        if not self.enabled or not self.client:
            return False
        try:
            return bool(self.client.set(key, value, ex=ex))
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

# Singleton instance
_cache_instance = None

def get_cache() -> RedisCache:
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance
