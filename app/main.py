from contextlib import asynccontextmanager

from fastapi import FastAPI, status

from app.core import create_db_and_tables
from app.models.response import APIResponse
from app.routers import user as user_router


@asynccontextmanager
async def lifespan(app):
    create_db_and_tables()   # 启动时建表
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(user_router.router)


@app.get("/", status_code=status.HTTP_200_OK)
def read_root():
    return APIResponse(
        data={"content": "Hello, world!"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
