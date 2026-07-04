import json
import asyncio
from loguru import logger

from langchain_core.messages import HumanMessage

from kirinchat.common.async_task.celery_app import celery_app
from kirinchat.common.file_storage.minio_service import minio_service
from kirinchat.common.security.prompt_sanitizer import PromptSanitizer
from kirinchat.common.security.prompt_constants import DATA_BOUNDARY_TEMPLATE, ANTI_INJECTION_INSTRUCTION
from kirinchat.database.dao.resume import ResumeDao
from kirinchat.prompts.resume_analysis import RESUME_ANALYSIS_PROMPT
from kirinchat.utils.llm_parser import parse_llm_json


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def analyze_resume_task(self, resume_id: str):
    """异步分析简历：解析文档 → LLM 分析 → 保存结果。"""
    try:
        asyncio.run(_analyze_resume(self, resume_id))
    except Exception as exc:
        logger.exception("Resume analysis failed for %s", resume_id)
        try:
            asyncio.run(ResumeDao.update_status(resume_id, "FAILED", str(exc)))
        except Exception:
            pass
        raise self.retry(exc=exc)


async def _analyze_resume(task, resume_id: str):
    from kirinchat.core.models.manager import ModelManager

    await ResumeDao.update_status(resume_id, "PROCESSING")

    resume = await ResumeDao.select_by_id(resume_id)
    if not resume:
        return

    # [L2] 使用 asyncio.to_thread 包装同步 MinIO 调用
    file_data = await asyncio.to_thread(minio_service.download_file, resume.file_path)
    raw_text = _parse_document(file_data, resume.filename, resume.content_type)
    cleaned_text = PromptSanitizer.sanitize(raw_text)

    if not cleaned_text:
        await ResumeDao.update_status(resume_id, "FAILED", "文档解析结果为空")
        return

    data_boundary = DATA_BOUNDARY_TEMPLATE.format(content=cleaned_text[:8000])
    prompt = RESUME_ANALYSIS_PROMPT.format(
        anti_injection=ANTI_INJECTION_INSTRUCTION,
        data_boundary=data_boundary,
    )

    llm = ModelManager.get_conversation_model()
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    content = response.content if hasattr(response, "content") else str(response)

    result = parse_llm_json(content)
    score = result.get("score", 0)

    await ResumeDao.update_analysis(resume_id, cleaned_text[:5000], result, float(score))


def _parse_document(file_data: bytes, filename: str, content_type: str) -> str:
    import tempfile
    import os

    ext = os.path.splitext(filename)[1].lower()

    if ext == ".txt":
        return file_data.decode("utf-8", errors="ignore")

    try:
        from unstructured.partition.auto import partition

        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
            f.write(file_data)
            tmp_path = f.name

        try:
            elements = partition(filename=tmp_path)
            return "\n".join(str(el) for el in elements)
        finally:
            os.unlink(tmp_path)
    except Exception as e:
        logger.warning("Unstructured parsing failed: %s, falling back", e)
        if ext == ".pdf":
            return _parse_pdf_fallback(file_data)
        return file_data.decode("utf-8", errors="ignore")


def _parse_pdf_fallback(file_data: bytes) -> str:
    try:
        from io import BytesIO
        import pdfplumber

        with pdfplumber.open(BytesIO(file_data)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception:
        return ""
