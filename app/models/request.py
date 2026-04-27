from pydantic import BaseModel


class UserCreateRequest(BaseModel):
    name: str
    password: str
    email: str


class UserLoginRequest(BaseModel):
    name: str
    password: str


class PasswordUpdateRequest(BaseModel):
    id:int
    old_password: str
    new_password: str

class UserUpdateRequest(BaseModel):
    id: int
    name: str
