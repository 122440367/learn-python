from passlib.context import CryptContext
from sqlmodel import Session, select

from app.models.user import User
from app.models.response import APIResponse, UserResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def register(session: Session, name: str, password: str, email: str) -> APIResponse:
    statement = select(User).where(User.name == name)
    existing = session.exec(statement).first()
    if existing is not None:
        return APIResponse(code=1, message="username already exists")

    user = User(
        name=name,
        password=hash_password(password),
        email=email,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return APIResponse(
        data=UserResponse(name=user.name, email=user.email),
    )


def login(session: Session, name: str, password: str) -> APIResponse:
    statement = select(User).where(User.name == name)
    user = session.exec(statement).first()
    if user is None:
        return APIResponse(code=1, message="user not found")
    if not verify_password(password, user.password):
        return APIResponse(code=2, message="wrong password")
    return APIResponse(
        data=UserResponse(name=user.name, email=user.email),
    )


def update_password(session: Session, user_id: int, old_password: str, new_password: str) -> APIResponse:
    user = session.get(User, user_id)
    if user is None:
        return APIResponse(code=1919810, message="user not found")
    if not verify_password(old_password, user.password):
        return APIResponse(code=2, message="wrong password")
    user.password = hash_password(new_password)
    session.add(user)
    session.commit()
    return APIResponse(message="password updated")


def update_name(session: Session, user_id: int, name: str) -> APIResponse:
    user = session.get(User, user_id)
    if user is None:
        return APIResponse(code=1919810, message="user not found")
    statement = select(User).where(User.name == name)
    existing = session.exec(statement).first()
    if existing is not None:
        return APIResponse(code=1, message="username already exists")
    user.name = name
    session.add(user)
    session.commit()
    session.refresh(user)
    return APIResponse(data=UserResponse(name=user.name, email=user.email))


def delete_user(session: Session, user_id: int) -> APIResponse:
    user = session.get(User, user_id)
    if user is None:
        return APIResponse(code=1919810, message="user not found")
    session.delete(user)
    session.commit()
    return APIResponse(message="user deleted")


def read_user(session: Session, user_id: int) -> APIResponse:
    user = session.get(User, user_id)
    if user is None:
        return APIResponse(code=1919810, message="user not found")
    return APIResponse(
        data=UserResponse(name=user.name, email=user.email)
    )
