# 前端样式统一整改方案

## Context

调研发现前端样式存在 4 类不统一问题:子页面根类名五花八门、96 处硬编码 rgba 颜色、116 处 box-shadow 未走 token、少量多 `<style>` 块未合并。

**关键修正(与最初判断不同):**
- HAppShell 已在 [App.vue:8-16](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/App.vue#L8-L16) 包裹全局 router-view,无需再让各页面自行包裹。
- [pages/index.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/index.vue) 是全局布局容器(桌面 sidebar + 移动端 HTitlebar/HBottomTab),其他页面都是它的子路由。
- 多 `<style>` 块实际只有 [agent-skill.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/agent-skill/agent-skill.vue) 需合并;[HSelect.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/components/ui/HSelect/HSelect.vue) 的双块是 teleport 场景的合理设计,不动。

用户已确认:① 引入 `.page` 通用类全量改子页面根类名;② rgba 彩色按语义映射,接受轻微变色。

---

## 任务 1:统一子页面根类名为 `.page`

### 1.1 在 [style.css](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/style.css) 末尾新增全局 `.page` 通用类

```css
/* ========== 页面通用基类 ========== */
.page {
  min-height: 100%;
  width: 100%;
  background: transparent;
}
```

只含真正通用的 3 个属性。`box-sizing` 已在全局 `*` 重置里定义,不重复。`padding` 各页面不一致(24px/32px),不强制统一,由各页面自定。

### 1.2 改子页面根节点

把每个一级路由子页面 template 根 `<div>` 的 class 改为 `page`,并在 scoped style 里删除根选择器中与 `.page` 重复的 `min-height/width/background` 声明,保留各自 padding 和特化布局。

**代表性文件与改动模式:**

| 文件 | 原根类名 | 改动 |
|---|---|---|
| [homepage.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/homepage/homepage.vue) | `.homepage` | class 改 `page`,保留居中 flex/padding,删 `height/background` |
| [dashboard.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/dashboard/dashboard.vue) | `.dashboard-container` | class 改 `page`,保留 `padding:24px`,删 `min-height/background` |
| [agent.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/agent/agent.vue) | `.agent-page` | class 改 `page`,保留 `max-width/margin/padding` |
| [mcp-server.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/mcp-server/mcp-server.vue) | `.mcp-server-page` | class 改 `page` |
| [model.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/model/model.vue) | `.model-page` | class 改 `page` |
| [tool.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/tool/tool.vue) | `.tool-page` | class 改 `page` |
| [knowledge.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/knowledge/knowledge.vue) | `.knowledge-page` | class 改 `page` |
| [profile.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/profile/profile.vue) | `.profile-page` | class 改 `page`,保留 `background-color`(非 transparent) |
| [agent-skill.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/agent-skill/agent-skill.vue) | `.skill-page` | class 改 `page` |

**同样模式应用到其余一级页面:** conversation、construct、configuration、knowledge-file、mcp-chat、model-editor、agent-editor、mars-chat、voice-interview/index。

**布局容器页面不动:** [index.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/index.vue)(`.ai-body` 是全局容器)、conversation/interview/workspace(它们是二级布局容器,有自己的 router-view,根类保留)。login/register/notFound(独立路由,非 index 子路由,单独评估,本轮不动)。

---

## 任务 2:清理 96 处 rgba → harmony-tokens(语义映射)

### 2.1 映射表

**中性色(白/黑半透明)→ 组件背景/阴影/遮罩 token:**

| rgba 模式 | 映射目标 |
|---|---|
| `rgba(255, 255, 255, 0.8~1)` 作 background | `var(--harmony-comp-background-primary)` |
| `rgba(255, 255, 255, 0.4~0.6)` 作 background | `var(--harmony-overlay-light)` 或保留(玻璃效果需具体看) |
| `rgba(0, 0, 0, 0.04~0.06)` 作 background | `var(--harmony-comp-background-tertiary)` |
| `rgba(0, 0, 0, 0.09~0.1)` 作 background | `var(--harmony-comp-background-secondary)` |
| `rgba(0, 0, 0, 0.2)` 作 border/divider | `var(--harmony-comp-divider)` |
| `rgba(0, 0, 0, 0.x)` 作 box-shadow 内的颜色 | 见任务 3,整体替换为 shadow token |
| `rgba(255, 255, 255, 0.7)` 等作遮罩 | `var(--harmony-overlay-light)` |

**彩色 → 语义色 token(接受轻微变色):**

| rgba 原值 | 语义 | 映射目标 |
|---|---|---|
| `rgba(64, 158, 255, x)` | 蓝/info | `var(--harmony-brand)` 及其透明变体 `--harmony-comp-emphasize-secondary`(0.2)/`--harmony-comp-emphasize-tertiary`(0.1) |
| `rgba(103, 194, 58, x)` | 绿/success | `var(--harmony-confirm)` |
| `rgba(245, 108, 108, x)` | 红/danger | `var(--harmony-warning)` |
| `rgba(59, 130, 246, x)` | 蓝 | `var(--harmony-brand)` |
| `rgba(232, 64, 38, x)` | 红(已是 warning 原值) | `var(--harmony-warning)` |

### 2.2 重点文件(按违规频次)

- [conversation/chatPage/chatPage.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/conversation/chatPage/chatPage.vue)(11 处,蓝/绿/红 message 气泡背景)
- [index.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/index.vue)(8 处,sidebar 玻璃效果)
- [construct.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/construct/construct.vue)(8 处)
- [homepage.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/homepage/homepage.vue)(7 处,search-box)
- [profile.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/profile/profile.vue)(8 处)
- [defaultPage.vue (conversation)](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/conversation/defaultPage/defaultPage.vue)(9 处)

**注意:** `index.vue` 的 sidebar 用了 `backdrop-filter: blur(80px)` + `rgba(255,255,255,0.4)` 的玻璃效果,这种半透明白色是玻璃效果必需的,不能直接换成不透明 token。保留这类玻璃专用 rgba,或在 harmony-tokens 里已有 `--harmony-overlay-light`(0.4)的就用它。

---

## 任务 3:box-shadow → `--harmony-shadow-*` token

### 3.1 按偏移量映射

| 原 box-shadow | 映射目标 |
|---|---|
| `0 1px 2px rgba(0,0,0,0.04)` | `var(--harmony-shadow-xs)` |
| `0 2px 4px rgba(0,0,0,0.04)` | `var(--harmony-shadow-sm)` |
| `0 4px 8px rgba(0,0,0,0.04)` | `var(--harmony-shadow-md)` |
| `0 8px 16px rgba(0,0,0,0.04)` | `var(--harmony-shadow-lg)` |
| `0 4px 16px rgba(0,0,0,0.08)` | `var(--harmony-shadow-card)` |
| `0 8px 24px rgba(0,0,0,0.12)` | `var(--harmony-shadow-dialog)` |
| `0 8px 32px rgba(0,0,0,0.06), 0 1px 4px rgba(0,0,0,0.04)`(组合) | `var(--harmony-shadow-lg)`(取主阴影) |
| `0 Xpx Ypx var(--harmony-comp-emphasize-*)`(颜色已用变量但未用整体 token) | 保留(颜色已合规,整体 token 无对应彩色版本) |

### 3.2 处理范围

116 处中以数字开头且颜色为 rgba 的 box-shadow(约 30-40 处真正违规)全部替换。已用 `var(--harmony-shadow-*)` 的跳过;已用 `var(--harmony-comp-emphasize-*)` 作颜色的保留。

---

## 任务 4:合并多 `<style>` 块

**只合并 1 个文件:** [agent-skill.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/agent-skill/agent-skill.vue)

它有两个 `<style lang="scss" scoped>` 块(行 1002 和 1802),都 `@use '../../styles/breakpoints.scss' as *`。合并方式:把第二个块的全部规则移到第一个块末尾,删除第二个 `<style>` 标签,保留一个 `@use` 声明。

**HSelect.vue 不动:** 它的第二个 `<style>`(非 scoped)服务 teleport 出去的 `.h-select__dropdown-teleported`,合并会破坏浮层样式。

---

## 验证方式

1. `cd src/frontend && npm run lint` — 确认无语法错误
2. `npm run dev` 启动开发服务器,逐页检查:
   - 桌面端:访问 /homepage、/dashboard、/agent、/mcp-server、/model、/tool、/knowledge、/profile、/agent-skill,确认布局无回归
   - 移动端(≤767px):同上页面,确认 padding/滚动/标题栏正常
   - 重点检查 conversation/chatPage 的蓝/绿/红 message 气泡颜色(已接受轻微变色)
   - 检查 index.vue sidebar 玻璃效果是否保留
3. `grep -r "rgba(" src/frontend/src --include="*.vue" | wc -l` — 确认 rgba 数量从 96 下降(玻璃效果保留的约 10-15 处)
4. `grep -rE "box-shadow:\s*(0|rgba)" src/frontend/src --include="*.vue" | wc -l` — 确认硬编码 box-shadow 显著下降
5. `grep -rE "<style" src/frontend/src/pages/agent-skill/agent-skill.vue` — 确认只剩 1 个 style 块

## 执行顺序

按风险从低到高:任务 4(1 文件) → 任务 3(box-shadow) → 任务 2(rgba) → 任务 1(根类名,影响面最大)。每完成一个任务验证一次,避免一次性改动太多难以定位回归。
