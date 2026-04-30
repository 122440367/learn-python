from fastapi import APIRouter, Depends

from app.core.cache import CacheBackend, get_cache
from app.services import comic as jmcomic_service

router = APIRouter(prefix="/jm", tags=["jm"])


@router.get("/download/{album_id}")
def download(album_id: int, cache: CacheBackend = Depends(get_cache)):
    return jmcomic_service.download_and_merge_pdf(album_id, cache)
