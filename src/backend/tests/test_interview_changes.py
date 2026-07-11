"""
验证面试功能改动后的关键逻辑。
运行: python tests/test_interview_changes.py
"""
import sys
import os

# 确保能导入项目模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_evaluation_to_hundred():
    """P1a: _to_hundred 将 0-10 分制正确转换为 0-100"""
    from kirinchat.api.services.evaluation import EvaluationService

    assert EvaluationService._to_hundred(10) == 100.0, f"10 -> {EvaluationService._to_hundred(10)}"
    assert EvaluationService._to_hundred(0) == 0.0, f"0 -> {EvaluationService._to_hundred(0)}"
    assert EvaluationService._to_hundred(5) == 50.0, f"5 -> {EvaluationService._to_hundred(5)}"
    assert EvaluationService._to_hundred(7.5) == 75.0, f"7.5 -> {EvaluationService._to_hundred(7.5)}"
    # 钳制超出范围
    assert EvaluationService._to_hundred(15) == 100.0, f"15 -> {EvaluationService._to_hundred(15)}"
    assert EvaluationService._to_hundred(-3) == 0.0, f"-3 -> {EvaluationService._to_hundred(-3)}"
    print("[PASS] test_evaluation_to_hundred")


def test_merge_batch_results_0_100_scale():
    """P1a: _merge_batch_results 输出的分数在 0-100 范围"""
    from kirinchat.api.services.evaluation import EvaluationService

    batch_results = [
        {
            "category_scores": {"前端基础": 8, "算法": 6},
            "question_scores": [
                {"id": "q1", "score": 9},
                {"id": "q2", "score": 7},
            ],
            "strengths": ["基础扎实"],
            "improvements": ["算法需加强"],
        },
        {
            "category_scores": {"前端基础": 9, "工程化": 7},
            "question_scores": [
                {"id": "q3", "score": 8},
                {"id": "q4", "score": 6},
            ],
            "strengths": ["工程化好"],
            "improvements": ["React 需深入"],
        },
    ]

    merged = EvaluationService._merge_batch_results(batch_results)

    # total_score 应该是 0-100 范围（原始 0-10 的均分 7.5 × 10 = 75.0）
    assert merged["total_score"] == 75.0, f"total_score={merged['total_score']} (expected 75.0)"

    # category_scores 应该在 0-100 范围
    for cat, score in merged["category_scores"].items():
        assert 0 <= score <= 100, f"category {cat} score={score} out of 0-100 range"

    # 前端基础 = (8+9)/2 * 10 = 85.0
    assert merged["category_scores"]["前端基础"] == 85.0, f"前端基础={merged['category_scores']['前端基础']}"

    # question_scores 每个分数应在 0-100 范围
    for qs in merged["question_scores"]:
        assert 0 <= float(qs["score"]) <= 100, f"question {qs['id']} score={qs['score']} out of range"

    # q1 score = 9 * 10 = 90
    q1 = next(qs for qs in merged["question_scores"] if qs["id"] == "q1")
    assert float(q1["score"]) == 90.0, f"q1 score={q1['score']} (expected 90.0)"

    print("[PASS] test_merge_batch_results_0_100_scale")


def test_answer_length_validation():
    """P3.1: InterviewAnswerReq 拒绝超过 10000 字符的答案"""
    from pydantic import ValidationError
    from kirinchat.schemas.interview import InterviewAnswerReq

    # 正常长度应通过
    valid = InterviewAnswerReq(session_id="s1", question_id="q1", answer="这是一个正常的答案")
    assert valid.answer == "这是一个正常的答案"

    # 超长答案应被拒绝
    long_answer = "A" * 10001
    try:
        InterviewAnswerReq(session_id="s1", question_id="q1", answer=long_answer)
        assert False, "Should have raised ValidationError for answer > 10000 chars"
    except ValidationError:
        pass  # expected

    # 恰好 10000 字符应通过
    max_answer = "B" * 10000
    req = InterviewAnswerReq(session_id="s1", question_id="q1", answer=max_answer)
    assert len(req.answer) == 10000

    print("[PASS] test_answer_length_validation")


def test_skill_cache():
    """P2c: SkillService 技能缓存正常工作"""
    from kirinchat.api.services.skill import SkillService

    # 清除缓存
    SkillService._skill_cache.clear()

    # 第一次加载 frontend 技能
    skill1 = SkillService.get_skill_by_id("frontend")
    assert skill1 is not None, "frontend skill should exist"
    assert "id" in skill1 or "name" in skill1, f"skill1={skill1}"

    # 验证缓存已写入
    assert "frontend" in SkillService._skill_cache, "skill should be cached"
    cached = SkillService._skill_cache["frontend"]
    assert "data" in cached and "ts" in cached, "cache entry should have data and ts"

    # 第二次加载应命中缓存
    skill2 = SkillService.get_skill_by_id("frontend")
    assert skill2 == skill1, "cached skill should be identical"

    print("[PASS] test_skill_cache")


def test_agent_no_global_cache():
    """P2c: 验证 _agent_cache 已被移除"""
    import kirinchat.api.v1.interview as interview_module

    assert not hasattr(interview_module, "_agent_cache"), "_agent_cache should be removed"
    print("[PASS] test_agent_no_global_cache")


def test_models_have_indexes():
    """P3.3: 验证数据库模型字段有 index=True"""
    from kirinchat.database.models.interview import (
        InterviewSessionTable,
        InterviewQuestionTable,
        EvaluationReportTable,
        EvaluationQuestionDetailTable,
    )

    # 检查 InterviewSessionTable.user_id 有索引
    user_id_field = InterviewSessionTable.model_fields.get("user_id")
    assert user_id_field is not None, "user_id field should exist"

    # SQLModel 中 index=True 会反映在 metadata 中
    from sqlalchemy import inspect
    mapper = inspect(InterviewSessionTable)
    table = mapper.local_table

    indexed_columns = {col.name for col in table.columns if col.index}
    assert "user_id" in indexed_columns, f"user_id should be indexed, indexed={indexed_columns}"
    assert "skill_id" in indexed_columns, f"skill_id should be indexed, indexed={indexed_columns}"
    assert "status" in indexed_columns, f"status should be indexed, indexed={indexed_columns}"

    # InterviewQuestionTable.session_id
    q_mapper = inspect(InterviewQuestionTable)
    q_indexed = {col.name for col in q_mapper.local_table.columns if col.index}
    assert "session_id" in q_indexed, f"question.session_id should be indexed, indexed={q_indexed}"

    # EvaluationReportTable.session_id
    r_mapper = inspect(EvaluationReportTable)
    r_indexed = {col.name for col in r_mapper.local_table.columns if col.index}
    assert "session_id" in r_indexed, f"report.session_id should be indexed, indexed={r_indexed}"

    # EvaluationQuestionDetailTable.evaluation_id / question_id
    d_mapper = inspect(EvaluationQuestionDetailTable)
    d_indexed = {col.name for col in d_mapper.local_table.columns if col.index}
    assert "evaluation_id" in d_indexed, f"detail.evaluation_id should be indexed, indexed={d_indexed}"
    assert "question_id" in d_indexed, f"detail.question_id should be indexed, indexed={d_indexed}"

    print("[PASS] test_models_have_indexes")


def test_evaluation_status_route_exists():
    """P2b: 验证评估状态接口路由已注册"""
    from kirinchat.api.v1.interview import router

    routes = {route.path for route in router.routes}
    assert "/interview/evaluation/status/{session_id}" in routes, \
        f"evaluation status route missing, routes={routes}"
    print("[PASS] test_evaluation_status_route_exists")


def test_require_session_access_exists():
    """P0: 验证 _require_session_access 函数存在"""
    from kirinchat.api.v1.interview import _require_session_access
    import inspect as _inspect

    assert _inspect.iscoroutinefunction(_require_session_access), \
        "_require_session_access should be async"
    print("[PASS] test_require_session_access_exists")


if __name__ == "__main__":
    print("=" * 60)
    print("Running interview change verification tests...")
    print("=" * 60)

    tests = [
        test_evaluation_to_hundred,
        test_merge_batch_results_0_100_scale,
        test_answer_length_validation,
        test_skill_cache,
        test_agent_no_global_cache,
        test_models_have_indexes,
        test_evaluation_status_route_exists,
        test_require_session_access_exists,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")
    print("=" * 60)

    sys.exit(1 if failed > 0 else 0)
