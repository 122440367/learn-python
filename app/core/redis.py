import os
from collections.abc import Generator
from typing import Any

from dotenv import load_dotenv
from redis import Redis
from redis import ConnectionPool

load_dotenv()

connection_pool = ConnectionPool(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    password=os.getenv("REDIS_PASSWORD") or None,
    db=int(os.getenv("REDIS_DB", "0")),
    decode_responses=True,       # 返回 str 而不是 bytes，省去手动 decode
    max_connections=20,          # 连接池最大连接数
    socket_timeout=5,            # 读写超时（秒）
    socket_connect_timeout=5,    # 连接超时（秒）
)

redis_client = Redis(connection_pool=connection_pool)


def get_redis() -> Generator[Redis, Any, None]:
    yield redis_client
