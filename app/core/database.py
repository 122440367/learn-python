import os
from typing import Any, Generator

from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine

load_dotenv()

DATABASE_URL = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME')}"
)

engine = create_engine(
    DATABASE_URL,
    echo=True,              # 打印执行的SQL语句
    pool_size=10,           # 连接池中保持的常驻连接数
    max_overflow=20,        # 超出pool_size后允许创建的最大额外连接数，总连接数上限为 pool_size + max_overflow = 30
    pool_timeout=30,        # 获取连接的最大等待时间（秒），超时抛出异常
    pool_recycle=900,       # 连接存活的最大时间（秒），超过后自动回收重建，防止MySQL断开空闲连接
    pool_pre_ping=True,     # 每次从池中取连接时先检测是否存活，避免使用已断开的连接
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, Any, None]:
    yield Session(engine)