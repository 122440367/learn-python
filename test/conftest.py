import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.main as main_module
from app.core.database import get_session
from app.main import app


@pytest.fixture(name="engine")
def engine_fixture():
    """创建 SQLite 内存数据库引擎，使用 StaticPool 保证单连接复用。"""
    engine = create_engine(
        "sqlite://",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(name="session")
def session_fixture(engine):
    """提供数据库会话，测试结束后回滚。"""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(engine):
    """提供 FastAPI TestClient，注入测试用的数据库会话，跳过真实数据库连接。"""
    def override_get_session():
        with Session(engine) as session:
            yield session

    # 替换 create_db_and_tables 为空操作，避免 lifespan 连接真实 MySQL
    original = main_module.create_db_and_tables
    main_module.create_db_and_tables = lambda: None

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

    # 恢复原始函数
    main_module.create_db_and_tables = original
