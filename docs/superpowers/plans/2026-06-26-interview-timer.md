# 面试答题计时器 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在面试页面显示当前题目计时和总面试时长的秒表

**Architecture:** 在 chatPage.vue 中新增 ref + setInterval 计时逻辑，在进度条区域显示 mm:ss 格式时间。纯前端，无后端改动。

**Tech Stack:** Vue 3 Composition API, setInterval

---

### Task 1: 实现计时器逻辑和 UI

**Files:**
- Modify: `src/frontend/src/pages/interview/chatPage/chatPage.vue`

- [ ] **Step 1: 添加 `onUnmounted` 导入**

找到 import 语句：
```typescript
import { ref, nextTick, onMounted, computed, watch } from 'vue'
```

替换为：
```typescript
import { ref, nextTick, onMounted, onUnmounted, computed, watch } from 'vue'
```

- [ ] **Step 2: 在草稿逻辑之后、`messagesContainer` ref 之前添加计时器状态和函数**

找到这一行：
```typescript
const messagesContainer = ref<HTMLElement | null>(null)
```

在其上方插入：
```typescript
// --- 答题计时器：当前题目耗时 + 总面试时长 ---
const questionSeconds = ref(0)
const totalSeconds = ref(0)
let timerInterval: ReturnType<typeof setInterval> | null = null

// 格式化秒数为 mm:ss
const formatTime = (seconds: number) => {
  const m = String(Math.floor(seconds / 60)).padStart(2, '0')
  const s = String(seconds % 60).padStart(2, '0')
  return `${m}:${s}`
}

// 启动计时器，每秒递增
const startTimer = () => {
  if (timerInterval) return
  timerInterval = setInterval(() => {
    questionSeconds.value += 1
    totalSeconds.value += 1
  }, 1000)
}

// 停止计时器
const stopTimer = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}
```

- [ ] **Step 3: 修改 currentQuestion watch，在恢复草稿的同时重置题目计时**

找到 currentQuestion 的 watch（在 `watch(answerInput, debounceSaveDraft)` 之后）：
```typescript
watch(() => interviewStore.currentQuestion, () => {
  nextTick(restoreDraft)
})
```

替换为：
```typescript
watch(() => interviewStore.currentQuestion, () => {
  questionSeconds.value = 0 // 新题目重置题目计时
  nextTick(restoreDraft)
})
```

- [ ] **Step 4: 在 onMounted 中启动计时器**

找到 `onMounted` 中 `restoreDraft()` 调用（约 line 144）：
```typescript
  restoreDraft() // 页面加载时恢复草稿
  scrollBottom()
```

替换为：
```typescript
  restoreDraft() // 页面加载时恢复草稿
  scrollBottom()
  startTimer() // 启动答题计时器
```

- [ ] **Step 5: 添加 onUnmounted 清理计时器**

在 `onMounted` 块结束（`})` 闭括号）之后插入：
```typescript
onUnmounted(() => {
  stopTimer()
})
```

- [ ] **Step 6: 在进度条模板中添加计时显示**

找到进度条区域的 `progress-skill` span：
```html
<span class="progress-skill">{{ interviewStore.skillName }}</span>
```

替换为：
```html
<span class="progress-skill">
  {{ interviewStore.skillName }}
  <span class="timer-display">⏱ {{ formatTime(questionSeconds) }} | 总 {{ formatTime(totalSeconds) }}</span>
</span>
```

- [ ] **Step 7: 添加计时器样式**

在 `<style>` 的 `.progress-skill` 样式之后插入：
```scss
.timer-display {
  margin-left: 12px;
  font-size: 12px;
  color: var(--color-text-tertiary, #9ca3af);
  font-variant-numeric: tabular-nums; // 等宽数字，避免计时跳动导致布局偏移
}
```

- [ ] **Step 8: 验证构建**

Run: `cd src/frontend && npm run build 2>&1 | tail -5`
Expected: 构建成功

- [ ] **Step 9: Commit**

```bash
git add src/frontend/src/pages/interview/chatPage/chatPage.vue
git commit -m "feat(interview): add answer timer with question and total elapsed time"
```
