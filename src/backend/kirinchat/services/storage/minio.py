import io
import os
import threading
from minio import Minio
from minio.error import S3Error
from loguru import logger
from kirinchat.settings import app_settings


class MinioClient:
    def __init__(self):
        storage_cfg = getattr(app_settings, "storage", None)
        minio_cfg = getattr(storage_cfg, "minio", None) if storage_cfg else None

        if minio_cfg:
            self.endpoint = getattr(minio_cfg, "endpoint", "127.0.0.1:9000")
            self.access_key_id = getattr(minio_cfg, "access_key_id", "minioadmin")
            self.secret_access_key = getattr(minio_cfg, "access_key_secret", "minioadmin")
            self.bucket_name = getattr(minio_cfg, "bucket_name", "agentchat")
        else:
            self.endpoint = app_settings.minio_endpoint
            self.access_key_id = app_settings.minio_access_key
            self.secret_access_key = app_settings.minio_secret_key
            self.bucket_name = app_settings.minio_bucket

        self.client = Minio(
            secure=False,
            endpoint=self.endpoint,
            access_key=self.access_key_id,
            secret_key=self.secret_access_key,
        )

        self._bucket_ensured = False
        self._bucket_ensured_lock = threading.Lock()

    def _ensure_bucket(self):
        """首次真正需要访问存储时，惰性地检查 / 创建 bucket。
        失败时只记录警告，不中断服务启动。
        """
        if self._bucket_ensured:
            return
        with self._bucket_ensured_lock:
            if self._bucket_ensured:
                return
            try:
                if not self.client.bucket_exists(self.bucket_name):
                    self.client.make_bucket(self.bucket_name)
                    logger.info(f"MinIO bucket '{self.bucket_name}' created")
                self._bucket_ensured = True
            except Exception as e:
                # bucket_exists 在 bucket 不存在时可能抛出 S3Error(AccessDenied)，
                # 因此只要不是「已存在」，就再试一次 make_bucket，失败就降级。
                try:
                    self.client.make_bucket(self.bucket_name)
                    logger.info(f"MinIO bucket '{self.bucket_name}' created (fallback)")
                    self._bucket_ensured = True
                except Exception as e2:
                    logger.warning(
                        f"MinIO bucket check/create failed (endpoint={self.endpoint}, bucket={self.bucket_name}): {e2}. "
                        f"后续存储相关操作会继续尝试连接，但请确认 MinIO 服务已启动并可访问。"
                    )

    def upload_file(self, object_name, data):
        self._ensure_bucket()
        try:
            if isinstance(data, (bytes, bytearray)):
                data_stream = io.BytesIO(data)
                length = len(data)
            else:
                data = data.encode("utf-8") if isinstance(data, str) else data
                data_stream = io.BytesIO(data)
                length = len(data)
            self.client.put_object(self.bucket_name, object_name, data_stream, length)
            logger.info(f"File uploaded successfully: {object_name}")
        except S3Error as e:
            logger.error(f"Failed to upload file: {e}")

    def upload_local_file(self, object_name, local_file):
        self._ensure_bucket()
        try:
            self.client.fput_object(self.bucket_name, object_name, local_file)
            logger.info(f"Local file uploaded successfully: {object_name}")
        except S3Error as e:
            logger.error(f"Failed to upload file : {e}")

    def delete_bucket(self):
        self._ensure_bucket()
        try:
            self.client.remove_bucket(self.bucket_name)
            logger.info("Bucket deleted successfully")
        except S3Error as e:
            logger.error(f"Failed to delete bucket: {e}")

    def sign_url_for_get(self, object_name, expiration=3600):
        self._ensure_bucket()
        try:
            from datetime import timedelta
            url = self.client.presigned_get_object(
                self.bucket_name, object_name, expires=timedelta(seconds=expiration)
            )
            return url
        except S3Error as e:
            logger.error(f"Failed to generate GET URL for {object_name}: {e}")

    def download_file(self, object_name, local_file):
        self._ensure_bucket()

        # 自动修复 object_name 中多余的 bucket 前缀
        # MinIO URL: http://host:port/bucket_name/object_key
        # urlparse 提取出的 path 为 /bucket_name/object_key
        # 而 fget_object 内部会自动拼接 bucket，导致双前缀
        bucket_prefix = f"{self.bucket_name}/"
        if object_name.startswith(bucket_prefix):
            object_name = object_name[len(bucket_prefix):]

        try:
            # 确保本地目标目录存在（临时目录可能尚未创建文件）
            local_dir = os.path.dirname(local_file)
            if local_dir and not os.path.exists(local_dir):
                os.makedirs(local_dir, exist_ok=True)

            self.client.fget_object(self.bucket_name, object_name, local_file)

            # 校验文件确实写入成功
            if not os.path.exists(local_file):
                raise FileNotFoundError(f"下载完成但目标文件不存在: {local_file}")

            logger.info(f"File {object_name} downloaded successfully to {local_file}")
        except S3Error as e:
            logger.error(f"Failed to download {object_name} to {local_file}: {e}")
            raise  # 重新抛出，让上层感知下载失败
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error downloading {object_name}: {e}")
            raise

    def list_files_in_folder(self, folder_path):
        """列出指定文件夹下的所有文件（不递归）。
        MinIO 不可用时返回空列表并打印警告，而不是让服务启动失败。
        """
        self._ensure_bucket()
        try:
            if folder_path and not folder_path.endswith('/'):
                folder_path += '/'

            objects = self.client.list_objects(
                self.bucket_name, prefix=folder_path, recursive=False
            )
            files_url = [
                obj.object_name for obj in objects
                if not obj.is_dir and not obj.object_name.endswith('/')
            ]
            return files_url
        except S3Error as e:
            logger.error(f"Failed to list files in folder {folder_path}: {e}")
            return []
        except Exception as e:
            logger.warning(f"MinIO 不可用，跳过列出文件 ({folder_path}): {e}")
            return []


