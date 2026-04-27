from fastapi import status
from fastapi import FastAPI
from app.models.response import APIResponse

app = FastAPI()


@app.get("/", status_code=status.HTTP_200_OK)
def read_root():
    return APIResponse(
        data={"content": "Hello, world!"},
    )


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)