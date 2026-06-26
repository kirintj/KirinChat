# 历史题目去重设计规范

**日期**: 2026-06-26
**状态**: 已批准
**范围**: 面试出题时排除同用户同技能方向的历史题目

---

## 1. 背景与目标

当前面试出题的去重机制仅限于**同一 session 内**的题目。用户多次练习同一技能方向时，可能反复抽到相同的题目。

**目标**：出题时排除该用户在**同技能方向**的所有历史 session 中已问过的 MAIN 类型题目。

**去重范围**：同用户 + 同技能方向 + 其他 session（排除当前 session）。

---

## 2. 改动范围

### 改动文件

| 文件 | 变更 |
|------|------|
| `src/backend/kirinchat/database/dao/interview.py` | 新增 `select_main_questions_by_user_skill` 查询方法 |
| `src/backend/kirinchat/api/services/interview.py` | 新增 `get_historical_questions` 编排方法 |
| `src/backend/kirinchat/core/agents/interview_agent.py` | `generate_first_question` 和 `generate_next_question` 新增 `user_id` 参数，合并历史题目到去重列表 |
| `src/backend/kirinchat/api/v1/interview.py` | `/interview/start` 和 `/interview/answer` 端点传入 `user.id` |

### 不变的部分

- `_get_dedup_prompt`：已是纯函数，无需修改
- `_select_category`：分类选择逻辑不变
- `generate_follow_up`：追问不涉及去重
- 数据库模型：无 schema 变更
- 前端：无变更

---

## 3. DAO 层变更

文件：`src/backend/kirinchat/database/dao/interview.py`

在 `InterviewQuestionDao` 类中新增方法：

```python
@classmethod
async def select_main_questions_by_user_skill(
    cls, user_id: str, skill_id: str, exclude_session_id: str, limit: int = 50
) -> list:
```

**查询逻辑**：
- JOIN `InterviewSessionTable`（通过 `session_id`）获取 `user_id` 和 `skill_id`
- WHERE 条件：`session.user_id = user_id` AND `session.skill_id = skill_id` AND `question.type = 'MAIN'` AND `question.session_id != exclude_session_id`
- ORDER BY `question.create_time DESC`
- LIMIT 50（避免 prompt 过长）
- 只返回 `content` 字段列表

**性能考量**：
- `interview_session` 表的 `user_id` 和 `skill_id` 字段已有索引（用于 `select_sessions_by_user` 查询）
- `interview_question` 表的 `session_id` 字段是外键，已有索引
- LIMIT 50 确保单次查询不会返回过多数据

---

## 4. Service 层变更

文件：`src/backend/kirinchat/api/services/interview.py`

在 `InterviewService` 类中新增方法：

```python
@staticmethod
async def get_historical_questions(
    user_id: str, skill_id: str, exclude_session_id: str
) -> list[str]:
    """获取同技能方向其他 session 的历史题目内容列表。
    
    用于出题时的跨 session 去重，返回值直接传给 _get_dedup_prompt。
    """
    questions = await InterviewQuestionDao.select_main_questions_by_user_skill(
        user_id, skill_id, exclude_session_id
    )
    return [q.content for q in questions]
```

---

## 5. Agent 层变更

文件：`src/backend/kirinchat/core/agents/interview_agent.py`

### 5.1 方法签名变更

`generate_first_question` 新增 `user_id` 参数：
```python
async def generate_first_question(self, session_id: str, user_id: str, difficulty: str = "MEDIUM"):
```

`generate_next_question` 新增 `user_id` 参数：
```python
async def generate_next_question(self, session_id: str, user_id: str, difficulty: str = "MEDIUM"):
```

### 5.2 去重逻辑变更

在两个方法中，在构建 `dedup_section` 之前，新增历史题目查询和合并：

```python
# 获取当前 session 题目（现有逻辑）
existing_topics = [q.content for q in existing_questions]

# 新增：获取同技能方向的历史题目
skill_id = self.skill.get("id", "")
historical_topics = await InterviewService.get_historical_questions(
    user_id, skill_id, exclude_session_id=session_id
)

# 合并去重列表，去重（set 去重后转回 list）
all_topics = list(set(existing_topics + historical_topics))
dedup_section = self._get_dedup_prompt(all_topics)
```

### 5.3 `_get_dedup_prompt` 不变

该方法已经是纯函数，接收 topic 列表并生成 prompt 文本，无需修改。

---

## 6. API 层变更

文件：`src/backend/kirinchat/api/v1/interview.py`

### 6.1 `/interview/start` 端点

现有代码已有 `user = Depends(get_login_user)`。修改 agent 调用：

```python
# 修改前
question = await agent.generate_first_question(session_id, difficulty=body.difficulty)

# 修改后
question = await agent.generate_first_question(session_id, user_id=user.id, difficulty=body.difficulty)
```

### 6.2 `/interview/answer` 端点

同理，修改 `generate_next_question` 调用：

```python
# 修改前
next_question = await agent.generate_next_question(session_id, difficulty=...)

# 修改后
next_question = await agent.generate_next_question(session_id, user_id=user.id, difficulty=...)
```

注意：`/interview/answer` 端点中 difficulty 来自 session 对象（`session.difficulty`），需在调用 `generate_next_question` 前从 session 中获取。检查现有代码确认 difficulty 的传递路径。

---

## 7. 已知限制

- 去重依赖 LLM 理解 prompt 中的"请避免重复"指令，不是精确匹配。如果题目表述差异较大，LLM 可能仍会出类似的题
- LIMIT 50 意味着只看最近 50 道历史题目。如果用户练习了非常多轮，最早的题目可能被"遗忘"
- 去重列表越长，prompt 越长，LLM 生成质量可能略有下降（50 道题约 500-1000 字，影响可控）
