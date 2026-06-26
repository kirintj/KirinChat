# 评估报告增强 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 持久化逐题评估反馈、新建题目详情页、报告页展示题目列表并支持 PDF 导出

**Architecture:** 新建 EvaluationQuestionDetailTable 存储逐题反馈，改造评估服务持久化 LLM 输出，在报告页下方添加题目列表，新建独立详情页展示单题反馈/参考答案，扩展 PdfService 增加逐题内容

**Tech Stack:** Python/FastAPI, SQLModel/SQLAlchemy, Vue 3, TypeScript, reportlab

---

### Task 1: 数据库模型 — 新建 EvaluationQuestionDetailTable

**Files:**
- Modify: `src/backend/kirinchat/database/models/interview.py`

- [ ] **Step 1: 在 EvaluationReportTable 之后添加新模型**

找到 `EvaluationReportTable` 类结束（约第 81 行 `}` 之后），在其后插入：

```python


class EvaluationQuestionDetailTable(SQLModelSerializable, table=True):
    """评估逐题详情表：存储每道题的得分、AI反馈和参考答案。"""
    __tablename__ = "evaluation_question_detail"

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True, description="详情ID")
    evaluation_id: str = Field(description="关联评估报告ID")
    question_id: str = Field(description="关联面试题目ID")
    score: int = Field(default=0, description="该题得分 (0-10)")
    feedback: str = Field(default="", sa_column=Column(Text), description="AI 对该题答案的评价")
    reference_answer: str = Field(default="", sa_column=Column(Text), description="参考答案")

    create_time: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text('CURRENT_TIMESTAMP')
        ),
        description="创建时间"
    )
```

- [ ] **Step 2: 验证 Python 语法**

Run: `cd "D:/HuaweiMoveData/Users/28966/Desktop/项目DEMO/KirinChat/src/backend" && python -c "from kirinchat.database.models.interview import EvaluationQuestionDetailTable; print('OK')"`
Expected: OK

- [ ] **Step 3: Commit**

```bash
git add src/backend/kirinchat/database/models/interview.py
git commit -m "feat(evaluation): add EvaluationQuestionDetailTable model"
```

---

### Task 2: 注册模型到数据库

**Files:**
- Modify: `src/backend/kirinchat/database/__init__.py`

- [ ] **Step 1: 添加 import**

找到 import 区域（第 1-30 行），不需要新增 import（模型在 `interview.py` 中已定义，`database/__init__.py` 不直接 import interview 模型）。确认 `interview.py` 中的模型在 Alembic 或 `create_all` 时会被发现即可。

检查是否有显式 import interview 模型的地方：

Run: `cd "D:/HuaweiMoveData/Users/28966/Desktop/项目DEMO/KirinChat/src/backend" && grep -n "interview" kirinchat/database/__init__.py`
Expected: 无结果（interview 模型通过其他方式注册）

如果模型未被自动发现，需要在 `__init__.py` 中添加：
```python
from kirinchat.database.models.interview import (  # noqa: F401
    InterviewSessionTable,
    InterviewQuestionTable,
    EvaluationReportTable,
    EvaluationQuestionDetailTable,
)
```

- [ ] **Step 2: Commit**

```bash
git add src/backend/kirinchat/database/__init__.py
git commit -m "feat(evaluation): register EvaluationQuestionDetailTable"
```

---

### Task 3: DAO 层 — 新增 EvaluationQuestionDetailDao

**Files:**
- Modify: `src/backend/kirinchat/database/dao/interview.py`

- [ ] **Step 1: 添加 import**

找到文件顶部 import（第 1-8 行），在已有 import 之后添加：

```python
from kirinchat.database.models.interview import (
    InterviewSessionTable,
    InterviewQuestionTable,
    EvaluationReportTable,
    EvaluationQuestionDetailTable,
)
```

替换现有的 models import：
```python
from kirinchat.database.models.interview import (
    InterviewSessionTable,
    InterviewQuestionTable,
    EvaluationReportTable,
    EvaluationQuestionDetailTable,
)
```

- [ ] **Step 2: 在文件末尾添加 EvaluationQuestionDetailDao**

找到文件末尾（`EvaluationReportDao` 类结束之后），添加：

```python


class EvaluationQuestionDetailDao:

    @classmethod
    async def batch_create(cls, details: list[EvaluationQuestionDetailTable]):
        """批量创建逐题评估详情。"""
        with session_getter() as session:
            for detail in details:
                session.add(detail)
            session.commit()

    @classmethod
    async def select_by_evaluation_id(cls, evaluation_id: str) -> list[EvaluationQuestionDetailTable]:
        """按评估报告 ID 查询所有逐题详情。"""
        with session_getter() as session:
            statement = select(EvaluationQuestionDetailTable).where(
                EvaluationQuestionDetailTable.evaluation_id == evaluation_id
            )
            result = session.exec(statement).all()
            return list(result)

    @classmethod
    async def select_by_question_id(cls, question_id: str):
        """按题目 ID 查询单题评估详情。"""
        with session_getter() as session:
            statement = select(EvaluationQuestionDetailTable).where(
                EvaluationQuestionDetailTable.question_id == question_id
            )
            result = session.exec(statement).first()
            return result
```

- [ ] **Step 3: 验证 Python 语法**

Run: `cd "D:/HuaweiMoveData/Users/28966/Desktop/项目DEMO/KirinChat/src/backend" && python -c "from kirinchat.database.dao.interview import EvaluationQuestionDetailDao; print('OK')"`
Expected: OK

- [ ] **Step 4: Commit**

```bash
git add src/backend/kirinchat/database/dao/interview.py
git commit -m "feat(evaluation): add EvaluationQuestionDetailDao"
```

---

### Task 4: 后端 Schema — 新增响应模型

**Files:**
- Modify: `src/backend/kirinchat/schemas/interview.py`

- [ ] **Step 1: 添加 QuestionDetailResp 和 QuestionDetailItem**

找到 `EvaluationReportResp` 类（约第 88 行），在其前插入：

```python
class QuestionDetailResp(BaseModel):
    """单题评估详情响应"""
    question_id: str = Field(..., description="题目ID")
    session_id: str = Field(default="", description="所属会话ID")
    content: str = Field(default="", description="题目内容")
    user_answer: Optional[str] = Field(None, description="用户答案")
    type: str = Field(default="MAIN", description="题目类型")
    category: str = Field(default="", description="题目分类")
    score: int = Field(default=0, description="得分 (0-10)")
    feedback: str = Field(default="", description="AI 反馈")
    reference_answer: str = Field(default="", description="参考答案")
    skill_name: str = Field(default="", description="技能名称")


class QuestionDetailItem(BaseModel):
    """评估报告中的逐题摘要项"""
    question_id: str = Field(..., description="题目ID")
    content: str = Field(default="", description="题目内容")
    user_answer: Optional[str] = Field(None, description="用户答案")
    type: str = Field(default="MAIN", description="题目类型")
    category: str = Field(default="", description="题目分类")
    score: int = Field(default=0, description="得分 (0-10)")
    feedback: str = Field(default="", description="AI 反馈")
    reference_answer: str = Field(default="", description="参考答案")


```

- [ ] **Step 2: 修改 EvaluationReportResp 添加 question_details**

找到 `EvaluationReportResp` 类（约第 88-95 行）：
```python
class EvaluationReportResp(BaseModel):
    """评估报告响应"""
    id: str = Field(..., description="评估ID")
    total_score: float = Field(..., description="总分")
    category_scores: Dict[str, float] = Field(default={}, description="各分类得分")
    summary: str = Field(..., description="总结")
    strengths: List[str] = Field(default=[], description="优势列表")
    improvements: List[str] = Field(default=[], description="待改进列表")
```

替换为：
```python
class EvaluationReportResp(BaseModel):
    """评估报告响应"""
    id: str = Field(..., description="评估ID")
    total_score: float = Field(..., description="总分")
    category_scores: Dict[str, float] = Field(default={}, description="各分类得分")
    summary: str = Field(..., description="总结")
    strengths: List[str] = Field(default=[], description="优势列表")
    improvements: List[str] = Field(default=[], description="待改进列表")
    question_details: List[QuestionDetailItem] = Field(default=[], description="逐题详情")
```

- [ ] **Step 3: 验证 Python 语法**

Run: `cd "D:/HuaweiMoveData/Users/28966/Desktop/项目DEMO/KirinChat/src/backend" && python -c "from kirinchat.schemas.interview import EvaluationReportResp, QuestionDetailResp, QuestionDetailItem; print('OK')"`
Expected: OK

- [ ] **Step 4: Commit**

```bash
git add src/backend/kirinchat/schemas/interview.py
git commit -m "feat(evaluation): add question detail response schemas"
```

---

### Task 5: 评估服务 — 持久化逐题详情

**Files:**
- Modify: `src/backend/kirinchat/api/services/evaluation.py`

- [ ] **Step 1: 添加 import**

找到文件顶部 import（第 1-12 行），修改为：

```python
import json
import asyncio
import logging

from kirinchat.api.services.interview import InterviewService
from kirinchat.core.models.manager import ModelManager
from kirinchat.database.dao.interview import (
    EvaluationReportDao,
    InterviewQuestionDao,
    EvaluationQuestionDetailDao,
)
from kirinchat.database.models.interview import EvaluationReportTable, EvaluationQuestionDetailTable
from kirinchat.utils.llm_parser import parse_llm_json
```

- [ ] **Step 2: 修改 _build_evaluation_prompt 追加 reference_answer 要求**

找到 `_build_evaluation_prompt` 方法中的 JSON 格式说明（约第 159-168 行）：

```python
            "请严格以如下 JSON 格式输出（不要输出其他内容）：\n"
            "```json\n"
            "{\n"
            '  "category_scores": {"分类名": 分数(0-10)},\n'
            '  "question_scores": [\n'
            '    {"id": "题目ID", "score": 分数(0-10), "feedback": "简短评价"}\n'
            "  ],\n"
            '  "strengths": ["优势1", "优势2"],\n'
            '  "improvements": ["改进1", "改进2"]\n'
            "}\n"
            "```\n\n"
```

替换为：
```python
            "请严格以如下 JSON 格式输出（不要输出其他内容）：\n"
            "```json\n"
            "{\n"
            '  "category_scores": {"分类名": 分数(0-10)},\n'
            '  "question_scores": [\n'
            '    {"id": "题目ID", "score": 分数(0-10), "feedback": "简短评价(50字以内)", "reference_answer": "该题的标准参考答案(100字以内)"}\n'
            "  ],\n"
            '  "strengths": ["优势1", "优势2"],\n'
            '  "improvements": ["改进1", "改进2"]\n'
            "}\n"
            "```\n\n"
```

- [ ] **Step 3: 修改 _parse_evaluation_result 保留 reference_answer**

找到 `_parse_evaluation_result` 方法中处理 question_scores 的部分（约第 184-190 行）：

```python
        category_scores = result.get("category_scores", {})
        question_scores = result.get("question_scores", [])

        scored_ids = {qs.get("id") for qs in question_scores}
        for q in batch:
            qid = q.get("id")
            if qid and qid not in scored_ids:
                question_scores.append({"id": qid, "score": 0.0, "feedback": "未评分"})
```

替换为：
```python
        category_scores = result.get("category_scores", {})
        question_scores = result.get("question_scores", [])

        scored_ids = {qs.get("id") for qs in question_scores}
        for q in batch:
            qid = q.get("id")
            if qid and qid not in scored_ids:
                question_scores.append({"id": qid, "score": 0.0, "feedback": "未评分", "reference_answer": ""})
```

- [ ] **Step 4: 修改 evaluate_session 持久化逐题详情**

找到 `evaluate_session` 方法中更新 question scores 的部分（约第 78-88 行）：

```python
        # Update question scores
        score_tasks = []
        for qs in merged.get("question_scores", []):
            qid = qs.get("id")
            score = qs.get("score")
            if qid and score is not None:
                score_tasks.append(
                    cls._update_question_score_safe(qid, float(score))
                )
        if score_tasks:
            await asyncio.gather(*score_tasks)
```

替换为：
```python
        # 持久化逐题评估详情（得分 + 反馈 + 参考答案）
        detail_objects = []
        for qs in merged.get("question_scores", []):
            qid = qs.get("id")
            score = qs.get("score")
            if qid and score is not None:
                detail = EvaluationQuestionDetailTable(
                    evaluation_id=report.id,
                    question_id=qid,
                    score=int(float(score)),
                    feedback=qs.get("feedback", ""),
                    reference_answer=qs.get("reference_answer", ""),
                )
                detail_objects.append(detail)
        if detail_objects:
            await EvaluationQuestionDetailDao.batch_create(detail_objects)
```

- [ ] **Step 5: 添加 get_details_by_evaluation 方法**

找到 `get_report_by_session` 方法之后（约第 99 行），添加：

```python
    @classmethod
    async def get_details_by_evaluation(cls, evaluation_id: str):
        """获取评估报告的逐题详情列表。"""
        return await EvaluationQuestionDetailDao.select_by_evaluation_id(evaluation_id)

    @classmethod
    async def get_detail_by_question(cls, question_id: str):
        """获取单题的评估详情。"""
        return await EvaluationQuestionDetailDao.select_by_question_id(question_id)
```

- [ ] **Step 6: 验证 Python 语法**

Run: `cd "D:/HuaweiMoveData/Users/28966/Desktop/项目DEMO/KirinChat/src/backend" && python -c "from kirinchat.api.services.evaluation import EvaluationService; print('OK')"`
Expected: OK

- [ ] **Step 7: Commit**

```bash
git add src/backend/kirinchat/api/services/evaluation.py
git commit -m "feat(evaluation): persist per-question feedback and reference answers"
```

---

### Task 6: 后端 API — 修改评估报告端点 + 新增题目详情端点

**Files:**
- Modify: `src/backend/kirinchat/api/v1/interview.py`

- [ ] **Step 1: 添加 import**

找到文件顶部 import（第 1-31 行），在 schemas import 中添加 `QuestionDetailResp` 和 `QuestionDetailItem`：

```python
from kirinchat.schemas.interview import (
    InterviewStartReq,
    InterviewStartResp,
    InterviewAnswerReq,
    InterviewAnswerResp,
    InterviewCompleteReq,
    InterviewCompleteResp,
    InterviewSessionResp,
    InterviewSessionDetailResp,
    EvaluationReportResp,
    InterviewHistoryResp,
    SkillDetailResp,
    SkillListResp,
    SkillInfoResp,
    SkillCategoryResp,
    QuestionResp,
    QuestionDetailResp,
    QuestionDetailItem,
)
```

- [ ] **Step 2: 添加辅助函数 _build_evaluation_resp**

找到 `_skill_to_detail` 函数结束（约第 90 行），在其后添加：

```python


async def _build_evaluation_resp(report) -> EvaluationReportResp:
    """构建包含逐题详情的评估报告响应。"""
    details = await EvaluationService.get_details_by_evaluation(report.id)
    questions = await InterviewService.get_session_questions(report.session_id)
    q_map = {q.id: q for q in questions}
    question_items = []
    for d in details:
        q = q_map.get(d.question_id)
        question_items.append(QuestionDetailItem(
            question_id=d.question_id,
            content=q.content if q else "",
            user_answer=q.user_answer if q else None,
            type=q.type if q else "MAIN",
            category=q.category if q else "",
            score=d.score,
            feedback=d.feedback,
            reference_answer=d.reference_answer,
        ))
    return EvaluationReportResp(
        id=report.id,
        total_score=report.total_score,
        category_scores=report.category_scores or {},
        summary=report.summary or "",
        strengths=report.strengths or [],
        improvements=report.improvements or [],
        question_details=question_items,
    )
```

- [ ] **Step 3: 修改 get_evaluation_report 端点**

找到 `get_evaluation_report` 函数（约第 336-358 行）：

```python
@router.get("/interview/evaluation/{evaluation_id}", response_model=UnifiedResponseModel)
async def get_evaluation_report(
    evaluation_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """Get an evaluation report by ID."""
    try:
        report = await EvaluationService.get_report_by_id(evaluation_id)
        if report is None:
            return resp_500(message="Evaluation report not found")

        data = EvaluationReportResp(
            id=report.id,
            total_score=report.total_score,
            category_scores=report.category_scores or {},
            summary=report.summary or "",
            strengths=report.strengths or [],
            improvements=report.improvements or [],
        )
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error(f"Get evaluation report error: {err}")
        return resp_500(message=str(err))
```

替换为：
```python
@router.get("/interview/evaluation/{evaluation_id}", response_model=UnifiedResponseModel)
async def get_evaluation_report(
    evaluation_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """Get an evaluation report by ID (includes per-question details)."""
    try:
        report = await EvaluationService.get_report_by_id(evaluation_id)
        if report is None:
            return resp_500(message="Evaluation report not found")

        data = await _build_evaluation_resp(report)
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error(f"Get evaluation report error: {err}")
        return resp_500(message=str(err))
```

- [ ] **Step 4: 修改 get_evaluation_by_session 端点**

找到 `get_evaluation_by_session` 函数（约第 361-383 行）：

```python
@router.get("/interview/evaluation/by-session/{session_id}", response_model=UnifiedResponseModel)
async def get_evaluation_by_session(
    session_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """Get an evaluation report by session ID."""
    try:
        report = await EvaluationService.get_report_by_session(session_id)
        if report is None:
            return resp_500(message="Evaluation report not found for this session")

        data = EvaluationReportResp(
            id=report.id,
            total_score=report.total_score,
            category_scores=report.category_scores or {},
            summary=report.summary or "",
            strengths=report.strengths or [],
            improvements=report.improvements or [],
        )
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error(f"Get evaluation by session error: {err}")
        return resp_500(message=str(err))
```

替换为：
```python
@router.get("/interview/evaluation/by-session/{session_id}", response_model=UnifiedResponseModel)
async def get_evaluation_by_session(
    session_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """Get an evaluation report by session ID (includes per-question details)."""
    try:
        report = await EvaluationService.get_report_by_session(session_id)
        if report is None:
            return resp_500(message="Evaluation report not found for this session")

        data = await _build_evaluation_resp(report)
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error(f"Get evaluation by session error: {err}")
        return resp_500(message=str(err))
```

- [ ] **Step 5: 在 get_evaluation_by_session 之后添加题目详情端点**

```python
@router.get("/interview/question-detail/{question_id}", response_model=UnifiedResponseModel)
async def get_question_detail(
    question_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """获取单题的评估详情（得分、反馈、参考答案）。"""
    try:
        detail = await EvaluationService.get_detail_by_question(question_id)
        if detail is None:
            return resp_500(message="Question detail not found")

        # 通过 evaluation_id 获取 session_id，再查找题目
        report = await EvaluationService.get_report_by_id(detail.evaluation_id)
        q = None
        session = None
        if report:
            session = await InterviewService.get_session(report.session_id)
            if session:
                questions = await InterviewService.get_session_questions(session.id)
                for candidate in questions:
                    if candidate.id == question_id:
                        q = candidate
                        break

        # 获取技能名称
        skill_name = ""
        if session:
                from kirinchat.api.services.skill import SkillService
                skill = SkillService.get_skill_by_id(session.skill_id)
                skill_name = skill.get("name", "") if skill else ""

        data = QuestionDetailResp(
            question_id=detail.question_id,
            session_id=q.session_id if q else "",
            content=q.content if q else "",
            user_answer=q.user_answer if q else None,
            type=q.type if q else "MAIN",
            category=q.category if q else "",
            score=detail.score,
            feedback=detail.feedback,
            reference_answer=detail.reference_answer,
            skill_name=skill_name,
        )
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error(f"Get question detail error: {err}")
        return resp_500(message=str(err))
```

- [ ] **Step 6: 验证 Python 语法**

Run: `cd "D:/HuaweiMoveData/Users/28966/Desktop/项目DEMO/KirinChat/src/backend" && python -c "from kirinchat.api.v1.interview import router; print('OK')"`
Expected: OK

- [ ] **Step 7: Commit**

```bash
git add src/backend/kirinchat/api/v1/interview.py
git commit -m "feat(evaluation): add question details to report API and new question detail endpoint"
```

---

### Task 7: 前端接口 — 新增类型和 API 函数

**Files:**
- Modify: `src/frontend/src/apis/interview.ts`

- [ ] **Step 1: 在 EvaluationReport 接口中添加 question_details**

找到 `EvaluationReport` 接口（约第 74-81 行）：

```typescript
export interface EvaluationReport {
  id: string
  total_score: number
  category_scores: Record<string, number>
  summary: string
  strengths: string[]
  improvements: string[]
}
```

替换为：
```typescript
export interface QuestionDetailItem {
  question_id: string
  content: string
  user_answer: string | null
  type: string
  category: string
  score: number
  feedback: string
  reference_answer: string
}

export interface EvaluationReport {
  id: string
  total_score: number
  category_scores: Record<string, number>
  summary: string
  strengths: string[]
  improvements: string[]
  question_details: QuestionDetailItem[]
}

export interface QuestionDetailData {
  question_id: string
  session_id: string
  content: string
  user_answer: string | null
  type: string
  category: string
  score: number
  feedback: string
  reference_answer: string
  skill_name: string
}
```

- [ ] **Step 2: 在 getLearningPathAPI 之前添加 getQuestionDetailAPI**

找到 `getLearningPathAPI` 函数（约第 276 行），在其前插入：

```typescript
/** 获取单题评估详情 */
export function getQuestionDetailAPI(questionId: string) {
  return request<UnifiedResponse<QuestionDetailData>>({
    url: `/api/v1/interview/question-detail/${questionId}`,
    method: 'GET'
  })
}

```

- [ ] **Step 3: Commit**

```bash
git add src/frontend/src/apis/interview.ts
git commit -m "feat(evaluation): add question detail types and API function"
```

---

### Task 8: 前端报告页 — 添加题目列表和 PDF 下载

**Files:**
- Modify: `src/frontend/src/pages/interview/reportPage/reportPage.vue`

- [ ] **Step 1: 添加 PDF 下载函数**

找到 `goBack` 函数之后（约第 118 行），添加：

```typescript
const downloadPDF = () => {
  if (!report.value) return
  const token = localStorage.getItem('token') || ''
  const url = `/api/v1/interview/evaluation/${report.value.id}/pdf`
  // 通过隐藏 iframe 触发下载，避免页面跳转
  const a = document.createElement('a')
  a.href = url
  a.download = `evaluation_${report.value.id}.pdf`
  // 需要带 Authorization header，使用 fetch + blob
  fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  })
    .then(res => res.blob())
    .then(blob => {
      const blobUrl = URL.createObjectURL(blob)
      a.href = blobUrl
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(blobUrl)
    })
    .catch(() => HMessage.error('PDF 下载失败'))
}

const goToQuestionDetail = (questionId: string) => {
  router.push({ path: `/interview/question/${questionId}` })
}
```

- [ ] **Step 2: 添加下载 PDF 按钮到操作栏**

找到 Actions 区域的 `report-actions`（约第 217-232 行），在"重新面试"按钮之前添加"下载 PDF"按钮：

```html
      <!-- Actions -->
      <div class="report-actions">
        <HButton type="secondary" size="large" @click="downloadPDF">
          下载 PDF
        </HButton>
        <HButton type="primary" size="large" @click="startNewInterview">
          重新面试
        </HButton>
```

- [ ] **Step 3: 在改进方向 section 之后、Actions 之前添加题目列表**

找到 `<!-- Improvements -->` section 结束（约第 214 行 `</div>` 之后），在其后、`<!-- Actions -->` 之前插入：

```html
      <!-- Question Details List -->
      <div v-if="report.question_details?.length" class="section">
        <h3 class="section-title">题目详情</h3>
        <div class="question-list">
          <div
            v-for="(q, index) in report.question_details"
            :key="q.question_id"
            class="question-item"
            @click="goToQuestionDetail(q.question_id)"
          >
            <div class="question-left">
              <span class="question-index">Q{{ index + 1 }}</span>
              <span class="question-text">{{ q.content }}</span>
            </div>
            <div class="question-right">
              <span
                class="question-score-badge"
                :class="{
                  'score-high': q.score >= 8,
                  'score-mid': q.score >= 6 && q.score < 8,
                  'score-low': q.score < 6,
                }"
              >
                {{ q.score }}/10
              </span>
              <span class="question-arrow">→</span>
            </div>
          </div>
        </div>
      </div>
```

- [ ] **Step 4: 添加题目列表的样式**

找到 `// Actions` 样式块之前（约第 436 行），添加：

```scss
// Question list
.question-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.question-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--duration-fast) var(--easing);

  &:hover {
    background: var(--color-primary-bg);
  }

  .question-left {
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 1;
    min-width: 0;

    .question-index {
      font-size: 12px;
      font-weight: 600;
      color: var(--color-primary);
      flex-shrink: 0;
    }

    .question-text {
      font-size: 14px;
      color: var(--color-text-primary);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }

  .question-right {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;

    .question-score-badge {
      font-size: 12px;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 10px;

      &.score-high {
        background: var(--color-success-bg);
        color: var(--color-success);
      }

      &.score-mid {
        background: var(--color-warning-bg);
        color: var(--color-warning);
      }

      &.score-low {
        background: rgba(244, 67, 54, 0.1);
        color: #f44336;
      }
    }

    .question-arrow {
      font-size: 14px;
      color: var(--color-text-tertiary);
    }
  }
}

```

- [ ] **Step 5: 验证构建**

Run: `cd src/frontend && npm run build 2>&1 | tail -5`
Expected: 构建成功

- [ ] **Step 6: Commit**

```bash
git add src/frontend/src/pages/interview/reportPage/reportPage.vue
git commit -m "feat(evaluation): add question list and PDF download to report page"
```

---

### Task 9: 前端 — 新建题目详情页

**Files:**
- Create: `src/frontend/src/pages/interview/questionDetailPage/questionDetailPage.vue`

- [ ] **Step 1: 创建题目详情页**

```vue
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { HButton, HMessage } from '@/components/ui'
import { getQuestionDetailAPI } from '../../../apis/interview'
import type { QuestionDetailData } from '../../../apis/interview'
import { marked } from 'marked'

const router = useRouter()
const detail = ref<QuestionDetailData | null>(null)
const loading = ref(false)

// 得分颜色
const scoreColor = computed(() => {
  if (!detail.value) return '#999'
  const s = detail.value.score
  if (s >= 8) return '#4caf50'
  if (s >= 6) return '#ff9800'
  return '#f44336'
})

// 渲染 Markdown
const renderMarkdown = (text: string) => {
  if (!text) return ''
  return marked.parse(text) as string
}

// 返回报告页
const goBack = () => {
  router.back()
}

onMounted(async () => {
  const questionId = router.currentRoute.value.params.questionId as string
  if (!questionId) {
    HMessage.error('题目ID不存在')
    router.replace('/interview')
    return
  }

  loading.value = true
  try {
    const res = await getQuestionDetailAPI(questionId)
    if (res.data.status_code === 200 && res.data.data) {
      detail.value = res.data.data
    } else {
      HMessage.error('获取题目详情失败')
    }
  } catch {
    HMessage.error('获取题目详情失败')
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="question-detail-page">
    <div v-if="loading" class="loading-state">正在加载题目详情...</div>

    <div v-else-if="!detail" class="empty-state">
      <div class="empty-icon">📭</div>
      <div class="empty-text">未找到题目详情</div>
      <HButton type="primary" @click="goBack">返回报告</HButton>
    </div>

    <div v-else class="detail-content">
      <!-- Header -->
      <div class="detail-header">
        <button class="back-btn" @click="goBack">← 返回报告</button>
        <h2 class="detail-title">题目详情</h2>
        <div v-if="detail.skill_name" class="detail-skill">{{ detail.skill_name }}</div>
      </div>

      <!-- Question content -->
      <div class="section">
        <h3 class="section-label">题目</h3>
        <div class="section-body question-text">{{ detail.content }}</div>
      </div>

      <!-- User answer -->
      <div class="section">
        <h3 class="section-label">我的答案</h3>
        <div class="section-body user-answer">
          {{ detail.user_answer || '未作答' }}
        </div>
      </div>

      <!-- Score and feedback -->
      <div class="section score-section">
        <div class="score-header">
          <h3 class="section-label">AI 评分</h3>
          <div class="score-badge" :style="{ background: scoreColor }">
            {{ detail.score }}/10
          </div>
        </div>
        <div class="section-body feedback-text" v-html="renderMarkdown(detail.feedback)"></div>
      </div>

      <!-- Reference answer -->
      <div v-if="detail.reference_answer" class="section">
        <h3 class="section-label">参考答案</h3>
        <div class="section-body reference-text" v-html="renderMarkdown(detail.reference_answer)"></div>
      </div>

      <!-- Back button -->
      <div class="detail-actions">
        <HButton type="primary" size="large" @click="goBack">返回报告</HButton>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.question-detail-page {
  height: 100%;
  overflow-y: auto;
  padding: 32px 40px;
}

.loading-state {
  text-align: center;
  padding: 80px 0;
  color: var(--color-text-secondary);
}

.empty-state {
  text-align: center;
  padding: 80px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;

  .empty-icon {
    font-size: 48px;
    opacity: 0.4;
  }

  .empty-text {
    color: var(--color-text-tertiary);
  }
}

.detail-content {
  max-width: 720px;
}

.detail-header {
  margin-bottom: 32px;

  .back-btn {
    background: none;
    border: none;
    color: var(--color-primary);
    cursor: pointer;
    font-size: 14px;
    font-family: inherit;
    padding: 0;
    margin-bottom: 16px;

    &:hover {
      text-decoration: underline;
    }
  }

  .detail-title {
    font-size: 24px;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0 0 8px;
  }

  .detail-skill {
    font-size: 14px;
    color: var(--color-text-secondary);
  }
}

.section {
  margin-bottom: 24px;

  .section-label {
    font-size: 14px;
    font-weight: 600;
    color: var(--color-text-secondary);
    margin: 0 0 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .section-body {
    font-size: 15px;
    line-height: 1.8;
    color: var(--color-text-primary);
    background: var(--color-bg-secondary);
    padding: 16px 20px;
    border-radius: var(--radius-md);
    white-space: pre-wrap;
  }
}

.score-section {
  .score-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }

  .score-badge {
    font-size: 14px;
    font-weight: 700;
    color: white;
    padding: 4px 12px;
    border-radius: 16px;
  }

  .feedback-text {
    :deep(p) {
      margin: 0 0 8px;
      &:last-child { margin-bottom: 0; }
    }
  }
}

.reference-text {
  border-left: 3px solid var(--color-primary);
  :deep(p) {
    margin: 0 0 8px;
    &:last-child { margin-bottom: 0; }
  }
}

.detail-actions {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--color-border);
}
</style>
```

- [ ] **Step 2: 验证构建**

Run: `cd src/frontend && npm run build 2>&1 | tail -5`
Expected: 构建成功

- [ ] **Step 3: Commit**

```bash
git add src/frontend/src/pages/interview/questionDetailPage/questionDetailPage.vue
git commit -m "feat(evaluation): add question detail page"
```

---

### Task 10: 前端 — 注册路由和导出

**Files:**
- Modify: `src/frontend/src/pages/interview/index.ts`
- Modify: `src/frontend/src/router/index.ts`

- [ ] **Step 1: 修改 index.ts 添加导出**

找到 `src/frontend/src/pages/interview/index.ts`，当前内容为：

```typescript
export { default as Interview } from './interview.vue'
export { default as InterviewDefault } from './defaultPage/defaultPage.vue'
export { default as InterviewChat } from './chatPage/chatPage.vue'
export { default as InterviewReport } from './reportPage/reportPage.vue'
export { default as InterviewLearning } from './learningPage/learningPage.vue'
export { default as InterviewHub } from './hubPage/hubPage.vue'
```

替换为：
```typescript
export { default as Interview } from './interview.vue'
export { default as InterviewDefault } from './defaultPage/defaultPage.vue'
export { default as InterviewChat } from './chatPage/chatPage.vue'
export { default as InterviewReport } from './reportPage/reportPage.vue'
export { default as InterviewLearning } from './learningPage/learningPage.vue'
export { default as InterviewHub } from './hubPage/hubPage.vue'
export { default as InterviewQuestionDetail } from './questionDetailPage/questionDetailPage.vue'
```

- [ ] **Step 2: 修改 router/index.ts 添加 import**

找到 router/index.ts 的 import 行（约第 30 行）：
```typescript
import { Interview, InterviewDefault, InterviewChat, InterviewReport, InterviewLearning, InterviewHub } from '../pages/interview'
```

替换为：
```typescript
import { Interview, InterviewDefault, InterviewChat, InterviewReport, InterviewLearning, InterviewHub, InterviewQuestionDetail } from '../pages/interview'
```

- [ ] **Step 3: 在路由 children 中添加题目详情路由**

找到 interview 路由的 children 数组中 `learning` 路由之后（约第 239 行），添加：

```typescript
          {
            path: 'question/:questionId',
            name: 'interviewQuestionDetail',
            component: InterviewQuestionDetail,
          },
```

- [ ] **Step 4: 验证构建**

Run: `cd src/frontend && npm run build 2>&1 | tail -5`
Expected: 构建成功

- [ ] **Step 5: Commit**

```bash
git add src/frontend/src/pages/interview/index.ts src/frontend/src/router/index.ts
git commit -m "feat(evaluation): register question detail route"
```

---

### Task 11: PDF 服务 — 扩展逐题内容

**Files:**
- Modify: `src/backend/kirinchat/common/export/pdf_service.py`

- [ ] **Step 1: 在 generate_evaluation_report 中添加逐题详情页**

找到 `generate_evaluation_report` 方法（约第 34-46 行）：

```python
    @classmethod
    def generate_evaluation_report(cls, report_data: dict, skill_name: str, output_path: str) -> str:
        cls._register_font()
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        cls._draw_cover(c, width, height, "面试评估报告", "Interview Report")
        c.showPage()
        cls._draw_score_overview(c, width, height, report_data, skill_name)
        c.showPage()
        cls._draw_summary_page(c, width, height, report_data)
        c.showPage()
        c.save()
        return output_path
```

替换为：
```python
    @classmethod
    def generate_evaluation_report(cls, report_data: dict, skill_name: str, output_path: str) -> str:
        cls._register_font()
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        cls._draw_cover(c, width, height, "面试评估报告", "Interview Report")
        c.showPage()
        cls._draw_score_overview(c, width, height, report_data, skill_name)
        c.showPage()
        # 逐题详情（在总结之前）
        question_details = report_data.get("question_details", [])
        if question_details:
            cls._draw_question_details(c, width, height, question_details)
            c.showPage()
        cls._draw_summary_page(c, width, height, report_data)
        c.showPage()
        c.save()
        return output_path
```

- [ ] **Step 2: 在 _draw_score_overview 方法之后添加 _draw_question_details 方法**

找到 `_draw_score_overview` 方法结束（约第 102 行），在其后添加：

```python
    @classmethod
    def _draw_question_details(cls, c, width, height, question_details):
        """绘制逐题评估详情页，每题显示得分、反馈和参考答案。"""
        cls._register_font()
        y = height - 80

        style = ParagraphStyle(
            "question_body",
            fontName=cls.FONT_NAME,
            fontSize=11,
            leading=16,
        )
        style_bold = ParagraphStyle(
            "question_label",
            fontName=cls.FONT_NAME,
            fontSize=11,
            leading=16,
            textColor=HexColor("#555555"),
        )

        for i, q in enumerate(question_details):
            # 每题最少需要 120pt 空间，不够则换页
            if y < 150:
                c.showPage()
                y = height - 80

            # 题目标题
            c.setFont(cls.FONT_NAME, 14)
            c.setFillColor(HexColor("#333333"))
            content = q.get("content", "")
            score = q.get("score", 0)
            c.drawString(2 * cm, y, f"Q{i + 1}: {content[:60]}{'...' if len(content) > 60 else ''}")
            c.setFont(cls.FONT_NAME, 12)
            score_color = "#4CAF50" if score >= 8 else "#FF9800" if score >= 6 else "#F44336"
            c.setFillColor(HexColor(score_color))
            c.drawRightString(width - 2 * cm, y, f"{score}/10")
            y -= 25

            # 反馈
            feedback = q.get("feedback", "")
            if feedback:
                c.setFillColor(HexColor("#333333"))
                c.setFont(cls.FONT_NAME, 11)
                c.drawString(2 * cm, y, "反馈:")
                y -= 18
                para = Paragraph(feedback, style)
                pw, ph = para.wrap(width - 4 * cm, 200)
                para.drawOn(c, 2 * cm, y - ph)
                y -= ph + 10

            # 参考答案
            ref = q.get("reference_answer", "")
            if ref:
                if y < 80:
                    c.showPage()
                    y = height - 80
                c.setFillColor(HexColor("#1976D2"))
                c.setFont(cls.FONT_NAME, 11)
                c.drawString(2 * cm, y, "参考答案:")
                y -= 18
                c.setFillColor(HexColor("#333333"))
                para = Paragraph(ref, style)
                pw, ph = para.wrap(width - 4 * cm, 200)
                para.drawOn(c, 2 * cm, y - ph)
                y -= ph + 20

            # 分隔线
            if i < len(question_details) - 1:
                c.setStrokeColor(HexColor("#E0E0E0"))
                c.line(2 * cm, y, width - 2 * cm, y)
                y -= 15
```

- [ ] **Step 3: 修改 download_evaluation_pdf 传入 question_details**

找到 `src/backend/kirinchat/api/v1/interview.py` 中的 `download_evaluation_pdf` 函数（约第 491-521 行）：

```python
@router.get("/interview/evaluation/{evaluation_id}/pdf")
async def download_evaluation_pdf(evaluation_id: str, login_user: UserPayload = Depends(get_login_user)):
    """下载面试评估报告 PDF。"""
    try:
        report = await EvaluationService.get_report_by_id(evaluation_id)
        if not report:
            return resp_500(message="评估报告不存在")

        from kirinchat.api.services.skill import SkillService
        from kirinchat.common.export.pdf_service import PdfService

        session = await InterviewService.get_session(report.session_id)
        skill = SkillService.get_skill_by_id(session.skill_id) if session else None
        skill_name = skill.get("name", "未知") if skill else "未知"

        report_data = {
            "total_score": report.total_score,
            "category_scores": report.category_scores,
            "summary": report.summary,
            "strengths": report.strengths,
            "improvements": report.improvements,
        }

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = f.name

        PdfService.generate_evaluation_report(report_data, skill_name, output_path)
        return FileResponse(output_path, filename=f"evaluation_{evaluation_id}.pdf", media_type="application/pdf")
    except Exception as e:
        logger.exception("Download evaluation PDF failed")
        return resp_500(message=str(e))
```

替换为：
```python
@router.get("/interview/evaluation/{evaluation_id}/pdf")
async def download_evaluation_pdf(evaluation_id: str, login_user: UserPayload = Depends(get_login_user)):
    """下载面试评估报告 PDF（含逐题详情）。"""
    try:
        report = await EvaluationService.get_report_by_id(evaluation_id)
        if not report:
            return resp_500(message="评估报告不存在")

        from kirinchat.api.services.skill import SkillService
        from kirinchat.common.export.pdf_service import PdfService

        session = await InterviewService.get_session(report.session_id)
        skill = SkillService.get_skill_by_id(session.skill_id) if session else None
        skill_name = skill.get("name", "未知") if skill else "未知"

        # 获取逐题详情
        details = await EvaluationService.get_details_by_evaluation(evaluation_id)
        questions = await InterviewService.get_session_questions(report.session_id) if session else []
        q_map = {q.id: q for q in questions}

        question_details = []
        for d in details:
            q = q_map.get(d.question_id)
            question_details.append({
                "content": q.content if q else "",
                "user_answer": q.user_answer if q else "",
                "score": d.score,
                "feedback": d.feedback,
                "reference_answer": d.reference_answer,
            })

        report_data = {
            "total_score": report.total_score,
            "category_scores": report.category_scores,
            "summary": report.summary,
            "strengths": report.strengths,
            "improvements": report.improvements,
            "question_details": question_details,
        }

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = f.name

        PdfService.generate_evaluation_report(report_data, skill_name, output_path)
        return FileResponse(output_path, filename=f"evaluation_{evaluation_id}.pdf", media_type="application/pdf")
    except Exception as e:
        logger.exception("Download evaluation PDF failed")
        return resp_500(message=str(e))
```

- [ ] **Step 4: 验证 Python 语法**

Run: `cd "D:/HuaweiMoveData/Users/28966/Desktop/项目DEMO/KirinChat/src/backend" && python -c "from kirinchat.common.export.pdf_service import PdfService; from kirinchat.api.v1.interview import router; print('OK')"`
Expected: OK

- [ ] **Step 5: Commit**

```bash
git add src/backend/kirinchat/common/export/pdf_service.py src/backend/kirinchat/api/v1/interview.py
git commit -m "feat(evaluation): extend PDF with per-question details"
```
