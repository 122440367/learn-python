from typing import Any

from fastapi.responses import FileResponse
from pydantic import BaseModel


class APIResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None


class UserResponse(BaseModel):
    name: str
    email: str


class PdfFileResponse(FileResponse):
    """PDF文件响应，用于返回下载生成的PDF文件。"""

    def __init__(self, path, filename=None):
        super().__init__(
            path,
            media_type="application/pdf",
            filename=filename,
        )