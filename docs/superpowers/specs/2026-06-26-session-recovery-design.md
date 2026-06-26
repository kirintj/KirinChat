# 未完成面试恢复设计规范

**日期**: 2026-06-26
**状态**: 已批准
**范围**: 当 localStorage 丢失时，从后端 API 重建面试对话状态

---

## 1. 背景与目标

KirinChat 的面试恢复依赖 Pinia store 的 localStorage 持久化。如果用户清除浏览器数据或换设备，面试对话历史无法恢复。

**目标**：在 chatPage 加载时，当 store 无数据但 URL 有 sessionId，从后端 API 获取 session 详情并重建完整的对话状态。

**范围**：修改后端 API 响应补充缺失字段 + 前端 chatPage 恢复逻辑。

---

## 2. 改动范围

### 改动文件

| 文件 | 变更 |
|------|------|
| `src/backend/kirinchat/api/v1/interview.py` | `_session_to_resp` 补充 difficulty；`_question_to_resp` 补充 user_answer |
| `src/backend/kirinchat/schemas/interview.py` | `InterviewSessionResp` 添加 difficulty；`QuestionResp` 添加 user_answer |
| `src/frontend/src/apis/interview.ts` | `SessionInfo` 添加 difficulty；`QuestionInfo` 添加 user_answer |
| `src/frontend/src/pages/interview/chatPage/chatPage.vue` | onMounted 中添加服务端恢复逻辑 |

### 不变的部分

- 数据库模型：无字段变更（字段已存在）
- DAO 层：无变更
- Service 层：无变更
- Pinia store：无变更

---

## 3. 设计方案

### 3.1 后端：补充 API 响应字段

**`_session_to_resp` 补充 difficulty：**
```python
def _session_to_resp(s) -> InterviewSessionResp:
    return InterviewSessionResp(
        id=s.id,
        skill_id=s.skill_id,
        status=s.status,
        difficulty=s.difficulty,  # 新增
        progress={...},
    )
```

**`_question_to_resp` 补充 user_answer：**
```python
def _question_to_resp(q) -> QuestionResp:
    return QuestionResp(
        id=q.id,
        type=q.type,
        category=q.category,
        content=q.content,
        user_answer=q.user_answer,  # 新增
    )
```

**Schema 补充：**
- `InterviewSessionResp` 添加 `difficulty: Optional[str] = None`
- `QuestionResp` 添加 `user_answer: Optional[str] = None`

### 3.2 前端：chatPage 恢复逻辑

在 `onMounted` 中，当 store 无活跃面试且 URL 有 sessionId 时：

```typescript
const res = await getSessionDetailAPI(sessionId)
const { session, questions } = res.data.data

if (session.status === 'COMPLETED') {
  router.replace({ path: '/interview/report', query: { sessionId } })
  return
}

// 从后端数据重建面试状态
interviewStore.sessionId = session.id
interviewStore.skillId = session.skill_id
interviewStore.difficulty = session.difficulty
interviewStore.questionCount = session.progress.total
interviewStore.status = 'IN_PROGRESS'

// 重建 messages 数组
const messages = []
let currentQ = null
for (const q of questions) {
  messages.push({ role: 'interviewer', content: q.content })
  if (q.user_answer) {
    messages.push({ role: 'candidate', content: q.user_answer })
  } else if (!currentQ) {
    currentQ = q  // 第一个未回答的题目
  }
}
interviewStore.messages = messages
interviewStore.currentQuestion = currentQ
interviewStore.progress = session.progress
```

### 3.3 skill_name 处理

`skill_name` 不在 session 详情中。两个选项：
- **选项 A**：用 `skillId` 调用 `getSkillByIdAPI` 获取名称（额外请求）
- **选项 B**：恢复时 skillName 暂时为空，用户重新选择时再填充

推荐选项 A，使用已有的 skill 列表 API。

---

## 4. 已知限制

- 恢复后计时器从 0 开始（不恢复之前的答题时间）
- 草稿数据仍依赖 localStorage（如果 localStorage 丢失，草稿也丢失）
- skill_name 需要额外一次 API 调用
