from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core import get_session
from app.models.response import APIResponse
from app.models.request import UserCreateRequest, UserLoginRequest, PasswordUpdateRequest, UserUpdateRequest
from app.services import user as user_service

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=APIResponse)
def read_user(user_id: int, session: Session = Depends(get_session)):
    return user_service.read_user(session, user_id)


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def register(req: UserCreateRequest, session: Session = Depends(get_session)):
    return user_service.register(session, req.name, req.password, req.email)


@router.post("/login", status_code=status.HTTP_200_OK, response_model=APIResponse)
def login(req: UserLoginRequest, session: Session = Depends(get_session)):
    return user_service.login(session, req.email, req.password)


@router.put("/password", status_code=status.HTTP_200_OK, response_model=APIResponse)
def update_password(req: PasswordUpdateRequest, session: Session = Depends(get_session)):
    return user_service.update_password(session, req.id, req.old_password, req.new_password)


@router.put("/name", status_code=status.HTTP_200_OK, response_model=APIResponse)
def update_name(req: UserUpdateRequest, session: Session = Depends(get_session)):
    return user_service.update_name(session, req.id, req.name)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK, response_model=APIResponse)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    return user_service.delete_user(session, user_id)
