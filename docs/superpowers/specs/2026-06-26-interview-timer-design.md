# 面试答题计时器设计规范

**日期**: 2026-06-26
**状态**: 已批准
**范围**: 面试答题时显示当前题目耗时和总面试时长

---

## 1. 背景与目标

用户在面试答题时没有时间感知，不知道每道题花了多长时间、整个面试持续了多久。

**目标**：在面试页面显示当前题目计时和总面试时长的秒表。

**范围**：纯前端功能，无需后端改动。

---

## 2. 改动范围

### 改动文件

| 文件 | 变更 |
|------|------|
| `src/frontend/src/pages/interview/chatPage/chatPage.vue` | 新增计时器逻辑和 UI |

### 不变的部分

- Pinia store：不改动
- 后端：无变更
- API：无变更

---

## 3. 设计方案

### 3.1 数据模型

```typescript
const questionSeconds = ref(0)   // 当前题目耗时秒数
const totalSeconds = ref(0)      // 面试总耗时秒数
let timerInterval: ReturnType<typeof setInterval> | null = null
```

### 3.2 计时逻辑

**启动计时**：在 `onMounted` 中，当面试处于 `isActive` 状态时启动 `setInterval`，每秒递增 `questionSeconds` 和 `totalSeconds`。

**题目切换重置**：`watch(() => interviewStore.currentQuestion, ...)` 中，收到新题目时重置 `questionSeconds = 0`。`totalSeconds` 不重置，持续累加直到面试结束。

**停止计时**：当 `interviewStore.isActive` 变为 false 时（面试结束），清除 interval。

### 3.3 UI 显示

位置：进度条区域右侧，与现有信息同行。

格式：`⏱ 02:15 | 总 08:32`（mm:ss，两位补零）

### 3.4 格式化函数

```typescript
const formatTime = (seconds: number) => {
  const m = String(Math.floor(seconds / 60)).padStart(2, '0')
  const s = String(seconds % 60).padStart(2, '0')
  return `${m}:${s}`
}
```

### 3.5 页面恢复

由于 Pinia store 有 `{ persist: true }`，但计时器状态（秒数）不应持久化——页面刷新后计时器从 0 重新开始是合理的。面试本身的持续时间由后端 session 的 `create_time` 和 `completed_at` 记录。

---

## 4. 已知限制

- 页面刷新后计时器从 0 重新开始，不恢复之前的时间（面试实际时长由后端记录）
- 计时器精度为 setInterval 约 1 秒间隔，浏览器标签页后台时可能不准（非关键场景可接受）
