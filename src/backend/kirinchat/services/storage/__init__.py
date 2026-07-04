import threading
from loguru import logger


def _get_storage_client():
    """惰性初始化存储客户端。
    在配置加载完成 / 首次真正使用时才实例化。
    MinIO / OSS 不可用时会记录警告，但不会让整个服务无法启动。
    """
    from kirinchat.services.storage.oss import OSSClient
    from kirinchat.services.storage.minio import MinioClient
    from kirinchat.settings import app_settings

    try:
        mode = getattr(getattr(app_settings, "storage", None), "mode", None) or "minio"
        if mode == "minio":
            return MinioClient()
        return OSSClient()
    except Exception as e:
        logger.warning(
            f"无法初始化存储客户端（当前配置 mode={getattr(getattr(app_settings, 'storage', None), 'mode', 'minio')}）：{e}。"
            f"存储相关功能会返回空结果，如需使用请启动对应服务（MinIO / OSS）并正确配置后重启。"
        )
        from kirinchat.services.storage.minio import MinioClient
        # 返回一个仅会在调用时打印警告的实例，避免调用方处理 None
        return MinioClient()


class _LazyStorageClient:
    """对 storage_client 的线程安全懒代理。"""

    def __init__(self):
        self._instance = None
        self._lock = threading.Lock()

    def _get(self):
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = _get_storage_client()
        return self._instance

    def __getattr__(self, item):
        return getattr(self._get(), item)


storage_client = _LazyStorageClient()

if __name__ == "__main__":
    storage_client.list_files_in_folder("icons/user/")