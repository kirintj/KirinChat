"""
JD（职位描述）服务模块
提供JD解析、分类和技能创建功能
"""
import os
from typing import Optional
from uuid import uuid4

from loguru import logger
from langchain_core.messages import HumanMessage

from kirinchat.core.models.manager import ModelManager
from kirinchat.common.security.prompt_sanitizer import PromptSanitizer
from kirinchat.common.security.prompt_constants import DATA_BOUNDARY_TEMPLATE, ANTI_INJECTION_INSTRUCTION
from kirinchat.prompts.jd_parse import JD_PARSE_PROMPT
from kirinchat.schemas.jd import JdParseResp, JdCategoryResp, JdCreateSkillReq, JdSkillResp
from kirinchat.utils.llm_parser import parse_llm_json

# 目录常量
SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "skills")
REFERENCES_DIR = os.path.join(SKILLS_DIR, "_shared", "references")

# ID前缀常量
SKILL_ID_PREFIX = "jd"
SKILL_ID_LENGTH = 8


class JdService:
    """JD服务类，提供职位描述相关的业务逻辑"""

    @classmethod
    async def parse_jd(cls, jd_text: str) -> JdParseResp:
        """
        解析JD文本并提取结构化信息

        Args:
            jd_text: 职位描述文本

        Returns:
            解析后的结构化JD数据

        Raises:
            ValueError: 解析失败或数据格式错误
        """
        cleaned = PromptSanitizer.sanitize(jd_text)
        data_boundary = DATA_BOUNDARY_TEMPLATE.format(content=cleaned)

        prompt = JD_PARSE_PROMPT.format(
            anti_injection=ANTI_INJECTION_INSTRUCTION,
            data_boundary=data_boundary,
        )

        llm = ModelManager.get_conversation_model()
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        content = response.content if hasattr(response, "content") else str(response)

        result = parse_llm_json(content)
        categories = cls._parse_categories(result.get("categories", []))

        return JdParseResp(
            company=result.get("company", "未知公司"),
            position=result.get("position", "未知职位"),
            experience_required=result.get("experience_required", ""),
            categories=categories,
            summary=result.get("summary", ""),
        )

    @classmethod
    def _parse_categories(cls, categories_data: list) -> list[JdCategoryResp]:
        """
        解析分类数据列表

        Args:
            categories_data: 原始分类数据列表

        Returns:
            解析后的JdCategoryResp列表
        """
        return [
            JdCategoryResp(
                key=c.get("key", ""),
                label=c.get("label", ""),
                priority=c.get("priority", "CORE"),
                keywords=c.get("keywords", []),
            )
            for c in categories_data
        ]

    @classmethod
    async def create_skill_from_jd(cls, req: JdCreateSkillReq) -> JdSkillResp:
        """
        从JD创建临时面试技能

        Args:
            req: 创建技能请求数据

        Returns:
            创建的技能信息
        """
        from kirinchat.api.services.skill import SkillService

        persona = cls._build_persona(req)
        refs = cls._load_references(req.categories)

        skill_id = f"{SKILL_ID_PREFIX}-{uuid4().hex[:SKILL_ID_LENGTH]}"
        skill_data = cls._build_skill_data(skill_id, req, persona, refs)
        SkillService.register_temp_skill(skill_data)

        return JdSkillResp(
            skill_id=skill_id,
            name=skill_data["name"],
            description=skill_data["description"],
            categories=[c.key for c in req.categories],
        )

    @classmethod
    def _build_persona(cls, req: JdCreateSkillReq) -> str:
        """
        构建面试官角色描述

        Args:
            req: 创建技能请求数据

        Returns:
            格式化的角色描述文本
        """
        categories_text = "\n".join(f"- {c.label}" for c in req.categories)
        return (
            f"你是一位{req.company}的技术面试官。\n"
            f"你要面试的职位是：{req.position}。\n"
            f"经验要求：{req.experience_required}。\n\n"
            f"面试重点：\n{categories_text}\n\n"
            f"请严格按照以上技术方向出题，贴近真实面试场景。"
        )

    @classmethod
    def _load_references(cls, categories: list) -> dict:
        """
        加载分类对应的参考文件内容

        Args:
            categories: 分类列表

        Returns:
            分类key到参考文件内容的映射字典
        """
        refs = {}
        for cat in categories:
            ref_content = cls._find_reference_file(cat.key)
            if ref_content:
                refs[cat.key] = ref_content
        return refs

    @classmethod
    def _build_skill_data(
        cls,
        skill_id: str,
        req: JdCreateSkillReq,
        persona: str,
        refs: dict
    ) -> dict:
        """
        构建技能数据字典

        Args:
            skill_id: 技能ID
            req: 创建技能请求数据
            persona: 角色描述
            refs: 参考文件映射

        Returns:
            技能数据字典
        """
        return {
            "id": skill_id,
            "name": f"{req.company} - {req.position}",
            "description": req.summary or f"{req.company} {req.position} 面试",
            "icon": "📋",
            "persona": persona,
            "categories": [
                {"key": c.key, "label": c.label, "priority": c.priority}
                for c in req.categories
            ],
            "references": refs,
            "is_temporary": True,
        }

    @classmethod
    def _find_reference_file(cls, key: str) -> Optional[str]:
        """
        查找并读取参考文件内容

        Args:
            key: 分类key，用于查找对应的.md文件

        Returns:
            文件内容字符串，如果文件不存在则返回None
        """
        if not os.path.isdir(REFERENCES_DIR):
            return None

        ref_path = os.path.join(REFERENCES_DIR, f"{key}.md")
        if os.path.isfile(ref_path):
            with open(ref_path, "r", encoding="utf-8") as f:
                return f.read()

        return None
