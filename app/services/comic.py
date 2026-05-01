from pathlib import Path

from jmcomic import *

from app.core.cache import CacheBackend
from app.core.lock import KeyLock
from app.models.response import PdfFileResponse

_option_path = Path(__file__).resolve().parent.parent / "option.yml"
option = create_option_by_file(str(_option_path))

DOWNLOAD_DIR = Path(option.dir_rule.base_dir)

_album_lock = KeyLock()


def download_and_merge_pdf(album_id: int, cache: CacheBackend) -> PdfFileResponse:
    """下载图集，img2pdf插件会自动将图片合并为PDF文件。

    如果缓存中已有该 album_id 对应的文件路径且文件存在，则直接返回；
    否则下载后将文件路径加入缓存。
    同一 album_id 的并发请求会通过锁串行化，避免重复下载。
    """
    cache_key = f"jmcomic:{album_id}"

    # 快速路径：缓存命中且文件存在，无需加锁
    cached_path = cache.get(cache_key)
    if cached_path is not None:
        pdf_path = Path(cached_path)
        if pdf_path.exists():
            return PdfFileResponse(pdf_path, filename=pdf_path.name)
        else:
            cache.delete(cache_key)

    # 对同一 album_id 加锁，防止并发重复下载
    with _album_lock.acquire(album_id):
        # double-check：拿到锁后再查一次缓存
        cached_path = cache.get(cache_key)
        if cached_path is not None:
            pdf_path = Path(cached_path)
            if pdf_path.exists():
                return PdfFileResponse(pdf_path, filename=pdf_path.name)
            else:
                cache.delete(cache_key)

        download_album(album_id, option)

        pdf_path = DOWNLOAD_DIR / f"{album_id}.pdf"
        if not pdf_path.exists():
            raise FileNotFoundError(f"相册 {album_id} 的PDF生成失败")

        cache.set(cache_key, str(pdf_path))

    # 锁释放后再构造响应，避免在持锁期间做文件 I/O 返回
    return PdfFileResponse(pdf_path, filename=pdf_path.name)
