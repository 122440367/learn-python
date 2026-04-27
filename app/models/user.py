from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):   # table=True 表示这是一个数据库表
    id: int | None = Field(default=None, primary_key=True)
    name: str
    password: str
    email: str