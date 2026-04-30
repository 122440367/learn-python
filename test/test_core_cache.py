import time
import threading
from unittest.mock import MagicMock, patch

import pytest

from app.core.cache import MemoryCache, RedisCache, create_cache, get_cache


class TestMemoryCache:
    """MemoryCache 内存缓存实现测试。"""

    @pytest.fixture
    def cache(self):
        return MemoryCache()

    def test_set_and_get(self, cache):
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_missing_key(self, cache):
        assert cache.get("nonexistent") is None

    def test_set_overwrite(self, cache):
        cache.set("key1", "value1")
        cache.set("key1", "value2")
        assert cache.get("key1") == "value2"

    def test_delete(self, cache):
        cache.set("key1", "value1")
        cache.delete("key1")
        assert cache.get("key1") is None

    def test_delete_nonexistent(self, cache):
        cache.delete("nonexistent")  # 不应抛异常

    def test_exists(self, cache):
        cache.set("key1", "value1")
        assert cache.exists("key1") is True
        assert cache.exists("nonexistent") is False

    def test_ttl_expiration(self, cache):
        """TTL过期后get应返回None。通过直接操作内部状态模拟过期。"""
        now = time.time()
        cache.set("key1", "value1", ex=60)  # expire_at = now + 60
        # 手动将过期时间改到过去，绕过 time.time() 精度问题
        cache._store["key1"] = (cache._store["key1"][0], now - 1)
        assert cache.get("key1") is None

    def test_ttl_not_expired(self, cache):
        cache.set("key1", "value1", ex=3600)
        assert cache.get("key1") == "value1"

    def test_exists_with_ttl_expired(self, cache):
        """TTL过期后exists应返回False。"""
        now = time.time()
        cache.set("key1", "value1", ex=60)
        cache._store["key1"] = (cache._store["key1"][0], now - 1)
        assert cache.exists("key1") is False

    def test_exists_with_ttl_not_expired(self, cache):
        cache.set("key1", "value1", ex=3600)
        assert cache.exists("key1") is True

    def test_set_without_ttl(self, cache):
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        assert cache.exists("key1") is True

    def test_ttl_expiration_does_not_affect_other_keys(self, cache):
        now = time.time()
        cache.set("expiring", "v1", ex=60)
        cache._store["expiring"] = (cache._store["expiring"][0], now - 1)
        cache.set("persistent", "v2")
        assert cache.get("expiring") is None
        assert cache.get("persistent") == "v2"

    def test_concurrent_set_and_get(self, cache):
        """并发写入和读取应不抛出异常。"""
        errors = []

        def writer():
            for i in range(100):
                try:
                    cache.set(f"key{i}", f"value{i}")
                except Exception as e:
                    errors.append(e)

        def reader():
            for i in range(100):
                try:
                    cache.get(f"key{i}")
                except Exception as e:
                    errors.append(e)

        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=writer))
            threads.append(threading.Thread(target=reader))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0

    def test_concurrent_delete_and_get(self, cache):
        """并发删除和读取应不抛出异常。"""
        cache.set("shared", "value")
        errors = []

        def deleter():
            try:
                cache.delete("shared")
            except Exception as e:
                errors.append(e)

        def reader():
            try:
                cache.get("shared")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=deleter) for _ in range(10)]
        threads += [threading.Thread(target=reader) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


class TestRedisCacheProtocol:
    """RedisCache 通过 mock Redis 客户端验证协议行为。"""

    def test_get_delegates_to_client(self):
        mock_client = MagicMock()
        mock_client.get.return_value = "cached_value"
        with patch("app.core.redis.redis_client", mock_client):
            cache = RedisCache()
            result = cache.get("key1")
            mock_client.get.assert_called_once_with("key1")
            assert result == "cached_value"

    def test_get_none(self):
        mock_client = MagicMock()
        mock_client.get.return_value = None
        with patch("app.core.redis.redis_client", mock_client):
            cache = RedisCache()
            assert cache.get("key1") is None

    def test_set_delegates_to_client(self):
        mock_client = MagicMock()
        with patch("app.core.redis.redis_client", mock_client):
            cache = RedisCache()
            cache.set("key1", "value1", ex=60)
            mock_client.set.assert_called_once_with("key1", "value1", ex=60)

    def test_set_without_ttl(self):
        mock_client = MagicMock()
        with patch("app.core.redis.redis_client", mock_client):
            cache = RedisCache()
            cache.set("key1", "value1")
            mock_client.set.assert_called_once_with("key1", "value1", ex=None)

    def test_delete_delegates_to_client(self):
        mock_client = MagicMock()
        with patch("app.core.redis.redis_client", mock_client):
            cache = RedisCache()
            cache.delete("key1")
            mock_client.delete.assert_called_once_with("key1")

    def test_exists_returns_true(self):
        mock_client = MagicMock()
        mock_client.exists.return_value = 1
        with patch("app.core.redis.redis_client", mock_client):
            cache = RedisCache()
            assert cache.exists("key1") is True

    def test_exists_returns_false(self):
        mock_client = MagicMock()
        mock_client.exists.return_value = 0
        with patch("app.core.redis.redis_client", mock_client):
            cache = RedisCache()
            assert cache.exists("key1") is False


class TestCreateCache:
    """create_cache 工厂函数测试。"""

    def test_default_returns_memory_cache(self):
        with patch("app.core.cache.os.getenv", return_value="memory"):
            cache = create_cache()
            assert isinstance(cache, MemoryCache)

    def test_redis_env_returns_redis_cache(self):
        with patch("app.core.cache.os.getenv", return_value="redis"):
            with patch("app.core.redis.redis_client", MagicMock()):
                cache = create_cache()
                assert isinstance(cache, RedisCache)

    def test_unknown_backend_returns_memory_cache(self):
        with patch("app.core.cache.os.getenv", return_value="invalid"):
            cache = create_cache()
            assert isinstance(cache, MemoryCache)


class TestGetCache:
    """get_cache 单例模式测试。"""

    def test_returns_cache_backend(self):
        gen = get_cache()
        cache = next(gen)
        assert cache is not None
        # 协议检查
        assert hasattr(cache, "get")
        assert hasattr(cache, "set")
        assert hasattr(cache, "delete")
        assert hasattr(cache, "exists")

    def test_returns_same_instance(self):
        gen1 = get_cache()
        gen2 = get_cache()
        cache1 = next(gen1)
        cache2 = next(gen2)
        assert cache1 is cache2
