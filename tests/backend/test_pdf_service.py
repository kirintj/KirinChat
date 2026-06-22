import pytest
import os
import tempfile
from kirinchat.common.export.pdf_service import PdfService


class TestPdfService:
    def test_generate_evaluation_report(self):
        report_data = {
            "total_score": 8.5,
            "category_scores": {"java": 8.0, "mysql": 7.0, "redis": 6.5},
            "summary": "整体表现良好",
            "strengths": ["Java基础扎实", "项目经验丰富"],
            "improvements": ["Redis需要加强"],
        }
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = f.name

        try:
            result = PdfService.generate_evaluation_report(
                report_data, "Java 后端开发", output_path
            )
            assert os.path.exists(result)
            assert os.path.getsize(result) > 0
        finally:
            os.unlink(output_path)

    def test_generate_resume_report(self):
        resume_data = {
            "filename": "test_resume.pdf",
            "score": 78,
            "analysis_result": {
                "basic_info": {"name": "张三", "education": "本科", "experience_years": 3},
                "skills": ["Java", "Spring", "MySQL"],
                "experience_analysis": "具备扎实的Java后端开发经验",
                "suggestions": ["补充系统设计经验"],
            },
        }
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = f.name

        try:
            result = PdfService.generate_resume_report(resume_data, output_path)
            assert os.path.exists(result)
            assert os.path.getsize(result) > 0
        finally:
            os.unlink(output_path)
