import os
from urllib.parse import urlparse, unquote
from fastapi import APIRouter, Body, Depends, Query

from kirinchat.services.storage import storage_client
from kirinchat.api.services.knowledge_file import KnowledgeFileService
from kirinchat.api.services.knowledge import KnowledgeService
from kirinchat.api.services.user import get_login_user, UserPayload
from kirinchat.api.responses.builder import UnifiedResponseModel, resp_200, resp_500
from kirinchat.utils.file_utils import get_save_tempfile

router = APIRouter(tags=["Knowledge-File"])


@router.post('/knowledge_file/create', response_model=UnifiedResponseModel)
async def upload_file(
    knowledge_id: str = Body(..., description="知识库的ID"),
    file_url: str = Body(..., description="文件上传后返回的URL"),
    login_user: UserPayload = Depends(get_login_user)
):
    try:
        # URL 解码文件名（修复中文/特殊字符文件名问题）
        file_name = unquote(file_url.split("/")[-1])
        local_file_path = get_save_tempfile(file_name)

        # 根据URL解析出 object key
        parsed = urlparse(file_url)
        object_key = parsed.path.lstrip('/')

        # 去除 URL 路径中多余的 bucket 前缀
        # MinIO URL 格式: http://host:port/bucket_name/object_key
        # fget_object 内部会自动拼接 bucket_name，所以 object_key 不能包含它
        bucket_prefix = f"{storage_client.bucket_name}/"
        if object_key.startswith(bucket_prefix):
            object_key = object_key[len(bucket_prefix):]

        storage_client.download_file(object_key, local_file_path)

        # 防御性校验：确保文件确实下载成功
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"文件下载失败，请检查 MinIO 中对象是否存在: {object_key}")

        file_size_bytes = os.path.getsize(local_file_path)

        name_part, ext_part = file_name.rsplit('.', 1) if '.' in file_name else (file_name, '')
        parts = name_part.split("_")
        file_name = "_".join(parts[:-1]) + f".{ext_part}"

        await KnowledgeFileService.create_knowledge_file(
            file_name=file_name,
            file_path=local_file_path,
            knowledge_id=knowledge_id,
            user_id=login_user.user_id,
            oss_url=file_url,
            file_size_bytes=file_size_bytes
        )
        return resp_200()
    except Exception as err:
        return resp_500(message=str(err))


@router.get('/knowledge_file/select', response_model=UnifiedResponseModel)
async def select_knowledge_file(
    knowledge_id: str = Query(...),
    login_user: UserPayload = Depends(get_login_user)
):
    try:
        # 验证用户权限
        await KnowledgeService.verify_user_permission(knowledge_id, login_user.user_id)

        results = await KnowledgeFileService.get_knowledge_file(knowledge_id)
        return resp_200(data=results)
    except Exception as err:
        return resp_500(message=str(err))


@router.delete('/knowledge_file/delete', response_model=UnifiedResponseModel)
async def delete_knowledge_file(
    knowledge_file_id: str = Body(..., embed=True),
    login_user: UserPayload = Depends(get_login_user)
):
    try:
        # 验证用户权限
        await KnowledgeFileService.verify_user_permission(knowledge_file_id, login_user.user_id)

        await KnowledgeFileService.delete_knowledge_file(knowledge_file_id)
        return resp_200()
    except Exception as err:
        return resp_500(message=str(err))

@router.get("/knowledge_file/status", response_model=UnifiedResponseModel)
async def get_knowledge_file_status(
    knowledge_file_id: str = Body(..., embed=True),
    login_user: UserPayload = Depends(get_login_user)
):
    try:
        # 验证用户权限
        await KnowledgeFileService.verify_user_permission(knowledge_file_id, login_user.user_id)
        knowledge_file = await KnowledgeFileService.select_knowledge_file_by_id(knowledge_file_id)
        return resp_200(data=knowledge_file.to_dict())
    except Exception as err:
        return resp_500(message=str(err))