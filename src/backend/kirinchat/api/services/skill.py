import os
import time
import yaml
from loguru import logger
from kirinchat.settings import app_settings


# Default skills directory: kirinchat/skills (next to api/, core/, database/)
SKILLS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "skills")
)

# Priority sort order (lower number = higher priority)
_PRIORITY_ORDER = {
    "ALWAYS_ONE": 0,
    "CORE": 1,
    "NORMAL": 2,
}

# 技能文件缓存 TTL（秒）
_SKILL_CACHE_TTL = 300


class SkillService:
    """Service for loading interview skill definitions from the filesystem."""

    _temp_skills: dict = {}  # 临时 Skill 存储（内存）
    _skill_cache: dict[str, dict] = {}  # 技能文件缓存 {skill_id: {"data": dict, "ts": float}}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @classmethod
    def get_all_skills(cls):
        """
        List all valid skills found under the skills directory.

        Returns a list of dicts, each containing skill metadata
        (without references loaded).
        """
        skills_dir = cls._get_skills_dir()
        if not os.path.isdir(skills_dir):
            return []

        skills = []
        for entry in sorted(os.listdir(skills_dir)):
            entry_path = os.path.join(skills_dir, entry)
            if not os.path.isdir(entry_path):
                continue
            if entry.startswith("_"):
                # Skip shared / hidden directories
                continue
            skill = cls._load_skill_from_dir(entry, entry_path)
            if skill is not None:
                skills.append(skill)
        return skills

    @classmethod
    def register_temp_skill(cls, skill_data: dict, persist: bool = True):
        """注册一个临时 Skill（如 JD 解析生成的）。

        persist=True 时同时写入文件系统，确保服务重启后不丢失。
        """
        skill_id = skill_data.get("id", "")
        cls._temp_skills[skill_id] = skill_data
        # 清除缓存，确保下次读取拿到最新数据
        cls._skill_cache.pop(skill_id, None)
        if persist:
            cls._persist_skill_to_disk(skill_data)

    @classmethod
    def _persist_skill_to_disk(cls, skill_data: dict):
        """将 JD 生成的技能持久化到 skills 目录下。"""
        skill_id = skill_data.get("id", "")
        if not skill_id:
            return

        skills_dir = cls._get_skills_dir()
        skill_dir = os.path.join(skills_dir, skill_id)
        os.makedirs(skill_dir, exist_ok=True)

        # 写入 SKILL.md
        skill_md_path = os.path.join(skill_dir, "SKILL.md")
        name = skill_data.get("name", skill_id)
        description = skill_data.get("description", "")
        persona = skill_data.get("persona", "")
        with open(skill_md_path, "w", encoding="utf-8") as f:
            f.write(f"---\nname: {name}\ndescription: {description}\n---\n{persona}")

        # 写入 skill.meta.yml
        meta_path = os.path.join(skill_dir, "skill.meta.yml")
        meta = {
            "display": {
                "icon": skill_data.get("icon", ""),
            },
            "categories": skill_data.get("categories", []),
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            yaml.dump(meta, f, allow_unicode=True, default_flow_style=False)

        logger.info(f"JD skill persisted to disk: {skill_dir}")

    @classmethod
    def get_skill_by_id(cls, skill_id: str):
        """
        Load a single skill by its directory name (id).

        Returns the skill dict with categories sorted by priority,
        or None if the skill doesn't exist or is invalid.
        Uses an in-memory TTL cache to avoid repeated disk reads.
        """
        if skill_id in cls._temp_skills:
            return cls._temp_skills[skill_id]

        # 检查 TTL 缓存
        cached = cls._skill_cache.get(skill_id)
        if cached and (time.time() - cached["ts"]) < _SKILL_CACHE_TTL:
            return cached["data"]

        skills_dir = cls._get_skills_dir()
        skill_path = os.path.join(skills_dir, skill_id)
        skill = cls._load_skill_from_dir(skill_id, skill_path, load_references=True)

        # 缓存结果（包括 None，避免重复探测不存在的路径）
        cls._skill_cache[skill_id] = {"data": skill, "ts": time.time()}
        return skill

    @classmethod
    def load_skill_references(cls, skill_id: str, category_ref: str):
        """
        Load a reference file for a given skill and category ref name.

        Lookup order:
        1. skills/{skill_id}/references/{category_ref}
        2. skills/_shared/references/{category_ref}

        Returns the file content as a string, or None if not found.
        """
        if not category_ref:
            return None

        skills_dir = cls._get_skills_dir()

        # 1. Skill-specific
        skill_ref_path = os.path.join(
            skills_dir, skill_id, "references", category_ref
        )
        if os.path.isfile(skill_ref_path):
            return cls._read_text_file(skill_ref_path)

        # 2. Shared
        shared_ref_path = os.path.join(
            skills_dir, "_shared", "references", category_ref
        )
        if os.path.isfile(shared_ref_path):
            return cls._read_text_file(shared_ref_path)

        return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_skills_dir():
        """Return the configured skills directory path."""
        return getattr(app_settings, "skills_dir", SKILLS_DIR)

    @classmethod
    def _load_skill_from_dir(cls, skill_id: str, skill_path: str, load_references=False):
        """
        Load a skill definition from a directory containing
        SKILL.md and skill.meta.yml.

        Returns a skill dict or None if loading fails.
        """
        if not os.path.isdir(skill_path):
            return None

        skill_md_path = os.path.join(skill_path, "SKILL.md")
        meta_path = os.path.join(skill_path, "skill.meta.yml")

        if not os.path.isfile(skill_md_path):
            return None
        if not os.path.isfile(meta_path):
            return None

        # Parse SKILL.md
        parsed = cls._parse_skill_md(skill_md_path)

        # Parse meta YAML
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = yaml.safe_load(f)
        except (yaml.YAMLError, OSError) as e:
            logger.error(f"Failed to load skill meta for {skill_id}: {e}")
            return None

        if meta is None:
            return None

        display = meta.get("display", {})
        categories = meta.get("categories", [])
        sorted_categories = cls._sort_by_priority(categories)

        skill = {
            "id": skill_id,
            "name": parsed.get("name", skill_id) or skill_id,
            "description": parsed.get("description", ""),
            "persona": parsed.get("body", ""),
            "icon": display.get("icon", ""),
            "gradient": display.get("gradient", ""),
            "categories": sorted_categories,
        }

        if load_references:
            skill["references"] = cls._load_all_references(skill_id, sorted_categories)

        return skill

    @staticmethod
    def _parse_skill_md(filepath: str):
        """
        Parse a SKILL.md file with optional YAML front-matter.

        Returns {"name": str, "description": str, "body": str}.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        name = ""
        description = ""
        body = content

        # Detect front-matter: starts with '---\n'
        if content.startswith("---\n") or content.startswith("---\r\n"):
            # Split on the closing ---
            parts = content.split("---", 2)
            if len(parts) >= 3:
                front_matter_str = parts[1]
                body = parts[2].strip()
                try:
                    front_matter = yaml.safe_load(front_matter_str)
                    if front_matter:
                        name = front_matter.get("name", "")
                        description = front_matter.get("description", "")
                except yaml.YAMLError:
                    pass

        return {"name": name, "description": description, "body": body}

    @staticmethod
    def _sort_by_priority(categories: list):
        """
        Sort categories by priority: ALWAYS_ONE -> CORE -> NORMAL.
        Returns a new list; does not mutate the input.
        """
        return sorted(
            categories,
            key=lambda c: _PRIORITY_ORDER.get(c.get("priority", "NORMAL"), 99),
        )

    @classmethod
    def _load_all_references(cls, skill_id: str, categories: list):
        """
        Load reference content for every category that has a 'ref' field.

        Returns a dict mapping category key -> reference text.
        """
        refs = {}
        for cat in categories:
            ref = cat.get("ref")
            if ref:
                content = cls.load_skill_references(skill_id, ref)
                if content is not None:
                    refs[cat["key"]] = content
        return refs

    @staticmethod
    def _read_text_file(filepath: str):
        """Read a UTF-8 text file and return its content."""
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
