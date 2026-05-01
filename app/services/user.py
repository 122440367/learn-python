from sqlmodel import Session

from app.models.response import APIResponse, UserResponse
from app.models.schemas import UserPublic
from app.repositories import user as user_repo


def _to_response(user: UserPublic) -> UserResponse:
    return UserResponse(name=user.name, email=user.email)


def register(session: Session, name: str, password: str, email: str) -> APIResponse:
    existing = user_repo.get_by_email(session, email)
    if existing is not None:
        return APIResponse(code=1, message="email already registered")

    public = user_repo.create(session, name, email, password)
    return APIResponse(data=_to_response(public))


def login(session: Session, email: str, password: str) -> APIResponse:
    public, error = user_repo.authenticate(session, email, password)
    if error == "not_found":
        return APIResponse(code=1, message="user not found")
    if error == "wrong_password":
        return APIResponse(code=2, message="wrong password")
    return APIResponse(data=_to_response(public))


def update_password(session: Session, user_id: int, old_password: str, new_password: str) -> APIResponse:
    error = user_repo.change_password(session, user_id, old_password, new_password)
    if error == "not_found":
        return APIResponse(code=1919810, message="user not found")
    if error == "wrong_password":
        return APIResponse(code=2, message="wrong password")
    return APIResponse(message="password updated")


def update_name(session: Session, user_id: int, name: str) -> APIResponse:
    public = user_repo.get_by_id(session, user_id)
    if public is None:
        return APIResponse(code=1919810, message="user not found")
    existing = user_repo.get_by_name(session, name)
    if existing is not None:
        return APIResponse(code=1, message="username already exists")
    public = user_repo.set_name(session, user_id, name)
    return APIResponse(data=_to_response(public))


def delete_user(session: Session, user_id: int) -> APIResponse:
    if not user_repo.remove(session, user_id):
        return APIResponse(code=1919810, message="user not found")
    return APIResponse(message="user deleted")


def read_user(session: Session, user_id: int) -> APIResponse:
    public = user_repo.get_by_id(session, user_id)
    if public is None:
        return APIResponse(code=1919810, message="user not found")
    return APIResponse(data=_to_response(public))
