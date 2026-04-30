import pytest
from sqlmodel import Session, select
from fastapi.testclient import TestClient

from app.core.database import get_session
from app.main import app
from app.models.tb_user import User


def _get_user_id(client: TestClient, name: str) -> int:
    """通过 override 的 session 拿到已注册用户的 ID。"""
    gen = app.dependency_overrides[get_session]()
    session = next(gen)
    user = session.exec(select(User).where(User.name == name)).first()
    return user.id


class TestRootEndpoint:
    """根路由测试。"""

    def test_read_root(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["content"] == "Hello, world!"


class TestRegisterEndpoint:
    """POST /user/register 测试。"""

    def test_register_success(self, client):
        resp = client.post("/user/register", json={
            "name": "alice",
            "password": "pass123",
            "email": "alice@example.com",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "alice"

    def test_register_duplicate_email(self, client):
        client.post("/user/register", json={
            "name": "bob", "password": "pass", "email": "bob@test.com",
        })
        resp = client.post("/user/register", json={
            "name": "bob2", "password": "pass2", "email": "bob@test.com",
        })
        assert resp.status_code == 201
        assert resp.json()["code"] == 1


class TestLoginEndpoint:
    """POST /user/login 测试。"""

    def test_login_success(self, client):
        client.post("/user/register", json={
            "name": "dave", "password": "pass123", "email": "dave@test.com",
        })
        resp = client.post("/user/login", json={
            "email": "dave@test.com", "password": "pass123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "dave"

    def test_login_not_found(self, client):
        resp = client.post("/user/login", json={
            "email": "nobody@test.com", "password": "pass",
        })
        assert resp.json()["code"] == 1

    def test_login_wrong_password(self, client):
        client.post("/user/register", json={
            "name": "eve", "password": "pass123", "email": "eve@test.com",
        })
        resp = client.post("/user/login", json={
            "email": "eve@test.com", "password": "wrong",
        })
        assert resp.json()["code"] == 2


class TestReadUserEndpoint:
    """GET /user/{user_id} 测试。"""

    def test_read_user_success(self, client):
        client.post("/user/register", json={
            "name": "frank", "password": "pass", "email": "frank@test.com",
        })
        user_id = _get_user_id(client, "frank")
        resp = client.get(f"/user/{user_id}")
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "frank"

    def test_read_user_not_found(self, client):
        resp = client.get("/user/99999")
        assert resp.json()["code"] == 1919810


class TestUpdatePasswordEndpoint:
    """PUT /user/password 测试。"""

    def test_update_password_success(self, client):
        client.post("/user/register", json={
            "name": "grace", "password": "oldpass", "email": "grace@test.com",
        })
        user_id = _get_user_id(client, "grace")
        resp = client.put("/user/password", json={
            "id": user_id,
            "old_password": "oldpass",
            "new_password": "newpass",
        })
        assert resp.status_code == 200
        assert resp.json()["code"] == 0
        # 验证新密码可登录
        login_resp = client.post("/user/login", json={
            "email": "grace@test.com", "password": "newpass",
        })
        assert login_resp.json()["code"] == 0

    def test_update_password_wrong_old(self, client):
        client.post("/user/register", json={
            "name": "heidi", "password": "pass", "email": "heidi@test.com",
        })
        user_id = _get_user_id(client, "heidi")
        resp = client.put("/user/password", json={
            "id": user_id,
            "old_password": "wrong",
            "new_password": "newpass",
        })
        assert resp.json()["code"] == 2


class TestUpdateNameEndpoint:
    """PUT /user/name 测试。"""

    def test_update_name_success(self, client):
        client.post("/user/register", json={
            "name": "ivan", "password": "pass", "email": "ivan@test.com",
        })
        user_id = _get_user_id(client, "ivan")
        resp = client.put("/user/name", json={
            "id": user_id, "name": "ivan_new",
        })
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "ivan_new"

    def test_update_name_duplicate(self, client):
        client.post("/user/register", json={
            "name": "judy", "password": "pass", "email": "judy@test.com",
        })
        client.post("/user/register", json={
            "name": "karl", "password": "pass", "email": "karl@test.com",
        })
        user_id2 = _get_user_id(client, "karl")
        resp = client.put("/user/name", json={
            "id": user_id2, "name": "judy",
        })
        assert resp.json()["code"] == 1


class TestDeleteUserEndpoint:
    """DELETE /user/{user_id} 测试。"""

    def test_delete_user_success(self, client):
        client.post("/user/register", json={
            "name": "mallory", "password": "pass", "email": "mallory@test.com",
        })
        user_id = _get_user_id(client, "mallory")
        resp = client.delete(f"/user/{user_id}")
        assert resp.status_code == 200
        assert resp.json()["code"] == 0
        assert resp.json()["message"] == "user deleted"
        # 再查应该 not found
        get_resp = client.get(f"/user/{user_id}")
        assert get_resp.json()["code"] == 1919810

    def test_delete_user_not_found(self, client):
        resp = client.delete("/user/99999")
        assert resp.json()["code"] == 1919810
