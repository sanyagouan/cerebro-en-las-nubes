import json
import os  # FIXED: faltaba para os.getenv()
import socket  # FIXED: faltaba para constantes TCP
import zlib
import time
from typing import Optional, Any, Dict, List
from datetime import timedelta
from collections import defaultdict

try:
    import redis
    from redis.connection import ConnectionPool

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from src.core.logging import logger


class CircuitBreaker:
    """
    Simple circuit breaker pattern for Redis.
    Opens circuit after N consecutive failures.
    """

    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    def record_failure(self):
        """Record a failure and potentially open circuit."""
        self.failures += 1
        self.last_failure_time = time.time()

        if self.failures >= self.failure_threshold:
            self.state = "open"
            logger.warning(
                f"Redis circuit breaker OPENED after {self.failures} consecutive failures"
            )

    def record_success(self):
        """Record a success and close/reset circuit."""
        self.failures = 0
        self.last_failure_time = None

        if self.state == "half-open":
            self.state = "closed"
            logger.info("Redis circuit breaker CLOSED (recovery successful)")

    def is_open(self) -> bool:
        """Check if circuit is open (requests should fail fast)."""
        if self.state == "closed":
            return False

        # Check if timeout expired
        if time.time() - (self.last_failure_time or 0) > self.timeout_seconds:
            self.state = "half-open"
            logger.info("Redis circuit breaker HALF-OPEN (testing recovery)")
            return False

        return True


class RedisCacheMetrics:
    """
    Track Redis cache performance metrics.
    """

    def __init__(self):
        self.hits = defaultdict(int)
        self.misses = defaultdict(int)
        self.errors = defaultdict(int)
        self.latencies = defaultdict(list)  # Last 100 latencies per operation

    def record_hit(self, operation: str):
        """Record cache hit."""
        self.hits[operation] += 1

    def record_miss(self, operation: str):
        """Record cache miss."""
        self.misses[operation] += 1

    def record_error(self, operation: str):
        """Record cache error."""
        self.errors[operation] += 1

    def record_latency(self, operation: str, duration_ms: float):
        """Record operation latency."""
        self.latencies[operation].append(duration_ms)
        # Keep only last 100
        if len(self.latencies[operation]) > 100:
            self.latencies[operation] = self.latencies[operation][-100:]

    def get_hit_rate(self, operation: str) -> float:
        """Calculate hit rate (0.0 to 1.0)."""
        total = self.hits[operation] + self.misses[operation]
        if total == 0:
            return 0.0
        return self.hits[operation] / total

    def get_avg_latency(self, operation: str) -> Optional[float]:
        """Calculate average latency in ms."""
        latencies = self.latencies.get(operation, [])
        if not latencies:
            return None
        return sum(latencies) / len(latencies)

    def get_stats(self, operation: str) -> Dict[str, Any]:
        """Get comprehensive stats for an operation."""
        return {
            "hits": self.hits[operation],
            "misses": self.misses[operation],
            "errors": self.errors[operation],
            "hit_rate": self.get_hit_rate(operation),
            "avg_latency_ms": self.get_avg_latency(operation),
            "total_requests": self.hits[operation]
            + self.misses[operation]
            + self.errors[operation],
        }


class RedisCache:
    """
    Optimized Redis cache wrapper with:
    - Connection pooling
    - SCAN instead of KEYS
    - Retry with exponential backoff
    - Circuit breaker
    - Automatic reconnection
    - Compression for large values
    - Performance metrics
    """

    def __init__(
        self,
        max_connections: int = 10,
        retry_attempts: int = 3,
        circuit_breaker_threshold: int = 5,
        compress_threshold: int = 1024,  # Compress values >1KB
    ):
        self.redis_client = None
        self.connection_pool = None
        self.enabled = False
        self.compress_threshold = compress_threshold
        self.retry_attempts = retry_attempts
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_breaker_threshold
        )
        self.metrics = RedisCacheMetrics()

        if not REDIS_AVAILABLE:
            logger.warning("Redis package not installed - cache disabled")
            return

        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            logger.warning("REDIS_URL not found in environment - cache disabled")
            return

        try:
            # Create connection pool
            self.connection_pool = ConnectionPool.from_url(
                redis_url,
                max_connections=max_connections,
                decode_responses=True,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={
                    socket.TCP_KEEPIDLE: 300,
                    socket.TCP_KEEPINTVL: 60,
                    socket.TCP_KEEPCNT: 3,
                },
            )

            # Initialize Redis client with connection pool
            self.redis_client = redis.Redis(
                connection_pool=self.connection_pool,
                health_check_interval=30,
                socket_timeout=5,
                socket_connect_timeout=5,
            )

            # Test connection with retry
            self._test_connection_with_retry()

            self.enabled = True
            logger.info(
                f"Redis cache initialized successfully (pool: {max_connections} connections)"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            self.enabled = False

    def _test_connection_with_retry(self):
        """Test connection with retry logic."""
        for attempt in range(self.retry_attempts):
            try:
                if self.redis_client:
                    self.redis_client.ping()
                self.circuit_breaker.record_success()
                return True
            except Exception as e:
                self.circuit_breaker.record_failure()
                if attempt < self.retry_attempts - 1:
                    backoff = 2**attempt  # Exponential backoff
                    logger.warning(
                        f"Redis connection attempt {attempt + 1} failed, "
                        f"retrying in {backoff}s..."
                    )
                    time.sleep(backoff)
                else:
                    logger.error(
                        f"Redis connection failed after {self.retry_attempts} attempts: {e}"
                    )
                    return False
        return False

    def _compress_if_large(self, value: str) -> str:
        """Compress value if larger than threshold."""
        if len(value) > self.compress_threshold:
            compressed = zlib.compress(value.encode("utf-8"))
            return f"compressed:{compressed.hex()}"
        return value

    def _decompress_if_needed(self, value: str) -> str:
        """Decompress value if it was compressed."""
        if value.startswith("compressed:"):
            try:
                compressed = bytes.fromhex(value[len("compressed:") :])
                return zlib.decompress(compressed).decode("utf-8")
            except Exception as e:
                logger.error(f"Failed to decompress value: {e}")
                return value
        return value

    def _retry_with_backoff(self, operation_name: str, func):
        """Execute function with retry and exponential backoff."""
        for attempt in range(self.retry_attempts):
            try:
                return func()
            except Exception as e:
                if attempt < self.retry_attempts - 1:
                    backoff = 2**attempt
                    logger.warning(
                        f"Redis {operation_name} attempt {attempt + 1} failed, "
                        f"retrying in {backoff}s... Error: {e}"
                    )
                    time.sleep(backoff)
                else:
                    self.metrics.record_error(operation_name)
                    self.circuit_breaker.record_failure()
                    logger.error(f"Redis {operation_name} failed after retries: {e}")
                    raise
        return None

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache by key.

        Uses SCAN-compatible approach for key existence check.
        """
        if not self.enabled:
            return None

        if self.circuit_breaker.is_open():
            logger.debug(f"Circuit breaker OPEN - skipping Redis GET for key '{key}'")
            return None

        start_time = time.time()

        def _get():
            # Use EXISTS first (O(1)) instead of assuming key exists
            if not self.redis_client.exists(key):
                self.metrics.record_miss("get")
                return None

            value = self.redis_client.get(key)
            if value:
                decompressed = self._decompress_if_needed(value)
                deserialized = json.loads(decompressed)
                self.metrics.record_hit("get")
                return deserialized
            return None

        try:
            result = self._retry_with_backoff("GET", _get)
            latency_ms = (time.time() - start_time) * 1000
            self.metrics.record_latency("get", latency_ms)
            return result
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set value in cache with optional TTL and compression.
        """
        if not self.enabled:
            return False

        if self.circuit_breaker.is_open():
            logger.debug(f"Circuit breaker OPEN - skipping Redis SET for key '{key}'")
            return False

        start_time = time.time()

        def _set():
            serialized = json.dumps(value, default=str)
            compressed = self._compress_if_large(serialized)
            self.redis_client.setex(key, ttl, compressed)
            return True

        try:
            result = self._retry_with_backoff("SET", _set)
            latency_ms = (time.time() - start_time) * 1000
            self.metrics.record_latency("set", latency_ms)
            if result:
                logger.debug(
                    f"Cached key '{key}' (compressed: {len(compressed) > self.compress_threshold})"
                )
            return result
        except Exception as e:
            return False

    def delete(self, key: str) -> bool:
        """
        Delete specific key from cache.
        """
        if not self.enabled:
            return False

        start_time = time.time()

        def _delete():
            return self.redis_client.delete(key) > 0

        try:
            result = self._retry_with_backoff("DELETE", _delete)
            latency_ms = (time.time() - start_time) * 1000
            self.metrics.record_latency("delete", latency_ms)
            return result
        except Exception:
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern using SCAN (O(N) instead of O(N)*).
        """
        if not self.enabled:
            return 0

        if self.circuit_breaker.is_open():
            logger.debug(
                f"Circuit breaker OPEN - skipping Redis DELETE_PATTERN for '{pattern}'"
            )
            return 0

        start_time = time.time()

        def _delete_pattern():
            keys = []
            cursor = "0"

            # Use SCAN to iterate through all keys matching pattern
            while cursor != 0:
                cursor, batch_keys = self.redis_client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=100,  # Fetch 100 keys at a time
                )
                keys.extend(batch_keys)

            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(
                    f"Deleted {deleted} keys matching pattern '{pattern}' (using SCAN)"
                )
                return deleted
            return 0

        try:
            result = self._retry_with_backoff("DELETE_PATTERN", _delete_pattern)
            latency_ms = (time.time() - start_time) * 1000
            self.metrics.record_latency("delete_pattern", latency_ms)
            return result
        except Exception as e:
            logger.error(f"Redis DELETE_PATTERN error for pattern '{pattern}': {e}")
            return 0

    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        """
        if not self.enabled:
            return False

        start_time = time.time()

        def _exists():
            return self.redis_client.exists(key) > 0

        try:
            result = self._retry_with_backoff("EXISTS", _exists)
            latency_ms = (time.time() - start_time) * 1000
            self.metrics.record_latency("exists", latency_ms)
            return result
        except Exception as e:
            logger.error(f"Redis EXISTS error for key '{key}': {e}")
            return False

    def set_with_pattern(
        self, key: str, value: Any, pattern: str, ttl: int = 3600
    ) -> bool:
        """
        Set value with automatic pattern tracking for bulk invalidation.
        """
        if not self.enabled:
            return False

        if self.circuit_breaker.is_open():
            logger.debug(f"Circuit breaker OPEN - skipping Redis SET_WITH_PATTERN")
            return False

        # Set actual key
        success = self.set(key, value, ttl)
        if not success:
            return False

        # Track pattern for invalidation
        pattern_key = f"patterns:{pattern}"

        start_time = time.time()

        def _track_pattern():
            self.redis_client.sadd(pattern_key, key)
            self.redis_client.expire(pattern_key, ttl * 2)
            return True

        try:
            result = self._retry_with_backoff("TRACK_PATTERN", _track_pattern)
            latency_ms = (time.time() - start_time) * 1000
            self.metrics.record_latency("set_with_pattern", latency_ms)
            if not result:
                logger.error(f"Redis PATTERN_TRACK error for '{pattern}': ")
            return result
        except Exception as e:
            logger.error(f"Redis PATTERN_TRACK error for '{pattern}': {e}")
            return False

    def delete_pattern_tracked(self, pattern: str) -> int:
        """
        Delete all keys that were tracked with a specific pattern.
        """
        if not self.enabled:
            return 0

        if self.circuit_breaker.is_open():
            logger.debug(f"Circuit breaker OPEN - skipping Redis INVALIDATE_PATTERN")
            return 0

        pattern_key = f"patterns:{pattern}"

        start_time = time.time()

        def _invalidate_pattern():
            keys = self.redis_client.smembers(pattern_key)
            if keys:
                # Delete all tracked keys
                deleted = self.redis_client.delete(*keys)
                # Remove pattern tracking
                self.redis_client.delete(pattern_key)
                logger.info(
                    f"Invalidated {deleted} tracked keys for pattern '{pattern}'"
                )
                return deleted
            return 0

        try:
            result = self._retry_with_backoff("INVALIDATE_PATTERN", _invalidate_pattern)
            latency_ms = (time.time() - start_time) * 1000
            self.metrics.record_latency("delete_pattern_tracked", latency_ms)
            return result
        except Exception as e:
            logger.error(f"Redis INVALIDATE_PATTERN error for '{pattern}': {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics.
        """
        if not self.enabled:
            return {"enabled": False}

        return {
            "enabled": True,
            "circuit_breaker": {
                "state": self.circuit_breaker.state,
                "failures": self.circuit_breaker.failures,
            },
            "operations": {
                "get": self.metrics.get_stats("get"),
                "set": self.metrics.get_stats("set"),
                "delete": self.metrics.get_stats("delete"),
                "delete_pattern": self.metrics.get_stats("delete_pattern"),
            },
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Check Redis health and connection status.
        """
        if not self.enabled:
            return {
                "status": "disabled",
                "reason": "Not configured or failed to initialize",
            }

        try:
            start_time = time.time()
            self.redis_client.ping()
            latency_ms = (time.time() - start_time) * 1000

            # Get connection pool stats
            pool_stats = (
                self.connection_pool.get_connection_kwargs()
                if self.connection_pool
                else {}
            )

            return {
                "status": "healthy",
                "latency_ms": round(latency_ms, 2),
                "circuit_breaker_state": self.circuit_breaker.state,
                "connection_pool": {
                    "max_connections": pool_stats.get("max_connections"),
                },
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# Singleton instance
_cache_instance = None


def get_cache(**kwargs) -> RedisCache:
    """
    Get or create singleton RedisCache instance.

    Args:
        **kwargs: Additional arguments for RedisCache initialization

    Returns:
        RedisCache instance (enabled or disabled depending on configuration)
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache(**kwargs)
    return _cache_instance
