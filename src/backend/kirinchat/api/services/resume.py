import asyncio
import hashlib
import os
from typing import Optional, List
from uuid import uuid4

from loguru import logger

from kirinchat.database.dao.resume import ResumeDao
from kirinchat.database.models.resume import ResumeTable
from kirinchat.common.file_storage.minio_service import minio_service


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class ResumeService:

    @classmethod
    async def upload_resume(cls, user_id: str, filename: str, file_data: bytes, content_type: str) -> ResumeTable:
        """上传简历：校验 → 存储 → 创建记录 → 触发异步分析。"""
        if not cls._validate_file_type(filename):
            raise ValueError(f"不支持的文件类型，仅支持: {', '.join(ALLOWED_EXTENSIONS)}")
        if not cls._validate_file_size(len(file_data)):
            raise ValueError(f"文件大小超过限制（最大 {MAX_FILE_SIZE // 1024 // 1024}MB）")

        file_hash = cls._compute_hash(file_data)
        existing = await ResumeDao.select_by_hash(file_hash)
        if existing:
            # 已有记录：已完成或处理中则直接返回，失败则重新分析
            if existing.status in ("COMPLETED", "PENDING", "PROCESSING"):
                return existing
            # status == "FAILED" → 重置状态并重新触发分析
            await ResumeDao.update_status(existing.id, "PENDING")
            try:
                from kirinchat.common.async_task.resume_tasks import analyze_resume_task
                analyze_resume_task.delay(existing.id)
            except Exception:
                logger.warning("Celery 未启动，跳过异步分析任务")
            return existing

        ext = os.path.splitext(filename)[1].lower()
        object_name = f"resumes/{user_id}/{file_hash[:16]}_{uuid4().hex[:8]}{ext}"

        # [L2] 使用 asyncio.to_thread 避免阻塞事件循环
        await asyncio.to_thread(minio_service.upload_file, file_data, object_name)

        resume = ResumeTable(
            user_id=user_id,
            filename=filename,
            file_path=object_name,
            file_size=len(file_data),
            content_type=content_type,
            file_hash=file_hash,
        )
        resume = await ResumeDao.create_resume(resume)

        # 触发异步分析任务
        try:
            from kirinchat.common.async_task.resume_tasks import analyze_resume_task
            analyze_resume_task.delay(resume.id)
        except Exception:
            logger.warning("Celery 未启动，跳过异步分析任务")

        return resume

    @classmethod
    async def get_resume(cls, resume_id: str) -> Optional[ResumeTable]:
        return await ResumeDao.select_by_id(resume_id)

    @classmethod
    async def get_user_resumes(cls, user_id: str) -> List[ResumeTable]:
        return await ResumeDao.select_by_user(user_id)

    @classmethod
    async def delete_resume(cls, resume_id: str, user_id: str) -> bool:
        resume = await ResumeDao.select_by_id(resume_id)
        if not resume or resume.user_id != user_id:
            return False
        try:
            await asyncio.to_thread(minio_service.delete_file, resume.file_path)
        except Exception as e:
            # [L3] MinIO 删除失败时记录日志，不静默跳过
            logger.warning("MinIO 文件删除失败 (path=%s): %s", resume.file_path, e)
        await ResumeDao.delete_resume(resume_id)
        return True

    @classmethod
    def _validate_file_type(cls, filename: str) -> bool:
        ext = os.path.splitext(filename)[1].lower()
        return ext in ALLOWED_EXTENSIONS

    @classmethod
    def _validate_file_size(cls, size: int) -> bool:
        return 0 < size <= MAX_FILE_SIZE

    @classmethod
    def _compute_hash(cls, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()
