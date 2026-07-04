import json
import os
from uuid import uuid4

from loguru import logger
from langchain_core.messages import HumanMessage

from kirinchat.core.models.manager import ModelManager
from kirinchat.common.security.prompt_sanitizer import PromptSanitizer
from kirinchat.common.security.prompt_constants import DATA_BOUNDARY_TEMPLATE, ANTI_INJECTION_INSTRUCTION
from kirinchat.prompts.jd_parse import JD_PARSE_PROMPT
from kirinchat.schemas.jd import JdParseResp, JdCategoryResp, JdCreateSkillReq, JdSkillResp

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "skills")
REFERENCES_DIR = os.path.join(SKILLS_DIR, "_shared", "references")


class JdService:

    @classmethod
    async def parse_jd(cls, jd_text: str) -> JdParseResp:
        cleaned = PromptSanitizer.sanitize(jd_text)
        data_boundary = DATA_BOUNDARY_TEMPLATE.format(content=cleaned)

        prompt = JD_PARSE_PROMPT.format(
            anti_injection=ANTI_INJECTION_INSTRUCTION,
            data_boundary=data_boundary,
        )

        llm = ModelManager.get_conversation_model()
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        content = response.content if hasattr(response, "content") else str(response)

        result = cls._parse_llm_json(content)
        categories = [
            JdCategoryResp(
                key=c.get("key", ""),
                label=c.get("label", ""),
                priority=c.get("priority", "CORE"),
                keywords=c.get("keywords", []),
            )
            for c in result.get("categories", [])
        ]

        return JdParseResp(
            company=result.get("company", "未知公司"),
            position=result.get("position", "未知职位"),
            experience_required=result.get("experience_required", ""),
            categories=categories,
            summary=result.get("summary", ""),
        )

    @classmethod
    async def create_skill_from_jd(cls, req: JdCreateSkillReq) -> JdSkillResp:
        from kirinchat.api.services.skill import SkillService

        persona = cls._build_persona(req)
        refs = {}
        for cat in req.categories:
            ref_path = cls._find_reference_file(cat.key)
            if ref_path:
                refs[cat.key] = ref_path

        skill_id = f"jd-{uuid4().hex[:8]}"
        skill_data = {
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
        SkillService.register_temp_skill(skill_data)

        return JdSkillResp(
            skill_id=skill_id,
            name=skill_data["name"],
            description=skill_data["description"],
            categories=[c.key for c in req.categories],
        )

    @classmethod
    def _build_persona(cls, req) -> str:
        categories_text = "\n".join(f"- {c.label}" for c in req.categories)
        return (
            f"你是一位{req.company}的技术面试官。\n"
            f"你要面试的职位是：{req.position}。\n"
            f"经验要求：{req.experience_required}。\n\n"
            f"面试重点：\n{categories_text}\n\n"
            f"请严格按照以上技术方向出题，贴近真实面试场景。"
        )

    @classmethod
    def _find_reference_file(cls, key: str):
        if not os.path.isdir(REFERENCES_DIR):
            return None
        for fname in os.listdir(REFERENCES_DIR):
            if fname == f"{key}.md":
                return os.path.join(REFERENCES_DIR, fname)
        return None

    @staticmethod
    def _parse_llm_json(content: str) -> dict:
        text = content.strip()
        if "```" in text:
            parts = text.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                if part.startswith("{"):
                    text = part
                    break
        return json.loads(text)
