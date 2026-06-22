import pytest
from unittest.mock import patch, MagicMock
from kirinchat.common.file_storage.minio_service import MinioService


class TestMinioService:
    @patch("kirinchat.common.file_storage.minio_service.Minio")
    def test_upload_file(self, mock_minio_cls):
        mock_client = MagicMock()
        mock_minio_cls.return_value = mock_client

        service = MinioService()
        result = service.upload_file(b"hello", "test.txt")

        assert result == "test.txt"
        mock_client.put_object.assert_called_once()

    @patch("kirinchat.common.file_storage.minio_service.Minio")
    def test_download_file(self, mock_minio_cls):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.read.return_value = b"file content"
        mock_response.close = MagicMock()
        mock_response.release_conn = MagicMock()
        mock_client.get_object.return_value = mock_response
        mock_minio_cls.return_value = mock_client

        service = MinioService()
        data = service.download_file("test.txt")

        assert data == b"file content"

    @patch("kirinchat.common.file_storage.minio_service.Minio")
    def test_delete_file(self, mock_minio_cls):
        mock_client = MagicMock()
        mock_minio_cls.return_value = mock_client

        service = MinioService()
        service.delete_file("test.txt")

        mock_client.remove_object.assert_called_once()

    @patch("kirinchat.common.file_storage.minio_service.Minio")
    def test_ensure_bucket_creates_when_missing(self, mock_minio_cls):
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = False
        mock_minio_cls.return_value = mock_client

        service = MinioService()
        service.ensure_bucket()

        mock_client.make_bucket.assert_called_once()
