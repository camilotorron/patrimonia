"""Servicio de caché en memoria usando cachetools.TTLCache."""

from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any

from cachetools import TTLCache

from app.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Wrapper sobre TTLCache con estadísticas."""

    def __init__(
        self, maxsize: int = 1000, ttl: int = settings.PRICE_CACHE_TTL
    ) -> None:
        self._cache: TTLCache[str, Any] = TTLCache(maxsize=maxsize, ttl=ttl)
        self._hits = 0
        self._misses = 0

    # ------------------------------------------------------------------ #
    # Operaciones básicas
    # ------------------------------------------------------------------ #
    def get(self, key: str) -> Any | None:
        value = self._cache.get(key)
        if value is not None:
            self._hits += 1
        else:
            self._misses += 1
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        self._cache[key] = value
        return True

    def delete(self, key: str) -> bool:
        return self._cache.pop(key, None) is not None

    def clear(self) -> bool:
        self._cache.clear()
        return True

    def exists(self, key: str) -> bool:
        return key in self._cache

    def ttl(self, key: str) -> int:
        """Retorna los segundos restantes (aproximado)."""
        # TTLCache no expone TTL directo, retornamos el configurado
        return self._cache.ttl if key in self._cache else 0

    # ------------------------------------------------------------------ #
    # Estadísticas
    # ------------------------------------------------------------------ #
    def get_stats(self) -> dict[str, int]:
        return {
            "hits": self._hits,
            "misses": self._misses,
            "size": len(self._cache),
        }

    def cleanup_expired(self) -> int:
        """Elimina entradas expiradas. Retorna cuántas se eliminaron."""
        before = len(self._cache)
        # TTLCache limpia lazy, forzamos acceso
        list(self._cache.items())
        after = len(self._cache)
        removed = before - after
        if removed > 0:
            logger.info("Cleaned up %d expired cache entries", removed)
        return removed


class PriceCacheService:
    """Servicio de caché especializado para precios."""

    def __init__(self, cache: CacheService | None = None) -> None:
        self.cache = cache or CacheService()

    def _make_key(self, asset_id: int) -> str:
        return f"price:{asset_id}"

    def get_cached_price(self, asset_id: int) -> tuple[Decimal, datetime] | None:
        value = self.cache.get(self._make_key(asset_id))
        if value is not None:
            return value["price"], value["timestamp"]
        return None

    def set_cached_price(
        self, asset_id: int, price: Decimal, ttl: int | None = None
    ) -> None:
        self.cache.set(
            self._make_key(asset_id),
            {"price": price, "timestamp": datetime.utcnow()},
            ttl=ttl,
        )

    def invalidate_cache(self, asset_id: int) -> bool:
        return self.cache.delete(self._make_key(asset_id))

    def get_cache_stats(self) -> dict[str, int]:
        return self.cache.get_stats()

    def cleanup_expired(self) -> int:
        return self.cache.cleanup_expired()


# Instancia singleton
cache_service = CacheService()
price_cache_service = PriceCacheService(cache_service)
