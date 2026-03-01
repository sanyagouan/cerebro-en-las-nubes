"""
Tests for Redis cache implementation.

Run with: pytest tests/unit/test_redis_cache.py -v
"""

import os
import sys
import time
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from unittest.mock import Mock, patch, MagicMock

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from src.infrastructure.cache.redis_cache import RedisCache, get_cache, CircuitBreaker


class TestCircuitBreaker:
    """Test circuit breaker pattern."""

    def test_circuit_breaker_closed_by_default(self):
        """Circuit should be closed initially."""
        cb = CircuitBreaker()
        assert cb.state == "closed"
        assert cb.failures == 0
        assert not cb.is_open()

    def test_circuit_breaker_opens_after_threshold(self):
        """Circuit should open after threshold failures."""
        cb = CircuitBreaker(failure_threshold=3)

        # Record failures
        for _ in range(3):
            cb.record_failure()

        assert cb.state == "open"
        assert cb.is_open()

    def test_circuit_breaker_half_open_after_timeout(self):
        """Circuit should be half-open after timeout."""
        cb = CircuitBreaker(failure_threshold=3, timeout_seconds=0.1)

        # Open circuit
        for _ in range(3):
            cb.record_failure()

        assert cb.state == "open"

        # Wait for timeout
        time.sleep(0.15)

        # Should be half-open (testing)
        assert cb.state == "half-open"
        assert not cb.is_open()

    def test_circuit_breaker_closes_on_success(self):
        """Circuit should close on successful recovery."""
        cb = CircuitBreaker(failure_threshold=3, timeout_seconds=0.1)

        # Open circuit
        for _ in range(3):
            cb.record_failure()

        # Wait for timeout
        time.sleep(0.15)

        # Record success (from half-open state)
        cb.record_success()

        assert cb.state == "closed"
        assert not cb.is_open()


class TestRedisCacheMetrics:
    """Test cache metrics tracking."""

    def test_metrics_record_hit(self):
        """Metrics should record cache hits."""
        from src.infrastructure.cache.redis_cache import RedisCacheMetrics

        metrics = RedisCacheMetrics()
        metrics.record_hit("get")

        assert metrics.hits["get"] == 1
        assert metrics.get_hit_rate("get") == 1.0

    def test_metrics_record_miss(self):
        """Metrics should record cache misses."""
        from src.infrastructure.cache.redis_cache import RedisCacheMetrics

        metrics = RedisCacheMetrics()
        metrics.record_miss("get")

        assert metrics.misses["get"] == 1
        assert metrics.get_hit_rate("get") == 0.0

    def test_metrics_hit_rate_calculation(self):
        """Metrics should calculate hit rate correctly."""
        from src.infrastructure.cache.redis_cache import RedisCacheMetrics

        metrics = RedisCacheMetrics()
        metrics.record_hit("get")
        metrics.record_hit("get")
        metrics.record_miss("get")

        # 2 hits, 1 miss = 66.7% hit rate
        assert abs(metrics.get_hit_rate("get") - 0.6667) < 0.01

    def test_metrics_latency_tracking(self):
        """Metrics should track latencies."""
        from src.infrastructure.cache.redis_cache import RedisCacheMetrics

        metrics = RedisCacheMetrics()
        metrics.record_latency("get", 10.5)
        metrics.record_latency("get", 20.3)

        avg = metrics.get_avg_latency("get")
        assert avg == pytest.approx(15.4, rel=0.01)

    def test_metrics_get_stats(self):
        """Metrics should return comprehensive stats."""
        from src.infrastructure.cache.redis_cache import RedisCacheMetrics

        metrics = RedisCacheMetrics()
        metrics.record_hit("get")
        metrics.record_miss("get")
        metrics.record_latency("get", 15.0)

        stats = metrics.get_stats("get")

        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["avg_latency_ms"] == 15.0
        assert stats["total_requests"] == 2


@pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not installed")
class TestRedisCache:
    """Test Redis cache operations."""

    @pytest.fixture
    def cache(self):
        """Create Redis cache instance for testing."""
        # Use test Redis URL if available, otherwise mock
        test_redis_url = os.getenv("REDIS_TEST_URL")

        if test_redis_url:
            with patch.dict(os.environ, {"REDIS_URL": test_redis_url}):
                cache = RedisCache()
                yield cache
        else:
            # Mock Redis client for testing
            mock_redis = Mock()
            mock_redis.ping.return_value = True
            mock_redis.exists.return_value = True
            mock_redis.get.return_value = None
            mock_redis.setex.return_value = True
            mock_redis.delete.return_value = 1
            mock_redis.scan.return_value = ("0", [])  # No keys
            mock_redis.smembers.return_value = set()

            with patch(
                "src.infrastructure.cache.redis_cache.redis"
            ) as mock_redis_module:
                mock_redis_module.Redis.return_value = mock_redis
                mock_redis_module.ConnectionPool.from_url.return_value = Mock()
                cache = RedisCache()
                yield cache

    def test_cache_disabled_without_url(self):
        """Cache should be disabled without REDIS_URL."""
        with patch.dict(os.environ, {}, clear=True):
            cache = RedisCache()
            assert not cache.enabled

    def test_cache_get_miss(self, cache):
        """Cache should return None for non-existent key."""
        if not cache.enabled:
            pytest.skip("Cache not enabled")

        result = cache.get("nonexistent_key")
        assert result is None

    def test_cache_set_and_get(self, cache):
        """Cache should set and retrieve values correctly."""
        if not cache.enabled:
            pytest.skip("Cache not enabled")

        # Set value
        success = cache.set("test_key", {"foo": "bar"}, ttl=60)
        assert success

        # Get value
        result = cache.get("test_key")
        assert result == {"foo": "bar"}

    def test_cache_set_with_compression(self, cache):
        """Cache should compress large values."""
        if not cache.enabled:
            pytest.skip("Cache not enabled")

        # Create large value (>1KB)
        large_value = {"data": "x" * 2000}  # ~2KB

        success = cache.set("large_key", large_value, ttl=60)
        assert success

        # Get and verify
        result = cache.get("large_key")
        assert result == large_value

    def test_cache_delete(self, cache):
        """Cache should delete keys correctly."""
        if not cache.enabled:
            pytest.skip("Cache not enabled")

        # Set and delete
        cache.set("delete_key", {"value": 123}, ttl=60)
        deleted = cache.delete("delete_key")
        assert deleted

        # Verify deleted
        result = cache.get("delete_key")
        assert result is None

    def test_cache_exists(self, cache):
        """Cache should check key existence correctly."""
        if not cache.enabled:
            pytest.skip("Cache not enabled")

        # Non-existent key
        assert not cache.exists("nonexistent")

        # Existing key
        cache.set("exists_key", {"value": 1}, ttl=60)
        assert cache.exists("exists_key")

    def test_cache_delete_pattern(self, cache):
        """Cache should delete keys matching pattern."""
        if not cache.enabled:
            pytest.skip("Cache not enabled")

        # Set multiple keys
        cache.set("pattern:test1", {"value": 1}, ttl=60)
        cache.set("pattern:test2", {"value": 2}, ttl=60)
        cache.set("other:key", {"value": 3}, ttl=60)

        # Delete matching pattern
        deleted = cache.delete_pattern("pattern:*")
        assert deleted >= 2  # At least 2 keys deleted

        # Verify pattern keys deleted
        assert cache.get("pattern:test1") is None
        assert cache.get("pattern:test2") is None
        # Other key should still exist
        assert cache.get("other:key") == {"value": 3}

    def test_cache_set_with_pattern_tracking(self, cache):
        """Cache should track patterns for bulk invalidation."""
        if not cache.enabled:
            pytest.skip("Cache not enabled")

        # Set with pattern tracking
        cache.set_with_pattern("key1", {"value": 1}, "test:*", ttl=60)
        cache.set_with_pattern("key2", {"value": 2}, "test:*", ttl=60)

        # Delete by pattern
        deleted = cache.delete_pattern_tracked("test:*")
        assert deleted == 2

    def test_cache_get_stats(self, cache):
        """Cache should return performance statistics."""
        if not cache.enabled:
            pytest.skip("Cache not enabled")

        # Perform some operations
        cache.set("stats_key", {"value": 1}, ttl=60)
        cache.get("stats_key")  # Hit
        cache.get("nonexistent")  # Miss

        stats = cache.get_stats()

        assert stats["enabled"] is True
        assert stats["operations"]["get"]["hits"] == 1
        assert stats["operations"]["get"]["misses"] == 1
        assert stats["operations"]["set"]["total_requests"] == 1

    def test_cache_health_check(self, cache):
        """Cache should return health status."""
        if not cache.enabled:
            pytest.skip("Cache not enabled")

        health = cache.health_check()

        assert health["status"] == "healthy"
        assert "latency_ms" in health
        assert "circuit_breaker_state" in health


class TestRedisCacheSingleton:
    """Test singleton pattern for cache instance."""

    def test_get_cache_returns_same_instance(self):
        """get_cache should return same instance."""
        # Clear singleton
        import src.infrastructure.cache.redis_cache as redis_module

        redis_module._cache_instance = None

        cache1 = get_cache()
        cache2 = get_cache()

        assert cache1 is cache2

    def test_get_cache_with_kwargs(self):
        """get_cache should accept kwargs for initialization."""
        import src.infrastructure.cache.redis_cache as redis_module

        redis_module._cache_instance = None

        cache = get_cache(max_connections=5, compress_threshold=512)

        assert cache is not None


class TestRedisCacheGracefulDegradation:
    """Test cache behavior when Redis is unavailable."""

    @pytest.fixture
    def disabled_cache(self):
        """Create disabled cache instance."""
        with patch.dict(os.environ, {}, clear=True):
            cache = RedisCache()
            yield cache

    def test_disabled_cache_get_returns_none(self, disabled_cache):
        """Disabled cache should return None for get."""
        assert disabled_cache.get("any_key") is None

    def test_disabled_cache_set_returns_false(self, disabled_cache):
        """Disabled cache should return False for set."""
        assert not disabled_cache.set("key", {"value": 1})

    def test_disabled_cache_delete_returns_false(self, disabled_cache):
        """Disabled cache should return False for delete."""
        assert not disabled_cache.delete("key")

    def test_disabled_cache_health_check(self, disabled_cache):
        """Disabled cache should return disabled health."""
        health = disabled_cache.health_check()
        assert health["status"] == "disabled"
        assert "reason" in health


class TestRedisCacheWithMockRedis:
    """Test cache with mocked Redis client."""

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        mock = Mock()
        mock.ping.return_value = True
        mock.exists.return_value = True
        mock.get.return_value = json.dumps({"cached": "value"})
        mock.setex.return_value = True
        mock.delete.return_value = 1
        mock.scan.return_value = ("0", ["key1", "key2"])
        mock.smembers.return_value = {"key1", "key2"}
        return mock

    def test_cache_uses_connection_pool(self, mock_redis):
        """Cache should use connection pool."""
        with patch("src.infrastructure.cache.redis_cache.redis") as mock_redis_module:
            mock_redis_module.ConnectionPool.from_url.return_value = Mock()
            mock_redis_module.Redis.return_value = mock_redis

            with patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379"}):
                cache = RedisCache()
                assert cache.enabled

    def test_cache_retry_on_failure(self, mock_redis):
        """Cache should retry on connection failures."""
        # Make ping fail twice, then succeed
        mock_redis.ping.side_effect = [Exception("Fail1"), Exception("Fail2"), True]
        mock_redis.exists.return_value = False

        with patch("src.infrastructure.cache.redis_cache.redis") as mock_redis_module:
            mock_redis_module.Redis.return_value = mock_redis
            mock_redis_module.ConnectionPool.from_url.return_value = Mock()

            with patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379"}):
                cache = RedisCache()
                assert cache.circuit_breaker.failures == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
