# AgentChat 鸿蒙宇宙蓝改造 — 执行计划

> 日期: 2026-06-17
> 基于设计文档: `2026-06-17-harmonyos-universe-blue-redesign.md`
> 执行策略: 垂直切片（方案 B）— 逐批次推进，组件与页面交替完成

---

## 1. 执行策略

采用**垂直切片**策略：主题系统 → P0 核心组件 → 第一批页面 → P1 组件 → 第二/三批页面 → P2 组件 → 第四/五批页面 → 移除 Element Plus。

**核心原则：**
- 每个阶段结束时 `npm run dev` 必须正常启动，页面可访问
- Element Plus 在阶段五才移除，之前新旧共存
- 每个阶段内先建/补组件，再迁移页面
- 组件在真实页面中验证，API 不合适立即调整

---

## 2. 阶段总览

| 阶段 | 内容 | 涉及文件数 | 预计工作量 |
|------|------|-----------|-----------|
| **阶段一：地基** | 主题系统 + P0 核心组件 + 第一批页面 | ~9 文件 | 中 |
| **阶段二：表单交互** | P1 组件 + 第二批页面 | ~11 文件 | 中 |
| **阶段三：中等页面** | P1 组件补全 + 第三批页面 | ~9 文件 | 中高 |
| **阶段四：重度页面** | P2 组件 + 第四批页面 | ~9 文件 | 高 |
| **阶段五：收尾** | 第五批页面 + 移除 Element Plus + 全局验收 | ~6 文件 | 中 |

---

## 3. 阶段一：地基

**目标：** 建立主题系统 + 核心组件 + 迁移最简单的 2 个布局页面

### 步骤 1.1：主题系统搭建

- 改写 `src/frontend/src/style.css`：替换现有 `:root` 变量为完整 token 体系
  - 暗色模式 `[data-theme="dark"]`：深空蓝三级背景、主色蓝、蓝光辉光阴影
  - 亮色模式 `[data-theme="light"]`：晴空蓝白背景、柔和灰影
  - 共用 tokens：圆角 8-16px、间距、动效 150-200ms、字体
- 新建 `src/frontend/src/composables/useTheme.ts`：主题切换逻辑（light/dark/system）
  - 使用 `useLocalStorage` 持久化偏好
  - 监听 `prefers-color-scheme` 系统偏好
  - 通过 `document.documentElement.setAttribute('data-theme', theme)` 切换
- 在 `App.vue` 或 `main.ts` 中初始化 `useTheme()`

### 步骤 1.2：P0 核心组件（4 个）

在 `src/components/ui/` 下创建：

| 组件 | 替换目标 | 使用量 | 说明 |
|------|---------|--------|------|
| HButton | el-button | 80 处 / 22 文件 | primary/secondary/text/danger 变体，支持 size、disabled、loading |
| HIcon | el-icon + @element-plus/icons-vue | 74 处 / 12 文件 | 封装 HarmonyOS Sans Symbols 图标 |
| HInput | el-input | 28 处 / 15 文件 | 支持 v-model、prefix/suffix 插槽、clearable、error 状态 |
| HMessage | ElMessage（API） | 372 处 / 30 文件 | HMessage.success/error/warning/info()，纯函数调用 |

同时创建 `src/components/ui/index.ts` 全局注册插件，在 `main.ts` 中 `app.use(UI)`。

### 步骤 1.3：第一批页面迁移（2 个）

| 文件 | el- 标签数 | 复杂度 |
|------|-----------|--------|
| `pages/index.vue`（主布局） | 4 | 低 |
| `pages/workspace/workspace.vue` | 5 | 低 |

### 阶段一完成标志

- [ ] `npm run dev` 正常启动
- [ ] 暗色/亮色主题切换生效
- [ ] HButton/HIcon/HInput/HMessage 在页面中可见可用
- [ ] index.vue 和 workspace.vue 无 el- 标签残留

---

## 4. 阶段二：表单交互

**目标：** 补齐 P1 组件 + 迁移 5 个低复杂度页面

### 步骤 2.1：P1 组件（6 个）

| 组件 | 替换目标 | 使用量 | 说明 |
|------|---------|--------|------|
| HSelect + HOption | el-select + el-option | 33 处 / 5 文件 | 自定义下拉面板，支持搜索过滤 |
| HForm + HFormItem | el-form + el-form-item | 22 处 / 4 文件 | 表单容器 + 标签/校验/布局 |
| HDialog | el-dialog | 3 处 / 3 文件 | 模态对话框，遮罩 + 居中 + 关闭按钮 |
| HMessageBox | ElMessageBox（API） | 18 处 / 13 文件 | confirm/alert/prompt 函数式调用 |
| HTooltip | el-tooltip | 15 处 / 5 文件 | hover 提示，支持 4 方向定位 |
| HDropdown | el-dropdown | 9 处 / 2 文件 | 下拉菜单，点击触发 |

### 步骤 2.2：第二批页面迁移（5 个）

| 文件 | el- 标签数 | 主要替换 |
|------|-----------|---------|
| `pages/login/login.vue` | 3 | el-input, el-button |
| `pages/login/register.vue` | 5 | el-input, el-form, el-button |
| `pages/agent/agent.vue` | 6 | el-button, el-dropdown, el-icon |
| `pages/configuration/configuration.vue` | 2 | el-form, el-button |
| `pages/conversation/test.vue` | 2 | el-input, el-button |

### 步骤 2.3：启动 ElMessage 批量替换

372 处 ElMessage 全局替换为 HMessage，此步骤跨阶段持续进行：

```typescript
// 替换前
import { ElMessage } from 'element-plus'
ElMessage.success('操作成功')

// 替换后
import { HMessage } from '@/components/ui'
HMessage.success('操作成功')
```

阶段二处理第二批页面中的 ElMessage，后续阶段继续处理剩余文件。
同步替换 `utils/dialog.ts` 中的 `ElMessageBox.confirm()` 封装。

### 阶段二完成标志

- [ ] 6 个 P1 组件可用
- [ ] 5 个低复杂度页面无 el- 标签
- [ ] login/register 页面表单提交正常
- [ ] HMessageBox 在删除确认等场景中工作正常
- [ ] 已处理文件中的 ElMessage 全部替换为 HMessage

---

## 5. 阶段三：中等复杂度页面

**目标：** 补齐剩余 P1 能力 + 迁移 9 个中等复杂度页面

### 步骤 3.1：P1 组件补全

无需新建组件，根据实际页面需要微调已有 P1 组件：

- **HMessageBox** 的 `prompt` 模式
- **HSelect** 的搜索过滤功能
- **HDialog** 的嵌套/自定义 footer 插槽

### 步骤 3.2：第三批页面迁移（9 个）

| 文件 | el- 标签数 | 主要替换 |
|------|-----------|---------|
| `pages/knowledge/knowledge-file.vue` | 3 | el-upload, el-button |
| `pages/agent/AgentDebug.vue` | 3 | el-input, el-button |
| `pages/dashboard/dashboard.vue` | 12 | el-select, el-button, el-icon |
| `pages/knowledge/knowledge.vue` | 12 | el-table 相关, el-button, el-upload |
| `pages/profile/profile.vue` | 13 | el-form, el-input, el-button |
| `pages/agent/agent-fixed.vue` | 9 | el-button, el-tag, el-icon |
| `pages/conversation/demo.vue` | 10 | el-input, el-button, el-icon |
| `pages/model/model.vue` | 11 | el-select, el-button, el-dialog |
| `pages/conversation/chatPage/chatPage.vue` | 14 | el-input, el-button, el-icon, el-dropdown |

### 步骤 3.3：特殊关注点

- **dashboard.vue**：含 ECharts 图表，需确认暗色模式下图表可读性，可能需要动态切换 ECharts 主题色
- **chatPage.vue**：核心聊天页面，含流式对话，需确保替换后消息发送/接收不受影响
- **knowledge.vue**：含文件上传，HUpload 组件虽归 P2 此处可能需提前搭建原型
- **profile.vue**：表单密集，HForm + HFormItem 组合在此页面充分验证

### 阶段三完成标志

- [ ] 9 个中等页面无 el- 标签
- [ ] 聊天页面流式对话正常
- [ ] ECharts 图表暗色模式可读
- [ ] 文件上传功能正常
- [ ] HSelect 搜索过滤正常工作
- [ ] 已处理页面的 ElMessage 全部替换完成

---

## 6. 阶段四：重度页面

**目标：** 建立 P2 专用组件 + 迁移 5 个高复杂度页面

### 步骤 4.1：P2 专用组件（9 个）

| 组件 | 替换目标 | 使用量 | 说明 |
|------|---------|--------|------|
| HTag | el-tag | 7 处 / 3 文件 | 彩色标签，支持 closable |
| HTable + HTableColumn | el-table | 仅 1 文件 | mcp-server.vue 专用，简化实现 |
| HUpload | el-upload | 6 处 / 5 文件 | 文件上传，支持拖拽 |
| HDrawer | el-drawer | 1 处 | 侧边抽屉 |
| HTabs + HTabPane | el-tabs | 1 处 | 选项卡（tool.vue） |
| HScrollbar | el-scrollbar | 2 处 | 自定义滚动条 |
| HAvatar | el-avatar | 2 处 | 头像 |
| HSkeleton | el-skeleton | 1 处 | 骨架屏 |
| HLoading（指令） | v-loading | 12 处 | 自定义 v-h-loading 指令 |

### 步骤 4.2：第四批页面迁移（5 个）

| 文件 | el- 标签数 | 难点 |
|------|-----------|------|
| `pages/mcp-server/mcp-chat.vue` | 14 | MCP 对话交互复杂 |
| `pages/tool/tool.vue` | 14 | 含 HTabs，工具详情展示 |
| `pages/model/model-editor.vue` | 21 | el-form 密集，字段多 |
| `pages/mcp-server/mcp-server.vue` | 21 | 含 HTable，表格 + 表单混合 |
| `pages/agent/agent-editor.vue` | 34 | 最重页面之一，表单 + 标签 + 图标 + 下拉 |

### 步骤 4.3：特殊关注点

- **agent-editor.vue（34 处）**：建议拆分子步骤——先替换图标和按钮，再替换表单和标签，最后处理下拉菜单，每步验证
- **mcp-server.vue**：HTable 组件在此页面是唯一使用者，简化实现即可
- **v-loading 替换**：12 处 v-loading 指令分散在多个文件，统一替换为 `v-h-loading`

### 阶段四完成标志

- [ ] 9 个 P2 组件可用
- [ ] 5 个高复杂度页面无 el- 标签
- [ ] agent-editor.vue 表单提交正常
- [ ] mcp-server.vue 表格展示正常
- [ ] tool.vue 选项卡切换正常
- [ ] v-loading 全部替换为 v-h-loading
- [ ] 已处理页面的 ElMessage/ElMessageBox 全部替换

---

## 7. 阶段五：收尾

**目标：** 迁移最后 3 个文件 + 彻底移除 Element Plus + 全局验收

### 步骤 5.1：第五批页面迁移（3 个）

| 文件 | el- 标签数 | 难点 |
|------|-----------|------|
| `components/dialog/create_agent/create_agent.vue` | 27 | 公共对话框组件，被多处引用 |
| `components/drawer/drawer.vue` | 6 | 公共抽屉组件，侧边栏核心 |
| `pages/agent-skill/agent-skill.vue` | 43 | 全项目最重页面，el- 标签最多 |

**agent-skill.vue（43 处）** 是整个改造的最后堡垒，建议拆分子步骤处理。

### 步骤 5.2：清除遗漏项

全局搜索扫描，确保零残留：

```bash
# el- 标签残留
grep -r "el-" --include="*.vue" src/frontend/src/

# ElMessage / ElMessageBox 残留
grep -r "ElMessage\|ElMessageBox\|ElLoading" --include="*.ts" --include="*.vue" src/frontend/src/

# Element Plus 图标残留
grep -r "@element-plus/icons-vue" --include="*.ts" --include="*.vue" src/frontend/src/

# element-plus import 残留
grep -r "from 'element-plus'" --include="*.ts" --include="*.vue" src/frontend/src/
```

### 步骤 5.3：依赖清理

**移除：**
- `element-plus`、`@element-plus/icons-vue`
- `unplugin-vue-components`、`unplugin-auto-import`（若仅用于 Element Plus）

**修改：**
- `vite.config.ts`：删除 `AutoImport` 和 `Components` 插件中的 `ElementPlusResolver`
- `main.ts`：删除 `import 'element-plus/dist/index.css'`
- 清理 `components.d.ts`、`auto-imports.d.ts` 自动生成文件

**新增：**
- `harmonyos-sans-symbols` 图标字体包

### 步骤 5.4：类型迁移

替换 Element Plus 类型引用：

| 原类型 | 替换为 |
|--------|--------|
| `UploadProps` | `HUploadProps` |
| `UploadUserFile` | `HUploadFile` |
| `FormInstance` | `HFormInstance` |
| `FormRules` | `HFormRules` |

### 步骤 5.5：全局验收

**功能验收（10 项）：**
- [ ] 全部 31 个页面在暗色和亮色模式下正常显示
- [ ] 主题切换（手动 + 系统跟随）工作正常
- [ ] 所有表单提交正常
- [ ] 所有消息提示显示正常
- [ ] 所有确认对话框功能正常
- [ ] 文件上传功能正常
- [ ] 侧边栏下拉菜单正常
- [ ] MCP Server 表格页面正常
- [ ] 聊天页面流式对话正常
- [ ] ECharts 图表在暗色模式下可读

**视觉验收（6 项）：**
- [ ] 所有颜色通过 CSS 变量引用，无硬编码色值
- [ ] 暗色模式：深空蓝背景 + 亮蓝主色，层次分明
- [ ] 亮色模式：晴空蓝白背景 + 蓝色主色，清爽简洁
- [ ] 圆角统一 8-16px 范围
- [ ] 图标统一使用 HarmonyOS Sans Symbols
- [ ] 微动效 150-200ms，不突兀

**技术验收（7 项）：**
- [ ] Element Plus 依赖已从 package.json 移除
- [ ] `@element-plus/icons-vue` 依赖已移除
- [ ] 代码中无 `el-` 前缀标签残留
- [ ] 代码中无 `ElMessage`、`ElMessageBox`、`ElLoading` 引用残留
- [ ] 组件库通过 Vue 插件全局注册
- [ ] TypeScript 类型无报错（`npx vue-tsc --noEmit`）
- [ ] 构建成功无警告（`npm run build`）

### 阶段五完成标志

- [ ] 全部 31 个页面 + 5 个公共组件迁移完成
- [ ] Element Plus 从 package.json 移除
- [ ] 全局 grep 零残留
- [ ] `npm run build` 成功无警告
- [ ] `npx vue-tsc --noEmit` 无类型错误
- [ ] 暗色/亮色模式全部页面视觉正确

---

## 8. 风险与注意事项

1. **Monaco Editor**：独立主题系统，需单独配置暗色/亮色主题与鸿蒙蓝对齐
2. **md-editor-v3**：Markdown 编辑器主题需通过其主题 API 切换
3. **ECharts**：图表组件需根据当前主题动态切换配色方案
4. **vditor**：编辑器主题需单独适配
5. **Google Fonts**：当前加载了 ZCOOL KuaiLe 等字体，需确认是否保留或替换为 HarmonyOS Sans
6. **第三方组件样式泄漏**：确保 Monaco Editor、md-editor-v3 等样式不与新主题冲突
