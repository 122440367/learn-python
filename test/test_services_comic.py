from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.models.response import PdfFileResponse


class TestDownloadAndMergePdf:
    """comic 服务 download_and_merge_pdf 测试。

    所有测试通过 mock jmcomic 库避免真实下载请求。
    """

    @pytest.fixture
    def mock_cache(self):
        cache = MagicMock()
        cache.get.return_value = None  # 默认缓存未命中
        return cache

    @pytest.fixture
    def mock_download_album(self):
        with patch("app.services.comic.download_album") as mock:
            yield mock

    @pytest.fixture
    def stub_exists_all_true(self):
        """Path.exists 始终返回 True。"""
        with patch("pathlib.Path.exists", return_value=True):
            yield

    @pytest.fixture
    def stub_exists_all_false(self):
        """Path.exists 始终返回 False。"""
        with patch("pathlib.Path.exists", return_value=False):
            yield

    # ---- cache hit ---- #

    def test_cache_hit_file_exists(
        self, mock_cache, mock_download_album, stub_exists_all_true
    ):
        """缓存命中且文件存在：不触发下载，直接返回。"""
        mock_cache.get.return_value = "/cached/42.pdf"

        from app.services.comic import download_and_merge_pdf

        result = download_and_merge_pdf(42, mock_cache)

        assert isinstance(result, PdfFileResponse)
        assert result.filename == "42.pdf"
        mock_download_album.assert_not_called()
        mock_cache.delete.assert_not_called()
        mock_cache.set.assert_not_called()

    # ---- cache miss ---- #

    def test_cache_miss_downloads(
        self, mock_cache, mock_download_album, stub_exists_all_true
    ):
        """缓存未命中：应触发下载，并将路径写入缓存。"""
        from app.services.comic import download_and_merge_pdf

        result = download_and_merge_pdf(1, mock_cache)

        assert isinstance(result, PdfFileResponse)
        mock_download_album.assert_called_once()
        mock_cache.set.assert_called_once()
        args = mock_cache.set.call_args[0]
        assert args[0] == "jmcomic:1"
        assert args[1].endswith(".pdf")

    # ---- stale cache (file gone) ---- #

    def test_cache_hit_but_file_gone_triggers_download(
        self, mock_cache, mock_download_album
    ):
        """缓存命中但文件已被删除：应先清除缓存再触发下载。"""
        mock_cache.get.side_effect = [
            "/nonexistent/path/1.pdf",  # 快速路径：缓存命中但文件不存在
            None,  # double-check after lock: 未命中
        ]

        # Path.exists 对 stale 路径返回 False，对下载后的路径返回 True
        def mock_exists(self_path):
            if str(self_path) == "/nonexistent/path/1.pdf":
                return False
            return True

        with patch.object(Path, "exists", mock_exists):
            from app.services.comic import download_and_merge_pdf

            result = download_and_merge_pdf(1, mock_cache)

        assert isinstance(result, PdfFileResponse)
        mock_cache.delete.assert_any_call("jmcomic:1")
        mock_download_album.assert_called_once()
        mock_cache.set.assert_called_once()

    # ---- download failure ---- #

    def test_download_failure_raises_error(
        self, mock_cache, mock_download_album, stub_exists_all_false
    ):
        """下载后 PDF 文件不存在：应抛出 FileNotFoundError。"""
        from app.services.comic import download_and_merge_pdf

        with pytest.raises(FileNotFoundError, match="PDF生成失败"):
            download_and_merge_pdf(999, mock_cache)

        mock_download_album.assert_called_once()

    # ---- double-check ---- #

    def test_double_check_after_lock_hit(
        self, mock_cache, mock_download_album, stub_exists_all_true
    ):
        """double-check：加锁后再查缓存，命中且文件存在则不下载。"""
        mock_cache.get.side_effect = [
            None,  # 快速路径：未命中
            "/cached/path.pdf",  # double-check：命中
        ]

        from app.services.comic import download_and_merge_pdf

        result = download_and_merge_pdf(1, mock_cache)

        assert isinstance(result, PdfFileResponse)
        assert result.filename == "path.pdf"
        mock_download_album.assert_not_called()
        assert mock_cache.set.call_count == 0

    def test_double_check_stale_cache(
        self, mock_cache, mock_download_album
    ):
        """double-check 命中但文件不存在：清除缓存并下载。"""
        mock_cache.get.side_effect = [
            None,  # 快速路径：未命中
            "/stale/path.pdf",  # double-check：命中但文件已删除
        ]

        def mock_exists(self_path):
            if str(self_path) == "/stale/path.pdf":
                return False
            return True

        with patch.object(Path, "exists", mock_exists):
            from app.services.comic import download_and_merge_pdf

            result = download_and_merge_pdf(1, mock_cache)

        assert isinstance(result, PdfFileResponse)
        mock_cache.delete.assert_any_call("jmcomic:1")
        mock_download_album.assert_called_once()
        mock_cache.set.assert_called_once()

    # ---- filename ---- #

    def test_filename_from_pdf_path(
        self, mock_cache, mock_download_album, stub_exists_all_true
    ):
        """返回的 PdfFileResponse 文件名取自 PDF 路径。"""
        from app.services.comic import download_and_merge_pdf

        result = download_and_merge_pdf(42, mock_cache)

        assert result.filename == "42.pdf"
