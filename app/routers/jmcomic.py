from fastapi import APIRouter

from app.services import jmcomic as jmcomic_service

router = APIRouter(prefix="/jm", tags=["jm"])


@router.get("/download/{album_id}")
def download(album_id: int):
    return jmcomic_service.download_and_merge_pdf(album_id)
