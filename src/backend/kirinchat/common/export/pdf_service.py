import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class PdfService:
    """PDF 报告生成服务。"""

    _font_registered = False
    FONT_NAME = "NotoSansSC"

    @classmethod
    def _register_font(cls):
        if cls._font_registered:
            return
        font_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "assets", "fonts", "NotoSansSC-Regular.ttf"
        )
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont(cls.FONT_NAME, font_path))
        else:
            cls.FONT_NAME = "Helvetica"
        cls._font_registered = True

    @classmethod
    def generate_evaluation_report(cls, report_data: dict, skill_name: str, output_path: str) -> str:
        cls._register_font()
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        cls._draw_cover(c, width, height, "面试评估报告", "Interview Report")
        c.showPage()
        cls._draw_score_overview(c, width, height, report_data, skill_name)
        c.showPage()
        cls._draw_summary_page(c, width, height, report_data)
        c.showPage()
        c.save()
        return output_path

    @classmethod
    def generate_resume_report(cls, resume_data: dict, output_path: str) -> str:
        cls._register_font()
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        cls._draw_cover(c, width, height, "简历分析报告", "Resume Analysis")
        c.showPage()
        cls._draw_resume_analysis(c, width, height, resume_data)
        c.showPage()
        c.save()
        return output_path

    @classmethod
    def _draw_cover(cls, c, width, height, title_cn, title_en):
        c.setFont(cls.FONT_NAME, 36)
        c.drawCentredString(width / 2, height - 200, title_cn)
        c.setFont(cls.FONT_NAME, 18)
        c.setFillColor(HexColor("#666666"))
        c.drawCentredString(width / 2, height - 240, title_en)
        c.setFont(cls.FONT_NAME, 14)
        c.setFillColor(HexColor("#333333"))
        c.drawCentredString(width / 2, height - 300, "麒麟智聊 KirinChat")
        c.drawCentredString(width / 2, height - 330, datetime.now().strftime("%Y-%m-%d"))

    @classmethod
    def _draw_score_overview(cls, c, width, height, report_data, skill_name):
        y = height - 80
        c.setFont(cls.FONT_NAME, 24)
        c.drawString(2 * cm, y, "评估概览")
        y -= 50

        total = report_data.get("total_score", 0)
        c.setFont(cls.FONT_NAME, 18)
        c.drawString(2 * cm, y, f"总分: {total}/10")
        y -= 30

        rating = "优秀" if total >= 8 else "良好" if total >= 6 else "及格" if total >= 4 else "需努力"
        c.setFont(cls.FONT_NAME, 14)
        c.drawString(2 * cm, y, f"评级: {rating}    面试方向: {skill_name}")
        y -= 50

        c.setFont(cls.FONT_NAME, 16)
        c.drawString(2 * cm, y, "分类得分:")
        y -= 30

        for cat, score in report_data.get("category_scores", {}).items():
            bar_width = score * 20
            c.setFillColor(HexColor("#4CAF50"))
            c.rect(2 * cm + 100, y - 3, bar_width, 14, fill=1)
            c.setFillColor(HexColor("#333333"))
            c.setFont(cls.FONT_NAME, 12)
            c.drawString(2 * cm, y, f"{cat}")
            c.drawString(2 * cm + 110 + bar_width, y, f"{score}")
            y -= 25

    @classmethod
    def _draw_summary_page(cls, c, width, height, report_data):
        y = height - 80
        c.setFont(cls.FONT_NAME, 24)
        c.drawString(2 * cm, y, "综合评价")
        y -= 50

        c.setFont(cls.FONT_NAME, 12)
        for line in cls._wrap_text(report_data.get("summary", ""), 30):
            c.drawString(2 * cm, y, line)
            y -= 20
        y -= 20

        c.setFont(cls.FONT_NAME, 16)
        c.drawString(2 * cm, y, "优势")
        y -= 25
        c.setFont(cls.FONT_NAME, 12)
        for s in report_data.get("strengths", []):
            c.drawString(2 * cm + 10, y, f"- {s}")
            y -= 20
        y -= 20

        c.setFont(cls.FONT_NAME, 16)
        c.drawString(2 * cm, y, "改进建议")
        y -= 25
        c.setFont(cls.FONT_NAME, 12)
        for s in report_data.get("improvements", []):
            c.drawString(2 * cm + 10, y, f"- {s}")
            y -= 20

    @classmethod
    def _draw_resume_analysis(cls, c, width, height, resume_data):
        y = height - 80
        c.setFont(cls.FONT_NAME, 24)
        c.drawString(2 * cm, y, "简历分析报告")
        y -= 50

        analysis = resume_data.get("analysis_result", {})
        basic = analysis.get("basic_info", {})

        c.setFont(cls.FONT_NAME, 14)
        c.drawString(2 * cm, y, "基本信息")
        y -= 25
        c.setFont(cls.FONT_NAME, 12)
        c.drawString(2 * cm, y, f"姓名: {basic.get('name', '未知')}    学历: {basic.get('education', '未知')}")
        y -= 20
        c.drawString(2 * cm, y, f"工作年限: {basic.get('experience_years', 0)}年")
        y -= 40

        c.setFont(cls.FONT_NAME, 14)
        c.drawString(2 * cm, y, "技能标签")
        y -= 25
        c.setFont(cls.FONT_NAME, 12)
        skills = analysis.get("skills", [])
        c.drawString(2 * cm, y, "  |  ".join(skills))
        y -= 40

        score = resume_data.get("score", 0)
        c.setFont(cls.FONT_NAME, 14)
        c.drawString(2 * cm, y, f"评分: {score}/100")
        y -= 40

        c.setFont(cls.FONT_NAME, 14)
        c.drawString(2 * cm, y, "改进建议")
        y -= 25
        c.setFont(cls.FONT_NAME, 12)
        for s in analysis.get("suggestions", []):
            c.drawString(2 * cm + 10, y, f"- {s}")
            y -= 20

    @staticmethod
    def _wrap_text(text: str, max_chars: int = 30) -> list:
        lines = []
        while text:
            if len(text) <= max_chars:
                lines.append(text)
                break
            lines.append(text[:max_chars])
            text = text[max_chars:]
        return lines or [""]
