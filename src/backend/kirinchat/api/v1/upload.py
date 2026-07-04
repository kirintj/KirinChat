"""
文件上传服务API路由模块
提供通用文件上传功能
"""
from loguru import logger
from fastapi import APIRouter, UploadFile, File, Depends

from kirinchat.api.services.user import UserPayload, get_login_user
from kirinchat.api.responses.builder import UnifiedResponseModel, resp_200, resp_500
from kirinchat.services.storage import storage_client
from kirinchat.settings import app_settings
from kirinchat.utils.file_utils import get_object_storage_base_path

router = APIRouter(tags=["Upload"])


@router.post("/upload", description="上传文件的接口", response_model=UnifiedResponseModel)
async def upload_file(
    *,
    file: UploadFile = File(description="支持常见的Pdf、Docx、Txt、Jpg等文件"),
    login_user: UserPayload = Depends(get_login_user)
):
    """
    上传文件接口

    Args:
        file: 上传的文件对象
        login_user: 当前登录用户

    Returns:
        上传成功后的文件访问URL

    Raises:
        Exception: 上传过程中的各种错误
    """
    try:
        file_content = await file.read()

        # 生成存储路径并上传
        oss_object_name = get_object_storage_base_path(file.filename)
        base_url = app_settings.storage.active.base_url.rstrip('/')
        sign_url = f"{base_url}/{oss_object_name.lstrip('/')}"

        # 上传文件到对象存储
        storage_client.sign_url_for_get(sign_url)
        storage_client.upload_file(oss_object_name, file_content)

        logger.info(f"文件 {file.filename} 上传成功，用户: {login_user.user_id}")
        return resp_200(sign_url)
    except Exception as err:
        logger.error(f"上传文件 {file.filename} 出错：{err}")
        return resp_500(message=str(err))
