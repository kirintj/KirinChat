from io import BytesIO
from loguru import logger

from minio import Minio
from kirinchat.settings import app_settings


class MinioService:
    """MinIO/S3 文件存储服务。"""

    def __init__(self):
        self._client = None
        self._bucket = None

    @property
    def client(self) -> Minio:
        """延迟初始化 MinIO 客户端，避免模块导入时连接失败。"""
        if self._client is None:
            self._client = Minio(
                app_settings.minio_endpoint,
                access_key=app_settings.minio_access_key,
                secret_key=app_settings.minio_secret_key,
                secure=app_settings.minio_secure,
            )
        return self._client

    @property
    def bucket(self) -> str:
        if self._bucket is None:
            self._bucket = app_settings.minio_bucket
        return self._bucket

    def ensure_bucket(self):
        """确保存储桶存在，不存在则创建。"""
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def upload_file(self, file_data: bytes, object_name: str) -> str:
        """上传文件到 MinIO，返回对象名。"""
        self.client.put_object(
            self.bucket,
            object_name,
            BytesIO(file_data),
            length=len(file_data),
        )
        return object_name

    def download_file(self, object_name: str) -> bytes:
        """从 MinIO 下载文件，返回字节数据。"""
        response = self.client.get_object(self.bucket, object_name)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def delete_file(self, object_name: str):
        """从 MinIO 删除文件。"""
        self.client.remove_object(self.bucket, object_name)


# 全局单例
minio_service = MinioService()
