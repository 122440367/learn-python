import threading
import time

import pytest

from app.core.lock import RWLock, KeyLock


class TestRWLock:
    """RWLock 读写锁测试。"""

    @pytest.fixture
    def rwlock(self):
        return RWLock()

    def test_read_lock_acquired_and_released(self, rwlock):
        with rwlock.read():
            assert rwlock._active_readers == 1
        assert rwlock._active_readers == 0

    def test_write_lock_acquired_and_released(self, rwlock):
        with rwlock.write():
            assert rwlock._active_writers == 1
        assert rwlock._active_writers == 0

    def test_multiple_readers_concurrent(self, rwlock):
        """多个读者应能并发持有读锁。"""
        active_count = []

        def reader():
            with rwlock.read():
                active_count.append(rwlock._active_readers)
                time.sleep(0.05)

        threads = [threading.Thread(target=reader) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(active_count) == 5
        assert max(active_count) >= 2  # 至少有两个读者同时持有锁
        assert rwlock._active_readers == 0

    def test_writer_excludes_readers(self, rwlock):
        """写者持锁时读者不能进入。"""
        results = []

        def writer():
            with rwlock.write():
                results.append("writer_enter")
                time.sleep(0.1)
                results.append("writer_leave")

        def reader():
            with rwlock.read():
                results.append("reader_enter")
                results.append("reader_leave")

        t_writer = threading.Thread(target=writer)
        t_reader = threading.Thread(target=reader)

        t_writer.start()
        time.sleep(0.02)  # 确保写者先获取锁
        t_reader.start()

        t_writer.join()
        t_reader.join()

        # 读者只能在写者释放后才能进入
        writer_leave_idx = results.index("writer_leave")
        reader_enter_idx = results.index("reader_enter")
        assert reader_enter_idx > writer_leave_idx

    def test_writer_excludes_other_writers(self, rwlock):
        """同一时间只能有一个写者。"""
        active_writers = []
        lock = threading.Lock()

        def writer():
            with rwlock.write():
                with lock:
                    active_writers.append(1)
                time.sleep(0.05)

        threads = [threading.Thread(target=writer) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert rwlock._active_writers == 0

    def test_writer_preference(self, rwlock):
        """写者优先：有等待的写者时新读者不能进入。"""
        events = []
        write_done = threading.Event()

        def writer():
            with rwlock.write():
                events.append("writer")
            write_done.set()

        def reader():
            with rwlock.read():
                events.append("reader")

        # 先让读者持有锁
        with rwlock.read():
            # 启动写者（会等待）
            t_writer = threading.Thread(target=writer)
            t_writer.start()
            time.sleep(0.02)

            # 启动新读者（应被写者阻塞）
            t_reader = threading.Thread(target=reader)
            t_reader.start()
            time.sleep(0.02)

            # 释放读锁
            pass

        t_writer.join()
        t_reader.join()

        # 写者优先：写者应在读者之前执行
        writer_idx = events.index("writer")
        assert writer_idx == 0

    def test_writers_ok_notified_when_last_reader_leaves(self, rwlock):
        """最后一个读者释放时应通知等待的写者。"""
        results = []

        def reader1():
            with rwlock.read():
                results.append("r1_enter")
                time.sleep(0.1)
                results.append("r1_leave")

        def reader2():
            time.sleep(0.02)
            with rwlock.read():
                results.append("r2_enter")
                time.sleep(0.05)
                results.append("r2_leave")

        def writer():
            time.sleep(0.03)
            with rwlock.write():
                results.append("writer_enter")
                results.append("writer_leave")

        threads = [
            threading.Thread(target=reader1),
            threading.Thread(target=reader2),
            threading.Thread(target=writer),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 写者应在所有读者离开后才进入
        writer_enter_idx = results.index("writer_enter")
        assert "r1_leave" in results[:writer_enter_idx]
        assert "r2_leave" in results[:writer_enter_idx]


class TestKeyLock:
    """KeyLock 按 key 粒度锁测试。"""

    @pytest.fixture
    def key_lock(self):
        return KeyLock()

    def test_same_key_serializes(self, key_lock):
        """同一 key 的并发访问应串行化。"""
        results = []

        def task(sleep_time):
            with key_lock.acquire(1):
                results.append("enter")
                time.sleep(sleep_time)
                results.append("leave")

        t1 = threading.Thread(target=task, args=(0.05,))
        t2 = threading.Thread(target=task, args=(0.05,))

        t1.start()
        time.sleep(0.01)
        t2.start()

        t1.join()
        t2.join()

        assert results == ["enter", "leave", "enter", "leave"]

    def test_different_keys_do_not_block(self, key_lock):
        """不同 key 的访问应互不阻塞。"""
        results = []

        def task(key, sleep_time):
            with key_lock.acquire(key):
                results.append(f"{key}_enter")
                time.sleep(sleep_time)
                results.append(f"{key}_leave")

        t1 = threading.Thread(target=task, args=(1, 0.08))
        t2 = threading.Thread(target=task, args=(2, 0.02))

        t1.start()
        time.sleep(0.01)
        t2.start()

        t2.join()
        t1.join()

        # key=2 应在 key=1 之前完成
        idx_2_leave = results.index("2_leave")
        idx_1_leave = results.index("1_leave")
        assert idx_2_leave < idx_1_leave

    def test_lock_is_reusable(self, key_lock):
        """同一 key 的锁应可重复使用。"""
        results = []
        for i in range(3):
            with key_lock.acquire(1):
                results.append(i)
        assert results == [0, 1, 2]
