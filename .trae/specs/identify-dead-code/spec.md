# 死代码与死文件清理 Spec

## Why
项目中积累了大量死代码、死文件和死导出，增加了维护负担、构建体积和认知复杂度。需要系统性地识别并清理它们。

## What Changes
- 删除前端死页面、死组件、死API模块、死Store、死Composable、死样式文件
- 删除后端死文件、死函数、死常量/类、临时测试目录
- 清理项目根目录的临时文件、过时脚本、冗余配置
- 移除前端 type.ts 和各 API 文件中的死导出
- 移除后端 helpers.py 中的死函数和死导入
- 清理 UI 组件库中从未被使用的组件

## Impact
- Affected code: 前端 src/frontend/src/、后端 src/backend/kirinchat/、项目根目录配置和脚本
- 无破坏性变更：所有被清理的代码均无消费者，删除后不影响任何功能

---

## 前端死文件清单

### 死页面（4个）
| 文件 | 说明 |
|------|------|
| `src/frontend/src/pages/agent/AgentDebug.vue` | 调试页面，未注册路由 |
| `src/frontend/src/pages/agent/agent-fixed.vue` | 旧版智能体页面，未注册路由 |
| `src/frontend/src/pages/conversation/test.vue` | 测试页面，未注册路由 |
| `src/frontend/src/pages/conversation/demo.vue` | 演示页面，未注册路由 |

### 连锁死组件（3个，因上游 agent-fixed.vue 死掉）
| 文件 | 说明 |
|------|------|
| `src/frontend/src/components/dialog/create_agent/create_agent.vue` | 唯一消费者 agent-fixed.vue 已死 |
| `src/frontend/src/components/dialog/create_agent/AgentFormDialog.vue` | 同上 |
| `src/frontend/src/components/dialog/create_agent/index.ts` | 仅导出上述死组件 |

### 死API/工具/Store/Composable/样式（5个）
| 文件 | 说明 |
|------|------|
| `src/frontend/src/apis/mars.ts` | Mars API，mars-chat.vue 直接用 fetchEventSource |
| `src/frontend/src/utils/function.ts` | getHistoryChat/scrollBottom，chatPage.vue 重新定义了同名函数 |
| `src/frontend/src/store/history_list/index.ts` | useHistoryListStore 无消费者 |
| `src/frontend/src/composables/useEChartsTheme.ts` | useEChartsTheme 无消费者 |
| `src/frontend/src/styles/breakpoints.scss` | 未被任何文件导入 |

### 死UI组件（12个，仅 barrel 导出，无任何消费）— 保留不删除
> UI 组件库属于基础设施，保留以备后续使用。

| 文件 | 说明 |
|------|------|
| `src/frontend/src/components/ui/shell/HAIBottomBar.vue` | 未使用 |
| `src/frontend/src/components/ui/shell/HEmpty.vue` | 未使用 |
| `src/frontend/src/components/ui/HChipsTab/HChipsTab.vue` | 未使用 |
| `src/frontend/src/components/ui/HScrollbar/HScrollbar.vue` | 未使用 |
| `src/frontend/src/components/ui/HTable/HTable.vue` | 未使用 |
| `src/frontend/src/components/ui/HUpload/HUpload.vue` | 未使用 |
| `src/frontend/src/components/ui/HSearch/HSearch.vue` | 未使用 |
| `src/frontend/src/components/ui/HSwitch/HSwitch.vue` | 未使用 |
| `src/frontend/src/components/ui/HToolbar/HToolbar.vue` | 未使用 |
| `src/frontend/src/components/ui/HDivider/HDivider.vue` | 未使用 |
| `src/frontend/src/components/ui/HDropdown/HDropdown.vue` | 未使用 |
| `src/frontend/src/components/ui/HDropdown/HDropdownItem.vue` | 未使用 |

### 死导出
**type.ts 中的死类型（5个）：** `DialogCreateType`、`AgentCreateType`、`AgentUpdateType`、`CardListType`、`KnowledgeFileStatus`

**API 死函数（14个）：**
- `apis/history.ts`: `MsgLikeCreateAPI`、`MsgDisLikeAPI`
- `apis/agent.ts`: `defaultParameterAPI`、`defaultCodeAPI`
- `apis/chat.ts`: `retrieveKnowledge`、`sendMarsExample`、`uploadFile`
- `apis/llm.ts`: `getPersonalLLMsAPI`
- `apis/agent-skill.ts`: `uploadAgentSkillFileAPI`
- `apis/mcp-server.ts`: `getMCPToolsAPI`、`deleteMCPUserConfigAPI`
- `apis/auth.ts`: `checkTokenAPI`
- `apis/knowledge.ts`: `knowledgeRetrievalAPI`
- `apis/lingseek.ts`: `generateLingSeekTasksAPI`

**其他死导出（2个）：** `apis/chat.ts` 的 `UploadResponse`、`apis/knowledge-file.ts` 的 `getFileExtension`

---

## 后端死文件清单

### 死文件（8个）
| 文件 | 说明 |
|------|------|
| `src/backend/kirinchat/utils/captcha.py` | verify_captcha 无调用，user.py 中调用已注释 |
| `src/backend/kirinchat/tools/crawl_web/action.py` | CrawlWebTool 未注册到工具列表 |
| `src/backend/kirinchat/tools/resume_optimizer/action.py` | ResumeEnhancer 未注册到工具列表 |
| `src/backend/kirinchat/api/services/mineru.py` | convert_pdf_to_markdown 无外部引用 |
| `src/backend/kirinchat/services/mars/deepsearch.py` | 自注"未入选Mars Tools"，从未被导入 |
| `src/backend/kirinchat/schemas/mcp_server.py` | 与 schemas/mcp.py 重复，从未被使用 |
| `src/backend/kirinchat/common/evaluation/unified_evaluation.py` | UnifiedEvaluationService 无消费者 |
| `src/backend/kirinchat/core/agents/text2sql_agent.py` | Text2SQLAgent 无消费者 |

### 临时测试目录（整个 kirinchat/test/）
包含 20+ 个临时测试脚本和 2 个子目录（test_a2a/、mcp_openai/），不属于正式测试套件（正式测试在 tests/backend/）

### 死导出（1个）
| 文件 | 说明 |
|------|------|
| `tools/__init__.py` | `google_search` 被导入但未加入任何工具字典 |

### 死函数（helpers.py 中约24个）
`build_completion_history_messages`、`fix_json_text`、`check_or_create`、`init_dir`、`check_input`、`filename_to_classname`、`load_scene_templates`、`load_all_scene_configs`、`send_message`、`is_slot_fully_filled`、`get_raw_slot`、`get_dynamic_example`、`get_slot_update_json`、`get_slot_query_user_json`、`update_slot`、`update_agent_json`、`clear_agent_json`、`clean_slot_json`、`update_agent_current_scene`、`get_agent_current_scene`、`format_name_value_for_logging`、`extract_json_from_string`、`fix_json`、`get_function`/`get_function_openai`/`get_function_qwen`/`get_function_by_name_type`

### 死常量/类
- `utils/constants.py`: `PRESET_QUESTION`、`CAPTCHA_PREFIX`、`USER_PASSWORD_ERROR`
- `api/errcode/user.py`: `UserPasswordExpireError`、`UserNotPasswordError`、`UserPasswordError`、`UserLoginOfflineError`、`UserNeedGroupAndRoleError`、`UserGroupNotDeleteError`
- `prompts/completion.py`: `Text2SQLGeneratePrompt`、`Text2SQLSummaryPrompt`
- `utils/convert.py`: `function_to_args_schema`

---

## 项目根目录死文件清单

### 临时文件（2个）
| 文件 | 说明 |
|------|------|
| `test.txt` | 仅含 "test"，无任何引用 |
| `stop` | 仅含 "MySQL80"，无任何引用 |

### 一次性补丁脚本（2个）
| 文件 | 说明 |
|------|------|
| `mh1.ps1` | 修改 mcp-server.vue 的临时脚本 |
| `modify-height.ps1` | 同上，另一版本 |

### 过时文件（2个）
| 文件 | 说明 |
|------|------|
| `scripts/start.py` | 旧启动脚本，已被 kirinchat.bat 替代 |
| `src/backend/requirements.txt` | 已改用 pyproject.toml + uv |

### 冗余配置（1个）
| 文件 | 说明 |
|------|------|
| `docker/docker-compose.override.yml` | 未被任何启动命令使用，引用了不存在的 .env |

### 工具缓存（1个目录）
| 路径 | 说明 |
|------|------|
| `.claude/worktrees/` | Claude AI worktree 缓存，含整个项目旧版副本 |

### 可能过时文档（2个）
| 文件 | 说明 |
|------|------|
| `docs/reference/migration.md` | v2.2.0 迁移指南，当前已是 v2.5.0 |
| `docs/reference/database.md` | 使用旧项目名 agentchat |
