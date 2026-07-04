# 面试流式输出 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 面试提交答案后，AI 追问题和下一题通过 SSE 流式输出，用户可以看到文字逐步生成

**Architecture:** 后端新增 SSE 端点 + Agent 流式方法，前端用 fetchEventSource 消费 SSE 并实时更新 UI

**Tech Stack:** Python/FastAPI, WatchedStreamingResponse, Vue 3, fetchEventSource

---

### Task 1: Agent 层 — 新增流式生成方法

**Files:**
- Modify: `src/backend/kirinchat/core/agents/interview_agent.py`

- [ ] **Step 1: 在 `generate_follow_up` 方法之后添加 `stream_follow_up` 方法**

找到 `generate_follow_up` 方法结束（约第 176 行 `return saved_question` 之后），在其后插入：

```python
    async def stream_follow_up(self, session_id: str, original_question: str, user_answer: str) -> AsyncGenerator[Dict[str, Any], None]:
        """流式生成追问题：逐步输出 LLM 响应，最后保存到数据库。

        Args:
            session_id: 面试会话 ID。
            original_question: 原始题目内容。
            user_answer: 用户答案。

        Yields:
            {"type": "follow_up_chunk", "data": {"chunk": "...", "accumulated": "..."}}
            最后一个 chunk 的 data 中额外包含 "done": True
        """
        prompt = f"""你是一位专业的技术面试官。

# 你的角色
{self.skill.get('persona', '')}

# 任务
候选人回答了以下面试题目，请判断是否需要追问。

# 原始题目
{original_question}

# 候选人回答
{user_answer}

# 规则
1. 如果回答过于简短、有明显遗漏、或存在可深挖的点，请生成一道追问
2. 如果回答已经完整且准确，回复 "NO_FOLLOW_UP"
3. 追问应引导候选人深入思考，不要重复原始题目
4. 只输出追问内容或 "NO_FOLLOW_UP"，不要输出其他说明"""

        accumulated = ""
        async for chunk in self.conversation_model.astream([HumanMessage(content=prompt)]):
            if chunk.content:
                accumulated += chunk.content
                yield {
                    "type": "follow_up_chunk",
                    "data": {"chunk": chunk.content, "accumulated": accumulated},
                }

        # 流式结束后，保存到数据库
        content = accumulated.strip()
        if content and content != "NO_FOLLOW_UP":
            question = InterviewQuestionTable(
                session_id=session_id,
                type="FOLLOW_UP",
                category="follow_up",
                content=content,
            )
            await InterviewService.save_question(question)
            logger.info(f"Follow-up question streamed and saved for session {session_id}: {content[:50]}...")
        else:
            logger.info(f"No follow-up needed for session {session_id}")
```

- [ ] **Step 2: 在 `generate_next_question` 方法之后添加 `stream_next_question` 方法**

找到 `generate_next_question` 方法结束（约第 262 行 `return saved_question` 之后），在其后插入：

```python
    async def stream_next_question(self, session_id: str, user_id: str, difficulty: str = "MEDIUM") -> AsyncGenerator[Dict[str, Any], None]:
        """流式生成下一题：逐步输出 LLM 响应，最后保存到数据库。

        如果已达题目上限，发送 is_completed=True 事件。

        Args:
            session_id: 面试会话 ID。
            user_id: 用户 ID（用于跨 session 去重）。
            difficulty: 难度等级。

        Yields:
            {"type": "next_question_chunk", "data": {"chunk": "...", "accumulated": "..."}}
            如果已完成: {"type": "next_question_chunk", "data": {"chunk": "", "accumulated": "", "is_completed": True}}
        """
        session = await InterviewService.get_session(session_id)
        if session is None:
            yield {"type": "next_question_chunk", "data": {"chunk": "", "accumulated": "", "is_completed": True}}
            return

        # 检查是否达到题目上限
        existing_questions = await InterviewService.get_session_questions(session_id)
        main_questions = [q for q in existing_questions if q.type == "MAIN"]

        if len(main_questions) >= session.question_count:
            await InterviewService.update_session_status(session_id, "COMPLETED")
            yield {"type": "next_question_chunk", "data": {"chunk": "", "accumulated": "", "is_completed": True}}
            return

        # 收集已有题目用于去重
        existing_topics = [q.content for q in main_questions]
        skill_id = self.skill.get("id", "")
        historical_topics = await InterviewService.get_historical_questions(
            user_id, skill_id, exclude_session_id=session_id
        )
        all_topics = list(dict.fromkeys(existing_topics + historical_topics))

        # 选择分类
        covered_categories = set(q.category for q in main_questions)
        categories = self.skill.get("categories", [])
        category = self._select_category(categories, existing_questions)

        # 构建 prompt
        difficulty_desc = _DIFFICULTY_MAP.get(difficulty, _DIFFICULTY_MAP["MEDIUM"])
        dedup_section = self._get_dedup_prompt(all_topics)
        category_name = category.get("name", "") if category else ""
        category_desc = category.get("description", "") if category else ""

        prompt = f"""你是一位专业的技术面试官。

# 你的角色
{self.skill.get('persona', '')}

# 任务
请生成下一道面试题目。这是第 {len(main_questions) + 1}/{session.question_count} 题。

# 已考察的分类
{', '.join(covered_categories) if covered_categories else '暂无'}

# 要求
- 分类: {category_name} - {category_desc}
- 难度: {difficulty_desc}
- 只输出题目内容，不要输出答案或其他说明
- 题目应简洁清晰，不超过 3 句话
{dedup_section}"""

        accumulated = ""
        async for chunk in self.conversation_model.astream([HumanMessage(content=prompt)]):
            if chunk.content:
                accumulated += chunk.content
                yield {
                    "type": "next_question_chunk",
                    "data": {"chunk": chunk.content, "accumulated": accumulated},
                }

        # 流式结束后，保存到数据库
        content = accumulated.strip()
        question = InterviewQuestionTable(
            session_id=session_id,
            type="MAIN",
            category=category.get("key", "general") if category else "general",
            content=content,
        )
        await InterviewService.save_question(question)
        logger.info(f"Next question streamed and saved for session {session_id}: {content[:50]}...")
```

- [ ] **Step 3: 验证 Python 语法**

Run: `cd "D:/HuaweiMoveData/Users/28966/Desktop/项目DEMO/KirinChat/src/backend" && python -c "from kirinchat.core.agents.interview_agent import InterviewAgent; print('OK')"`
Expected: OK

- [ ] **Step 4: Commit**

```bash
git add src/backend/kirinchat/core/agents/interview_agent.py
git commit -m "feat(interview): add streaming follow-up and next-question methods"
```

---

### Task 2: 后端 — 新增 SSE 端点

**Files:**
- Modify: `src/backend/kirinchat/api/v1/interview.py`

- [ ] **Step 1: 添加 import**

找到文件顶部的 import 区域（第 1-27 行），在已有 import 之后添加：

```python
import json
from kirinchat.api.responses.streaming import WatchedStreamingResponse
```

- [ ] **Step 2: 在 `submit_answer` 端点之后添加流式端点**

找到 `submit_answer` 函数结束（约第 190 行 `return resp_500(message=str(err))` 之后），在其后插入：

```python
@router.post("/interview/answer/stream")
async def submit_answer_stream(
    req: InterviewAnswerReq,
    login_user: UserPayload = Depends(get_login_user),
):
    """提交答案，流式返回追问题和下一题（SSE）。"""
    try:
        session = await InterviewService.get_session(req.session_id)
        if session is None:
            return resp_500(message="Session not found")

        # 保存用户答案
        await InterviewService.submit_answer(req.question_id, req.answer)

        # 获取原始题目内容
        questions = await InterviewService.get_session_questions(req.session_id)
        original_question = ""
        for q in questions:
            if q.id == req.question_id:
                original_question = q.content
                break

        # 初始化 agent
        agent = InterviewAgent(agent_config={})
        await agent.init_interview_agent(skill_id=session.skill_id)

        async def stream():
            follow_up_content = ""
            next_question_content = ""
            is_completed = False

            # 阶段一：流式生成追问题
            async for event in agent.stream_follow_up(
                session_id=req.session_id,
                original_question=original_question,
                user_answer=req.answer,
            ):
                follow_up_content = event["data"]["accumulated"]
                yield f"data: {json.dumps(event)}\n\n"

            # 如果有追问题，发送 done 事件并结束（不生成下一题）
            if follow_up_content.strip() and follow_up_content.strip() != "NO_FOLLOW_UP":
                done_data = {
                    "type": "done",
                    "data": {
                        "follow_up": {"content": follow_up_content.strip()},
                        "next_question": None,
                        "is_completed": False,
                    },
                }
                yield f"data: {json.dumps(done_data)}\n\n"
                return

            # 阶段二：流式生成下一题
            async for event in agent.stream_next_question(
                session_id=req.session_id,
                user_id=login_user.user_id,
                difficulty=session.difficulty,
            ):
                data = event["data"]
                if data.get("is_completed"):
                    is_completed = True
                    break
                next_question_content = data["accumulated"]
                yield f"data: {json.dumps(event)}\n\n"

            # 发送完成事件
            done_data = {
                "type": "done",
                "data": {
                    "follow_up": None,
                    "next_question": {"content": next_question_content.strip()} if next_question_content.strip() else None,
                    "is_completed": is_completed,
                },
            }
            yield f"data: {json.dumps(done_data)}\n\n"

        return WatchedStreamingResponse(
            content=stream(),
            media_type="text/event-stream",
        )
    except ValueError as err:
        logger.warning(f"Submit answer stream validation error: {err}")
        return resp_500(message=str(err))
    except Exception as err:
        logger.error(f"Submit answer stream error: {err}")
        return resp_500(message=str(err))
```

- [ ] **Step 3: 验证 Python 语法**

Run: `cd "D:/HuaweiMoveData/Users/28966/Desktop/项目DEMO/KirinChat/src/backend" && python -c "from kirinchat.api.v1.interview import router; print('OK')"`
Expected: OK

- [ ] **Step 4: Commit**

```bash
git add src/backend/kirinchat/api/v1/interview.py
git commit -m "feat(interview): add SSE streaming answer endpoint"
```

---

### Task 3: 前端 — 新增 SSE API 函数

**Files:**
- Modify: `src/frontend/src/apis/interview.ts`

- [ ] **Step 1: 添加 fetchEventSource import**

找到文件顶部（第 1 行）：
```typescript
import { request } from '../utils/request'
```

替换为：
```typescript
import { request } from '../utils/request'
import { fetchEventSource } from '@microsoft/fetch-event-source'
```

- [ ] **Step 2: 在 `submitAnswerAPI` 函数之后添加流式版本**

找到 `submitAnswerAPI` 函数结束（约第 140 行），在其后插入：

```typescript
/** Submit answer with SSE streaming (follow-up + next question) */
export function submitAnswerStreamAPI(
  data: InterviewAnswerRequest,
  callbacks: {
    onFollowUpChunk: (chunk: string, accumulated: string) => void
    onNextQuestionChunk: (chunk: string, accumulated: string) => void
    onDone: (result: { follow_up: { content: string } | null; next_question: { content: string } | null; is_completed: boolean }) => void
    onError: (err: Error) => void
  },
) {
  const ctrl = new AbortController()

  fetchEventSource('/api/v1/interview/answer/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
    },
    body: JSON.stringify(data),
    signal: ctrl.signal,
    openWhenHidden: true,
    async onopen(response: Response) {
      if (response.status !== 200) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
    },
    onmessage(msg: { data: string }) {
      try {
        const event = JSON.parse(msg.data)
        if (event.type === 'follow_up_chunk') {
          callbacks.onFollowUpChunk(event.data.chunk, event.data.accumulated)
        } else if (event.type === 'next_question_chunk') {
          callbacks.onNextQuestionChunk(event.data.chunk, event.data.accumulated)
        } else if (event.type === 'done') {
          callbacks.onDone(event.data)
        }
      } catch (error) {
        console.error('解析 SSE 消息出错:', error)
      }
    },
    onclose() {
      // 连接关闭
    },
    onerror(err: Error) {
      callbacks.onError(err)
      ctrl.abort()
      throw err
    },
  })

  return ctrl
}
```

- [ ] **Step 3: Commit**

```bash
git add src/frontend/src/apis/interview.ts
git commit -m "feat(interview): add SSE streaming API function"
```

---

### Task 4: 前端 Store — 新增流式提交 action

**Files:**
- Modify: `src/frontend/src/store/interview/index.ts`

- [ ] **Step 1: 添加 import**

找到 import 语句（第 4-9 行）：
```typescript
import {
  startInterviewAPI,
  submitAnswerAPI,
  completeInterviewAPI,
  getEvaluationReportAPI,
} from '../../apis/interview'
```

替换为：
```typescript
import {
  startInterviewAPI,
  submitAnswerAPI,
  submitAnswerStreamAPI,
  completeInterviewAPI,
  getEvaluationReportAPI,
} from '../../apis/interview'
```

- [ ] **Step 2: 在 `submitAnswer` 函数之后添加 `submitAnswerStream` 函数**

找到 `submitAnswer` 函数结束（约第 113 行 `}` 之后），在其后插入：

```typescript
  async function submitAnswerStream(answer: string): Promise<boolean> {
    if (!currentQuestion.value || !sessionId.value) return false
    loading.value = true

    // 添加候选人消息
    messages.value.push({ role: 'candidate', content: answer })

    return new Promise((resolve) => {
      // 添加空的 AI 消息气泡（用于流式填充）
      const aiMessageIndex = messages.value.length
      messages.value.push({ role: 'interviewer', content: '' })

      submitAnswerStreamAPI(
        {
          session_id: sessionId.value,
          question_id: currentQuestion.value!.id,
          answer,
        },
        {
          onFollowUpChunk(_chunk: string, accumulated: string) {
            // 实时更新追问题消息内容
            messages.value[aiMessageIndex].content = accumulated
          },
          onNextQuestionChunk(_chunk: string, accumulated: string) {
            // 如果追问题后需要切换到下一题消息
            if (aiMessageIndex === messages.value.length - 1 && messages.value[aiMessageIndex].content !== '') {
              // 追问题已完成，添加新的下一题消息气泡
              messages.value.push({ role: 'interviewer', content: accumulated })
            } else if (messages.value.length > aiMessageIndex + 1) {
              // 已经有下一题消息气泡，更新它
              messages.value[messages.value.length - 1].content = accumulated
            }
          },
          onDone(result: { follow_up: { content: string } | null; next_question: { content: string } | null; is_completed: boolean }) {
            if (result.is_completed) {
              status.value = 'COMPLETED'
              currentQuestion.value = null
              // 添加面试结束消息
              messages.value.push({
                role: 'interviewer',
                content: '面试已结束！正在为你生成评估报告...',
              })
            } else if (result.next_question) {
              // 更新 currentQuestion 为下一题
              currentQuestion.value = {
                id: '', // ID 由后端管理
                type: 'MAIN',
                category: '',
                content: result.next_question.content,
                user_answer: null,
              }
              // 更新进度
              const answeredType = currentQuestion.value?.type
              if (answeredType === 'MAIN') {
                progress.value.current += 1
              }
            }
            loading.value = false
            resolve(true)
          },
          onError() {
            loading.value = false
            resolve(false)
          },
        },
      )
    })
  }
```

- [ ] **Step 3: 在 return 中添加 submitAnswerStream**

找到 return 语句（约第 157-180 行），在 `submitAnswer,` 之后添加 `submitAnswerStream,`：

```typescript
    // Actions
    startInterview,
    submitAnswer,
    submitAnswerStream,
    endInterview,
```

- [ ] **Step 4: Commit**

```bash
git add src/frontend/src/store/interview/index.ts
git commit -m "feat(interview): add streaming submit action to store"
```

---

### Task 5: 前端 chatPage — 切换到流式 API

**Files:**
- Modify: `src/frontend/src/pages/interview/chatPage/chatPage.vue`

- [ ] **Step 1: 修改 submitAnswer 调用流式版本**

找到 `submitAnswer` 函数（约第 118-130 行）：
```typescript
const submitAnswer = async () => {
  const answer = answerInput.value.trim()
  if (!answer || !canSubmit.value) return

  answerInput.value = ''
  clearDraft() // 提交成功后清除草稿
  const success = await interviewStore.submitAnswer(answer)
  scrollBottom()

  if (!success) {
    HMessage.error('提交答案失败，请重试')
  }
}
```

替换为：
```typescript
const submitAnswer = async () => {
  const answer = answerInput.value.trim()
  if (!answer || !canSubmit.value) return

  answerInput.value = ''
  clearDraft() // 提交成功后清除草稿
  const success = await interviewStore.submitAnswerStream(answer)
  scrollBottom()

  if (!success) {
    HMessage.error('提交答案失败，请重试')
  }
}
```

- [ ] **Step 2: 验证构建**

Run: `cd src/frontend && npm run build 2>&1 | tail -5`
Expected: 构建成功

- [ ] **Step 3: Commit**

```bash
git add src/frontend/src/pages/interview/chatPage/chatPage.vue
git commit -m "feat(interview): switch to streaming answer submission"
```
