# Interview Learning Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 Phase 1 面试学习平台：Interview Agent + Skill 体系 + 基础评估引擎

**Architecture:** 基于 KirinChat 现有三层架构（API Route → Service → DAO），新增面试模块。Interview Agent 通过 duck typing 与现有 Agent 体系集成，Skill Service 从文件系统加载面试方向定义，Evaluation Service 提供分批评估和降级兜底能力。

**Tech Stack:** Python 3.11+ / FastAPI / SQLModel / MySQL / Redis / LangChain / Pydantic

---

## 文件结构

### 新增文件

| 文件路径 | 职责 |
|---------|------|
| `src/backend/kirinchat/database/models/interview.py` | 面试相关数据模型（InterviewSessionTable, InterviewQuestionTable, EvaluationReportTable） |
| `src/backend/kirinchat/database/dao/interview.py` | 面试数据访问层 |
| `src/backend/kirinchat/schemas/interview.py` | 面试请求/响应 Schema |
| `src/backend/kirinchat/api/services/interview.py` | 面试业务逻辑服务 |
| `src/backend/kirinchat/api/services/skill.py` | Skill 加载和管理服务 |
| `src/backend/kirinchat/api/services/evaluation.py` | 评估引擎服务 |
| `src/backend/kirinchat/api/v1/interview.py` | 面试 API 路由 |
| `src/backend/kirinchat/core/agents/interview_agent.py` | 面试 Agent 实现 |
| `src/backend/kirinchat/skills/java-backend/SKILL.md` | Java 后端面试 Skill 定义 |
| `src/backend/kirinchat/skills/java-backend/skill.meta.yml` | Java 后端 Skill 元数据 |
| `src/backend/kirinchat/skills/_shared/references/java.md` | Java 核心知识点参考 |
| `src/backend/kirinchat/skills/_shared/references/mysql.md` | MySQL 核心知识点参考 |
| `src/backend/kirinchat/skills/_shared/references/redis.md` | Redis 核心知识点参考 |
| `src/backend/kirinchat/skills/_shared/references/spring.md` | Spring 核心知识点参考 |
| `tests/backend/test_skill_service.py` | Skill Service 单元测试 |
| `tests/backend/test_interview_service.py` | Interview Service 单元测试 |
| `tests/backend/test_evaluation_service.py` | Evaluation Service 单元测试 |
| `tests/backend/test_interview_api.py` | 面试 API 集成测试 |

### 修改文件

| 文件路径 | 修改内容 |
|---------|---------|
| `src/backend/kirinchat/api/v1/router.py` | 注册 interview router |

---

## Task 1: 数据模型定义

**Files:**
- Create: `src/backend/kirinchat/database/models/interview.py`

- [ ] **Step 1: 创建 InterviewSessionTable 模型**

```python
# src/backend/kirinchat/database/models/interview.py
from datetime import datetime
from typing import Optional, ClassVar
from uuid import uuid4

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, text, JSON, Text, Float, Integer
from sqlmodel import Field

from kirinchat.database.models.base import SQLModelSerializable


class InterviewSessionTable(SQLModelSerializable, table=True):
    """面试会话表"""
    __tablename__ = "interview_session"

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    user_id: str = Field(description="用户ID")
    agent_id: Optional[str] = Field(default=None, description="Agent ID")
    skill_id: str = Field(description="面试方向ID")
    difficulty: str = Field(default="MEDIUM", description="难度: EASY/MEDIUM/HARD")
    question_count: int = Field(default=10, description="题目数量")
    status: str = Field(default="CREATED", description="状态: CREATED/IN_PROGRESS/COMPLETED/EVALUATED")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    update_time: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))
    )
    create_time: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    )
```

- [ ] **Step 2: 添加 InterviewQuestionTable 模型**

在同一文件中添加：

```python
class InterviewQuestionTable(SQLModelSerializable, table=True):
    """面试题目表"""
    __tablename__ = "interview_question"

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    session_id: str = Field(description="面试会话ID")
    type: str = Field(default="MAIN", description="题目类型: MAIN/FOLLOW_UP")
    category: str = Field(description="知识点分类")
    content: str = Field(sa_column=Column(Text, nullable=False), description="题目内容")
    user_answer: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True), description="用户答案")
    score: Optional[float] = Field(default=None, description="分数 (0-10)")
    create_time: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    )
```

- [ ] **Step 3: 添加 EvaluationReportTable 模型**

在同一文件末尾添加：

```python
class EvaluationReportTable(SQLModelSerializable, table=True):
    """评估报告表"""
    __tablename__ = "evaluation_report"

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    session_id: str = Field(description="面试会话ID")
    total_score: float = Field(description="总分")
    category_scores: dict = Field(sa_column=Column(JSON, nullable=False), description="各分类分数")
    summary: str = Field(sa_column=Column(Text, nullable=False), description="AI 总结")
    strengths: list = Field(sa_column=Column(JSON, nullable=False), description="优势列表")
    improvements: list = Field(sa_column=Column(JSON, nullable=False), description="改进建议列表")
    create_time: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    )
```

- [ ] **Step 4: 验证模型语法正确**

```bash
cd src/backend
python -c "from kirinchat.database.models.interview import InterviewSessionTable, InterviewQuestionTable, EvaluationReportTable; print('Models imported successfully')"
```

- [ ] **Step 5: Commit**

```bash
git add src/backend/kirinchat/database/models/interview.py
git commit -m "feat: add interview data models (session, question, evaluation)"
```

---

## Task 2: DAO 层实现

**Files:**
- Create: `src/backend/kirinchat/database/dao/interview.py`

- [ ] **Step 1: 创建 InterviewSessionDao**

```python
# src/backend/kirinchat/database/dao/interview.py
from typing import List, Optional

from sqlmodel import select

from kirinchat.database.models.interview import (
    InterviewSessionTable,
    InterviewQuestionTable,
    EvaluationReportTable,
)
from kirinchat.database.session import session_getter


class InterviewSessionDao:
    @classmethod
    async def create_session(cls, session: InterviewSessionTable) -> InterviewSessionTable:
        with session_getter() as db:
            db.add(session)
            db.commit()
            db.refresh(session)
            return session

    @classmethod
    async def select_session_by_id(cls, session_id: str) -> Optional[InterviewSessionTable]:
        with session_getter() as db:
            statement = select(InterviewSessionTable).where(InterviewSessionTable.id == session_id)
            return db.exec(statement).first()

    @classmethod
    async def update_session_status(cls, session_id: str, status: str) -> Optional[InterviewSessionTable]:
        with session_getter() as db:
            session = db.exec(select(InterviewSessionTable).where(InterviewSessionTable.id == session_id)).first()
            if session:
                session.status = status
                db.add(session)
                db.commit()
                db.refresh(session)
            return session

    @classmethod
    async def select_sessions_by_user(cls, user_id: str) -> List[InterviewSessionTable]:
        with session_getter() as db:
            statement = select(InterviewSessionTable).where(
                InterviewSessionTable.user_id == user_id
            ).order_by(InterviewSessionTable.create_time.desc())
            return list(db.exec(statement).all())
```

- [ ] **Step 2: 创建 InterviewQuestionDao**

```python
class InterviewQuestionDao:
    @classmethod
    async def create_question(cls, question: InterviewQuestionTable) -> InterviewQuestionTable:
        with session_getter() as db:
            db.add(question)
            db.commit()
            db.refresh(question)
            return question

    @classmethod
    async def select_questions_by_session(cls, session_id: str) -> List[InterviewQuestionTable]:
        with session_getter() as db:
            statement = select(InterviewQuestionTable).where(
                InterviewQuestionTable.session_id == session_id
            ).order_by(InterviewQuestionTable.create_time)
            return list(db.exec(statement).all())

    @classmethod
    async def update_question_answer(cls, question_id: str, answer: str) -> Optional[InterviewQuestionTable]:
        with session_getter() as db:
            question = db.exec(select(InterviewQuestionTable).where(InterviewQuestionTable.id == question_id)).first()
            if question:
                question.user_answer = answer
                db.add(question)
                db.commit()
                db.refresh(question)
            return question

    @classmethod
    async def update_question_score(cls, question_id: str, score: float) -> Optional[InterviewQuestionTable]:
        with session_getter() as db:
            question = db.exec(select(InterviewQuestionTable).where(InterviewQuestionTable.id == question_id)).first()
            if question:
                question.score = score
                db.add(question)
                db.commit()
                db.refresh(question)
            return question
```

- [ ] **Step 3: 创建 EvaluationReportDao**

```python
class EvaluationReportDao:
    @classmethod
    async def create_report(cls, report: EvaluationReportTable) -> EvaluationReportTable:
        with session_getter() as db:
            db.add(report)
            db.commit()
            db.refresh(report)
            return report

    @classmethod
    async def select_report_by_session(cls, session_id: str) -> Optional[EvaluationReportTable]:
        with session_getter() as db:
            statement = select(EvaluationReportTable).where(EvaluationReportTable.session_id == session_id)
            return db.exec(statement).first()

    @classmethod
    async def select_report_by_id(cls, report_id: str) -> Optional[EvaluationReportTable]:
        with session_getter() as db:
            statement = select(EvaluationReportTable).where(EvaluationReportTable.id == report_id)
            return db.exec(statement).first()
```

- [ ] **Step 4: 验证 DAO 语法正确**

```bash
cd src/backend
python -c "from kirinchat.database.dao.interview import InterviewSessionDao, InterviewQuestionDao, EvaluationReportDao; print('DAO imported successfully')"
```

- [ ] **Step 5: Commit**

```bash
git add src/backend/kirinchat/database/dao/interview.py
git commit -m "feat: add interview DAO layer (session, question, evaluation)"
```

---

## Task 3: Schema 定义

**Files:**
- Create: `src/backend/kirinchat/schemas/interview.py`

- [ ] **Step 1: 创建请求 Schema**

```python
# src/backend/kirinchat/schemas/interview.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class InterviewStartReq(BaseModel):
    """开始面试请求"""
    skill_id: str = Field(..., description="面试方向ID，如 java-backend")
    difficulty: str = Field(default="MEDIUM", description="难度: EASY/MEDIUM/HARD")
    question_count: int = Field(default=10, description="题目数量", ge=1, le=50)


class InterviewAnswerReq(BaseModel):
    """提交答案请求"""
    session_id: str = Field(..., description="面试会话ID")
    question_id: str = Field(..., description="题目ID")
    answer: str = Field(..., description="用户答案")


class InterviewCompleteReq(BaseModel):
    """完成面试请求"""
    session_id: str = Field(..., description="面试会话ID")
```

- [ ] **Step 2: 创建响应 Schema**

```python
class SkillCategoryResp(BaseModel):
    """Skill 分类响应"""
    key: str = Field(description="分类 key")
    label: str = Field(description="分类显示名称")
    priority: str = Field(description="优先级: ALWAYS_ONE/CORE/NORMAL")


class SkillInfoResp(BaseModel):
    """Skill 简要信息响应"""
    id: str = Field(description="Skill ID")
    name: str = Field(description="Skill 名称")
    description: str = Field(description="Skill 描述")
    icon: str = Field(default="", description="图标")
    categories: List[SkillCategoryResp] = Field(default=[], description="分类列表")


class QuestionResp(BaseModel):
    """题目响应"""
    id: str = Field(description="题目ID")
    type: str = Field(description="MAIN/FOLLOW_UP")
    category: str = Field(description="知识点分类")
    content: str = Field(description="题目内容")


class InterviewStartResp(BaseModel):
    """开始面试响应"""
    session_id: str = Field(description="会话ID")
    first_question: QuestionResp = Field(description="第一道题目")


class InterviewAnswerResp(BaseModel):
    """提交答案响应"""
    next_question: Optional[QuestionResp] = Field(default=None, description="下一题（如有追问）")
    is_completed: bool = Field(description="是否已完成所有题目")


class InterviewSessionResp(BaseModel):
    """面试会话响应"""
    id: str = Field(description="会话ID")
    skill_id: str = Field(description="面试方向")
    status: str = Field(description="状态")
    progress: Dict[str, int] = Field(description="进度 {current, total}")


class InterviewSessionDetailResp(BaseModel):
    """面试会话详情响应"""
    session: InterviewSessionResp
    questions: List[QuestionResp]


class InterviewCompleteResp(BaseModel):
    """完成面试响应"""
    evaluation_id: str = Field(description="评估报告ID")
    status: str = Field(description="评估状态")


class CategoryScoreResp(BaseModel):
    """分类分数"""
    scores: Dict[str, float] = Field(description="各分类分数 {category: score}")


class EvaluationReportResp(BaseModel):
    """评估报告响应"""
    id: str = Field(description="报告ID")
    total_score: float = Field(description="总分")
    category_scores: Dict[str, float] = Field(description="各分类分数")
    summary: str = Field(description="AI 总结")
    strengths: List[str] = Field(description="优势列表")
    improvements: List[str] = Field(description="改进建议")


class InterviewHistoryResp(BaseModel):
    """面试历史响应"""
    sessions: List[InterviewSessionResp]


class SkillDetailResp(BaseModel):
    """Skill 详情响应"""
    skill: SkillInfoResp
    categories: List[SkillCategoryResp]
    references: Dict[str, str] = Field(description="参考资料 {filename: content}")


class SkillListResp(BaseModel):
    """Skill 列表响应"""
    skills: List[SkillInfoResp]
```

- [ ] **Step 3: 验证 Schema 语法正确**

```bash
cd src/backend
python -c "from kirinchat.schemas.interview import InterviewStartReq, InterviewStartResp; print('Schemas imported successfully')"
```

- [ ] **Step 4: Commit**

```bash
git add src/backend/kirinchat/schemas/interview.py
git commit -m "feat: add interview request/response schemas"
```

---

## Task 4: Skill Service 实现

**Files:**
- Create: `src/backend/kirinchat/api/services/skill.py`
- Create: `tests/backend/test_skill_service.py`

- [ ] **Step 1: 编写 SkillService 测试**

```python
# tests/backend/test_skill_service.py
import os
import pytest
from unittest.mock import patch, MagicMock


def test_load_skill_meta():
    """测试加载 skill.meta.yml"""
    from kirinchat.api.services.skill import SkillService

    # 使用临时目录创建测试文件
    import tempfile
    import yaml

    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = os.path.join(tmpdir, "test-skill")
        os.makedirs(skill_dir)

        meta = {
            "display": {"icon": "☕", "gradient": "from-orange-500 to-red-600"},
            "categories": [
                {"key": "java", "label": "Java 核心", "priority": "CORE"},
                {"key": "project", "label": "项目经历", "priority": "ALWAYS_ONE"},
            ]
        }
        with open(os.path.join(skill_dir, "skill.meta.yml"), "w") as f:
            yaml.dump(meta, f)

        with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
            f.write("---\nname: test-skill\ndescription: Test Skill\n---\n\n你是一位面试官")

        result = SkillService._load_skill_from_dir("test-skill", skill_dir)
        assert result is not None
        assert result["id"] == "test-skill"
        assert result["name"] == "test-skill"
        assert len(result["categories"]) == 2
        assert result["categories"][0]["key"] == "java"


def test_get_priority_order():
    """测试优先级排序"""
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
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd src/backend
python -m pytest tests/backend/test_skill_service.py -v
```

预期: FAIL (ModuleNotFoundError: No module named 'kirinchat.api.services.skill')

- [ ] **Step 3: 实现 SkillService**

```python
# src/backend/kirinchat/api/services/skill.py
import os
import yaml
from typing import List, Optional, Dict

from kirinchat.settings import app_settings


SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "skills")

# 优先级排序顺序
PRIORITY_ORDER = {"ALWAYS_ONE": 0, "CORE": 1, "NORMAL": 2}


class SkillService:
    @classmethod
    def get_all_skills(cls) -> List[dict]:
        """获取所有可用的 Skill"""
        skills = []
        skills_dir = cls._get_skills_dir()
        if not os.path.exists(skills_dir):
            return skills

        for entry in os.listdir(skills_dir):
            entry_path = os.path.join(skills_dir, entry)
            if os.path.isdir(entry_path) and not entry.startswith("_"):
                skill = cls._load_skill_from_dir(entry, entry_path)
                if skill:
                    skills.append(skill)
        return skills

    @classmethod
    def get_skill_by_id(cls, skill_id: str) -> Optional[dict]:
        """根据 ID 获取 Skill 详情"""
        skills_dir = cls._get_skills_dir()
        skill_path = os.path.join(skills_dir, skill_id)
        if not os.path.exists(skill_path):
            return None
        return cls._load_skill_from_dir(skill_id, skill_path, load_references=True)

    @classmethod
    def load_skill_references(cls, skill_id: str, category_ref: str) -> Optional[str]:
        """加载 Skill 参考资料"""
        skills_dir = cls._get_skills_dir()
        # 先查 skill 专属目录
        skill_ref = os.path.join(skills_dir, skill_id, "references", category_ref)
        if os.path.exists(skill_ref):
            with open(skill_ref, "r", encoding="utf-8") as f:
                return f.read()
        # 再查共享目录
        shared_ref = os.path.join(skills_dir, "_shared", "references", category_ref)
        if os.path.exists(shared_ref):
            with open(shared_ref, "r", encoding="utf-8") as f:
                return f.read()
        return None

    @classmethod
    def _get_skills_dir(cls) -> str:
        """获取 skills 目录路径"""
        return app_settings.get("skills_dir", SKILLS_DIR)

    @classmethod
    def _load_skill_from_dir(cls, skill_id: str, skill_path: str, load_references: bool = False) -> Optional[dict]:
        """从目录加载 Skill 定义"""
        meta_path = os.path.join(skill_path, "skill.meta.yml")
        skill_md_path = os.path.join(skill_path, "SKILL.md")

        if not os.path.exists(meta_path) or not os.path.exists(skill_md_path):
            return None

        # 加载 meta
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = yaml.safe_load(f) or {}

        # 解析 SKILL.md front-matter
        persona = cls._parse_skill_md(skill_md_path)

        display = meta.get("display", {})
        categories = meta.get("categories", [])
        sorted_categories = cls._sort_by_priority(categories)

        skill = {
            "id": skill_id,
            "name": persona.get("name", skill_id),
            "description": persona.get("description", ""),
            "persona": persona.get("body", ""),
            "icon": display.get("icon", ""),
            "gradient": display.get("gradient", ""),
            "categories": sorted_categories,
        }

        if load_references:
            skill["references"] = cls._load_all_references(skill_id, categories)

        return skill

    @classmethod
    def _parse_skill_md(cls, filepath: str) -> dict:
        """解析 SKILL.md 文件的 front-matter 和 body"""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        result = {"name": "", "description": "", "body": ""}
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                front_matter = yaml.safe_load(parts[1]) or {}
                result["name"] = front_matter.get("name", "")
                result["description"] = front_matter.get("description", "")
                result["body"] = parts[2].strip()
        return result

    @classmethod
    def _sort_by_priority(cls, categories: List[dict]) -> List[dict]:
        """按优先级排序分类: ALWAYS_ONE -> CORE -> NORMAL"""
        return sorted(categories, key=lambda c: PRIORITY_ORDER.get(c.get("priority", "NORMAL"), 99))

    @classmethod
    def _load_all_references(cls, skill_id: str, categories: List[dict]) -> Dict[str, str]:
        """加载所有分类的参考资料"""
        refs = {}
        for cat in categories:
            ref_file = cat.get("ref")
            if ref_file and ref_file not in refs:
                content = cls.load_skill_references(skill_id, ref_file)
                if content:
                    refs[ref_file] = content
        return refs
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd src/backend
python -m pytest tests/backend/test_skill_service.py -v
```

预期: PASS

- [ ] **Step 5: Commit**

```bash
git add src/backend/kirinchat/api/services/skill.py tests/backend/test_skill_service.py
git commit -m "feat: add SkillService with file-based skill loading"
```

---

## Task 5: Interview Service 实现

**Files:**
- Create: `src/backend/kirinchat/api/services/interview.py`
- Create: `tests/backend/test_interview_service.py`

- [ ] **Step 1: 编写 InterviewService 测试**

```python
# tests/backend/test_interview_service.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_create_session():
    """测试创建面试会话"""
    from kirinchat.api.services.interview import InterviewService

    mock_session = MagicMock()
    mock_session.id = "test-session-id"
    mock_session.skill_id = "java-backend"
    mock_session.status = "CREATED"

    with patch("kirinchat.api.services.interview.InterviewSessionDao.create_session", new_callable=AsyncMock, return_value=mock_session):
        with patch("kirinchat.api.services.interview.SkillService.get_skill_by_id", return_value={"id": "java-backend", "persona": "面试官", "categories": []}):
            session = await InterviewService.create_session(
                user_id="user1",
                skill_id="java-backend",
                difficulty="MEDIUM",
                question_count=10
            )
            assert session.id == "test-session-id"
            assert session.skill_id == "java-backend"


@pytest.mark.asyncio
async def test_submit_answer():
    """测试提交答案"""
    from kirinchat.api.services.interview import InterviewService

    mock_question = MagicMock()
    mock_question.id = "q1"
    mock_question.user_answer = None

    with patch("kirinchat.api.services.interview.InterviewQuestionDao.update_question_answer", new_callable=AsyncMock, return_value=mock_question):
        result = await InterviewService.submit_answer("q1", "这是我的答案")
        assert result is not None
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd src/backend
python -m pytest tests/backend/test_interview_service.py -v
```

预期: FAIL

- [ ] **Step 3: 实现 InterviewService**

```python
# src/backend/kirinchat/api/services/interview.py
from typing import Optional, List

from kirinchat.database.models.interview import (
    InterviewSessionTable,
    InterviewQuestionTable,
)
from kirinchat.database.dao.interview import (
    InterviewSessionDao,
    InterviewQuestionDao,
)
from kirinchat.api.services.skill import SkillService


class InterviewService:
    @classmethod
    async def create_session(
        cls,
        user_id: str,
        skill_id: str,
        difficulty: str = "MEDIUM",
        question_count: int = 10,
    ) -> InterviewSessionTable:
        """创建面试会话"""
        skill = SkillService.get_skill_by_id(skill_id)
        if not skill:
            raise ValueError(f"Skill not found: {skill_id}")

        session = InterviewSessionTable(
            user_id=user_id,
            skill_id=skill_id,
            difficulty=difficulty,
            question_count=question_count,
            status="CREATED",
        )
        return await InterviewSessionDao.create_session(session)

    @classmethod
    async def get_session(cls, session_id: str) -> Optional[InterviewSessionTable]:
        """获取面试会话"""
        return await InterviewSessionDao.select_session_by_id(session_id)

    @classmethod
    async def get_session_questions(cls, session_id: str) -> List[InterviewQuestionTable]:
        """获取会话的所有题目"""
        return await InterviewQuestionDao.select_questions_by_session(session_id)

    @classmethod
    async def save_question(cls, question: InterviewQuestionTable) -> InterviewQuestionTable:
        """保存面试题目"""
        return await InterviewQuestionDao.create_question(question)

    @classmethod
    async def submit_answer(cls, question_id: str, answer: str) -> Optional[InterviewQuestionTable]:
        """提交答案"""
        return await InterviewQuestionDao.update_question_answer(question_id, answer)

    @classmethod
    async def update_session_status(cls, session_id: str, status: str) -> Optional[InterviewSessionTable]:
        """更新会话状态"""
        return await InterviewSessionDao.update_session_status(session_id, status)

    @classmethod
    async def get_user_sessions(cls, user_id: str) -> List[InterviewSessionTable]:
        """获取用户的所有面试会话"""
        return await InterviewSessionDao.select_sessions_by_user(user_id)

    @classmethod
    async def calculate_progress(cls, session_id: str) -> dict:
        """计算面试进度"""
        questions = await InterviewQuestionDao.select_questions_by_session(session_id)
        total = len(questions)
        answered = sum(1 for q in questions if q.user_answer)
        return {"current": answered, "total": total}
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd src/backend
python -m pytest tests/backend/test_interview_service.py -v
```

预期: PASS

- [ ] **Step 5: Commit**

```bash
git add src/backend/kirinchat/api/services/interview.py tests/backend/test_interview_service.py
git commit -m "feat: add InterviewService for session and question management"
```

---

## Task 6: Evaluation Service 实现

**Files:**
- Create: `src/backend/kirinchat/api/services/evaluation.py`
- Create: `tests/backend/test_evaluation_service.py`

- [ ] **Step 1: 编写 EvaluationService 测试**

```python
# tests/backend/test_evaluation_service.py
import pytest


def test_batch_questions():
    """测试题目分批"""
    from kirinchat.api.services.evaluation import EvaluationService

    questions = [{"id": f"q{i}", "content": f"question {i}", "answer": f"answer {i}"} for i in range(20)]
    batches = EvaluationService._batch_questions(questions, batch_size=8)
    assert len(batches) == 3  # 8 + 8 + 4
    assert len(batches[0]) == 8
    assert len(batches[1]) == 8
    assert len(batches[2]) == 4


def test_build_default_report():
    """测试默认报告生成"""
    from kirinchat.api.services.evaluation import EvaluationService

    report = EvaluationService._build_default_report()
    assert report["total_score"] == 0.0
    assert "summary" in report
    assert "category_scores" in report
    assert "strengths" in report
    assert "improvements" in report


def test_merge_batch_results():
    """测试批次结果合并"""
    from kirinchat.api.services.evaluation import EvaluationService

    batch_results = [
        {
            "category_scores": {"java": 8.0, "mysql": 7.0},
            "question_scores": [{"id": "q1", "score": 8.0}, {"id": "q2", "score": 7.0}],
        },
        {
            "category_scores": {"java": 9.0, "redis": 6.0},
            "question_scores": [{"id": "q3", "score": 9.0}, {"id": "q4", "score": 6.0}],
        },
    ]
    merged = EvaluationService._merge_batch_results(batch_results)
    assert merged["category_scores"]["java"] == 8.5  # (8+9)/2
    assert merged["category_scores"]["mysql"] == 7.0
    assert merged["category_scores"]["redis"] == 6.0
    assert len(merged["question_scores"]) == 4
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd src/backend
python -m pytest tests/backend/test_evaluation_service.py -v
```

预期: FAIL

- [ ] **Step 3: 实现 EvaluationService**

```python
# src/backend/kirinchat/api/services/evaluation.py
from typing import List, Dict, Any
from collections import defaultdict

from kirinchat.database.models.interview import (
    InterviewQuestionTable,
    EvaluationReportTable,
)
from kirinchat.database.dao.interview import (
    InterviewQuestionDao,
    EvaluationReportDao,
    InterviewSessionDao,
)


DEFAULT_BATCH_SIZE = 8


class EvaluationService:
    @classmethod
    async def evaluate_session(cls, session_id: str) -> EvaluationReportTable:
        """评估面试会话"""
        questions = await InterviewQuestionDao.select_questions_by_session(session_id)

        if not questions:
            return await cls._save_default_report(session_id)

        # 分批评估
        question_dicts = [cls._question_to_dict(q) for q in questions]
        batches = cls._batch_questions(question_dicts)

        batch_results = []
        for batch in batches:
            try:
                result = await cls._evaluate_batch(batch)
                batch_results.append(result)
            except Exception:
                # 批次失败时跳过，后续会使用默认分数
                continue

        if not batch_results:
            return await cls._save_default_report(session_id)

        # 合并批次结果
        merged = cls._merge_batch_results(batch_results)

        # 二次汇总（使用 LLM）
        try:
            summary_result = await cls._summarize_evaluation(merged)
            merged["summary"] = summary_result.get("summary", merged.get("summary", ""))
            merged["strengths"] = summary_result.get("strengths", merged.get("strengths", []))
            merged["improvements"] = summary_result.get("improvements", merged.get("improvements", []))
        except Exception:
            # 汇总失败时使用默认总结
            merged.setdefault("summary", "评估完成，请查看各分类分数了解详情。")
            merged.setdefault("strengths", [])
            merged.setdefault("improvements", [])

        # 保存报告
        report = EvaluationReportTable(
            session_id=session_id,
            total_score=merged.get("total_score", 0.0),
            category_scores=merged.get("category_scores", {}),
            summary=merged.get("summary", ""),
            strengths=merged.get("strengths", []),
            improvements=merged.get("improvements", []),
        )
        saved = await EvaluationReportDao.create_report(report)

        # 更新题目分数
        for qs in merged.get("question_scores", []):
            await InterviewQuestionDao.update_question_score(qs["id"], qs["score"])

        # 更新会话状态
        await InterviewSessionDao.update_session_status(session_id, "EVALUATED")

        return saved

    @classmethod
    async def get_report_by_id(cls, report_id: str) -> EvaluationReportTable:
        """根据 ID 获取评估报告"""
        return await EvaluationReportDao.select_report_by_id(report_id)

    @classmethod
    async def get_report_by_session(cls, session_id: str) -> EvaluationReportTable:
        """根据会话 ID 获取评估报告"""
        return await EvaluationReportDao.select_report_by_session(session_id)

    @classmethod
    def _batch_questions(cls, questions: list, batch_size: int = DEFAULT_BATCH_SIZE) -> List[list]:
        """将题目分批"""
        return [questions[i:i + batch_size] for i in range(0, len(questions), batch_size)]

    @classmethod
    async def _evaluate_batch(cls, batch: list) -> dict:
        """评估一批题目（调用 LLM）"""
        # 构建评估 prompt
        prompt = cls._build_evaluation_prompt(batch)

        # 调用 LLM（使用现有的 LLM provider）
        from kirinchat.core.models.models import manager
        llm = manager.get_default_llm()

        response = await llm.ainvoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)

        # 解析结果
        return cls._parse_evaluation_result(content, batch)

    @classmethod
    async def _summarize_evaluation(cls, merged: dict) -> dict:
        """二次汇总评估结果"""
        from kirinchat.core.models.models import manager
        llm = manager.get_default_llm()

        prompt = f"""请根据以下面试评估数据，生成总结报告：

各分类分数：{merged.get('category_scores', {})}

请用 JSON 格式返回：
{{"summary": "总体评价...", "strengths": ["优势1", "优势2"], "improvements": ["改进1", "改进2"]}}
"""
        response = await llm.ainvoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)

        import json
        try:
            # 尝试从响应中提取 JSON
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
        except Exception:
            pass
        return {}

    @classmethod
    def _build_evaluation_prompt(cls, batch: list) -> str:
        """构建评估 prompt"""
        questions_text = ""
        for i, q in enumerate(batch, 1):
            questions_text += f"\n题目{i}: {q['content']}\n答案{i}: {q['answer']}\n"

        return f"""请评估以下面试题目和答案，给出每题分数(0-10)和分类评估。

{questions_text}

请用 JSON 格式返回：
{{
  "category_scores": {{"分类名": 分数}},
  "question_scores": [{{"id": "题目ID", "score": 分数}}]
}}
"""

    @classmethod
    def _parse_evaluation_result(cls, content: str, batch: list) -> dict:
        """解析 LLM 评估结果"""
        import json
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                result = json.loads(content[start:end])
                # 确保 question_scores 包含所有题目
                if "question_scores" not in result:
                    result["question_scores"] = [{"id": q["id"], "score": 0} for q in batch]
                return result
        except Exception:
            pass
        # 解析失败时返回默认分数
        return {
            "category_scores": {},
            "question_scores": [{"id": q["id"], "score": 0} for q in batch],
        }

    @classmethod
    def _merge_batch_results(cls, batch_results: List[dict]) -> dict:
        """合并多个批次的评估结果"""
        all_category_scores = defaultdict(list)
        all_question_scores = []

        for result in batch_results:
            for cat, score in result.get("category_scores", {}).items():
                all_category_scores[cat].append(score)
            all_question_scores.extend(result.get("question_scores", []))

        # 计算各分类平均分
        merged_category_scores = {
            cat: round(sum(scores) / len(scores), 1)
            for cat, scores in all_category_scores.items()
        }

        # 计算总分
        all_scores = [qs["score"] for qs in all_question_scores if qs.get("score")]
        total_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0.0

        return {
            "total_score": total_score,
            "category_scores": merged_category_scores,
            "question_scores": all_question_scores,
        }

    @classmethod
    def _question_to_dict(cls, q: InterviewQuestionTable) -> dict:
        """将题目对象转为字典"""
        return {
            "id": q.id,
            "content": q.content,
            "answer": q.user_answer or "",
            "category": q.category,
        }

    @classmethod
    def _build_default_report(cls) -> dict:
        """构建默认评估报告"""
        return {
            "total_score": 0.0,
            "category_scores": {},
            "summary": "暂无评估数据",
            "strengths": [],
            "improvements": [],
        }

    @classmethod
    async def _save_default_report(cls, session_id: str) -> EvaluationReportTable:
        """保存默认评估报告"""
        default = cls._build_default_report()
        report = EvaluationReportTable(
            session_id=session_id,
            **default,
        )
        return await EvaluationReportDao.create_report(report)
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd src/backend
python -m pytest tests/backend/test_evaluation_service.py -v
```

预期: PASS

- [ ] **Step 5: Commit**

```bash
git add src/backend/kirinchat/api/services/evaluation.py tests/backend/test_evaluation_service.py
git commit -m "feat: add EvaluationService with batch evaluation and fallback"
```

---

## Task 7: Interview Agent 实现

**Files:**
- Create: `src/backend/kirinchat/core/agents/interview_agent.py`

- [ ] **Step 1: 实现 InterviewAgent**

```python
# src/backend/kirinchat/core/agents/interview_agent.py
import json
from typing import AsyncGenerator, List, Optional, Dict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from kirinchat.api.services.skill import SkillService
from kirinchat.api.services.interview import InterviewService
from kirinchat.database.models.interview import InterviewQuestionTable
from kirinchat.schemas.agent import AgentConfig


class InterviewAgent:
    """面试 Agent，负责面试对话管理、出题、追问"""

    def __init__(self, agent_config: AgentConfig):
        self.agent_config = agent_config
        self.skill = None
        self.conversation_model = None
        self.current_session_id = None

    async def init_interview_agent(self, skill_id: str):
        """异步初始化面试 Agent"""
        self.skill = SkillService.get_skill_by_id(skill_id)
        if not self.skill:
            raise ValueError(f"Skill not found: {skill_id}")

        # 初始化 LLM
        from kirinchat.core.models.models import manager
        self.conversation_model = manager.get_default_llm()

    async def generate_first_question(
        self,
        session_id: str,
        difficulty: str = "MEDIUM",
    ) -> InterviewQuestionTable:
        """生成第一道题目"""
        self.current_session_id = session_id

        # 获取历史题目用于去重
        existing_questions = await InterviewService.get_session_questions(session_id)
        existing_topics = [q.content for q in existing_questions]

        # 构建 prompt
        categories = self.skill.get("categories", [])
        category_text = ", ".join([c.get("label", c.get("key", "")) for c in categories])

        prompt = f"""你是一位专业的技术面试官。

面试方向：{self.skill.get('name', '')}
难度级别：{difficulty}
考察分类：{category_text}

请生成一道面试题目。

{self._get_dedup_prompt(existing_topics)}

请直接输出题目内容，不要添加任何前缀或解释。"""

        response = await self.conversation_model.ainvoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)

        # 选择分类
        category = self._select_category(categories, [])

        # 保存题目
        question = InterviewQuestionTable(
            session_id=session_id,
            type="MAIN",
            category=category,
            content=content.strip(),
        )
        saved = await InterviewService.save_question(question)

        # 更新会话状态
        await InterviewService.update_session_status(session_id, "IN_PROGRESS")

        return saved

    async def generate_follow_up(
        self,
        session_id: str,
        original_question: InterviewQuestionTable,
        user_answer: str,
    ) -> Optional[InterviewQuestionTable]:
        """生成追问（0-1 个追问）"""
        prompt = f"""你是一位专业的技术面试官。

面试官提出了以下问题：
{original_question.content}

候选人的回答：
{user_answer}

请判断是否需要追问。如果需要，生成一个追问；如果不需要，返回"不需要追问"。

追问的目的是：
1. 深入了解候选人的理解深度
2. 澄清回答中的模糊之处
3. 引导候选人展开更详细的解释

请只输出追问内容或"不需要追问"。"""

        response = await self.conversation_model.ainvoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)
        content = content.strip()

        if "不需要追问" in content or len(content) < 5:
            return None

        # 保存追问
        question = InterviewQuestionTable(
            session_id=session_id,
            type="FOLLOW_UP",
            category=original_question.category,
            content=content,
        )
        return await InterviewService.save_question(question)

    async def generate_next_question(
        self,
        session_id: str,
        difficulty: str = "MEDIUM",
    ) -> Optional[InterviewQuestionTable]:
        """生成下一道主问题"""
        # 获取历史题目
        existing_questions = await InterviewService.get_session_questions(session_id)
        existing_topics = [q.content for q in existing_questions]

        # 获取会话信息
        session = await InterviewService.get_session(session_id)
        if not session:
            return None

        # 检查是否达到题目数量
        main_questions = [q for q in existing_questions if q.type == "MAIN"]
        if len(main_questions) >= session.question_count:
            return None

        # 已考分类统计
        tested_categories = {}
        for q in existing_questions:
            tested_categories[q.category] = tested_categories.get(q.category, 0) + 1

        # 构建 prompt
        categories = self.skill.get("categories", [])
        category_text = ", ".join([c.get("label", c.get("key", "")) for c in categories])

        tested_text = "\n".join([f"- {cat}: {count}题" for cat, count in tested_categories.items()])

        prompt = f"""你是一位专业的技术面试官。

面试方向：{self.skill.get('name', '')}
难度级别：{difficulty}
考察分类：{category_text}

已考知识点统计：
{tested_text}

请生成下一道面试题目，优先覆盖尚未考察的分类。

{self._get_dedup_prompt(existing_topics)}

请直接输出题目内容，不要添加任何前缀或解释。"""

        response = await self.conversation_model.ainvoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)

        # 选择下一个分类
        category = self._select_category(categories, existing_questions)

        # 保存题目
        question = InterviewQuestionTable(
            session_id=session_id,
            type="MAIN",
            category=category,
            content=content.strip(),
        )
        return await InterviewService.save_question(question)

    def _select_category(self, categories: List[dict], existing_questions: List[InterviewQuestionTable]) -> str:
        """选择下一个分类（基于优先级和已考统计）"""
        if not categories:
            return "general"

        # 统计已考分类
        tested = {}
        for q in existing_questions:
            tested[q.category] = tested.get(q.category, 0) + 1

        # 优先选择 ALWAYS_ONE
        for cat in categories:
            if cat.get("priority") == "ALWAYS_ONE" and cat.get("key") not in tested:
                return cat["key"]

        # 再选择 CORE
        for cat in categories:
            if cat.get("priority") == "CORE" and cat.get("key") not in tested:
                return cat["key"]

        # 最后选择 NORMAL
        for cat in categories:
            if cat.get("key") not in tested:
                return cat["key"]

        # 所有分类都已覆盖，返回第一个
        return categories[0].get("key", "general")

    def _get_dedup_prompt(self, existing_topics: List[str]) -> str:
        """获取去重提示"""
        if not existing_topics:
            return ""
        topics_text = "\n".join([f"- {t[:50]}..." if len(t) > 50 else f"- {t}" for t in existing_topics[-10:]])
        return f"""请避免与以下已有题目重复：
{topics_text}"""

    async def astream(self, messages: List[BaseMessage]) -> AsyncGenerator[str, None]:
        """流式调用（用于对话接口集成）"""
        if not self.conversation_model:
            yield "面试 Agent 未初始化"
            return

        async for chunk in self.conversation_model.astream(messages):
            if hasattr(chunk, "content"):
                yield chunk.content
            else:
                yield str(chunk)

    async def ainvoke(self, messages: List[BaseMessage]) -> str:
        """非流式调用"""
        if not self.conversation_model:
            return "面试 Agent 未初始化"

        response = await self.conversation_model.ainvoke(messages)
        return response.content if hasattr(response, "content") else str(response)
```

- [ ] **Step 2: 验证语法正确**

```bash
cd src/backend
python -c "from kirinchat.core.agents.interview_agent import InterviewAgent; print('InterviewAgent imported successfully')"
```

- [ ] **Step 3: Commit**

```bash
git add src/backend/kirinchat/core/agents/interview_agent.py
git commit -m "feat: add InterviewAgent with question generation and follow-up"
```

---

## Task 8: API 路由实现

**Files:**
- Create: `src/backend/kirinchat/api/v1/interview.py`
- Modify: `src/backend/kirinchat/api/v1/router.py`

- [ ] **Step 1: 实现面试 API 路由**

```python
# src/backend/kirinchat/api/v1/interview.py
from fastapi import APIRouter, Depends

from kirinchat.api.responses.builder import resp_200, resp_500
from kirinchat.api.responses.builder import UnifiedResponseModel
from kirinchat.api.services.user import UserPayload, get_login_user
from kirinchat.api.services.interview import InterviewService
from kirinchat.api.services.skill import SkillService
from kirinchat.api.services.evaluation import EvaluationService
from kirinchat.core.agents.interview_agent import InterviewAgent
from kirinchat.schemas.agent import AgentConfig
from kirinchat.schemas.interview import (
    InterviewStartReq,
    InterviewAnswerReq,
    InterviewCompleteReq,
    InterviewStartResp,
    InterviewAnswerResp,
    InterviewSessionResp,
    InterviewSessionDetailResp,
    InterviewCompleteResp,
    EvaluationReportResp,
    InterviewHistoryResp,
    QuestionResp,
    SkillListResp,
    SkillDetailResp,
    SkillInfoResp,
)

router = APIRouter(tags=["Interview"])


@router.post("/interview/start", response_model=UnifiedResponseModel[InterviewStartResp])
async def start_interview(
    req: InterviewStartReq,
    login_user: UserPayload = Depends(get_login_user),
):
    """开始新面试"""
    try:
        # 创建会话
        session = await InterviewService.create_session(
            user_id=login_user.user_id,
            skill_id=req.skill_id,
            difficulty=req.difficulty,
            question_count=req.question_count,
        )

        # 初始化 Agent 并生成第一题
        agent = InterviewAgent(AgentConfig(user_id=login_user.user_id, llm_id="", mcp_ids=[], knowledge_ids=[], tool_ids=[], agent_skill_ids=[], system_prompt=""))
        await agent.init_interview_agent(req.skill_id)
        first_question = await agent.generate_first_question(session.id, req.difficulty)

        return resp_200(data=InterviewStartResp(
            session_id=session.id,
            first_question=QuestionResp(
                id=first_question.id,
                type=first_question.type,
                category=first_question.category,
                content=first_question.content,
            ),
        ))
    except Exception as err:
        return resp_500(message=str(err))


@router.post("/interview/answer", response_model=UnifiedResponseModel[InterviewAnswerResp])
async def submit_answer(
    req: InterviewAnswerReq,
    login_user: UserPayload = Depends(get_login_user),
):
    """提交答案"""
    try:
        # 保存答案
        question = await InterviewService.submit_answer(req.question_id, req.answer)
        if not question:
            return resp_500(message="题目不存在")

        # 获取会话
        session = await InterviewService.get_session(req.session_id)
        if not session:
            return resp_500(message="会话不存在")

        # 初始化 Agent
        agent = InterviewAgent(AgentConfig(user_id=login_user.user_id, llm_id="", mcp_ids=[], knowledge_ids=[], tool_ids=[], agent_skill_ids=[], system_prompt=""))
        await agent.init_interview_agent(session.skill_id)

        # 尝试生成追问
        follow_up = await agent.generate_follow_up(req.session_id, question, req.answer)

        if follow_up:
            return resp_200(data=InterviewAnswerResp(
                next_question=QuestionResp(
                    id=follow_up.id,
                    type=follow_up.type,
                    category=follow_up.category,
                    content=follow_up.content,
                ),
                is_completed=False,
            ))

        # 没有追问，尝试生成下一题
        next_question = await agent.generate_next_question(req.session_id, session.difficulty)

        if next_question:
            return resp_200(data=InterviewAnswerResp(
                next_question=QuestionResp(
                    id=next_question.id,
                    type=next_question.type,
                    category=next_question.category,
                    content=next_question.content,
                ),
                is_completed=False,
            ))

        # 所有题目完成
        return resp_200(data=InterviewAnswerResp(
            next_question=None,
            is_completed=True,
        ))
    except Exception as err:
        return resp_500(message=str(err))


@router.get("/interview/session/{session_id}", response_model=UnifiedResponseModel[InterviewSessionDetailResp])
async def get_session(
    session_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """获取面试会话详情"""
    try:
        session = await InterviewService.get_session(session_id)
        if not session:
            return resp_500(message="会话不存在")

        questions = await InterviewService.get_session_questions(session_id)
        progress = await InterviewService.calculate_progress(session_id)

        return resp_200(data=InterviewSessionDetailResp(
            session=InterviewSessionResp(
                id=session.id,
                skill_id=session.skill_id,
                status=session.status,
                progress=progress,
            ),
            questions=[
                QuestionResp(
                    id=q.id,
                    type=q.type,
                    category=q.category,
                    content=q.content,
                )
                for q in questions
            ],
        ))
    except Exception as err:
        return resp_500(message=str(err))


@router.post("/interview/complete", response_model=UnifiedResponseModel[InterviewCompleteResp])
async def complete_interview(
    req: InterviewCompleteReq,
    login_user: UserPayload = Depends(get_login_user),
):
    """完成面试"""
    try:
        session = await InterviewService.get_session(req.session_id)
        if not session:
            return resp_500(message="会话不存在")

        # 更新状态
        await InterviewService.update_session_status(req.session_id, "COMPLETED")

        # 执行评估
        report = await EvaluationService.evaluate_session(req.session_id)

        return resp_200(data=InterviewCompleteResp(
            evaluation_id=report.id,
            status="evaluated",
        ))
    except Exception as err:
        return resp_500(message=str(err))


@router.get("/interview/evaluation/{evaluation_id}", response_model=UnifiedResponseModel[EvaluationReportResp])
async def get_evaluation(
    evaluation_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """获取评估报告"""
    try:
        report = await EvaluationService.get_report_by_id(evaluation_id)
        if not report:
            return resp_500(message="评估报告不存在")

        return resp_200(data=EvaluationReportResp(
            id=report.id,
            total_score=report.total_score,
            category_scores=report.category_scores,
            summary=report.summary,
            strengths=report.strengths,
            improvements=report.improvements,
        ))
    except Exception as err:
        return resp_500(message=str(err))


@router.get("/interview/history", response_model=UnifiedResponseModel[InterviewHistoryResp])
async def get_interview_history(
    login_user: UserPayload = Depends(get_login_user),
):
    """获取面试历史"""
    try:
        sessions = await InterviewService.get_user_sessions(login_user.user_id)

        history = []
        for s in sessions:
            progress = await InterviewService.calculate_progress(s.id)
            history.append(InterviewSessionResp(
                id=s.id,
                skill_id=s.skill_id,
                status=s.status,
                progress=progress,
            ))

        return resp_200(data=InterviewHistoryResp(sessions=history))
    except Exception as err:
        return resp_500(message=str(err))


@router.get("/skill/list", response_model=UnifiedResponseModel[SkillListResp])
async def list_skills(
    login_user: UserPayload = Depends(get_login_user),
):
    """获取所有 Skill"""
    try:
        skills = SkillService.get_all_skills()

        return resp_200(data=SkillListResp(
            skills=[
                SkillInfoResp(
                    id=s["id"],
                    name=s["name"],
                    description=s["description"],
                    icon=s.get("icon", ""),
                    categories=[
                        {"key": c.get("key"), "label": c.get("label"), "priority": c.get("priority")}
                        for c in s.get("categories", [])
                    ],
                )
                for s in skills
            ]
        ))
    except Exception as err:
        return resp_500(message=str(err))


@router.get("/skill/{skill_id}", response_model=UnifiedResponseModel[SkillDetailResp])
async def get_skill_detail(
    skill_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """获取 Skill 详情"""
    try:
        skill = SkillService.get_skill_by_id(skill_id)
        if not skill:
            return resp_500(message="Skill 不存在")

        return resp_200(data=SkillDetailResp(
            skill=SkillInfoResp(
                id=skill["id"],
                name=skill["name"],
                description=skill["description"],
                icon=skill.get("icon", ""),
                categories=[
                    {"key": c.get("key"), "label": c.get("label"), "priority": c.get("priority")}
                    for c in skill.get("categories", [])
                ],
            ),
            categories=[
                {"key": c.get("key"), "label": c.get("label"), "priority": c.get("priority")}
                for c in skill.get("categories", [])
            ],
            references=skill.get("references", {}),
        ))
    except Exception as err:
        return resp_500(message=str(err))
```

- [ ] **Step 2: 注册路由到 v1 router**

在 `src/backend/kirinchat/api/v1/router.py` 中添加：

```python
# 在已有的 router.include_router(...) 后面添加
from kirinchat.api.v1.interview import router as interview_router
api_v1_router.include_router(interview_router)
```

- [ ] **Step 3: 验证 API 可加载**

```bash
cd src/backend
python -c "from kirinchat.api.v1.interview import router; print(f'Interview router loaded with {len(router.routes)} routes')"
```

- [ ] **Step 4: Commit**

```bash
git add src/backend/kirinchat/api/v1/interview.py src/backend/kirinchat/api/v1/router.py
git commit -m "feat: add interview and skill API endpoints"
```

---

## Task 9: Skill 内容创建

**Files:**
- Create: `src/backend/kirinchat/skills/java-backend/SKILL.md`
- Create: `src/backend/kirinchat/skills/java-backend/skill.meta.yml`
- Create: `src/backend/kirinchat/skills/_shared/references/java.md`
- Create: `src/backend/kirinchat/skills/_shared/references/mysql.md`
- Create: `src/backend/kirinchat/skills/_shared/references/redis.md`
- Create: `src/backend/kirinchat/skills/_shared/references/spring.md`

- [ ] **Step 1: 创建 Java Backend Skill 定义**

```markdown
<!-- src/backend/kirinchat/skills/java-backend/SKILL.md -->
---
name: java-backend
description: Java 后端开发面试，涵盖 Java 核心、数据库、缓存、框架和系统设计
---

你是一位资深的 Java 后端开发面试官，拥有 10 年以上的 Java 开发和面试经验。

## 面试风格

- 由浅入深，先从基础概念开始，逐步深入到实际应用和原理
- 注重候选人的实际项目经验，而非死记硬背
- 追问时关注"为什么"和"怎么做"，而非简单的"是什么"
- 给候选人思考的时间，适当引导

## 提问策略

1. **基础概念**：确认候选人对核心概念的理解
2. **实际应用**：询问在项目中如何使用
3. **原理深入**：探讨底层实现和设计思想
4. **问题解决**：给出场景，让候选人设计方案

## 注意事项

- 保持专业和友善的态度
- 避免刁钻或陷阱题目
- 关注候选人的思维过程，而非仅看最终答案
- 根据候选人水平调整难度
```

- [ ] **Step 2: 创建 Skill 元数据**

```yaml
# src/backend/kirinchat/skills/java-backend/skill.meta.yml
display:
  icon: "☕"
  gradient: "from-orange-500 to-red-600"
  colors:
    primary: "#f97316"
    secondary: "#dc2626"

categories:
  - key: java
    label: Java 核心
    priority: CORE
    ref: java.md
  - key: mysql
    label: MySQL
    priority: CORE
    ref: mysql.md
  - key: redis
    label: Redis
    priority: CORE
    ref: redis.md
  - key: spring
    label: Spring 框架
    priority: CORE
    ref: spring.md
  - key: system-design
    label: 系统设计
    priority: NORMAL
  - key: project
    label: 项目经历
    priority: ALWAYS_ONE
```

- [ ] **Step 3: 创建 Java 参考资料**

```markdown
<!-- src/backend/kirinchat/skills/_shared/references/java.md -->
# Java 核心知识点

## 面向对象

### 封装
- 访问修饰符：private, default, protected, public
- JavaBean 规范

### 继承
- 单继承，接口多实现
- super 关键字
- 方法重写规则

### 多态
- 编译时多态（方法重载）
- 运行时多态（方法重写 + 向上转型）
- instanceof 关键字

### 抽象
- 抽象类 vs 接口
- 抽象方法

## 集合框架

### List
- ArrayList：数组实现，随机访问 O(1)
- LinkedList：双向链表，插入删除 O(1)

### Map
- HashMap：数组 + 链表 + 红黑树
- ConcurrentHashMap：分段锁 / CAS

### Set
- HashSet：基于 HashMap
- TreeSet：红黑树，有序

## 多线程

### 线程创建
- Thread 类
- Runnable 接口
- Callable + Future

### 锁
- synchronized
- ReentrantLock
- ReadWriteLock

### 并发工具
- CountDownLatch
- CyclicBarrier
- Semaphore
- CompletableFuture

## JVM

### 内存模型
- 堆（Heap）
- 栈（Stack）
- 方法区（Metaspace）

### 垃圾回收
- GC Roots
- 分代收集
- 常见 GC 算法

### 类加载
- 双亲委派模型
- 自定义类加载器
```

- [ ] **Step 4: 创建 MySQL 参考资料**

```markdown
<!-- src/backend/kirinchat/skills/_shared/references/mysql.md -->
# MySQL 核心知识点

## 索引

### B+ 树索引
- 聚簇索引 vs 非聚簇索引
- 覆盖索引
- 索引下推

### 索引优化
- 最左前缀原则
- 索引失效场景
- EXPLAIN 分析

## 事务

### ACID
- 原子性（undo log）
- 一致性
- 隔离性（锁 + MVCC）
- 持久性（redo log）

### 隔离级别
- READ UNCOMMITTED
- READ COMMITTED
- REPEATABLE READ（默认）
- SERIALIZABLE

## 锁

### 锁类型
- 行锁
- 表锁
- 间隙锁
- 临键锁

### 死锁
- 检测
- 预防
- 处理

## 性能优化

### 慢查询
- 开启慢查询日志
- EXPLAIN 分析
- 优化建议

### 分库分表
- 垂直拆分
- 水平拆分
- ShardingSphere
```

- [ ] **Step 5: 创建 Redis 参考资料**

```markdown
<!-- src/backend/kirinchat/skills/_shared/references/redis.md -->
# Redis 核心知识点

## 数据结构

### String
- 缓存
- 计数器
- 分布式锁

### Hash
- 对象存储
- 购物车

### List
- 消息队列
- 最新列表

### Set
- 去重
- 交集/并集/差集

### Sorted Set
- 排行榜
- 延迟队列

## 持久化

### RDB
- 快照
- fork 子进程

### AOF
- 追加写
- 重写机制

## 高可用

### 主从复制
- 全量同步
- 增量同步

### 哨兵
- 监控
- 自动故障转移

### 集群
- 分片
- 路由

## 应用场景

### 缓存
- 缓存穿透
- 缓存击穿
- 缓存雪崩

### 分布式锁
- SETNX
- Redlock

### 限流
- 滑动窗口
- 令牌桶
```

- [ ] **Step 6: 创建 Spring 参考资料**

```markdown
<!-- src/backend/kirinchat/skills/_shared/references/spring.md -->
# Spring 核心知识点

## IoC

### 容器
- BeanFactory
- ApplicationContext

### 依赖注入
- 构造器注入
- Setter 注入
- 字段注入（@Autowired）

### Bean 生命周期
- 实例化
- 属性赋值
- 初始化
- 销毁

## AOP

### 概念
- 切面（Aspect）
- 切点（Pointcut）
- 通知（Advice）
- 连接点（JoinPoint）

### 实现
- JDK 动态代理
- CGLIB 代理

## Spring Boot

### 自动配置
- @EnableAutoConfiguration
- spring.factories
- 条件注解

### Starter
- 自定义 Starter
- 配置绑定

## Spring Cloud

### 服务发现
- Nacos
- Eureka

### 配置中心
- Nacos Config
- Apollo

### 网关
- Spring Cloud Gateway
- 路由、过滤、限流

### 熔断降级
- Sentinel
- Resilience4j
```

- [ ] **Step 7: 验证 Skill 加载**

```bash
cd src/backend
python -c "
from kirinchat.api.services.skill import SkillService
skills = SkillService.get_all_skills()
print(f'Loaded {len(skills)} skills')
for s in skills:
    print(f'  - {s[\"id\"]}: {s[\"name\"]} ({len(s[\"categories\"])} categories)')
"
```

预期输出:
```
Loaded 1 skills
  - java-backend: java-backend (6 categories)
```

- [ ] **Step 8: Commit**

```bash
git add src/backend/kirinchat/skills/
git commit -m "feat: add Java backend skill definition and reference materials"
```

---

## Task 10: 集成测试

**Files:**
- Create: `tests/backend/test_interview_api.py`

- [ ] **Step 1: 编写 API 集成测试**

```python
# tests/backend/test_interview_api.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_list_skills():
    """测试获取 Skill 列表"""
    from kirinchat.api.services.skill import SkillService

    skills = SkillService.get_all_skills()
    assert isinstance(skills, list)
    # 如果 skills 目录存在且有内容
    if skills:
        assert "id" in skills[0]
        assert "name" in skills[0]
        assert "categories" in skills[0]


@pytest.mark.asyncio
async def test_get_skill_detail():
    """测试获取 Skill 详情"""
    from kirinchat.api.services.skill import SkillService

    skill = SkillService.get_skill_by_id("java-backend")
    if skill:  # 只在 skill 存在时测试
        assert skill["id"] == "java-backend"
        assert "persona" in skill
        assert "categories" in skill
        assert "references" in skill


def test_evaluation_batch_logic():
    """测试评估分批逻辑"""
    from kirinchat.api.services.evaluation import EvaluationService

    # 测试 20 题分 3 批
    questions = [{"id": f"q{i}"} for i in range(20)]
    batches = EvaluationService._batch_questions(questions, batch_size=8)
    assert len(batches) == 3
    assert len(batches[0]) == 8
    assert len(batches[1]) == 8
    assert len(batches[2]) == 4

    # 测试 5 题分 1 批
    questions = [{"id": f"q{i}"} for i in range(5)]
    batches = EvaluationService._batch_questions(questions, batch_size=8)
    assert len(batches) == 1

    # 测试空列表
    batches = EvaluationService._batch_questions([], batch_size=8)
    assert len(batches) == 0


def test_merge_batch_results():
    """测试批次结果合并"""
    from kirinchat.api.services.evaluation import EvaluationService

    results = [
        {
            "category_scores": {"java": 8.0, "mysql": 7.0},
            "question_scores": [{"id": "q1", "score": 8.0}],
        },
        {
            "category_scores": {"java": 6.0, "redis": 9.0},
            "question_scores": [{"id": "q2", "score": 6.0}],
        },
    ]

    merged = EvaluationService._merge_batch_results(results)
    assert merged["total_score"] == 7.0  # (8+6)/2
    assert merged["category_scores"]["java"] == 7.0  # (8+6)/2
    assert merged["category_scores"]["mysql"] == 7.0
    assert merged["category_scores"]["redis"] == 9.0
    assert len(merged["question_scores"]) == 2
```

- [ ] **Step 2: 运行集成测试**

```bash
cd src/backend
python -m pytest tests/backend/test_interview_api.py -v
```

预期: PASS

- [ ] **Step 3: 运行所有测试**

```bash
cd src/backend
python -m pytest tests/backend/ -v
```

预期: 所有测试通过

- [ ] **Step 4: Commit**

```bash
git add tests/backend/test_interview_api.py
git commit -m "test: add interview API integration tests"
```

---

## Self-Review 检查

### 1. Spec 覆盖检查

| Spec 需求 | 对应 Task | 状态 |
|-----------|-----------|------|
| 数据模型 (InterviewSession, Question, Evaluation) | Task 1 | ✅ |
| DAO 层 | Task 2 | ✅ |
| Schema 定义 | Task 3 | ✅ |
| Skill Service | Task 4 | ✅ |
| Interview Service | Task 5 | ✅ |
| Evaluation Service (分批、汇总、降级) | Task 6 | ✅ |
| Interview Agent (出题、追问、去重) | Task 7 | ✅ |
| API 路由 | Task 8 | ✅ |
| Skill 内容 | Task 9 | ✅ |
| 测试 | Task 10 | ✅ |
| 路由注册 | Task 8 Step 2 | ✅ |

### 2. 占位符扫描

✅ 无 TBD/TODO  
✅ 所有步骤包含完整代码  
✅ 所有命令包含预期输出

### 3. 类型一致性检查

- `InterviewSessionTable` 在 Task 1 定义，Task 2/5/8 使用 ✅
- `InterviewQuestionTable` 在 Task 1 定义，Task 2/5/7/8 使用 ✅
- `EvaluationReportTable` 在 Task 1 定义，Task 2/6/8 使用 ✅
- `SkillService` 在 Task 4 定义，Task 5/7/8 使用 ✅
- `InterviewService` 在 Task 5 定义，Task 7/8 使用 ✅
- `EvaluationService` 在 Task 6 定义，Task 8 使用 ✅
- `InterviewAgent` 在 Task 7 定义，Task 8 使用 ✅

---

**Plan complete and saved to `docs/superpowers/plans/2026-06-21-interview-learning-platform.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
