"""Tests para el servicio de caché."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from app.services.cache_service import CacheService, PriceCacheService


class TestCacheService:
    def test_get_set(self):
        cache = CacheService(maxsize=10, ttl=60)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        assert cache.get("nonexistent") is None

    def test_delete(self):
        cache = CacheService(maxsize=10, ttl=60)
        cache.set("key1", "value1")
        assert cache.delete("key1") is True
        assert cache.get("key1") is None

    def test_clear(self):
        cache = CacheService(maxsize=10, ttl=60)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_exists(self):
        cache = CacheService(maxsize=10, ttl=60)
        cache.set("key1", "value1")
        assert cache.exists("key1") is True
        assert cache.exists("key2") is False

    def test_stats(self):
        cache = CacheService(maxsize=10, ttl=60)
        cache.set("key1", "value1")
        cache.get("key1")  # hit
        cache.get("key2")  # miss
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1


class TestPriceCacheService:
    def test_get_set_price(self):
        service = PriceCacheService(CacheService(maxsize=10, ttl=60))
        service.set_cached_price(1, Decimal("150.50"))
        result = service.get_cached_price(1)
        assert result is not None
        assert result[0] == Decimal("150.50")
        assert isinstance(result[1], datetime)

    def test_invalidate(self):
        service = PriceCacheService(CacheService(maxsize=10, ttl=60))
        service.set_cached_price(1, Decimal("150"))
        assert service.invalidate_cache(1) is True
        assert service.get_cached_price(1) is None

    def test_stats(self):
        service = PriceCacheService(CacheService(maxsize=10, ttl=60))
        service.set_cached_price(1, Decimal("150"))
        service.get_cached_price(1)  # hit
        stats = service.get_cache_stats()
        assert stats["hits"] == 1
