import os
import pytest
import tempfile
import yaml


def _create_skill_dir(tmpdir, skill_id="test-skill", meta=None, persona=None):
    """Helper: create a skill directory with meta and SKILL.md files."""
    skill_dir = os.path.join(tmpdir, skill_id)
    os.makedirs(skill_dir)

    if meta is None:
        meta = {
            "display": {"icon": "☕", "gradient": "from-orange-500 to-red-600"},
            "categories": [
                {"key": "java", "label": "Java 核心", "priority": "CORE"},
                {"key": "project", "label": "项目经历", "priority": "ALWAYS_ONE"},
            ],
        }
    with open(os.path.join(skill_dir, "skill.meta.yml"), "w", encoding="utf-8") as f:
        yaml.dump(meta, f, allow_unicode=True)

    if persona is None:
        persona = "你是一位资深的面试官，擅长考察候选人的综合能力。"
    skill_md = f"---\nname: {skill_id}\ndescription: Test Skill\n---\n\n{persona}"
    with open(os.path.join(skill_dir, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write(skill_md)

    return skill_dir


class TestLoadSkillFromDir:
    """Tests for SkillService._load_skill_from_dir"""

    def test_load_skill_meta(self):
        """Test loading skill.meta.yml and SKILL.md from a directory."""
        from kirinchat.api.services.skill import SkillService

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = _create_skill_dir(tmpdir, "test-skill")

            result = SkillService._load_skill_from_dir("test-skill", skill_dir)
            assert result is not None
            assert result["id"] == "test-skill"
            assert result["name"] == "test-skill"
            assert result["description"] == "Test Skill"
            assert result["icon"] == "☕"
            assert result["gradient"] == "from-orange-500 to-red-600"
            assert len(result["categories"]) == 2
            assert result["persona"] == "你是一位资深的面试官，擅长考察候选人的综合能力。"

    def test_returns_none_for_missing_skill_md(self):
        """Should return None if SKILL.md is missing."""
        from kirinchat.api.services.skill import SkillService

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = os.path.join(tmpdir, "bad-skill")
            os.makedirs(skill_dir)
            meta = {"display": {"icon": "x", "gradient": "g"}, "categories": []}
            with open(os.path.join(skill_dir, "skill.meta.yml"), "w", encoding="utf-8") as f:
                yaml.dump(meta, f, allow_unicode=True)
            # No SKILL.md

            result = SkillService._load_skill_from_dir("bad-skill", skill_dir)
            assert result is None

    def test_returns_none_for_missing_meta_yml(self):
        """Should return None if skill.meta.yml is missing."""
        from kirinchat.api.services.skill import SkillService

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = os.path.join(tmpdir, "bad-skill")
            os.makedirs(skill_dir)
            # No skill.meta.yml
            with open(os.path.join(skill_dir, "SKILL.md"), "w", encoding="utf-8") as f:
                f.write("---\nname: bad-skill\ndescription: Bad\n---\n\nPersona")

            result = SkillService._load_skill_from_dir("bad-skill", skill_dir)
            assert result is None

    def test_returns_none_for_invalid_yaml(self):
        """Should return None if skill.meta.yml is invalid YAML."""
        from kirinchat.api.services.skill import SkillService

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = os.path.join(tmpdir, "bad-skill")
            os.makedirs(skill_dir)
            with open(os.path.join(skill_dir, "skill.meta.yml"), "w", encoding="utf-8") as f:
                f.write("{{{{invalid yaml")
            with open(os.path.join(skill_dir, "SKILL.md"), "w", encoding="utf-8") as f:
                f.write("---\nname: bad-skill\ndescription: Bad\n---\n\nPersona")

            result = SkillService._load_skill_from_dir("bad-skill", skill_dir)
            assert result is None

    def test_returns_none_for_nonexistent_dir(self):
        """Should return None if the directory does not exist."""
        from kirinchat.api.services.skill import SkillService

        result = SkillService._load_skill_from_dir("no-skill", "/nonexistent/path")
        assert result is None


class TestSortByPriority:
    """Tests for SkillService._sort_by_priority"""

    def test_sort_order(self):
        """ALWAYS_ONE should come first, then CORE, then NORMAL."""
        from kirinchat.api.services.skill import SkillService

        categories = [
            {"key": "normal1", "priority": "NORMAL"},
            {"key": "always", "priority": "ALWAYS_ONE"},
            {"key": "core1", "priority": "CORE"},
            {"key": "normal2", "priority": "NORMAL"},
        ]
        result = SkillService._sort_by_priority(categories)
        assert result[0]["priority"] == "ALWAYS_ONE"
        assert result[1]["priority"] == "CORE"
        assert result[2]["priority"] == "NORMAL"
        assert result[3]["priority"] == "NORMAL"

    def test_empty_list(self):
        """Sorting an empty list should return an empty list."""
        from kirinchat.api.services.skill import SkillService

        result = SkillService._sort_by_priority([])
        assert result == []

    def test_single_item(self):
        """Sorting a single-item list should return the same list."""
        from kirinchat.api.services.skill import SkillService

        result = SkillService._sort_by_priority([{"key": "x", "priority": "CORE"}])
        assert len(result) == 1
        assert result[0]["key"] == "x"


class TestParseSkillMd:
    """Tests for SkillService._parse_skill_md"""

    def test_parse_with_frontmatter(self):
        """Should extract name, description from front-matter and body."""
        from kirinchat.api.services.skill import SkillService

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write("---\nname: java-backend\ndescription: Java 后端\n---\n\n你是一位面试官")
            f.flush()
            result = SkillService._parse_skill_md(f.name)

        os.unlink(f.name)
        assert result["name"] == "java-backend"
        assert result["description"] == "Java 后端"
        assert "面试官" in result["body"]

    def test_parse_without_frontmatter(self):
        """Should handle file with no front-matter."""
        from kirinchat.api.services.skill import SkillService

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write("Just plain text, no front-matter.")
            f.flush()
            result = SkillService._parse_skill_md(f.name)

        os.unlink(f.name)
        assert result["name"] == ""
        assert result["description"] == ""
        assert "plain text" in result["body"]


class TestGetAllSkills:
    """Tests for SkillService.get_all_skills"""

    def test_get_all_skills(self):
        """Should list all valid skill directories."""
        from kirinchat.api.services.skill import SkillService

        with tempfile.TemporaryDirectory() as tmpdir:
            _create_skill_dir(tmpdir, "skill-a")
            _create_skill_dir(tmpdir, "skill-b")
            # Create a non-skill directory (missing SKILL.md)
            os.makedirs(os.path.join(tmpdir, "_shared"))

            with pytest.MonkeyPatch.context() as m:
                m.setattr(
                    "kirinchat.api.services.skill.SkillService._get_skills_dir",
                    lambda: tmpdir,
                )
                skills = SkillService.get_all_skills()

            assert len(skills) == 2
            ids = {s["id"] for s in skills}
            assert "skill-a" in ids
            assert "skill-b" in ids

    def test_get_all_skills_empty_dir(self):
        """Should return empty list if skills dir has no valid skills."""
        from kirinchat.api.services.skill import SkillService

        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.MonkeyPatch.context() as m:
                m.setattr(
                    "kirinchat.api.services.skill.SkillService._get_skills_dir",
                    lambda: tmpdir,
                )
                skills = SkillService.get_all_skills()

            assert skills == []


class TestGetSkillById:
    """Tests for SkillService.get_skill_by_id"""

    def test_get_existing_skill(self):
        """Should return skill data for an existing skill."""
        from kirinchat.api.services.skill import SkillService

        with tempfile.TemporaryDirectory() as tmpdir:
            _create_skill_dir(tmpdir, "java-backend")

            with pytest.MonkeyPatch.context() as m:
                m.setattr(
                    "kirinchat.api.services.skill.SkillService._get_skills_dir",
                    lambda: tmpdir,
                )
                result = SkillService.get_skill_by_id("java-backend")

            assert result is not None
            assert result["id"] == "java-backend"

    def test_get_nonexistent_skill(self):
        """Should return None for a skill that doesn't exist."""
        from kirinchat.api.services.skill import SkillService

        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.MonkeyPatch.context() as m:
                m.setattr(
                    "kirinchat.api.services.skill.SkillService._get_skills_dir",
                    lambda: tmpdir,
                )
                result = SkillService.get_skill_by_id("nonexistent")

            assert result is None


class TestLoadSkillReferences:
    """Tests for SkillService.load_skill_references and _load_all_references"""

    def test_load_reference_from_skill_dir(self):
        """Should load reference from skill-specific references directory."""
        from kirinchat.api.services.skill import SkillService

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = _create_skill_dir(tmpdir, "test-skill")
            ref_dir = os.path.join(skill_dir, "references")
            os.makedirs(ref_dir)
            with open(os.path.join(ref_dir, "java.md"), "w", encoding="utf-8") as f:
                f.write("# Java Reference Content")

            with pytest.MonkeyPatch.context() as m:
                m.setattr(
                    "kirinchat.api.services.skill.SkillService._get_skills_dir",
                    lambda: tmpdir,
                )
                result = SkillService.load_skill_references("test-skill", "java.md")

            assert result is not None
            assert "Java Reference Content" in result

    def test_load_reference_from_shared_dir(self):
        """Should fallback to shared references directory."""
        from kirinchat.api.services.skill import SkillService

        with tempfile.TemporaryDirectory() as tmpdir:
            _create_skill_dir(tmpdir, "test-skill")
            shared_ref_dir = os.path.join(tmpdir, "_shared", "references")
            os.makedirs(shared_ref_dir)
            with open(os.path.join(shared_ref_dir, "common.md"), "w", encoding="utf-8") as f:
                f.write("# Common Reference")

            with pytest.MonkeyPatch.context() as m:
                m.setattr(
                    "kirinchat.api.services.skill.SkillService._get_skills_dir",
                    lambda: tmpdir,
                )
                result = SkillService.load_skill_references("test-skill", "common.md")

            assert result is not None
            assert "Common Reference" in result

    def test_skill_dir_takes_precedence(self):
        """Skill-specific reference should take precedence over shared."""
        from kirinchat.api.services.skill import SkillService

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = _create_skill_dir(tmpdir, "test-skill")
            # Skill-specific
            ref_dir = os.path.join(skill_dir, "references")
            os.makedirs(ref_dir)
            with open(os.path.join(ref_dir, "dup.md"), "w", encoding="utf-8") as f:
                f.write("# Skill-specific")
            # Shared
            shared_ref_dir = os.path.join(tmpdir, "_shared", "references")
            os.makedirs(shared_ref_dir)
            with open(os.path.join(shared_ref_dir, "dup.md"), "w", encoding="utf-8") as f:
                f.write("# Shared")

            with pytest.MonkeyPatch.context() as m:
                m.setattr(
                    "kirinchat.api.services.skill.SkillService._get_skills_dir",
                    lambda: tmpdir,
                )
                result = SkillService.load_skill_references("test-skill", "dup.md")

            assert "Skill-specific" in result

    def test_load_nonexistent_reference(self):
        """Should return None for a reference file that doesn't exist."""
        from kirinchat.api.services.skill import SkillService

        with tempfile.TemporaryDirectory() as tmpdir:
            _create_skill_dir(tmpdir, "test-skill")

            with pytest.MonkeyPatch.context() as m:
                m.setattr(
                    "kirinchat.api.services.skill.SkillService._get_skills_dir",
                    lambda: tmpdir,
                )
                result = SkillService.load_skill_references("test-skill", "nope.md")

            assert result is None

    def test_load_all_references(self):
        """Should load references for categories that have a ref field."""
        from kirinchat.api.services.skill import SkillService

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = _create_skill_dir(tmpdir, "test-skill")
            ref_dir = os.path.join(skill_dir, "references")
            os.makedirs(ref_dir)
            with open(os.path.join(ref_dir, "java.md"), "w", encoding="utf-8") as f:
                f.write("# Java Content")

            categories = [
                {"key": "java", "label": "Java", "priority": "CORE", "ref": "java.md"},
                {"key": "project", "label": "Project", "priority": "ALWAYS_ONE"},
            ]

            with pytest.MonkeyPatch.context() as m:
                m.setattr(
                    "kirinchat.api.services.skill.SkillService._get_skills_dir",
                    lambda: tmpdir,
                )
                result = SkillService._load_all_references("test-skill", categories)

            assert "java" in result
            assert "Java Content" in result["java"]
            assert "project" not in result
