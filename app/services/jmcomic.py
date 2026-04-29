from pathlib import Path

from jmcomic import *

from app.models.response import PdfFileResponse

_option_path = Path(__file__).resolve().parent.parent / "option.yml"
option = create_option_by_file(str(_option_path))

DOWNLOAD_DIR = Path(option.dir_rule.base_dir)


def download_and_merge_pdf(album_id: int) -> PdfFileResponse:
    """下载图集，img2pdf插件会自动将图片合并为PDF文件。

    返回生成的PDF文件响应。
    """
    download_album(album_id, option)

    pdf_path = DOWNLOAD_DIR / f"{album_id}.pdf"
    if not pdf_path.exists():
        raise FileNotFoundError(f"相册 {album_id} 的PDF生成失败")

    return PdfFileResponse(pdf_path, filename=pdf_path.name)
