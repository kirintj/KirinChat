import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Mock the database layer so that importing the service never triggers a real
# database connection (pymysql / aiomysql are not available in test env).
# ---------------------------------------------------------------------------

_mock_interview_session_dao = MagicMock()
_mock_interview_question_dao = MagicMock()
_mock_evaluation_report_dao = MagicMock()
_mock_interview_models = MagicMock()

# Inject fake modules into sys.modules before the service is imported.
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

# Now it's safe to import the service -- it will grab our mocked DAOs.
from kirinchat.api.services.evaluation import EvaluationService  # noqa: E402

# Restore original sys.modules entries to prevent contamination of other tests.
for _k, _v in _saved_modules.items():
    if _v is None:
        sys.modules.pop(_k, None)
    else:
        sys.modules[_k] = _v


# ---------------------------------------------------------------------------
# Pure helper tests (no mocking needed)
# ---------------------------------------------------------------------------


def test_batch_questions():
    """测试题目分批"""
    questions = [{"id": f"q{i}", "content": f"question {i}", "answer": f"answer {i}"} for i in range(20)]
    batches = EvaluationService._batch_questions(questions, batch_size=8)
    assert len(batches) == 3  # 8 + 8 + 4
    assert len(batches[0]) == 8
    assert len(batches[1]) == 8
    assert len(batches[2]) == 4


def test_batch_questions_exact_size():
    """测试题目分批 - 刚好整除"""
    questions = [{"id": f"q{i}"} for i in range(16)]
    batches = EvaluationService._batch_questions(questions, batch_size=8)
    assert len(batches) == 2
    assert len(batches[0]) == 8
    assert len(batches[1]) == 8


def test_batch_questions_single_batch():
    """测试题目分批 - 少于一批"""
    questions = [{"id": f"q{i}"} for i in range(3)]
    batches = EvaluationService._batch_questions(questions, batch_size=8)
    assert len(batches) == 1
    assert len(batches[0]) == 3


def test_batch_questions_empty():
    """测试题目分批 - 空列表"""
    batches = EvaluationService._batch_questions([], batch_size=8)
    assert len(batches) == 0


def test_build_default_report():
    """测试默认报告生成"""
    report = EvaluationService._build_default_report()
    assert report["total_score"] == 0.0
    assert "summary" in report
    assert "category_scores" in report
    assert "strengths" in report
    assert "improvements" in report
    assert isinstance(report["category_scores"], dict)
    assert isinstance(report["strengths"], list)
    assert isinstance(report["improvements"], list)


def test_merge_batch_results():
    """测试批次结果合并"""
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


def test_merge_batch_results_single():
    """测试批次结果合并 - 单个批次"""
    batch_results = [
        {
            "category_scores": {"java": 8.0},
            "question_scores": [{"id": "q1", "score": 8.0}],
        },
    ]
    merged = EvaluationService._merge_batch_results(batch_results)
    assert merged["category_scores"]["java"] == 8.0
    assert len(merged["question_scores"]) == 1
    assert merged["total_score"] == 8.0


def test_merge_batch_results_empty():
    """测试批次结果合并 - 空列表"""
    merged = EvaluationService._merge_batch_results([])
    assert merged["total_score"] == 0.0
    assert merged["category_scores"] == {}
    assert merged["question_scores"] == []


def test_question_to_dict():
    """测试题目对象转字典"""
    mock_q = MagicMock()
    mock_q.id = "q1"
    mock_q.content = "什么是多态?"
    mock_q.user_answer = "多态是面向对象的特性"
    mock_q.category = "java"
    mock_q.type = "MAIN"

    result = EvaluationService._question_to_dict(mock_q)
    assert result["id"] == "q1"
    assert result["content"] == "什么是多态?"
    assert result["answer"] == "多态是面向对象的特性"
    assert result["category"] == "java"


def test_build_evaluation_prompt():
    """测试构建评估 prompt"""
    batch = [
        {"id": "q1", "content": "什么是多态?", "answer": "多态是OOP特性", "category": "java"},
        {"id": "q2", "content": "解释 SOLID", "answer": "SOLID是设计原则", "category": "java"},
    ]
    prompt = EvaluationService._build_evaluation_prompt(batch)
    assert "q1" in prompt or "什么是多态" in prompt
    assert "q2" in prompt or "SOLID" in prompt


def test_parse_evaluation_result():
    """测试解析 LLM 评估结果"""
    content = """```json
    {
        "category_scores": {"java": 8.0},
        "question_scores": [
            {"id": "q1", "score": 8.0, "feedback": "good"}
        ],
        "strengths": ["逻辑清晰"],
        "improvements": ["需要更多细节"]
    }
    ```"""
    batch = [{"id": "q1", "content": "test", "category": "java"}]
    result = EvaluationService._parse_evaluation_result(content, batch)
    assert result is not None
    assert result["category_scores"]["java"] == 8.0
    assert len(result["question_scores"]) == 1
    assert result["question_scores"][0]["id"] == "q1"


def test_parse_evaluation_result_invalid():
    """测试解析无效的 LLM 结果"""
    content = "This is not valid JSON at all"
    batch = [{"id": "q1"}]
    result = EvaluationService._parse_evaluation_result(content, batch)
    assert result is None


# ---------------------------------------------------------------------------
# Async tests with mocked dependencies
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_report_by_id():
    """测试根据 ID 获取评估报告"""
    mock_report = MagicMock()
    mock_report.id = "report-1"
    mock_report.session_id = "session-1"
    mock_report.total_score = 8.5

    _mock_evaluation_report_dao.select_report_by_id = AsyncMock(return_value=mock_report)
    result = await EvaluationService.get_report_by_id("report-1")
    assert result is not None
    assert result.id == "report-1"


@pytest.mark.asyncio
async def test_get_report_by_session():
    """测试根据会话 ID 获取评估报告"""
    mock_report = MagicMock()
    mock_report.id = "report-1"
    mock_report.session_id = "session-1"

    _mock_evaluation_report_dao.select_report_by_session = AsyncMock(return_value=mock_report)
    result = await EvaluationService.get_report_by_session("session-1")
    assert result is not None
    assert result.session_id == "session-1"


@pytest.mark.asyncio
async def test_evaluate_session_no_questions():
    """测试评估会话 - 没有题目时返回默认报告"""
    _mock_interview_question_dao.select_questions_by_session = AsyncMock(return_value=[])
    mock_report = MagicMock()
    mock_report.id = "default-report"
    mock_report.total_score = 0.0
    _mock_evaluation_report_dao.create_report = AsyncMock(return_value=mock_report)

    with patch("kirinchat.api.services.evaluation.InterviewService") as mock_service:
        mock_service.get_session_questions = AsyncMock(return_value=[])
        mock_service.get_session = AsyncMock(return_value=MagicMock())
        mock_service.update_session_status = AsyncMock()

        result = await EvaluationService.evaluate_session("session-1")
        assert result is not None
        mock_service.update_session_status.assert_called_once_with("session-1", "EVALUATED")


@pytest.mark.asyncio
async def test_evaluate_session_success():
    """测试评估会话 - 成功评估"""
    mock_q1 = MagicMock()
    mock_q1.id = "q1"
    mock_q1.content = "什么是多态?"
    mock_q1.user_answer = "多态是面向对象的核心特性"
    mock_q1.category = "java"
    mock_q1.type = "MAIN"

    mock_q2 = MagicMock()
    mock_q2.id = "q2"
    mock_q2.content = "解释 SOLID 原则"
    mock_q2.user_answer = "SOLID 是五个设计原则的缩写"
    mock_q2.category = "java"
    mock_q2.type = "MAIN"

    llm_response = MagicMock()
    llm_response.content = '''```json
    {
        "category_scores": {"java": 8.5},
        "question_scores": [
            {"id": "q1", "score": 8.0, "feedback": "good"},
            {"id": "q2", "score": 9.0, "feedback": "excellent"}
        ],
        "strengths": ["理解准确"],
        "improvements": ["可以更深入"]
    }
    ```'''

    summary_response = MagicMock()
    summary_response.content = "整体表现良好，对 Java 基础有扎实的理解。"

    mock_report = MagicMock()
    mock_report.id = "report-1"
    mock_report.total_score = 8.5

    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(side_effect=[llm_response, summary_response])

    with (
        patch("kirinchat.api.services.evaluation.InterviewService") as mock_service,
        patch("kirinchat.api.services.evaluation.ModelManager") as mock_manager,
    ):
        mock_service.get_session_questions = AsyncMock(return_value=[mock_q1, mock_q2])
        mock_service.get_session = AsyncMock(return_value=MagicMock())
        mock_service.update_session_status = AsyncMock()

        mock_manager.get_conversation_model.return_value = mock_llm

        _mock_evaluation_report_dao.create_report = AsyncMock(return_value=mock_report)
        _mock_interview_question_dao.update_question_score = AsyncMock()

        result = await EvaluationService.evaluate_session("session-1")
        assert result is not None
        mock_service.update_session_status.assert_called_once_with("session-1", "EVALUATED")


@pytest.mark.asyncio
async def test_evaluate_session_llm_failure():
    """测试评估会话 - LLM 调用失败时使用默认报告"""
    mock_q = MagicMock()
    mock_q.id = "q1"
    mock_q.content = "什么是多态?"
    mock_q.user_answer = "多态是OOP特性"
    mock_q.category = "java"
    mock_q.type = "MAIN"

    mock_report = MagicMock()
    mock_report.id = "default-report"
    mock_report.total_score = 0.0

    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(side_effect=Exception("LLM service unavailable"))

    with (
        patch("kirinchat.api.services.evaluation.InterviewService") as mock_service,
        patch("kirinchat.api.services.evaluation.ModelManager") as mock_manager,
    ):
        mock_service.get_session_questions = AsyncMock(return_value=[mock_q])
        mock_service.get_session = AsyncMock(return_value=MagicMock())
        mock_service.update_session_status = AsyncMock()

        mock_manager.get_conversation_model.return_value = mock_llm

        _mock_evaluation_report_dao.create_report = AsyncMock(return_value=mock_report)

        result = await EvaluationService.evaluate_session("session-1")
        assert result is not None
        # Should still mark session as evaluated even on failure
        mock_service.update_session_status.assert_called_once_with("session-1", "EVALUATED")


@pytest.mark.asyncio
async def test_save_default_report():
    """测试保存默认评估报告"""
    mock_report = MagicMock()
    mock_report.id = "default-report"
    mock_report.total_score = 0.0
    mock_report.session_id = "session-1"

    _mock_evaluation_report_dao.create_report = AsyncMock(return_value=mock_report)
    result = await EvaluationService._save_default_report("session-1")
    assert result is not None
    assert result.total_score == 0.0
