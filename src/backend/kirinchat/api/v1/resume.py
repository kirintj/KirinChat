"""
简历服务API路由模块
提供简历上传、查询、下载等REST接口
"""
import os
import tempfile

from loguru import logger
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from kirinchat.api.services.resume import ResumeService
from kirinchat.schemas.resume import (
    ResumeInfoResp,
    ResumeDetailResp,
    ResumeStatusResp,
    ResumeListResp,
)
from kirinchat.api.responses.builder import resp_200, resp_500, UnifiedResponseModel
from kirinchat.api.services.user import UserPayload, get_login_user

router = APIRouter(tags=["Resume"])

# 常量定义
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
MAX_UPLOAD_SIZE_MB = MAX_UPLOAD_SIZE // 1024 // 1024

# 错误消息常量
ERROR_RESUME_NOT_FOUND = "简历不存在"
ERROR_RESUME_NOT_COMPLETED = "简历分析尚未完成"
ERROR_RESUME_NO_PERMISSION = "简历不存在或无权删除"


# ---------------------------------------------------------------------------
# 数据转换辅助函数
# ---------------------------------------------------------------------------


def _resume_to_info(resume) -> ResumeInfoResp:
    """
    将ResumeTable转换为ResumeInfoResp（列表展示用）

    Args:
        resume: 数据库中的简历对象

    Returns:
        简历信息响应对象
    """
    return ResumeInfoResp(
        id=resume.id,
        filename=resume.filename,
        file_size=resume.file_size,
        content_type=resume.content_type,
        status=resume.status,
        score=resume.score,
        create_time=str(resume.create_time) if resume.create_time else None,
    )


def _resume_to_detail(resume) -> ResumeDetailResp:
    """
    将ResumeTable转换为ResumeDetailResp（详情展示用）

    Args:
        resume: 数据库中的简历对象

    Returns:
        简历详情响应对象
    """
    return ResumeDetailResp(
        id=resume.id,
        filename=resume.filename,
        file_size=resume.file_size,
        content_type=resume.content_type,
        status=resume.status,
        score=resume.score,
        raw_text=resume.raw_text or "",
        analysis_result=resume.analysis_result,
        error_message=resume.error_message or "",
        create_time=str(resume.create_time) if resume.create_time else None,
    )


def _validate_file_size(file_data: bytes) -> None:
    """
    验证文件大小是否在限制范围内

    Args:
        file_data: 文件内容字节数据

    Raises:
        ValueError: 文件大小超过限制
    """
    if len(file_data) > MAX_UPLOAD_SIZE:
        raise ValueError(f"文件大小超过限制（最大 {MAX_UPLOAD_SIZE_MB}MB）")


def _check_resume_permission(resume, user_id: str) -> bool:
    """
    检查用户是否有权限访问该简历

    Args:
        resume: 简历对象
        user_id: 用户ID

    Returns:
        是否有权限
    """
    return resume is not None and resume.user_id == user_id


# ---------------------------------------------------------------------------
# 简历API端点（注意: 带后缀的路由必须在 {resume_id} 参数路由之前）
# ---------------------------------------------------------------------------


@router.get("/resume/list", response_model=UnifiedResponseModel)
async def list_resumes(
    login_user: UserPayload = Depends(get_login_user),
):
    """获取当前用户的所有简历列表"""
    try:
        resumes = await ResumeService.get_user_resumes(login_user.user_id)
        data = ResumeListResp(
            resumes=[_resume_to_info(r) for r in resumes],
        )
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error("List resumes error: %s", err)
        return resp_500(message="获取简历列表失败")


@router.post("/resume/upload", response_model=UnifiedResponseModel)
async def upload_resume(
    file: UploadFile = File(...),
    login_user: UserPayload = Depends(get_login_user),
):
    """上传简历文件（支持PDF、DOCX、DOC、TXT格式）"""
    try:
        file_data = await file.read()
        _validate_file_size(file_data)

        resume = await ResumeService.upload_resume(
            user_id=login_user.user_id,
            filename=file.filename,
            file_data=file_data,
            content_type=file.content_type or "application/octet-stream",
        )
        return resp_200(data=_resume_to_info(resume).model_dump())
    except ValueError as err:
        logger.warning("Upload resume validation error: %s", err)
        return resp_500(message=str(err))
    except Exception as err:
        logger.error("Upload resume error: %s", err)
        return resp_500(message="上传简历失败，请稍后重试")


@router.get("/resume/{resume_id}/status", response_model=UnifiedResponseModel)
async def get_resume_status(
    resume_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """获取简历分析状态"""
    try:
        resume = await ResumeService.get_resume(resume_id)
        if resume is None:
            return resp_500(message=ERROR_RESUME_NOT_FOUND)

        data = ResumeStatusResp(
            id=resume.id,
            status=resume.status,
            score=resume.score,
        )
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error("Get resume status error: %s", err)
        return resp_500(message="获取简历状态失败")


@router.get("/resume/{resume_id}/pdf")
async def download_resume_pdf(
    resume_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """下载简历分析报告PDF"""
    try:
        resume = await ResumeService.get_resume(resume_id)

        if not _check_resume_permission(resume, login_user.user_id):
            return resp_500(message=ERROR_RESUME_NOT_FOUND)

        if resume.status != "COMPLETED":
            return resp_500(message=ERROR_RESUME_NOT_COMPLETED)

        return _generate_and_return_pdf(resume_id, resume)
    except Exception as e:
        logger.exception("Download resume PDF failed")
        return resp_500(message="下载简历报告失败")


def _generate_and_return_pdf(resume_id: str, resume) -> FileResponse:
    """
    生成并返回PDF文件响应

    Args:
        resume_id: 简历ID
        resume: 简历对象

    Returns:
        FileResponse对象
    """
    from kirinchat.common.export.pdf_service import PdfService

    resume_data = {
        "filename": resume.filename,
        "score": resume.score,
        "analysis_result": resume.analysis_result,
    }

    # 使用临时文件 + BackgroundTask清理
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    output_path = tmp.name
    tmp.close()

    PdfService.generate_resume_report(resume_data, output_path)
    return FileResponse(
        output_path,
        filename=f"resume_{resume_id}.pdf",
        media_type="application/pdf",
        background=BackgroundTask(os.unlink, output_path),
    )


@router.get("/resume/{resume_id}", response_model=UnifiedResponseModel)
async def get_resume_detail(
    resume_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """获取简历详情"""
    try:
        resume = await ResumeService.get_resume(resume_id)
        if resume is None:
            return resp_500(message=ERROR_RESUME_NOT_FOUND)

        data = _resume_to_detail(resume)
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error("Get resume detail error: %s", err)
        return resp_500(message="获取简历详情失败")


@router.delete("/resume/{resume_id}", response_model=UnifiedResponseModel)
async def delete_resume(
    resume_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """删除简历"""
    try:
        success = await ResumeService.delete_resume(resume_id, login_user.user_id)
        if not success:
            return resp_500(message=ERROR_RESUME_NO_PERMISSION)
        return resp_200(data=None)
    except Exception as err:
        logger.error("Delete resume error: %s", err)
        return resp_500(message="删除简历失败")
