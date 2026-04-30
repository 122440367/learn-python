import os
import time
from typing import Any, Protocol, runtime_checkable, Generator

from dotenv import load_dotenv

from app.core.lock import RWLock

load_dotenv()


@runtime_checkable
class CacheBackend(Protocol):
    def get(self, key: str) -> str | None: ...
    def set(self, key: str, value: str, ex: int | None = None) -> None: ...
    def delete(self, key: str) -> None: ...
    def exists(self, key: str) -> bool: ...


class RedisCache:
    def __init__(self) -> None:
        from app.core.redis import redis_client
        self._client = redis_client

    def get(self, key: str) -> str | None:
        return self._client.get(key)

    def set(self, key: str, value: str, ex: int | None = None) -> None:
        self._client.set(key, value, ex=ex)

    def delete(self, key: str) -> None:
        self._client.delete(key)

    def exists(self, key: str) -> bool:
        return bool(self._client.exists(key))


class MemoryCache:
    def __init__(self) -> None:
        self._store: dict[str, tuple[str, float | None]] = {}
        self._rwlock = RWLock()

    def get(self, key: str) -> str | None:
        with self._rwlock.read():
            if key not in self._store:
                return None
            value, expire_at = self._store[key]
            if expire_at and time.time() > expire_at:
                return None
            return value

    def set(self, key: str, value: str, ex: int | None = None) -> None:
        with self._rwlock.write():
            expire_at = time.time() + ex if ex else None
            self._store[key] = (value, expire_at)

    def delete(self, key: str) -> None:
        with self._rwlock.write():
            self._store.pop(key, None)

    def exists(self, key: str) -> bool:
        return self.get(key) is not None


def create_cache() -> CacheBackend:
    backend = os.getenv("CACHE_BACKEND", "memory")
    if backend == "redis":
        return RedisCache()
    return MemoryCache()


_cache: CacheBackend | None = None


def get_cache() -> Generator[CacheBackend | None, Any, None]:
    global _cache
    if _cache is None:
        _cache = create_cache()
    yield _cache
