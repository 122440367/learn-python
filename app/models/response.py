from typing import Any
from pydantic import BaseModel


class APIResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None


class UserResponse(BaseModel):
    name: str
    email: str