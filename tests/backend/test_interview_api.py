# tests/backend/test_interview_api.py
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock

# ---------------------------------------------------------------------------
# Mock the database layer so that importing EvaluationService (which pulls in
# InterviewService -> database DAOs/models) never triggers a real DB connection.
# ---------------------------------------------------------------------------

_mock_interview_session_dao = MagicMock()
_mock_interview_question_dao = MagicMock()
_mock_evaluation_report_dao = MagicMock()
_mock_interview_models = MagicMock()

# Inject fake modules into sys.modules before the service is imported.
# NOTE: We forcefully replace (no "if not in" guard) to avoid contamination
# from other test files that may have injected their own mocks first.
sys.modules["kirinchat.database"] = MagicMock()
sys.modules["kirinchat.database.session"] = MagicMock()
sys.modules["kirinchat.database.models"] = MagicMock()
sys.modules["kirinchat.database.models.interview"] = _mock_interview_models
sys.modules["kirinchat.database.dao"] = MagicMock()
sys.modules["kirinchat.database.dao.interview"] = MagicMock(
    InterviewSessionDao=_mock_interview_session_dao,
    InterviewQuestionDao=_mock_interview_question_dao,
    EvaluationReportDao=_mock_evaluation_report_dao,
)

from kirinchat.api.services.evaluation import EvaluationService  # noqa: E402


# ---------------------------------------------------------------------------
# Skill service tests (no DB dependency -- direct filesystem access)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Evaluation service tests (uses mocked database layer above)
# ---------------------------------------------------------------------------


def test_evaluation_batch_logic():
    """测试评估分批逻辑"""
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
