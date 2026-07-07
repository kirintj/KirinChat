<script setup lang="ts">
import { ref } from 'vue'
import { sendMessage, uploadFile } from '../../apis/chat'
import { HButton, HInput, HMessage } from '@/components/ui'

const testInput = ref('')
const uploadedFile = ref('')
const chatLog = ref<Array<{role: string, content: string}>>([])

const sendTestMessage = () => {
  if (!testInput.value.trim()) {
    HMessage.warning('请输入消息内容')
    return
  }
  
  // 添加用户消息到日志
  chatLog.value.push({
    role: '用户',
    content: testInput.value
  })
  
  // 模拟发送消息
  const testData = {
    dialogId: 'test-dialog-123',
    userInput: testInput.value,
    fileUrl: uploadedFile.value || undefined
  }
  
  try {
    sendMessage(
      testData,
      (msg: any) => {
        try {
          const parsedData = JSON.parse(msg.data)
          if (parsedData.chunk) {
            // 添加AI回复到日志
            const lastMessage = chatLog.value.find(m => m.role === 'AI')
            if (lastMessage) {
              lastMessage.content += parsedData.chunk
            } else {
              chatLog.value.push({
                role: 'AI',
                content: parsedData.chunk
              })
            }
          }
        } catch (error) {
          console.error('解析消息失败:', error)
        }
      },
      () => {
        HMessage.success('对话完成')
        uploadedFile.value = '' // 清空文件
      }
    )
    
    testInput.value = ''
  } catch (error) {
    HMessage.error('发送消息失败')
    console.error('发送消息错误:', error)
  }
}

const testFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return
  
  try {
    HMessage.info('正在上传文件...')
    const response = await uploadFile(file)
    if (response.code === 200) {
      uploadedFile.value = response.data
      HMessage.success('文件上传成功')
    } else {
      HMessage.error(response.message || '文件上传失败')
    }
  } catch (error) {
    HMessage.error('文件上传失败')
    console.error('文件上传错误:', error)
  }
  
  // 清空文件输入
  if (target) {
    target.value = ''
  }
}
</script>

<template>
  <div class="test-chat">
    <h2>对话功能测试</h2>
    
    <div class="test-section">
      <h3>基本对话测试</h3>
      <HInput
        v-model="testInput"
        placeholder="输入测试消息"
        @keyup.enter="sendTestMessage"
      />
      <HButton @click="sendTestMessage" type="primary">发送测试消息</HButton>
    </div>
    
    <div class="test-section">
      <h3>文件上传测试</h3>
      <input 
        type="file" 
        @change="testFileUpload" 
        accept=".jpg,.jpeg,.png,.gif,.pdf,.txt,.docx"
      />
      <p v-if="uploadedFile">已上传文件: {{ uploadedFile }}</p>
    </div>
    
    <div class="test-section">
      <h3>聊天记录</h3>
      <div class="chat-log">
        <div v-for="(msg, index) in chatLog" :key="index" class="message">
          <strong>{{ msg.role }}:</strong> {{ msg.content }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.test-chat {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.test-section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid var(--harmony-comp-divider);
  border-radius: 8px;
}

.test-section h3 {
  margin-bottom: 15px;
  color: var(--harmony-font-primary);
}

.chat-log {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid var(--harmony-comp-divider);
  padding: 10px;
  background-color: var(--harmony-comp-background-secondary);
}

.message {
  margin-bottom: 10px;
  padding: 8px;
  background-color: var(--harmony-comp-background-primary);
  border-radius: 4px;
}

.message strong {
  color: var(--harmony-brand));
}
</style> 