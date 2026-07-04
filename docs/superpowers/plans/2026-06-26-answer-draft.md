# 面试答案草稿自动保存 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 面试答题时自动保存草稿到 localStorage，页面刷新或恢复时自动恢复已输入内容

**Architecture:** 在 chatPage.vue 中新增草稿工具函数（saveDraft/restoreDraft/clearDraft），通过 watch + debounce 自动保存，watch currentQuestion 变化触发恢复。纯前端，无后端改动。

**Tech Stack:** Vue 3 Composition API, localStorage, watch + debounce

---

## 文件结构

| 文件 | 职责 |
|------|------|
| `src/frontend/src/pages/interview/chatPage/chatPage.vue` | 唯一改动文件，新增草稿保存/恢复逻辑 |

---

### Task 1: 实现草稿保存/恢复逻辑

**Files:**
- Modify: `src/frontend/src/pages/interview/chatPage/chatPage.vue`

- [ ] **Step 1: 添加 `watch` 导入**

找到 import 语句：
```typescript
import { ref, nextTick, onMounted, computed } from 'vue'
```

替换为：
```typescript
import { ref, nextTick, onMounted, computed, watch } from 'vue'
```

- [ ] **Step 2: 在 `answerInput` ref 之后添加草稿工具函数**

找到这一行：
```typescript
const answerInput = ref('')
```

在其下方插入：
```typescript
// --- 草稿自动保存：localStorage 按 sessionId + questionId 存取 ---
const DRAFT_PREFIX = 'interview_draft_'

// 生成草稿 key：interview_draft_{sessionId}_{questionId}
const getDraftKey = () => {
  const qId = interviewStore.currentQuestion?.id
  if (!interviewStore.sessionId || !qId) return null
  return `${DRAFT_PREFIX}${interviewStore.sessionId}_${qId}`
}

// 保存草稿到 localStorage（空内容时删除 key）
const saveDraft = () => {
  const key = getDraftKey()
  if (!key) return
  const value = answerInput.value.trim()
  if (value) {
    localStorage.setItem(key, value)
  } else {
    localStorage.removeItem(key)
  }
}

// 从 localStorage 恢复草稿
const restoreDraft = () => {
  const key = getDraftKey()
  if (!key) return
  const saved = localStorage.getItem(key)
  if (saved) {
    answerInput.value = saved
  }
}

// 清除当前题目的草稿
const clearDraft = () => {
  const key = getDraftKey()
  if (key) {
    localStorage.removeItem(key)
  }
}

// debounce 工具：延迟执行，重复调用时重置计时器
let draftTimer: ReturnType<typeof setTimeout> | null = null
const debounceSaveDraft = () => {
  if (draftTimer) clearTimeout(draftTimer)
  draftTimer = setTimeout(saveDraft, 500)
}
```

- [ ] **Step 3: 添加 watch 监听**

在 `debounceSaveDraft` 函数之后插入：
```typescript
// 监听输入变化，debounce 500ms 自动保存草稿
watch(answerInput, debounceSaveDraft)

// 监听当前题目变化，恢复新题目的草稿（提交答案后 currentQuestion 会更新）
watch(() => interviewStore.currentQuestion, () => {
  nextTick(restoreDraft)
})
```

- [ ] **Step 4: 修改 `submitAnswer` 成功路径，清除草稿**

找到 `submitAnswer` 函数中的这一段：
```typescript
const submitAnswer = async () => {
  const answer = answerInput.value.trim()
  if (!answer || !canSubmit.value) return

  answerInput.value = ''
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
  const success = await interviewStore.submitAnswer(answer)
  scrollBottom()

  if (!success) {
    HMessage.error('提交答案失败，请重试')
  }
}
```

- [ ] **Step 5: 修改 `onMounted`，添加草稿恢复**

找到 `onMounted` 中的 `scrollBottom()` 调用（约 line 87）：
```typescript
  scrollBottom()
```

替换为：
```typescript
  restoreDraft() // 页面加载时恢复草稿
  scrollBottom()
```

- [ ] **Step 6: 验证构建**

Run: `cd src/frontend && npm run build 2>&1 | tail -5`
Expected: 构建成功，无错误

- [ ] **Step 7: Commit**

```bash
git add src/frontend/src/pages/interview/chatPage/chatPage.vue
git commit -m "feat(interview): auto-save answer draft to localStorage"
```
