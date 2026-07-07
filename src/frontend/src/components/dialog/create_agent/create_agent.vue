<script lang="ts" setup>
import { ref, onMounted } from "vue"
import { HMessage, HDialog, HButton, HSelect, HOption, HFormItem } from '@/components/ui'
import { createAgentAPI, updateAgentAPI } from "../../../apis/agent"
import { uploadFileAPI } from "../../../apis/file"
import { Agent, AgentFormData } from "../../../type"

const fileList = ref<{url?: string; name: string}[]>([])
const emits = defineEmits<(event: "update") => void>()
const visible = ref<boolean>(false)
const formRef = ref()
const eventType = ref("")
const id = ref('')
const uploadLoading = ref(false)

const form = ref<AgentFormData>({
  name: "",
  description: "",
  logo_url: "",
  system_prompt: "",
  llm_id: "",
  tool_ids: [],
  mcp_ids: [],
  knowledge_ids: [],
  enable_memory: false
})

const collapseItems = ref({
  aiModel: true,
  mcpAgent: false,
  knowledge: false,
  tools: false
})

const recommendedQuestions = ref([
  "你能帮助我理解复杂的文本内容吗？",
  "如何生成高质量的文本回答？",
  "你可以提供哪些步骤指导来完成特定任务？"
])

const rules = ref({
  system_prompt: [{ required: true, message: "系统提示词不能为空", trigger: "blur" }],
  llm_id: [{ required: true, message: "请选择大模型", trigger: "change" }],
})

const llmOptions = ref([
  { id: '1', name: 'GPT-4', model: 'gpt-4' },
  { id: '2', name: 'GPT-3.5-turbo', model: 'gpt-3.5-turbo' },
  { id: '3', name: 'Claude-3', model: 'claude-3' }
])

const toolOptions = ref([
  { id: '1', name: 'Web搜索', description: '网络搜索工具' },
  { id: '2', name: '代码执行', description: '代码运行工具' },
  { id: '3', name: '图片生成', description: '图片生成工具' }
])

const mcpOptions = ref([
  { id: '1', name: '天气服务', description: '天气查询服务' },
  { id: '2', name: '邮件服务', description: '邮件发送服务' }
])

const knowledgeOptions = ref([
  { id: '1', name: '技术文档', description: '技术相关文档' },
  { id: '2', name: '产品手册', description: '产品使用手册' }
])

onMounted(async () => { })

const open = async (event: string, item?: Agent) => {
  visible.value = true
  eventType.value = event
  fileList.value = []

  if (event === "create") {
    form.value = {
      name: "",
      description: "",
      logo_url: "",
      system_prompt: "你是一个智能助手 tmg-GPT，具有丰富的自然语言处理经验，擅长理解和生成文本内容，你的任务是帮助用户解决问题并提供信息支持，确保按照用户的指示执行任务。",
      llm_id: "",
      tool_ids: [],
      mcp_ids: [],
      knowledge_ids: [],
      enable_memory: false
    }
  } else {
    if (item) {
      fileList.value.push({
        url: item.logo_url,
        name: "avatar",
      })
      form.value = {
        name: item.name,
        description: item.description,
        logo_url: item.logo_url,
        system_prompt: item.system_prompt,
        llm_id: item.llm_id,
        tool_ids: item.tool_ids || [],
        mcp_ids: item.mcp_ids || [],
        knowledge_ids: item.knowledge_ids || [],
        enable_memory: item.enable_memory
      }
      id.value = item.agent_id
    }
  }
}

const close = () => {
  visible.value = false
}

const handleFileChange = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    await uploadAvatarFile(file)
  }
}

const uploadAvatarFile = async (file: File) => {
  // 文件大小和类型检查
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    HMessage.error('上传头像图片大小不能超过 2MB!')
    return
  }
  const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png'
  if (!isJpgOrPng) {
    HMessage.error('上传头像图片只能是 JPG/PNG 格式!')
    return
  }
  
  // 开始上传
  uploadLoading.value = true
  try {
    const uploadFormData = new FormData()
    uploadFormData.append('file', file)
    
    const response = await uploadFileAPI(uploadFormData)
    
    if (response.data.status_code === 200) {
      form.value.logo_url = response.data.data
      HMessage.success('头像上传成功')
    } else {
      HMessage.error(response.data.status_message || '头像上传失败')
    }
  } catch (error) {
    console.error('头像上传失败:', error)
    HMessage.error('头像上传失败')
  } finally {
    uploadLoading.value = false
  }
}

const handleConfirm = async () => {
  try {
    await formRef.value.validate()
    if (eventType.value === "create") {
      await createAgentAPI(form.value)
      HMessage.success('智能体创建成功')
    } else {
      await updateAgentAPI({
        agent_id: id.value,
        ...form.value
      })
      HMessage.success('智能体更新成功')
    }
    emits("update")
    close()
  } catch (error) {
    console.error('操作失败:', error)
    HMessage.error(eventType.value === "create" ? '创建失败' : '更新失败')
  }
}

const toggleCollapse = (key: keyof typeof collapseItems.value) => {
  collapseItems.value[key] = !collapseItems.value[key]
}

defineExpose({ open, close })
</script>

<template>
  <HDialog
    v-model="visible"
    width="90%"
    title=""
    :close-on-click-modal="false"
  >
    <template #default>
      <div class="agent-config-dialog-inner">
        <div class="dialog-header">
          <div class="header-left">
            <span class="header-icon">&#9998;</span>
            <span class="header-title">{{ eventType === "create" ? "助手系统提示词与配置" : "编辑助手" }}</span>
          </div>
          <div class="header-actions">
            <HButton @click="handleConfirm" type="primary">
              {{ eventType === "create" ? "创建" : "保存" }}
            </HButton>
            <HButton @click="close" type="secondary">&#10005;</HButton>
          </div>
        </div>
        <div class="dialog-content">
          <!-- 左侧：系统提示词编辑区 -->
          <div class="left-panel">
            <h4>系统提示词</h4>
            <textarea
              v-model="form.system_prompt"
              :rows="24"
              placeholder="请输入系统提示词"
              class="prompt-textarea"
            ></textarea>
          </div>
          <!-- 中间：四项配置 -->
          <div class="middle-panel">
            <div class="config-sections">
              <!-- AI模型配置 -->
              <div class="config-section">
                <div class="section-header" @click="toggleCollapse('aiModel')">
                  <span class="collapse-arrow">{{ collapseItems.aiModel ? '&#9660;' : '&#9654;' }}</span>
                  <span>AI模型</span>
                </div>
                <div v-show="collapseItems.aiModel" class="section-content">
                  <HFormItem label="选择模型">
                    <HSelect v-model="form.llm_id" placeholder="请选择大模型" style="width: 100%">
                      <HOption
                        v-for="llm in llmOptions"
                        :key="llm.id"
                        :label="llm.name"
                        :value="llm.id"
                      />
                    </HSelect>
                  </HFormItem>
                </div>
              </div>
              <!-- MCP Agent -->
              <div class="config-section">
                <div class="section-header" @click="toggleCollapse('mcpAgent')">
                  <span class="collapse-arrow">{{ collapseItems.mcpAgent ? '&#9660;' : '&#9654;' }}</span>
                  <span>MCP Agent</span>
                </div>
                <div v-show="collapseItems.mcpAgent" class="section-content">
                  <HFormItem label="MCP服务器">
                    <HSelect
                      v-model="form.mcp_ids"
                      placeholder="请选择MCP服务器"
                      style="width: 100%"
                    >
                      <HOption
                        v-for="mcp in mcpOptions"
                        :key="mcp.id"
                        :label="mcp.name"
                        :value="mcp.id"
                      />
                    </HSelect>
                  </HFormItem>
                </div>
              </div>
              <!-- 知识库 -->
              <div class="config-section">
                <div class="section-header" @click="toggleCollapse('knowledge')">
                  <span class="collapse-arrow">{{ collapseItems.knowledge ? '&#9660;' : '&#9654;' }}</span>
                  <span>知识库</span>
                </div>
                <div v-show="collapseItems.knowledge" class="section-content">
                  <HFormItem label="选择知识库">
                    <HSelect
                      v-model="form.knowledge_ids"
                      placeholder="请选择知识库"
                      style="width: 100%"
                    >
                      <HOption
                        v-for="knowledge in knowledgeOptions"
                        :key="knowledge.id"
                        :label="knowledge.name"
                        :value="knowledge.id"
                      />
                    </HSelect>
                  </HFormItem>
                </div>
              </div>
              <!-- 工具 -->
              <div class="config-section">
                <div class="section-header" @click="toggleCollapse('tools')">
                  <span class="collapse-arrow">{{ collapseItems.tools ? '&#9660;' : '&#9654;' }}</span>
                  <span>工具</span>
                </div>
                <div v-show="collapseItems.tools" class="section-content">
                  <HFormItem label="选择工具">
                    <HSelect
                      v-model="form.tool_ids"
                      placeholder="请选择工具"
                      style="width: 100%"
                    >
                      <HOption
                        v-for="tool in toolOptions"
                        :key="tool.id"
                        :label="tool.name"
                        :value="tool.id"
                      />
                    </HSelect>
                  </HFormItem>
                </div>
              </div>
            </div>
          </div>
          <!-- 右侧：调试预览 -->
          <div class="right-panel">
            <div class="panel-header">
              <HButton type="secondary" class="debug-btn">
                &#9998; 调试预览
              </HButton>
            </div>
            <div class="debug-content">
              <div class="config-status">
                <span class="status-text">配置已更新</span>
              </div>
              <div class="chat-preview">
                <div class="chat-message ai-message">
                  <div class="message-avatar">
                    <img v-if="form.logo_url" :src="form.logo_url" alt="助手头像" />
                    <span v-else>+</span>
                  </div>
                  <div class="message-content">
                    <p>{{ form.description || '你好，我是智能助手 tmg-GPT，擅长理解和生成文本内容，随时准备帮助你解决问题并提供信息支持。' }}</p>
                  </div>
                </div>
              </div>
              <div class="recommended-questions">
                <h4>推荐问题</h4>
                <div class="question-list">
                  <div
                    v-for="(question, index) in recommendedQuestions"
                    :key="index"
                    class="question-item"
                  >
                    {{ question }}
                  </div>
                </div>
              </div>
              <div class="chat-input">
                <div class="input-wrapper">
                  <span class="input-icon">&#9998;</span>
                  <input type="text" placeholder="请输入问题" class="chat-input-field" />
                  <HButton type="primary" class="send-btn">
                    &#10148;
                  </HButton>
                </div>
                <div class="input-footer">
                  <span>内容由AI生成，仅供参考！</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </HDialog>
</template>

<style lang="scss" scoped>
.agent-config-dialog-inner {
  .dialog-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    border-bottom: 1px solid var(--harmony-comp-divider);
    background: var(--harmony-comp-background-primary);

    .header-left {
      display: flex;
      align-items: center;
      gap: 8px;

      .header-icon {
        font-size: 20px;
      }

      .header-title {
        font-size: 18px;
        font-weight: 600;
        color: var(--harmony-font-primary);
      }
    }

    .header-actions {
      display: flex;
      gap: 8px;
    }
  }

  .dialog-content {
    display: flex;
    height: 85vh;
    width: 100%;

    .left-panel {
      width: 25%;
      min-width: 300px;
      background-color: var(--harmony-comp-background-tertiary);
      border-right: 1px solid var(--harmony-comp-divider);
      overflow-y: auto;
      flex-shrink: 0;
      padding: 32px 24px;

      h4 {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 16px;
        color: var(--harmony-font-primary);
      }

      .prompt-textarea {
        width: 100%;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 14px;
        line-height: 1.5;
        border-radius: 6px;
        padding: 12px;
        border: 1px solid var(--harmony-comp-divider);
        background: var(--harmony-comp-background-primary);
        color: var(--harmony-font-primary);
        resize: vertical;
        box-sizing: border-box;

        &:focus {
          outline: none;
          border-color: var(--harmony-brand));
        }
      }
    }

    .middle-panel {
      width: 35%;
      min-width: 400px;
      background-color: var(--harmony-comp-background-primary);
      border-right: 1px solid var(--harmony-comp-divider);
      overflow-y: auto;
      flex-shrink: 0;
      padding: 32px 24px;

      .config-sections {
        .config-section {
          margin-bottom: 16px;
          border: 1px solid var(--harmony-comp-divider);
          border-radius: 8px;
          background-color: var(--harmony-comp-background-tertiary);

          .section-header {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px 16px;
            cursor: pointer;
            user-select: none;
            font-size: 15px;
            font-weight: 500;
            color: var(--harmony-font-primary);

            &:hover {
              background-color: var(--harmony-interactive-hover);
            }

            .collapse-arrow {
              font-size: 12px;
            }

            span {
              flex: 1;
              font-weight: 500;
            }
          }

          .section-content {
            padding: 16px;
            background-color: var(--harmony-comp-background-primary);
            border-top: 1px solid var(--harmony-comp-divider);
          }
        }
      }
    }

    .right-panel {
      width: 40%;
      min-width: 400px;
      background-color: var(--harmony-comp-background-tertiary);
      overflow-y: auto;
      flex-shrink: 0;
      padding: 32px 24px;

      .panel-header {
        margin-bottom: 16px;
      }

      .debug-content {
        .config-status {
          text-align: center;
          margin-bottom: 20px;

          .status-text {
            color: var(--harmony-confirm);
            font-size: 12px;
            border: 1px dashed var(--harmony-confirm);
            padding: 4px 12px;
            border-radius: 4px;
            background-color: var(--harmony-confirm-bg);
          }
        }

        .chat-preview {
          margin-bottom: 20px;

          .chat-message {
            display: flex;
            gap: 12px;
            margin-bottom: 16px;

            .message-avatar {
              width: 32px;
              height: 32px;
              border-radius: 6px;
              overflow: hidden;
              display: flex;
              align-items: center;
              justify-content: center;
              background-color: var(--harmony-comp-background-tertiary);

              img {
                width: 100%;
                height: 100%;
                object-fit: cover;
              }
            }

            .message-content {
              flex: 1;
              background-color: var(--harmony-comp-background-primary);
              padding: 12px;
              border-radius: 8px;
              box-shadow: var(--harmony-shadow-sm);

              p {
                margin: 0;
                color: var(--harmony-font-primary);
                font-size: 14px;
                line-height: 1.5;
              }
            }
          }
        }

        .recommended-questions {
          margin-bottom: 20px;

          h4 {
            margin: 0 0 12px 0;
            font-size: 14px;
            color: var(--harmony-font-primary);
          }

          .question-list {
            .question-item {
              padding: 8px 12px;
              background-color: var(--harmony-interactive-hover);
              border-radius: 6px;
              margin-bottom: 8px;
              font-size: 13px;
              color: var(--harmony-font-secondary);
              cursor: pointer;
              transition: all 0.3s;

              &:hover {
                background-color: var(--harmony-comp-emphasize-tertiary);
                color: var(--harmony-brand));
              }
            }
          }
        }

        .chat-input {
          .input-wrapper {
            display: flex;
            align-items: center;
            background-color: var(--harmony-comp-background-primary);
            border-radius: 8px;
            padding: 12px;
            box-shadow: var(--harmony-shadow-sm);

            .input-icon {
              color: var(--harmony-font-tertiary);
              margin-right: 8px;
            }

            .chat-input-field {
              flex: 1;
              border: none;
              outline: none;
              font-size: 14px;
              color: var(--harmony-font-primary);
              background: transparent;

              &::placeholder {
                color: var(--harmony-font-fourth);
              }
            }

            .send-btn {
              margin-left: 8px;
            }
          }

          .input-footer {
            text-align: center;
            margin-top: 8px;

            span {
              color: var(--harmony-font-tertiary);
              font-size: 12px;
            }
          }
        }
      }
    }
  }
}
</style>
