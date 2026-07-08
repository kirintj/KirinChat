# Tasks

- [x] Task 1: 清理前端死页面和连锁死组件
  - [x] 1.1 删除 agent-fixed.vue、AgentDebug.vue、conversation/test.vue、conversation/demo.vue
  - [x] 1.2 删除 components/dialog/create_agent/ 整个目录
  - [x] 1.3 检查并清理路由配置中对已删除页面的引用（无残留）

- [x] Task 2: 清理前端死API/工具/Store/Composable文件
  - [x] 2.1 删除 apis/mars.ts
  - [x] 2.2 删除 utils/function.ts
  - [x] 2.3 删除 store/history_list/ 目录
  - [x] 2.4 删除 composables/useEChartsTheme.ts
  - [x] 2.5 breakpoints.scss 经发现被 vite.config.ts 全局注入，已恢复

- [x] Task 3: ~~清理前端死UI组件及 barrel 导出~~ （用户决定保留 UI 组件库，不删除）

- [x] Task 4: 清理前端死导出
  - [x] 4.1 清理 type.ts 中 4 个死类型导出（AgentCreateType、AgentUpdateType、CardListType、KnowledgeFileStatus；DialogCreateType 保留）
  - [x] 4.2 清理各 API 文件中 14 个死函数导出
  - [x] 4.3 清理 chat.ts 中 UploadResponse（getFileExtension 保留因被 getFileType 调用）

- [x] Task 5: 清理后端死文件
  - [x] 5.1 删除 utils/captcha.py、tools/crawl_web/、tools/resume_optimizer/、api/services/mineru.py
  - [x] 5.2 删除 services/mars/deepsearch.py、schemas/mcp_server.py
  - [x] 5.3 删除 common/evaluation/unified_evaluation.py、core/agents/text2sql_agent.py

- [x] Task 6: 清理后端临时测试目录
  - [x] 6.1 删除 kirinchat/test/ 整个目录

- [x] Task 7: 清理后端死导出和死函数
  - [x] 7.1 清理 tools/__init__.py 中未使用的 google_search 导入
  - [x] 7.2 清理 utils/helpers.py 中 27 个死函数及仅被死函数使用的导入（435行→114行）
  - [x] 7.3 清理 utils/constants.py 中 3 个死常量
  - [x] 7.4 清理 api/errcode/user.py 中 6 个死错误类
  - [x] 7.5 清理 prompts/completion.py 中 2 个死 Prompt
  - [x] 7.6 清理 utils/convert.py 中 function_to_args_schema

- [x] Task 8: 清理项目根目录死文件
  - [x] 8.1 删除 test.txt、stop、mh1.ps1、modify-height.ps1
  - [x] 8.2 删除 scripts/start.py、src/backend/requirements.txt
  - [x] 8.3 删除 docker/docker-compose.override.yml
  - [x] 8.4 清理 .claude/worktrees/ 目录

- [x] Task 9: 验证构建和功能完整性
  - [x] 9.1 前端 vite build 验证编译通过
  - [x] 9.2 前端 vue-tsc 类型检查通过
