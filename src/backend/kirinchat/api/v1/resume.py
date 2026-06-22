from loguru import logger
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import FileResponse
import tempfile

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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resume_to_info(r) -> ResumeInfoResp:
    """Convert a ResumeTable to a ResumeInfoResp."""
    return ResumeInfoResp(
        id=r.id,
        filename=r.filename,
        file_size=r.file_size,
        content_type=r.content_type,
        status=r.status,
        score=r.score,
        create_time=str(r.create_time) if r.create_time else None,
    )


def _resume_to_detail(r) -> ResumeDetailResp:
    """Convert a ResumeTable to a ResumeDetailResp."""
    return ResumeDetailResp(
        id=r.id,
        filename=r.filename,
        file_size=r.file_size,
        content_type=r.content_type,
        status=r.status,
        score=r.score,
        raw_text=r.raw_text or "",
        analysis_result=r.analysis_result,
        error_message=r.error_message or "",
        create_time=str(r.create_time) if r.create_time else None,
    )


# ---------------------------------------------------------------------------
# Resume endpoints
# ---------------------------------------------------------------------------


@router.post("/resume/upload", response_model=UnifiedResponseModel)
async def upload_resume(
    file: UploadFile = File(...),
    login_user: UserPayload = Depends(get_login_user),
):
    """Upload a resume file (PDF, DOCX, DOC, TXT)."""
    try:
        file_data = await file.read()
        resume = await ResumeService.upload_resume(
            user_id=login_user.user_id,
            filename=file.filename,
            file_data=file_data,
            content_type=file.content_type or "application/octet-stream",
        )
        return resp_200(data=_resume_to_info(resume).model_dump())
    except ValueError as err:
        logger.warning(f"Upload resume validation error: {err}")
        return resp_500(message=str(err))
    except Exception as err:
        logger.error(f"Upload resume error: {err}")
        return resp_500(message=str(err))


@router.get("/resume/list", response_model=UnifiedResponseModel)
async def list_resumes(
    login_user: UserPayload = Depends(get_login_user),
):
    """Get all resumes for the current user."""
    try:
        resumes = await ResumeService.get_user_resumes(login_user.user_id)
        data = ResumeListResp(
            resumes=[_resume_to_info(r) for r in resumes],
        )
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error(f"List resumes error: {err}")
        return resp_500(message=str(err))


@router.get("/resume/{resume_id}", response_model=UnifiedResponseModel)
async def get_resume_detail(
    resume_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """Get resume detail by ID."""
    try:
        resume = await ResumeService.get_resume(resume_id)
        if resume is None:
            return resp_500(message="Resume not found")

        data = _resume_to_detail(resume)
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error(f"Get resume detail error: {err}")
        return resp_500(message=str(err))


@router.delete("/resume/{resume_id}", response_model=UnifiedResponseModel)
async def delete_resume(
    resume_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """Delete a resume by ID."""
    try:
        success = await ResumeService.delete_resume(resume_id, login_user.user_id)
        if not success:
            return resp_500(message="Resume not found or unauthorized")
        return resp_200(data=None)
    except Exception as err:
        logger.error(f"Delete resume error: {err}")
        return resp_500(message=str(err))


@router.get("/resume/{resume_id}/status", response_model=UnifiedResponseModel)
async def get_resume_status(
    resume_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """Get resume analysis status."""
    try:
        resume = await ResumeService.get_resume(resume_id)
        if resume is None:
            return resp_500(message="Resume not found")

        data = ResumeStatusResp(
            id=resume.id,
            status=resume.status,
            score=resume.score,
        )
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error(f"Get resume status error: {err}")
        return resp_500(message=str(err))


@router.get("/resume/{resume_id}/pdf")
async def download_resume_pdf(resume_id: str, login_user: UserPayload = Depends(get_login_user)):
    """下载简历分析报告 PDF。"""
    try:
        resume = await ResumeService.get_resume(resume_id)
        if not resume or resume.user_id != login_user.user_id:
            return resp_500(message="简历不存在")
        if resume.status != "COMPLETED":
            return resp_500(message="简历分析尚未完成")

        from kirinchat.common.export.pdf_service import PdfService

        resume_data = {
            "filename": resume.filename,
            "score": resume.score,
            "analysis_result": resume.analysis_result,
        }

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = f.name

        PdfService.generate_resume_report(resume_data, output_path)
        return FileResponse(output_path, filename=f"resume_{resume_id}.pdf", media_type="application/pdf")
    except Exception as e:
        logger.exception("Download resume PDF failed")
        return resp_500(message=str(e))
