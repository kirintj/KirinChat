# 评估报告增强设计规范

**日期**: 2026-06-26
**状态**: 已批准
**范围**: 持久化逐题反馈、题目详情页、PDF 导出

---

## 1. 背景与目标

当前评估流程中，LLM 已生成逐题 `feedback`，但后端只保存了 `score`，丢弃了反馈文字。报告页仅展示会话级分数，无逐题详情。

**目标**：
- 持久化逐题反馈（feedback）和参考答案（reference_answer）
- 新建题目详情页，展示每题的得分、AI 反馈、参考答案
- 报告页新增题目列表和 PDF 导出功能

**范围**：新建数据库表 + 改造评估服务 + 新增 API 端点 + 前端详情页 + PDF 导出

---

## 2. 改动范围

### 新增文件

| 文件 | 说明 |
|------|------|
| `src/frontend/src/pages/interview/questionDetailPage/questionDetailPage.vue` | 题目详情页 |

### 修改文件

| 文件 | 变更 |
|------|------|
| `src/backend/kirinchat/database/models/evaluation_question_detail.py` | 新建详情表模型 |
| `src/backend/kirinchat/database/__init__.py` | 注册新模型 |
| `src/backend/kirinchat/database/dao/evaluation_question_detail_dao.py` | 新建 DAO |
| `src/backend/kirinchat/api/services/evaluation.py` | 评估流程持久化逐题详情 |
| `src/backend/kirinchat/schemas/interview.py` | 新增详情响应 Schema |
| `src/backend/kirinchat/api/v1/interview.py` | 修改评估报告 API + 新增题目详情 API |
| `src/backend/kirinchat/common/export/pdf_service.py` | PDF 内容扩展 |
| `src/frontend/src/apis/interview.ts` | 新增题目详情 API 函数 |
| `src/frontend/src/pages/interview/reportPage/reportPage.vue` | 新增题目列表 + PDF 下载按钮 |
| `src/frontend/src/pages/interview/index.ts` | 注册新路由 |

### 不变的部分

- 面试流程（chatPage、agent）无变更
- 技能系统无变更
- 面试会话和题目表结构不变

---

## 3. 数据模型

### 3.1 新建 EvaluationQuestionDetailTable

```python
class EvaluationQuestionDetailTable(SQLModel, table=True):
    """评估逐题详情表"""
    __tablename__ = "evaluation_question_details"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    evaluation_id: str = Field(foreign_key="evaluation_reports.id", index=True)
    question_id: str = Field(foreign_key="interview_questions.id")
    score: int = Field(default=0, description="该题得分 (0-10)")
    feedback: str = Field(default="", description="AI 对该题答案的评价")
    reference_answer: str = Field(default="", description="参考答案")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### 3.2 DAO 方法

```python
class EvaluationQuestionDetailDao:
    @classmethod
    async def batch_create(cls, details: list[EvaluationQuestionDetailTable]) -> None
    """批量创建逐题详情"""

    @classmethod
    async def select_by_evaluation_id(cls, evaluation_id: str) -> list[EvaluationQuestionDetailTable]
    """按评估报告 ID 查询所有逐题详情"""

    @classmethod
    async def select_by_question_id(cls, question_id: str) -> EvaluationQuestionDetailTable | None
    """按题目 ID 查询单题详情"""
```

---

## 4. 评估流程改造

### 4.1 LLM Prompt 追加要求

在 `_build_evaluation_prompt()` 的输出格式要求中，每个 question_score 追加 `reference_answer` 字段：

```json
{
  "question_scores": [
    {"id": "...", "score": 8, "feedback": "...", "reference_answer": "标准答案..."}
  ]
}
```

### 4.2 数据持久化

`_merge_batch_results()` 收集逐题数据后：
1. 创建 `EvaluationQuestionDetailTable` 列表
2. 调用 `EvaluationQuestionDetailDao.batch_create()` 批量写入
3. 不再调用 `InterviewQuestionDao.update_question_score()`（score 改存详情表）

---

## 5. API 设计

### 5.1 修改：GET /interview/evaluation/{evaluation_id}

响应新增 `question_details` 字段：

```json
{
  "id": "...",
  "total_score": 78,
  "category_scores": {...},
  "summary": "...",
  "strengths": [...],
  "improvements": [...],
  "question_details": [
    {
      "question_id": "...",
      "content": "什么是闭包？",
      "user_answer": "闭包是...",
      "type": "MAIN",
      "category": "javascript-core",
      "score": 8,
      "feedback": "回答基本正确，但缺少对作用域链的解释",
      "reference_answer": "闭包是指函数与其词法环境的组合..."
    }
  ]
}
```

### 5.2 新增：GET /interview/question-detail/{question_id}

返回单题完整详情：

```json
{
  "question_id": "...",
  "session_id": "...",
  "content": "什么是闭包？",
  "user_answer": "闭包是...",
  "type": "MAIN",
  "category": "javascript-core",
  "score": 8,
  "feedback": "回答基本正确，但缺少对作用域链的解释",
  "reference_answer": "闭包是指函数与其词法环境的组合...",
  "skill_name": "前端基础"
}
```

---

## 6. 前端设计

### 6.1 报告页改动 (reportPage.vue)

在现有内容下方新增题目列表区域：

```
┌─────────────────────────────────────┐
│ 题目详情                            │
├─────────────────────────────────────┤
│ Q1: 什么是闭包? .............. 8/10 →│
│ Q2: 解释原型链 .............. 6/10 →│
│ Q3: Promise 的原理 .......... 9/10 →│
└─────────────────────────────────────┘
```

顶部操作栏新增"下载 PDF"按钮，调用已有端点。

### 6.2 新建详情页 (questionDetailPage.vue)

路由：`/interview/question/:questionId`

布局：
- 顶部：返回按钮 + "题目详情"标题
- 题目内容区：题目文字
- 我的答案区：用户提交的原文
- 评分区：得分圆环 + AI 反馈文字
- 参考答案区：LLM 生成的标准答案
- 底部：返回报告按钮

---

## 7. PDF 导出

扩展现有 `PdfService.generate_evaluation_report()`（基于 reportlab）：

- 输入 `report_data` dict 追加 `question_details` 字段
- PDF 内容顺序：总分 → 分类得分条 → 逐题详情（得分/反馈/参考答案）→ 总结 → 优势/改进
- 雷达图不嵌入 PDF（reportlab 绘制雷达图成本高），用已有的分类得分条替代
- 现有 `/interview/evaluation/{id}/pdf` 端点无需修改（只改 PdfService 内部实现）
- 在 `_draw_summary_page` 之前新增 `_draw_question_details` 方法，自动分页

---

## 8. 已知限制

- PDF 中不包含雷达图，用分类得分条替代（reportlab 绘制雷达图成本高）
- 参考答案由 LLM 生成，质量取决于模型能力
- 逐题详情在评估完成后才可用，评估期间无法查看
