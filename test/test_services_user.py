import pytest
from sqlmodel import Session

from sqlmodel import select as sqlmodel_select

from app.models.tb_user import User
from app.models.response import APIResponse
from app.services import user as user_service
from app.repositories import user as user_repo


class TestPasswordHashing:
    """密码哈希与验证测试。"""

    def test_hash_password_returns_hash(self):
        hashed = user_repo.hash_password("secret123")
        assert isinstance(hashed, str)
        assert hashed != "secret123"

    def test_verify_password_correct(self):
        hashed = user_repo.hash_password("secret123")
        assert user_repo.verify_password("secret123", hashed) is True

    def test_verify_password_wrong(self):
        hashed = user_repo.hash_password("secret123")
        assert user_repo.verify_password("wrong_password", hashed) is False


class TestRegister:
    """用户注册测试。"""

    def test_register_success(self, session):
        resp = user_service.register(session, "alice", "pass123", "alice@example.com")
        assert isinstance(resp, APIResponse)
        assert resp.code == 0
        assert resp.message == "success"
        assert resp.data.name == "alice"
        assert resp.data.email == "alice@example.com"

    def test_register_duplicate_email(self, session):
        user_service.register(session, "bob", "pass123", "bob@example.com")
        resp = user_service.register(session, "bob2", "pass456", "bob@example.com")
        assert resp.code == 1
        assert resp.message == "email already registered"

    def test_register_stores_hashed_password(self, session):
        user_service.register(session, "charlie", "mypass", "charlie@example.com")
        user = session.exec(
            sqlmodel_select(User).where(User.name == "charlie")
        ).first()
        assert user is not None
        assert user.password != "mypass"
        assert user_repo.verify_password("mypass", user.password)


class TestLogin:
    """用户登录测试。"""

    def test_login_success(self, session):
        user_service.register(session, "dave", "pass123", "dave@example.com")
        resp = user_service.login(session, "dave@example.com", "pass123")
        assert resp.code == 0
        assert resp.data.name == "dave"
        assert resp.data.email == "dave@example.com"

    def test_login_user_not_found(self, session):
        resp = user_service.login(session, "nobody@example.com", "pass123")
        assert resp.code == 1
        assert resp.message == "user not found"

    def test_login_wrong_password(self, session):
        user_service.register(session, "eve", "pass123", "eve@example.com")
        resp = user_service.login(session, "eve@example.com", "wrong")
        assert resp.code == 2
        assert resp.message == "wrong password"


class TestReadUser:
    """读取用户测试。"""

    def test_read_user_success(self, session):
        user_service.register(session, "frank", "pass123", "frank@example.com")
        user = session.exec(
            sqlmodel_select(User).where(User.name == "frank")
        ).first()
        resp = user_service.read_user(session, user.id)
        assert resp.code == 0
        assert resp.data.name == "frank"
        assert resp.data.email == "frank@example.com"

    def test_read_user_not_found(self, session):
        resp = user_service.read_user(session, 99999)
        assert resp.code == 1919810
        assert resp.message == "user not found"


class TestUpdatePassword:
    """修改密码测试。"""

    def test_update_password_success(self, session):
        user_service.register(session, "grace", "oldpass", "grace@example.com")
        user = session.exec(
            sqlmodel_select(User).where(User.name == "grace")
        ).first()
        resp = user_service.update_password(session, user.id, "oldpass", "newpass")
        assert resp.code == 0
        assert resp.message == "password updated"
        # 验证新密码可以登录
        login_resp = user_service.login(session, "grace@example.com", "newpass")
        assert login_resp.code == 0

    def test_update_password_user_not_found(self, session):
        resp = user_service.update_password(session, 99999, "old", "new")
        assert resp.code == 1919810
        assert resp.message == "user not found"

    def test_update_password_wrong_old_password(self, session):
        user_service.register(session, "heidi", "pass123", "heidi@example.com")
        user = session.exec(
            sqlmodel_select(User).where(User.name == "heidi")
        ).first()
        resp = user_service.update_password(session, user.id, "wrong", "newpass")
        assert resp.code == 2
        assert resp.message == "wrong password"


class TestUpdateName:
    """修改用户名测试。"""

    def test_update_name_success(self, session):
        user_service.register(session, "ivan", "pass123", "ivan@example.com")
        user = session.exec(
            sqlmodel_select(User).where(User.name == "ivan")
        ).first()
        resp = user_service.update_name(session, user.id, "ivan_new")
        assert resp.code == 0
        assert resp.data.name == "ivan_new"

    def test_update_name_user_not_found(self, session):
        resp = user_service.update_name(session, 99999, "new_name")
        assert resp.code == 1919810
        assert resp.message == "user not found"

    def test_update_name_duplicate(self, session):
        user_service.register(session, "judy", "pass123", "judy@example.com")
        user_service.register(session, "karl", "pass456", "karl@example.com")
        user_judy = session.exec(
            sqlmodel_select(User).where(User.name == "judy")
        ).first()
        resp = user_service.update_name(session, user_judy.id, "karl")
        assert resp.code == 1
        assert resp.message == "username already exists"


class TestDeleteUser:
    """删除用户测试。"""

    def test_delete_user_success(self, session):
        user_service.register(session, "mallory", "pass123", "mallory@example.com")
        user = session.exec(
            sqlmodel_select(User).where(User.name == "mallory")
        ).first()
        resp = user_service.delete_user(session, user.id)
        assert resp.code == 0
        assert resp.message == "user deleted"
        # 验证用户已被删除
        deleted = session.get(User, user.id)
        assert deleted is None

    def test_delete_user_not_found(self, session):
        resp = user_service.delete_user(session, 99999)
        assert resp.code == 1919810
        assert resp.message == "user not found"
