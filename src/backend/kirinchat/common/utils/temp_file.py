import tempfile
import os
import uuid
import logging
from contextlib import contextmanager
from typing import Generator

logger = logging.getLogger(__name__)


def make_temp_path(suffix: str = ".pdf") -> str:
    """
    生成唯一的临时文件路径（不创建文件）。

    使用 UUID 确保文件名唯一，避免并发冲突。
    调用方负责在使用完毕后清理文件。

    Args:
        suffix: 文件后缀，默认为 .pdf

    Returns:
        str: 临时文件的完整路径
    """
    unique_id = uuid.uuid4().hex[:8]
    tmp_dir = tempfile.gettempdir()
    return os.path.join(tmp_dir, f"temp_{unique_id}{suffix}")


def cleanup_temp_file(path: str) -> None:
    """
    安全地清理临时文件。

    如果文件存在则删除，删除失败时记录警告（不抛异常）。

    Args:
        path: 要清理的临时文件路径
    """
    if os.path.exists(path):
        try:
            os.unlink(path)
            logger.debug(f"临时文件已清理: {path}")
        except OSError as e:
            logger.warning(
                f"清理临时文件失败: {path}, 错误: {e}. "
                "可能需要手动清理。"
            )


@contextmanager
def temporary_pdf(suffix: str = ".pdf") -> Generator[str, None, None]:
    """
    安全的临时文件上下文管理器

    特点：
    1. 使用 UUID 确保文件名唯一，避免并发冲突
    2. 自动清理临时文件，即使发生异常
    3. 记录清理失败的情况（不吞掉异常）

    注意：此管理器在退出 with 块时立即删除文件。
    如果需要将文件路径传递给异步消费者（如 FileResponse），
    请改用 make_temp_path() + cleanup_temp_file()。

    Args:
        suffix: 文件后缀，默认为 .pdf

    Yields:
        str: 临时文件的完整路径

    Example:
        with temporary_pdf() as pdf_path:
            generate_pdf_content(pdf_path)
            await upload_to_minio(pdf_path)
            # 离开 with 块时自动清理
    """
    tmp_path = make_temp_path(suffix)
    try:
        yield tmp_path
    finally:
        cleanup_temp_file(tmp_path)
