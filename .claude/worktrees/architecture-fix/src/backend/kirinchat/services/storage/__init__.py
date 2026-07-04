from kirinchat.services.storage.oss import OSSClient
from kirinchat.services.storage.minio import MinioClient
from kirinchat.settings import app_settings

# 延迟初始化存储客户端，避免在配置加载前访问
storage_client = None

def get_storage_client():
    """获取存储客户端（延迟初始化）"""
    global storage_client
    if storage_client is None:
        if app_settings.storage and app_settings.storage.mode == "minio":
            storage_client = MinioClient()
        else:
            storage_client = OSSClient()
    return storage_client

# 为了保持向后兼容，导出一个代理对象
class StorageClientProxy:
    def __getattr__(self, name):
        return getattr(get_storage_client(), name)

storage_client = StorageClientProxy()

if __name__ == "__main__":
    storage_client.list_files_in_folder("icons/user/")