from io import BytesIO
from minio import Minio
from kirinchat.settings import app_settings


class MinioService:
    """MinIO/S3 文件存储服务。"""

    def __init__(self):
        self.client = Minio(
            app_settings.minio_endpoint,
            access_key=app_settings.minio_access_key,
            secret_key=app_settings.minio_secret_key,
            secure=app_settings.minio_secure,
        )
        self.bucket = app_settings.minio_bucket

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
