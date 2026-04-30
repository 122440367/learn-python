import threading
from contextlib import contextmanager
from typing import Generator


class RWLock:
    """读写锁：多个读者可并发持有，写者独占。写者优先策略防止写者饥饿。"""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._readers_ok = threading.Condition(self._lock)
        self._writers_ok = threading.Condition(self._lock)
        self._active_readers = 0
        self._active_writers = 0
        self._waiting_writers = 0

    @contextmanager
    def read(self) -> Generator[None, None, None]:
        with self._lock:
            while self._active_writers > 0 or self._waiting_writers > 0:
                self._readers_ok.wait()
            self._active_readers += 1
        try:
            yield
        finally:
            with self._lock:
                self._active_readers -= 1
                if self._active_readers == 0:
                    self._writers_ok.notify()

    @contextmanager
    def write(self) -> Generator[None, None, None]:
        with self._lock:
            self._waiting_writers += 1
            while self._active_readers > 0 or self._active_writers > 0:
                self._writers_ok.wait()
            self._waiting_writers -= 1
            self._active_writers += 1
        try:
            yield
        finally:
            with self._lock:
                self._active_writers -= 1
                self._readers_ok.notify_all()
                self._writers_ok.notify()


class KeyLock:
    """按 key 粒度分配独立锁，不同 key 互不阻塞。"""

    def __init__(self) -> None:
        self._guard = threading.Lock()
        self._locks: dict[int, threading.Lock] = {}

    @contextmanager
    def acquire(self, key: int) -> Generator[None, None, None]:
        with self._guard:
            if key not in self._locks:
                self._locks[key] = threading.Lock()
            lock = self._locks[key]
        with lock:
            yield
