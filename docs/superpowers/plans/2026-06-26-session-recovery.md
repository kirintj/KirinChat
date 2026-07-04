# 未完成面试恢复 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 当 localStorage 丢失时，从后端 API 重建面试对话状态，支持跨设备恢复

**Architecture:** 后端补充 API 响应字段（difficulty、user_answer），前端 chatPage 在 onMounted 中从 getSessionDetail 重建 messages 数组和面试状态

**Tech Stack:** Python/FastAPI, Vue 3 Composition API, TypeScript

---

### Task 1: 后端 Schema — 补充缺失字段

**Files:**
- Modify: `src/backend/kirinchat/schemas/interview.py:46-51,66-71`

- [ ] **Step 1: QuestionResp 添加 user_answer 字段**

找到 `QuestionResp` 类（第 46-51 行）：
```python
class QuestionResp(BaseModel):
    """题目响应"""
    id: str = Field(..., description="题目ID")
    type: str = Field(..., description="题目类型")
    category: str = Field(..., description="题目分类")
    content: str = Field(..., description="题目内容")
```

替换为：
```python
class QuestionResp(BaseModel):
    """题目响应"""
    id: str = Field(..., description="题目ID")
    type: str = Field(..., description="题目类型")
    category: str = Field(..., description="题目分类")
    content: str = Field(..., description="题目内容")
    user_answer: Optional[str] = Field(None, description="用户答案（未答则为 null）")
```

- [ ] **Step 2: InterviewSessionResp 添加 difficulty 字段**

找到 `InterviewSessionResp` 类（第 66-71 行）：
```python
class InterviewSessionResp(BaseModel):
    """面试会话响应"""
    id: str = Field(..., description="会话ID")
    skill_id: str = Field(..., description="技能ID")
    status: str = Field(..., description="会话状态")
    progress: Dict[str, int] = Field(default={}, description="进度信息")
```

替换为：
```python
class InterviewSessionResp(BaseModel):
    """面试会话响应"""
    id: str = Field(..., description="会话ID")
    skill_id: str = Field(..., description="技能ID")
    status: str = Field(..., description="会话状态")
    difficulty: Optional[str] = Field(None, description="难度等级")
    progress: Dict[str, int] = Field(default={}, description="进度信息")
```

- [ ] **Step 3: 验证 Python 语法**

Run: `cd "D:/HuaweiMoveData/Users/28966/Desktop/项目DEMO/KirinChat/src/backend" && python -c "from kirinchat.schemas.interview import QuestionResp, InterviewSessionResp; print('OK')"`
Expected: OK

- [ ] **Step 4: Commit**

```bash
git add src/backend/kirinchat/schemas/interview.py
git commit -m "feat(interview): add difficulty and user_answer to response schemas"
```

---

### Task 2: 后端 API — 补充 helper 函数映射

**Files:**
- Modify: `src/backend/kirinchat/api/v1/interview.py:39-56`

- [ ] **Step 1: 修改 _question_to_resp 映射 user_answer**

找到 `_question_to_resp` 函数（第 39-46 行）：
```python
def _question_to_resp(q) -> QuestionResp:
    """Convert an InterviewQuestionTable to a QuestionResp."""
    return QuestionResp(
        id=q.id,
        type=q.type,
        category=q.category,
        content=q.content,
    )
```

替换为：
```python
def _question_to_resp(q) -> QuestionResp:
    """Convert an InterviewQuestionTable to a QuestionResp."""
    return QuestionResp(
        id=q.id,
        type=q.type,
        category=q.category,
        content=q.content,
        user_answer=q.user_answer,
    )
```

- [ ] **Step 2: 修改 _session_to_resp 映射 difficulty**

找到 `_session_to_resp` 函数（第 49-56 行）：
```python
def _session_to_resp(session) -> InterviewSessionResp:
    """Convert an InterviewSessionTable to an InterviewSessionResp."""
    return InterviewSessionResp(
        id=session.id,
        skill_id=session.skill_id,
        status=session.status,
        progress={},
    )
```

替换为：
```python
def _session_to_resp(session) -> InterviewSessionResp:
    """Convert an InterviewSessionTable to an InterviewSessionResp."""
    return InterviewSessionResp(
        id=session.id,
        skill_id=session.skill_id,
        status=session.status,
        difficulty=session.difficulty,
        progress={},
    )
```

- [ ] **Step 3: 验证 Python 语法**

Run: `cd "D:/HuaweiMoveData/Users/28966/Desktop/项目DEMO/KirinChat/src/backend" && python -c "from kirinchat.api.v1.interview import router; print('OK')"`
Expected: OK

- [ ] **Step 4: Commit**

```bash
git add src/backend/kirinchat/api/v1/interview.py
git commit -m "feat(interview): map difficulty and user_answer in API helpers"
```

---

### Task 3: 前端接口 — 补充 TypeScript 类型

**Files:**
- Modify: `src/frontend/src/apis/interview.ts:37-49`

- [ ] **Step 1: InterviewQuestion 添加 user_answer**

找到 `InterviewQuestion` 接口（第 37-42 行）：
```typescript
export interface InterviewQuestion {
  id: string
  type: string
  category: string
  content: string
}
```

替换为：
```typescript
export interface InterviewQuestion {
  id: string
  type: string
  category: string
  content: string
  user_answer: string | null
}
```

- [ ] **Step 2: InterviewSession 添加 difficulty**

找到 `InterviewSession` 接口（第 44-49 行）：
```typescript
export interface InterviewSession {
  id: string
  skill_id: string
  status: string
  progress: { current: number; total: number }
}
```

替换为：
```typescript
export interface InterviewSession {
  id: string
  skill_id: string
  status: string
  difficulty: string | null
  progress: { current: number; total: number }
}
```

- [ ] **Step 3: Commit**

```bash
git add src/frontend/src/apis/interview.ts
git commit -m "feat(interview): add difficulty and user_answer to TS interfaces"
```

---

### Task 4: 前端 chatPage — 实现服务端恢复逻辑

**Files:**
- Modify: `src/frontend/src/pages/interview/chatPage/chatPage.vue:152-177`

- [ ] **Step 1: 修改 onMounted 的恢复逻辑**

找到 `onMounted` 中的 session 恢复逻辑（第 152-177 行）：
```typescript
onMounted(async () => {
  // If no active interview, try to restore from route query
  if (!interviewStore.isActive && !interviewStore.isCompleted) {
    const sessionId = router.currentRoute.value.query.sessionId as string
    if (sessionId) {
      try {
        const res = await getSessionDetailAPI(sessionId)
        if (res.data.status_code === 200 && res.data.data) {
          // Redirect to report if completed
          const session = res.data.data.session
          if (session.status === 'COMPLETED') {
            router.replace({ path: '/interview/report', query: { sessionId } })
            return
          }
        }
      } catch { /* ignore */ }
    }
    // No active session, go back to selection
    router.replace('/interview')
    return
  }

  restoreDraft() // 页面加载时恢复草稿
  scrollBottom()
  startTimer() // 启动答题计时器
})
```

替换为：
```typescript
onMounted(async () => {
  // 如果没有活跃面试，尝试从 URL sessionId 恢复
  if (!interviewStore.isActive && !interviewStore.isCompleted) {
    const sessionId = router.currentRoute.value.query.sessionId as string
    if (sessionId) {
      try {
        const res = await getSessionDetailAPI(sessionId)
        if (res.data.status_code === 200 && res.data.data) {
          const { session, questions } = res.data.data

          // 已完成的面试跳转到报告页
          if (session.status === 'COMPLETED') {
            router.replace({ path: '/interview/report', query: { sessionId } })
            return
          }

          // 从后端数据重建面试状态（服务端恢复）
          interviewStore.sessionId = session.id
          interviewStore.skillId = session.skill_id
          interviewStore.difficulty = session.difficulty || 'MEDIUM'
          interviewStore.questionCount = session.progress.total
          interviewStore.status = 'IN_PROGRESS'

          // 重建对话历史：遍历题目，已回答的生成 interviewer+candidate 消息对
          const restoredMessages: { role: 'interviewer' | 'candidate'; content: string }[] = []
          let restoredQuestion = null
          for (const q of questions) {
            restoredMessages.push({ role: 'interviewer', content: q.content })
            if (q.user_answer) {
              restoredMessages.push({ role: 'candidate', content: q.user_answer })
            } else if (!restoredQuestion) {
              restoredQuestion = q // 第一个未回答的题目作为当前题
            }
          }
          interviewStore.messages = restoredMessages
          interviewStore.currentQuestion = restoredQuestion
          interviewStore.progress = session.progress
        }
      } catch { /* ignore */ }
    }
    // 恢复失败，回到选择页
    if (!interviewStore.isActive) {
      router.replace('/interview')
      return
    }
  }

  restoreDraft() // 页面加载时恢复草稿
  scrollBottom()
  startTimer() // 启动答题计时器
})
```

- [ ] **Step 2: 验证构建**

Run: `cd src/frontend && npm run build 2>&1 | tail -5`
Expected: 构建成功

- [ ] **Step 3: Commit**

```bash
git add src/frontend/src/pages/interview/chatPage/chatPage.vue
git commit -m "feat(interview): implement server-side session recovery in chatPage"
```
