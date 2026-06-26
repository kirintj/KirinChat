# 面试答案草稿自动保存设计规范

**日期**: 2026-06-26
**状态**: 已批准
**范围**: 面试答题时自动保存草稿到 localStorage，页面恢复时自动恢复

---

## 1. 背景与目标

用户在面试过程中输入答案时，如果页面意外刷新、浏览器崩溃或误操作导航离开，已输入但未提交的答案会丢失。

**目标**：自动将用户正在输入的答案保存到 localStorage，页面恢复时自动恢复草稿。

**范围**：纯前端功能，无需后端改动。

---

## 2. 改动范围

### 改动文件

| 文件 | 变更 |
|------|------|
| `src/frontend/src/pages/interview/chatPage/chatPage.vue` | 新增草稿保存/恢复逻辑 |

### 不变的部分

- Pinia store（`store/interview/index.ts`）：不改动，draft 是临时 UI 状态
- 后端：无变更
- API：无变更

---

## 3. 设计方案

### 3.1 localStorage Key 设计

格式：`interview_draft_{sessionId}_{questionId}`

- `sessionId`：当前面试会话 ID（来自 `interviewStore.sessionId`）
- `questionId`：当前题目 ID（来自 `interviewStore.currentQuestion.id`）
- 每道题的草稿独立存储，互不干扰

### 3.2 核心逻辑

**保存草稿（saveDraft）**：
- 将 `answerInput.value` 写入 localStorage
- 如果 `answerInput.value` 为空字符串，则删除该 key（避免存储空值）
- 使用 debounce 500ms 避免频繁写入

**恢复草稿（restoreDraft）**：
- 从 localStorage 读取当前 sessionId + questionId 对应的草稿
- 如果存在，填充到 `answerInput.value`
- 在 `onMounted` 和 `currentQuestion` 变化时调用

**清除草稿（clearDraft）**：
- 删除当前 sessionId + questionId 对应的 key
- 在 `submitAnswer` 成功后调用

### 3.3 触发时机

| 事件 | 动作 |
|------|------|
| 用户输入（answerInput 变化） | debounce 500ms 后 saveDraft |
| 收到新题目（currentQuestion 变化） | restoreDraft |
| 页面加载（onMounted） | restoreDraft |
| 提交答案成功 | clearDraft + 清空 answerInput |
| 面试结束 | 无需额外处理（key 按 sessionId+questionId 命名，不影响后续面试） |

### 3.4 Watch 依赖

需要 watch `currentQuestion` 的变化来触发草稿恢复。当用户提交答案后收到新题目，`currentQuestion` ref 会更新，此时恢复新题目的草稿（如果之前有保存过）。

---

## 4. 已知限制

- 草稿仅存储在浏览器本地，换设备或清浏览器缓存会丢失
- debounce 500ms 意味着用户快速输入后立即关闭页面，最多丢失最后 500ms 的输入
- localStorage 有大小限制（约 5MB），但单道题草稿很小，不会触及限制
