from pydantic import BaseModel


class UserPublic(BaseModel):
    """不含密码的用户公开模型，用于 repo -> service 层之间流转。"""

    id: int
    name: str
    email: str
