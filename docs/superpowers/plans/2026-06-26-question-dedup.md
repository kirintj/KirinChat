# 历史题目去重 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 出题时排除该用户在同技能方向所有历史 session 中已问过的 MAIN 类型题目

**Architecture:** 在 DAO 层新增 JOIN 查询获取历史题目 content，Agent 层将历史题目合并到现有去重列表，API 层传入 `user_id`。改动范围小且集中在 4 个文件，无 schema 变更。

**Tech Stack:** Python, SQLModel/SQLAlchemy, FastAPI

---

## 文件结构

| 文件 | 职责 |
|------|------|
| `src/backend/kirinchat/database/dao/interview.py` | 数据访问层，新增 `select_main_questions_by_user_skill` |
| `src/backend/kirinchat/api/services/interview.py` | 业务编排层，新增 `get_historical_questions` |
| `src/backend/kirinchat/core/agents/interview_agent.py` | 出题 Agent，修改两个生成方法合并历史题目 |
| `src/backend/kirinchat/api/v1/interview.py` | API 端点，传入 `login_user.user_id` |

---

### Task 1: DAO 层 — 新增历史题目查询

**Files:**
- Modify: `src/backend/kirinchat/database/dao/interview.py:78-118`

- [ ] **Step 1: 在 `InterviewQuestionDao` 类末尾添加新方法**

在 `update_question_score` 方法之后、`class EvaluationReportDao` 之前插入：

```python
from sqlmodel import select, update
# 新增导入（加入文件头部的 import 区域）：
from sqlalchemy import and_

# InterviewQuestionDao 类中新增方法：
@classmethod
async def select_main_questions_by_user_skill(
    cls, user_id: str, skill_id: str, exclude_session_id: str, limit: int = 50
) -> list:
    """查询同用户同技能方向其他 session 的历史 MAIN 题目。

    通过 JOIN interview_session 表筛选 user_id 和 skill_id，
    排除当前 session，按创建时间倒序返回最近 limit 条 ORM 对象。
    """
    with session_getter() as session:
        statement = (
            select(InterviewQuestionTable)
            .join(
                InterviewSessionTable,
                InterviewQuestionTable.session_id == InterviewSessionTable.id,
            )
            .where(
                and_(
                    InterviewSessionTable.user_id == user_id,
                    InterviewSessionTable.skill_id == skill_id,
                    InterviewQuestionTable.type == "MAIN",
                    InterviewQuestionTable.session_id != exclude_session_id,
                )
            )
            .order_by(InterviewQuestionTable.create_time.desc())
            .limit(limit)
        )
        result = session.exec(statement).all()
        return list(result)
```

- [ ] **Step 2: 在文件头部添加 `and_` 导入**

在现有 `from sqlmodel import select, update` 行下方添加：

```python
from sqlalchemy import and_
```

- [ ] **Step 3: 验证语法**

Run: `cd src/backend && python -c "from kirinchat.database.dao.interview import InterviewQuestionDao; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add src/backend/kirinchat/database/dao/interview.py
git commit -m "feat(dao): add select_main_questions_by_user_skill for cross-session dedup"
```

---

### Task 2: Service 层 — 新增历史题目编排方法

**Files:**
- Modify: `src/backend/kirinchat/api/services/interview.py:57-85`

- [ ] **Step 1: 在 `InterviewService` 类的 `calculate_progress` 方法之后添加新方法**

在 `src/backend/kirinchat/api/services/interview.py` 中，找到 `calculate_progress` 方法末尾（`return {"current": answered, "total": total}` 之后），插入：

```python
@classmethod
async def get_historical_questions(
    cls, user_id: str, skill_id: str, exclude_session_id: str
) -> list[str]:
    """获取同技能方向其他 session 的历史题目内容列表。

    用于出题时的跨 session 去重，返回值直接传给 _get_dedup_prompt。
    """
    questions = await InterviewQuestionDao.select_main_questions_by_user_skill(
        user_id, skill_id, exclude_session_id
    )
    return [q.content for q in questions]
```

- [ ] **Step 2: 验证语法**

Run: `cd src/backend && python -c "from kirinchat.api.services.interview import InterviewService; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/backend/kirinchat/api/services/interview.py
git commit -m "feat(service): add get_historical_questions for cross-session dedup"
```

---

### Task 3: Agent 层 — 修改出题方法合并历史题目

**Files:**
- Modify: `src/backend/kirinchat/core/agents/interview_agent.py:50-113`（`generate_first_question`）
- Modify: `src/backend/kirinchat/core/agents/interview_agent.py:170-246`（`generate_next_question`）

- [ ] **Step 1: 修改 `generate_first_question` 方法签名，新增 `user_id` 参数**

找到方法定义：
```python
async def generate_first_question(self, session_id: str, difficulty: str = "MEDIUM") -> InterviewQuestionTable:
```

替换为：
```python
async def generate_first_question(self, session_id: str, user_id: str, difficulty: str = "MEDIUM") -> InterviewQuestionTable:
```

- [ ] **Step 2: 在 `generate_first_question` 中添加历史题目查询逻辑**

找到这一行（约 line 69）：
```python
        existing_topics = [q.content for q in existing_questions]
```

在其下方插入：
```python
        # 跨 session 去重：获取同技能方向其他 session 的历史题目
        skill_id = self.skill.get("id", "")
        historical_topics = await InterviewService.get_historical_questions(
            user_id, skill_id, exclude_session_id=session_id
        )
        # 合并当前 session 和历史题目，dict.fromkeys 保序去重
        all_topics = list(dict.fromkeys(existing_topics + historical_topics))
```

找到这一行：
```python
        dedup_section = self._get_dedup_prompt(existing_topics)
```

替换为：
```python
        dedup_section = self._get_dedup_prompt(all_topics)
```

- [ ] **Step 3: 修改 `generate_next_question` 方法签名，新增 `user_id` 参数**

找到方法定义：
```python
async def generate_next_question(self, session_id: str, difficulty: str = "MEDIUM") -> InterviewQuestionTable | None:
```

替换为：
```python
async def generate_next_question(self, session_id: str, user_id: str, difficulty: str = "MEDIUM") -> InterviewQuestionTable | None:
```

- [ ] **Step 4: 在 `generate_next_question` 中添加历史题目查询逻辑**

找到这一行（约 line 200）：
```python
        existing_topics = [q.content for q in main_questions]
```

在其下方插入：
```python
        # 跨 session 去重：获取同技能方向其他 session 的历史题目
        skill_id = self.skill.get("id", "")
        historical_topics = await InterviewService.get_historical_questions(
            user_id, skill_id, exclude_session_id=session_id
        )
        # 合并当前 session 和历史题目，dict.fromkeys 保序去重
        all_topics = list(dict.fromkeys(existing_topics + historical_topics))
```

找到这一行：
```python
        dedup_section = self._get_dedup_prompt(existing_topics)
```

替换为：
```python
        dedup_section = self._get_dedup_prompt(all_topics)
```

- [ ] **Step 5: 验证语法**

Run: `cd src/backend && python -c "from kirinchat.core.agents.interview_agent import InterviewAgent; print('OK')"`
Expected: `OK`

- [ ] **Step 6: Commit**

```bash
git add src/backend/kirinchat/core/agents/interview_agent.py
git commit -m "feat(agent): merge historical questions into dedup list"
```

---

### Task 4: API 层 — 端点传入 user_id

**Files:**
- Modify: `src/backend/kirinchat/api/v1/interview.py:110-113`（`/interview/start`）
- Modify: `src/backend/kirinchat/api/v1/interview.py:167-170`（`/interview/answer`）

- [ ] **Step 1: 修改 `/interview/start` 端点的 agent 调用**

找到这一段：
```python
        first_question = await agent.generate_first_question(
            session_id=session.id,
            difficulty=req.difficulty,
        )
```

替换为：
```python
        first_question = await agent.generate_first_question(
            session_id=session.id,
            user_id=login_user.user_id,
            difficulty=req.difficulty,
        )
```

- [ ] **Step 2: 修改 `/interview/answer` 端点的 agent 调用**

找到这一段：
```python
            next_q = await agent.generate_next_question(
                session_id=req.session_id,
                difficulty=session.difficulty,
            )
```

替换为：
```python
            next_q = await agent.generate_next_question(
                session_id=req.session_id,
                user_id=login_user.user_id,
                difficulty=session.difficulty,
            )
```

- [ ] **Step 3: 验证语法**

Run: `cd src/backend && python -c "from kirinchat.api.v1.interview import router; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add src/backend/kirinchat/api/v1/interview.py
git commit -m "feat(api): pass login_user.user_id to agent for cross-session dedup"
```

---

### Task 5: 集成验证

- [ ] **Step 1: 全量导入验证**

Run: `cd src/backend && python -c "
from kirinchat.database.dao.interview import InterviewQuestionDao
from kirinchat.api.services.interview import InterviewService
from kirinchat.core.agents.interview_agent import InterviewAgent
from kirinchat.api.v1.interview import router
print('All imports OK')
"`
Expected: `All imports OK`

- [ ] **Step 2: 检查无遗留语法错误**

Run: `cd src/backend && python -m py_compile kirinchat/database/dao/interview.py && python -m py_compile kirinchat/api/services/interview.py && python -m py_compile kirinchat/core/agents/interview_agent.py && python -m py_compile kirinchat/api/v1/interview.py && echo "All files compile OK"`
Expected: `All files compile OK`

- [ ] **Step 3: 最终 Commit（如有遗漏修复）**

```bash
git add -A && git commit -m "feat: complete cross-session question deduplication"
```
