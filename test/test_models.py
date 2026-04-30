import pytest
from pydantic import ValidationError

from app.models.request import (
    UserCreateRequest,
    UserLoginRequest,
    PasswordUpdateRequest,
    UserUpdateRequest,
)
from app.models.response import APIResponse, UserResponse, PdfFileResponse
from app.models.schemas import UserPublic
from app.models.tb_user import User


class TestAPIResponse:
    """APIResponse 模型测试。"""

    def test_default_values(self):
        resp = APIResponse()
        assert resp.code == 0
        assert resp.message == "success"
        assert resp.data is None

    def test_custom_values(self):
        resp = APIResponse(code=1, message="error", data={"key": "value"})
        assert resp.code == 1
        assert resp.message == "error"
        assert resp.data == {"key": "value"}


class TestUserResponse:
    """UserResponse 模型测试。"""

    def test_create(self):
        resp = UserResponse(name="alice", email="alice@test.com")
        assert resp.name == "alice"
        assert resp.email == "alice@test.com"


class TestUserCreateRequest:
    """UserCreateRequest 模型测试。"""

    def test_valid(self):
        req = UserCreateRequest(name="alice", password="pass", email="a@b.com")
        assert req.name == "alice"
        assert req.password == "pass"
        assert req.email == "a@b.com"

    def test_missing_field(self):
        with pytest.raises(ValidationError):
            UserCreateRequest(name="alice", password="pass")  # 缺少 email


class TestUserLoginRequest:
    """UserLoginRequest 模型测试。"""

    def test_valid(self):
        req = UserLoginRequest(email="alice@test.com", password="pass")
        assert req.email == "alice@test.com"

    def test_missing_field(self):
        with pytest.raises(ValidationError):
            UserLoginRequest(email="alice@test.com")  # 缺少 password


class TestPasswordUpdateRequest:
    """PasswordUpdateRequest 模型测试。"""

    def test_valid(self):
        req = PasswordUpdateRequest(id=1, old_password="old", new_password="new")
        assert req.id == 1
        assert req.old_password == "old"
        assert req.new_password == "new"

    def test_missing_field(self):
        with pytest.raises(ValidationError):
            PasswordUpdateRequest(id=1, old_password="old")  # 缺少 new_password


class TestUserUpdateRequest:
    """UserUpdateRequest 模型测试。"""

    def test_valid(self):
        req = UserUpdateRequest(id=1, name="new_name")
        assert req.id == 1
        assert req.name == "new_name"

    def test_missing_field(self):
        with pytest.raises(ValidationError):
            UserUpdateRequest(id=1)  # 缺少 name


class TestUserModel:
    """User SQLModel 测试。"""

    def test_create_instance(self):
        user = User(name="alice", password="hashed", email="a@b.com")
        assert user.name == "alice"
        assert user.id is None  # 自动生成主键

    def test_create_with_id(self):
        user = User(id=1, name="bob", password="hashed", email="b@b.com")
        assert user.id == 1


class TestUserPublic:
    """UserPublic DTO 模型测试。"""

    def test_create(self):
        user = UserPublic(id=1, name="alice", email="alice@test.com")
        assert user.id == 1
        assert user.name == "alice"
        assert user.email == "alice@test.com"

    def test_missing_field(self):
        with pytest.raises(ValidationError):
            UserPublic(id=1, name="alice")  # 缺少 email

    def test_no_password_field(self):
        """UserPublic 不应包含 password 字段。"""
        user = UserPublic(id=1, name="alice", email="alice@test.com")
        assert not hasattr(user, "password")


class TestPdfFileResponse:
    """PdfFileResponse 模型测试。"""

    def test_media_type_is_pdf(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf:
            tf.write(b"%PDF-1.4 test")
            tf.flush()
            resp = PdfFileResponse(tf.name, filename="test.pdf")
            assert resp.media_type == "application/pdf"
            assert resp.filename == "test.pdf"

    def test_default_filename(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf:
            tf.write(b"%PDF-1.4 test")
            resp = PdfFileResponse(tf.name)
            assert resp.media_type == "application/pdf"
