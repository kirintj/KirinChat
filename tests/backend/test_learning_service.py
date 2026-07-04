import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Mock the database layer
# ---------------------------------------------------------------------------

_mock_interview_session_dao = MagicMock()
_mock_interview_question_dao = MagicMock()
_mock_evaluation_report_dao = MagicMock()
_mock_interview_models = MagicMock()

# Only mock leaf submodules, NOT parent packages (kirinchat.database,
# kirinchat.database.dao).  The conftest pre-imports those with a working
# SQLite engine, so they are real packages with __path__.
_MOCK_KEYS = [
    "kirinchat.database.models.interview",
    "kirinchat.database.dao.interview",
]
_saved_modules = {k: sys.modules.get(k) for k in _MOCK_KEYS}

sys.modules["kirinchat.database.models.interview"] = _mock_interview_models
sys.modules["kirinchat.database.dao.interview"] = MagicMock(
    InterviewSessionDao=_mock_interview_session_dao,
    InterviewQuestionDao=_mock_interview_question_dao,
    EvaluationReportDao=_mock_evaluation_report_dao,
)

# Force re-import
if "kirinchat.api.services.learning" in sys.modules:
    del sys.modules["kirinchat.api.services.learning"]

from kirinchat.api.services.learning import LearningService  # noqa: E402

# Restore original sys.modules entries to prevent contamination of other tests.
for _k, _v in _saved_modules.items():
    if _v is None:
        sys.modules.pop(_k, None)
    else:
        sys.modules[_k] = _v


@pytest.fixture(autouse=True)
def _reset_mocks():
    _mock_interview_session_dao.reset_mock()
    _mock_evaluation_report_dao.reset_mock()
    _mock_interview_session_dao.select_sessions_by_user = AsyncMock()
    _mock_evaluation_report_dao.select_report_by_session = AsyncMock()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_empty_history_returns_empty():
    """空面试历史返回空列表"""
    _mock_interview_session_dao.select_sessions_by_user = AsyncMock(return_value=[])

    result = await LearningService.get_user_weak_categories("user1", "java-backend")
    assert result == []


@pytest.mark.asyncio
async def test_weak_categories_aggregation():
    """多次面试的分数聚合正确"""
    # Create mock sessions
    s1 = MagicMock()
    s1.id = "sess-1"
    s1.status = "COMPLETED"
    s1.skill_id = "java-backend"
    s2 = MagicMock()
    s2.id = "sess-2"
    s2.status = "COMPLETED"
    s2.skill_id = "java-backend"

    _mock_interview_session_dao.select_sessions_by_user = AsyncMock(return_value=[s1, s2])

    # Mock reports
    r1 = MagicMock()
    r1.category_scores = {"java": 8.0, "mysql": 4.0}
    r2 = MagicMock()
    r2.category_scores = {"java": 6.0, "mysql": 6.0}

    _mock_evaluation_report_dao.select_report_by_session = AsyncMock(side_effect=[r1, r2])

    with patch("kirinchat.api.services.learning.SkillService.get_skill_by_id", return_value={
        "id": "java-backend",
        "categories": [
            {"key": "java", "label": "Java 核心"},
            {"key": "mysql", "label": "MySQL"},
        ],
    }):
        result = await LearningService.get_user_weak_categories("user1", "java-backend")

    assert len(result) == 2
    # mysql avg = 5.0, java avg = 7.0 → mysql first
    assert result[0]["category"] == "mysql"
    assert result[0]["avg_score"] == 5.0
    assert result[0]["session_count"] == 2
    assert result[1]["category"] == "java"
    assert result[1]["avg_score"] == 7.0


@pytest.mark.asyncio
async def test_study_order_sorted_by_score():
    """study_order 按分数从低到高排序"""
    s1 = MagicMock()
    s1.id = "sess-1"
    s1.status = "COMPLETED"
    s1.skill_id = "java-backend"

    _mock_interview_session_dao.select_sessions_by_user = AsyncMock(return_value=[s1])

    r1 = MagicMock()
    r1.category_scores = {"java": 9.0, "mysql": 3.0, "redis": 6.0}
    _mock_evaluation_report_dao.select_report_by_session = AsyncMock(return_value=r1)

    with patch("kirinchat.api.services.learning.SkillService.get_skill_by_id", return_value={
        "id": "java-backend",
        "categories": [
            {"key": "java", "label": "Java"},
            {"key": "mysql", "label": "MySQL"},
            {"key": "redis", "label": "Redis"},
        ],
        "references": {},
    }):
        path = await LearningService.get_learning_path("user1", "java-backend")

    assert path is not None
    assert path["study_order"] == ["mysql", "redis", "java"]
    assert path["total_sessions"] == 1
    assert path["overall_avg_score"] == 6.0  # (3+6+9)/3


@pytest.mark.asyncio
async def test_learning_path_with_resources():
    """参考资料正确匹配"""
    s1 = MagicMock()
    s1.id = "sess-1"
    s1.status = "COMPLETED"
    s1.skill_id = "java-backend"

    _mock_interview_session_dao.select_sessions_by_user = AsyncMock(return_value=[s1])

    r1 = MagicMock()
    r1.category_scores = {"mysql": 4.0}
    _mock_evaluation_report_dao.select_report_by_session = AsyncMock(return_value=r1)

    with patch("kirinchat.api.services.learning.SkillService.get_skill_by_id", return_value={
        "id": "java-backend",
        "name": "Java 后端",
        "categories": [
            {"key": "mysql", "label": "MySQL", "ref": "mysql.md"},
        ],
        "references": {"mysql": "# MySQL 核心知识点"},
    }):
        path = await LearningService.get_learning_path("user1", "java-backend")

    assert path is not None
    assert "mysql" in path["resources"]
    assert path["resources"]["mysql"]["reference"] == "# MySQL 核心知识点"


@pytest.mark.asyncio
async def test_learning_path_skill_not_found():
    """skill 不存在返回 None"""
    with patch("kirinchat.api.services.learning.SkillService.get_skill_by_id", return_value=None):
        result = await LearningService.get_learning_path("user1", "nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_overall_level_calculation():
    """整体水平计算正确"""
    s1 = MagicMock()
    s1.id = "sess-1"
    s1.status = "COMPLETED"
    s1.skill_id = "java-backend"

    # get_learning_path calls select_sessions_by_user twice:
    # once via get_user_weak_categories, once for total_sessions
    _mock_interview_session_dao.select_sessions_by_user = AsyncMock(return_value=[s1, s1])

    r1 = MagicMock()
    r1.category_scores = {"java": 9.0, "mysql": 9.0}
    _mock_evaluation_report_dao.select_report_by_session = AsyncMock(return_value=r1)

    with patch("kirinchat.api.services.learning.SkillService.get_skill_by_id", return_value={
        "id": "java-backend",
        "categories": [
            {"key": "java", "label": "Java"},
            {"key": "mysql", "label": "MySQL"},
        ],
        "references": {},
    }):
        path = await LearningService.get_learning_path("user1", "java-backend")

    assert path["overall_level"] == "excellent"
    assert path["overall_level_label"] == "优秀"
