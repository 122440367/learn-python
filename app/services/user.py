import bcrypt
from sqlmodel import Session

from app.models.tb_user import User
from app.models.response import APIResponse, UserResponse
from app.repositories import user as user_repo


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def register(session: Session, name: str, password: str, email: str) -> APIResponse:
    existing = user_repo.get_by_email(session, email)
    if existing is not None:
        return APIResponse(code=1, message="email already registered")

    user = User(
        name=name,
        password=hash_password(password),
        email=email,
    )
    user = user_repo.create(session, user)
    return APIResponse(
        data=UserResponse(name=user.name, email=user.email),
    )


def login(session: Session, email: str, password: str) -> APIResponse:
    user = user_repo.get_by_email(session, email)
    if user is None:
        return APIResponse(code=1, message="user not found")
    if not verify_password(password, user.password):
        return APIResponse(code=2, message="wrong password")
    return APIResponse(
        data=UserResponse(name=user.name, email=user.email),
    )


def update_password(session: Session, user_id: int, old_password: str, new_password: str) -> APIResponse:
    user = user_repo.get_by_id(session, user_id)
    if user is None:
        return APIResponse(code=1919810, message="user not found")
    if not verify_password(old_password, user.password):
        return APIResponse(code=2, message="wrong password")
    user.password = hash_password(new_password)
    user_repo.update(session, user)
    return APIResponse(message="password updated")


def update_name(session: Session, user_id: int, name: str) -> APIResponse:
    user = user_repo.get_by_id(session, user_id)
    if user is None:
        return APIResponse(code=1919810, message="user not found")
    existing = user_repo.get_by_name(session, name)
    if existing is not None:
        return APIResponse(code=1, message="username already exists")
    user.name = name
    user = user_repo.update(session, user)
    return APIResponse(data=UserResponse(name=user.name, email=user.email))


def delete_user(session: Session, user_id: int) -> APIResponse:
    user = user_repo.get_by_id(session, user_id)
    if user is None:
        return APIResponse(code=1919810, message="user not found")
    user_repo.delete(session, user)
    return APIResponse(message="user deleted")


def read_user(session: Session, user_id: int) -> APIResponse:
    user = user_repo.get_by_id(session, user_id)
    if user is None:
        return APIResponse(code=1919810, message="user not found")
    return APIResponse(
        data=UserResponse(name=user.name, email=user.email)
    )
