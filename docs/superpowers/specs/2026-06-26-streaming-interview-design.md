# 面试流式输出设计规范

**日期**: 2026-06-26
**状态**: 已批准
**范围**: 面试提交答案后，AI 追问题和下一题通过 SSE 流式输出

---

## 1. 背景与目标

当前面试提交答案后，用户需要等待整个 LLM 响应完成才能看到结果（追问题 + 下一题），等待时间长且无反馈。

**目标**：将追问题和下一题的 LLM 输出改为 SSE 流式，用户可以看到文字逐步生成。

**范围**：新增后端 SSE 端点 + 修改前端消费逻辑。复用已有 SSE 基础设施。

---

## 2. 改动范围

### 改动文件

| 文件 | 变更 |
|------|------|
| `src/backend/kirinchat/api/v1/interview.py` | 新增 `/answer/stream` SSE 端点 |
| `src/backend/kirinchat/core/agents/interview_agent.py` | 新增流式版本的 follow-up 和 next-question 方法 |
| `src/frontend/src/apis/interview.ts` | 新增 `submitAnswerStreamAPI` SSE 消费函数 |
| `src/frontend/src/store/interview/index.ts` | 新增 `submitAnswerStream` action |
| `src/frontend/src/pages/interview/chatPage/chatPage.vue` | 调用流式 API 替代原 API |

### 不变的部分

- 原 `/api/v1/interview/answer` POST 端点保持不变（向后兼容）
- 数据库模型：无变更
- DAO 层：无变更
- Service 层：无变更

---

## 3. 设计方案

### 3.1 后端 SSE 端点

新增 `POST /api/v1/interview/answer/stream`，返回 `WatchedStreamingResponse`：

```python
@router.post("/answer/stream")
async def submit_answer_stream(req: InterviewAnswerReq, login_user: UserPayload):
    # 1. 保存用户答案（同原端点逻辑）
    # 2. 流式生成 follow-up
    #    - 用 astream() 调用 LLM
    #    - 每个 chunk 发送 SSE: {"type":"follow_up_chunk","data":{"chunk":"...","accumulated":"..."}}
    #    - 完成后保存到 DB
    # 3. 流式生成 next question
    #    - 同上，SSE type 为 "next_question_chunk"
    #    - 完成后保存到 DB
    # 4. 发送结束事件: {"type":"done","data":{"follow_up":{...},"next_question":{...},"is_completed":bool}}
```

### 3.2 Agent 流式方法

在 `InterviewAgent` 中新增两个流式方法：

- `stream_follow_up(session_id, question_id, user_answer)` → AsyncGenerator，流式生成追问题
- `stream_next_question(session_id, user_id, difficulty)` → AsyncGenerator，流式生成下一题

这两个方法复用现有 `ainvoke` 方法中的 prompt 构建逻辑，但调用 `self.conversation_model.astream()` 替代 `ainvoke()`，并使用 `yield` 返回 chunk。

### 3.3 前端 SSE 消费

```typescript
// apis/interview.ts
export function submitAnswerStreamAPI(
  data: InterviewAnswerRequest,
  onFollowUpChunk: (chunk: string, accumulated: string) => void,
  onNextQuestionChunk: (chunk: string, accumulated: string) => void,
  onDone: (result: { follow_up: any, next_question: any, is_completed: boolean }) => void,
  onError: (err: Error) => void,
) {
  const ctrl = new AbortController()
  fetchEventSource('/api/v1/interview/answer/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(data),
    signal: ctrl.signal,
    onmessage(msg) {
      const event = JSON.parse(msg.data)
      if (event.type === 'follow_up_chunk') onFollowUpChunk(event.data.chunk, event.data.accumulated)
      else if (event.type === 'next_question_chunk') onNextQuestionChunk(event.data.chunk, event.data.accumulated)
      else if (event.type === 'done') onDone(event.data)
    },
    onerror(err) { onError(err); ctrl.abort() },
  })
  return ctrl
}
```

### 3.4 Store 流式 action

```typescript
async function submitAnswerStream(answer: string) {
  // 1. 添加 candidate 消息
  // 2. 添加空的 follow-up 消气泡（role: 'interviewer', content: ''）
  // 3. 调用 SSE API，chunk 到达时更新 follow-up 消息的 content
  // 4. follow-up 完成后，添加空的 next-question 消气泡
  // 5. chunk 到达时更新 next-question 消息的 content
  // 6. done 事件到达时，更新 currentQuestion、progress、status
}
```

### 3.5 chatPage 改动

`submitAnswer` 改为调用 `interviewStore.submitAnswerStream(answer)` 替代 `interviewStore.submitAnswer(answer)`。

---

## 4. SSE 事件格式

| type | data | 说明 |
|------|------|------|
| `follow_up_chunk` | `{chunk, accumulated}` | 追问题生成中的文本片段 |
| `next_question_chunk` | `{chunk, accumulated}` | 下一题生成中的文本片段 |
| `done` | `{follow_up, next_question, is_completed}` | 完成，包含完整数据 |

---

## 5. 已知限制

- 原 POST `/answer` 端点保持不变，向后兼容
- 流式过程中如果用户刷新页面，chunk 数据丢失（可通过 session recovery 恢复）
- follow-up 为 "NO_FOLLOW_UP" 时不发送 follow_up_chunk，直接进入 next_question
