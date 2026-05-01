import tempfile
from unittest.mock import patch, MagicMock

import pytest

from app.core.cache import get_cache
from app.main import app


class TestDownloadEndpoint:
    """GET /jm/download/{album_id} 测试。

    通过依赖覆盖注入 mock 的 CacheBackend，通过 patch 服务层避免真实下载。
    """

    @pytest.fixture(autouse=True)
    def mock_cache_dependency(self):
        """注入 mock MemoryCache，只 pop 自身 key 避免影响其他覆盖。"""
        mock_cache = MagicMock()
        mock_cache.get.return_value = None

        def override_get_cache():
            yield mock_cache

        app.dependency_overrides[get_cache] = override_get_cache
        yield mock_cache
        # 只清除自己的覆盖，不影响 client fixture 设置的 get_session
        app.dependency_overrides.pop(get_cache, None)

    def test_download_endpoint_calls_service(self, client, mock_cache_dependency):
        """路由应将 album_id 和 cache 透传给服务层。"""
        from app.models.response import PdfFileResponse

        # PdfFileResponse 需要真实文件才能渲染，创建临时文件
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf:
            tf.write(b"%PDF-1.4 test")
            pdf_path = tf.name

        mock_response = PdfFileResponse(pdf_path, filename="1.pdf")

        with patch(
            "app.services.comic.download_and_merge_pdf",
            return_value=mock_response,
        ) as mock_service:
            resp = client.get("/jm/download/1")

            assert resp.status_code == 200
            mock_service.assert_called_once()
            args = mock_service.call_args[0]
            assert args[0] == 1  # album_id
            assert args[1] is mock_cache_dependency

    def test_download_service_exception(self, client, mock_cache_dependency):
        """服务层抛出异常时 TestClient 应传播该异常。"""
        with patch(
            "app.services.comic.download_and_merge_pdf",
            side_effect=FileNotFoundError("相册 999 的PDF生成失败"),
        ) as mock_service:
            with pytest.raises(FileNotFoundError, match="PDF生成失败"):
                client.get("/jm/download/999")

            mock_service.assert_called_once()
