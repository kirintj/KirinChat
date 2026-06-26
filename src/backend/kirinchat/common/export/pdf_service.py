import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import ParagraphStyle


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
        # 逐题详情（在总结之前）
        question_details = report_data.get("question_details", [])
        if question_details:
            cls._draw_question_details(c, width, height, question_details)
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
    def _draw_question_details(cls, c, width, height, question_details):
        """绘制逐题评估详情页，每题显示得分、反馈和参考答案。"""
        cls._register_font()
        y = height - 80

        style = ParagraphStyle(
            "question_body",
            fontName=cls.FONT_NAME,
            fontSize=11,
            leading=16,
        )

        for i, q in enumerate(question_details):
            # 每题最少需要 150pt 空间，不够则换页
            if y < 150:
                c.showPage()
                y = height - 80

            # 题目标题
            c.setFont(cls.FONT_NAME, 14)
            c.setFillColor(HexColor("#333333"))
            content = q.get("content", "")
            score = q.get("score", 0)
            display_text = content[:60] + ('...' if len(content) > 60 else '')
            c.drawString(2 * cm, y, f"Q{i + 1}: {display_text}")
            c.setFont(cls.FONT_NAME, 12)
            score_color = "#4CAF50" if score >= 8 else "#FF9800" if score >= 6 else "#F44336"
            c.setFillColor(HexColor(score_color))
            c.drawRightString(width - 2 * cm, y, f"{score}/10")
            y -= 25

            # 反馈
            feedback = q.get("feedback", "")
            if feedback:
                c.setFillColor(HexColor("#333333"))
                c.setFont(cls.FONT_NAME, 11)
                c.drawString(2 * cm, y, "反馈:")
                y -= 18
                para = Paragraph(feedback, style)
                pw, ph = para.wrap(width - 4 * cm, 200)
                para.drawOn(c, 2 * cm, y - ph)
                y -= ph + 10

            # 参考答案
            ref = q.get("reference_answer", "")
            if ref:
                if y < 80:
                    c.showPage()
                    y = height - 80
                c.setFillColor(HexColor("#1976D2"))
                c.setFont(cls.FONT_NAME, 11)
                c.drawString(2 * cm, y, "参考答案:")
                y -= 18
                c.setFillColor(HexColor("#333333"))
                para = Paragraph(ref, style)
                pw, ph = para.wrap(width - 4 * cm, 200)
                para.drawOn(c, 2 * cm, y - ph)
                y -= ph + 20

            # 分隔线
            if i < len(question_details) - 1:
                c.setStrokeColor(HexColor("#E0E0E0"))
                c.line(2 * cm, y, width - 2 * cm, y)
                y -= 15

    @classmethod
    def _draw_summary_page(cls, c, width, height, report_data):
        y = height - 80
        c.setFont(cls.FONT_NAME, 24)
        c.drawString(2 * cm, y, "综合评价")
        y -= 50

        # [P3] 使用 Paragraph 自动换行代替手动截断
        style = ParagraphStyle(
            "body",
            fontName=cls.FONT_NAME,
            fontSize=12,
            leading=18,
        )
        summary_text = report_data.get("summary", "")
        if summary_text:
            para = Paragraph(summary_text, style)
            pw, ph = para.wrap(width - 4 * cm, 200)
            para.drawOn(c, 2 * cm, y - ph)
            y -= ph + 20

        c.setFont(cls.FONT_NAME, 16)
        c.drawString(2 * cm, y, "优势")
        y -= 25
        c.setFont(cls.FONT_NAME, 12)
        for s in report_data.get("strengths", []):
            if y < 60:
                c.showPage()
                y = height - 80
            c.drawString(2 * cm + 10, y, f"- {s}")
            y -= 20
        y -= 20

        if y < 100:
            c.showPage()
            y = height - 80

        c.setFont(cls.FONT_NAME, 16)
        c.drawString(2 * cm, y, "改进建议")
        y -= 25
        c.setFont(cls.FONT_NAME, 12)
        for s in report_data.get("improvements", []):
            if y < 60:
                c.showPage()
                y = height - 80
            c.drawString(2 * cm + 10, y, f"- {s}")
            y -= 20

    @classmethod
    def _draw_resume_analysis(cls, c, width, height, resume_data):
        y = height - 80
        c.setFont(cls.FONT_NAME, 24)
        c.drawString(2 * cm, y, "简历分析报告")
        y -= 50

        analysis = resume_data.get("analysis_result") or {}
        basic = analysis.get("basic_info") or {}

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
        skills = analysis.get("skills") or []
        c.drawString(2 * cm, y, "  |  ".join(skills))
        y -= 40

        score = resume_data.get("score", 0)
        c.setFont(cls.FONT_NAME, 14)
        c.drawString(2 * cm, y, f"评分: {score}/100")
        y -= 40

        # [P3] 使用 Paragraph 自动换行
        style = ParagraphStyle(
            "body",
            fontName=cls.FONT_NAME,
            fontSize=12,
            leading=18,
        )

        experience_text = analysis.get("experience_analysis", "")
        if experience_text:
            c.setFont(cls.FONT_NAME, 14)
            c.drawString(2 * cm, y, "经历分析")
            y -= 25
            para = Paragraph(experience_text, style)
            pw, ph = para.wrap(width - 4 * cm, 300)
            para.drawOn(c, 2 * cm, y - ph)
            y -= ph + 20

        if y < 150:
            c.showPage()
            y = height - 80

        c.setFont(cls.FONT_NAME, 14)
        c.drawString(2 * cm, y, "改进建议")
        y -= 25
        c.setFont(cls.FONT_NAME, 12)
        for s in analysis.get("suggestions") or []:
            if y < 60:
                c.showPage()
                y = height - 80
            c.drawString(2 * cm + 10, y, f"- {s}")
            y -= 20
