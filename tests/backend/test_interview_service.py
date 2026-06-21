import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Mock the database layer so that importing the service never triggers a real
# database connection (pymysql / aiomysql are not available in test env).
# ---------------------------------------------------------------------------

_mock_interview_session_dao = MagicMock()
_mock_interview_question_dao = MagicMock()
_mock_interview_models = MagicMock()

# Inject fake modules into sys.modules before the service is imported.
if "kirinchat.database" not in sys.modules:
    sys.modules["kirinchat.database"] = MagicMock()
if "kirinchat.database.session" not in sys.modules:
    sys.modules["kirinchat.database.session"] = MagicMock()
if "kirinchat.database.models" not in sys.modules:
    sys.modules["kirinchat.database.models"] = MagicMock()
if "kirinchat.database.models.interview" not in sys.modules:
    sys.modules["kirinchat.database.models.interview"] = _mock_interview_models
if "kirinchat.database.dao" not in sys.modules:
    sys.modules["kirinchat.database.dao"] = MagicMock()
if "kirinchat.database.dao.interview" not in sys.modules:
    sys.modules["kirinchat.database.dao.interview"] = MagicMock(
        InterviewSessionDao=_mock_interview_session_dao,
        InterviewQuestionDao=_mock_interview_question_dao,
    )

# Now it's safe to import the service -- it will grab our mocked DAOs.
from kirinchat.api.services.interview import InterviewService  # noqa: E402


@pytest.mark.asyncio
async def test_create_session():
    """测试创建面试会话"""
    mock_session = MagicMock()
    mock_session.id = "test-session-id"
    mock_session.skill_id = "java-backend"
    mock_session.status = "CREATED"

    _mock_interview_session_dao.create_session = AsyncMock(return_value=mock_session)
    with patch("kirinchat.api.services.interview.SkillService.get_skill_by_id", return_value={"id": "java-backend", "persona": "面试官", "categories": []}):
        session = await InterviewService.create_session(
            user_id="user1",
            skill_id="java-backend",
            difficulty="MEDIUM",
            question_count=10,
        )
        assert session.id == "test-session-id"
        assert session.skill_id == "java-backend"


@pytest.mark.asyncio
async def test_create_session_invalid_skill():
    """测试创建面试会话时 skill 不存在"""
    with patch("kirinchat.api.services.interview.SkillService.get_skill_by_id", return_value=None):
        with pytest.raises(ValueError, match="Skill not found"):
            await InterviewService.create_session(
                user_id="user1",
                skill_id="nonexistent",
                difficulty="MEDIUM",
                question_count=10,
            )


@pytest.mark.asyncio
async def test_get_session():
    """测试获取面试会话"""
    mock_session = MagicMock()
    mock_session.id = "session-1"
    mock_session.skill_id = "java-backend"
    mock_session.status = "IN_PROGRESS"

    _mock_interview_session_dao.select_session_by_id = AsyncMock(return_value=mock_session)
    result = await InterviewService.get_session("session-1")
    assert result is not None
    assert result.id == "session-1"


@pytest.mark.asyncio
async def test_get_session_questions():
    """测试获取会话的所有题目"""
    mock_q1 = MagicMock()
    mock_q1.id = "q1"
    mock_q1.content = "什么是多态?"
    mock_q2 = MagicMock()
    mock_q2.id = "q2"
    mock_q2.content = "解释 SOLID 原则"

    _mock_interview_question_dao.select_questions_by_session = AsyncMock(return_value=[mock_q1, mock_q2])
    questions = await InterviewService.get_session_questions("session-1")
    assert len(questions) == 2
    assert questions[0].id == "q1"
    assert questions[1].id == "q2"


@pytest.mark.asyncio
async def test_save_question():
    """测试保存面试题目"""
    mock_question = MagicMock()
    mock_question.id = "new-q1"
    mock_question.session_id = "session-1"
    mock_question.content = "什么是多态?"

    _mock_interview_question_dao.create_question = AsyncMock(return_value=mock_question)
    result = await InterviewService.save_question(mock_question)
    assert result.id == "new-q1"
    assert result.session_id == "session-1"


@pytest.mark.asyncio
async def test_submit_answer():
    """测试提交答案"""
    mock_question = MagicMock()
    mock_question.id = "q1"
    mock_question.user_answer = None

    _mock_interview_question_dao.update_question_answer = AsyncMock(return_value=mock_question)
    result = await InterviewService.submit_answer("q1", "这是我的答案")
    assert result is not None


@pytest.mark.asyncio
async def test_update_session_status():
    """测试更新会话状态"""
    _mock_interview_session_dao.update_session_status = AsyncMock()
    await InterviewService.update_session_status("session-1", "COMPLETED")
    _mock_interview_session_dao.update_session_status.assert_called_once_with("session-1", "COMPLETED")


@pytest.mark.asyncio
async def test_get_user_sessions():
    """测试获取用户的所有面试会话"""
    mock_s1 = MagicMock()
    mock_s1.id = "session-1"
    mock_s1.user_id = "user1"
    mock_s2 = MagicMock()
    mock_s2.id = "session-2"
    mock_s2.user_id = "user1"

    _mock_interview_session_dao.select_sessions_by_user = AsyncMock(return_value=[mock_s1, mock_s2])
    sessions = await InterviewService.get_user_sessions("user1")
    assert len(sessions) == 2
    assert sessions[0].id == "session-1"
    assert sessions[1].id == "session-2"


@pytest.mark.asyncio
async def test_calculate_progress():
    """测试计算面试进度"""
    mock_q1 = MagicMock()
    mock_q1.user_answer = "答案1"
    mock_q2 = MagicMock()
    mock_q2.user_answer = None
    mock_q3 = MagicMock()
    mock_q3.user_answer = "答案3"

    _mock_interview_question_dao.select_questions_by_session = AsyncMock(return_value=[mock_q1, mock_q2, mock_q3])
    progress = await InterviewService.calculate_progress("session-1")
    assert progress == {"current": 2, "total": 3}


@pytest.mark.asyncio
async def test_calculate_progress_no_questions():
    """测试计算面试进度 - 没有题目"""
    _mock_interview_question_dao.select_questions_by_session = AsyncMock(return_value=[])
    progress = await InterviewService.calculate_progress("session-1")
    assert progress == {"current": 0, "total": 0}
