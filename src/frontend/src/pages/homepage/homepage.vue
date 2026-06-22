<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const searchQuery = ref('')

const isMac = computed(() => {
  return typeof navigator !== 'undefined' && navigator.platform.toUpperCase().indexOf('MAC') >= 0
})

const examples = [
  { title: '自动构建智能体', category: '自动模式', description: '使用多个工具相互配合完成自动构建智能体的任务' },
  { title: '深度搜索', category: '搜索模式', description: '连接外部互联网资源，扩展系统能力和数据源' },
  { title: 'AI日报', category: '生成模式', description: '对最近的AI新闻进行整理总结，可生成下载链接' },
  { title: '知识库问答', category: '知识库模式', description: '基于已有知识库进行精准问答和信息检索' }
]

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ path: '/mars', query: { message: searchQuery.value } })
  }
}

const handleKeydown = (event: KeyboardEvent) => {
  if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
    event.preventDefault()
    handleSearch()
  }
}

const handleExampleClick = (_: any, index: number) => {
  router.push({ path: '/mars', query: { example_id: String(index + 1) } })
}
</script>

<template>
  <div class="homepage">
    <!-- Logo -->
    <div class="logo-section">
      <img src="../../assets/mars-agent.svg" alt="Mars Agent" class="logo" />
      <h1 class="brand-name">Mars Agent</h1>
    </div>

    <!-- 搜索框 -->
    <div class="search-section">
      <div class="search-box">
        <textarea
          v-model="searchQuery"
          placeholder="Mars Agent会完成你的任务并输出结果。"
          class="search-input"
          @keydown="handleKeydown"
        ></textarea>
        <div class="search-footer">
          <button class="send-btn" @click="handleSearch">➤</button>
        </div>
      </div>
    </div>

    <!-- 案例 -->
    <div class="examples-section">
      <div class="examples-grid">
        <div
          v-for="(example, index) in examples"
          :key="index"
          class="example-card"
          @click="handleExampleClick(example, index)"
        >
          <div class="card-header">
            <h3 class="card-title">{{ example.title }}</h3>
            <span class="card-tag">{{ example.category }}</span>
          </div>
          <p class="card-desc">{{ example.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.homepage {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 24px;
  padding: 0 24px;
  background: var(--color-bg);
}

/* Logo */
.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;

  .logo {
    width: 48px;
    height: 48px;
  }

  .brand-name {
    font-size: 36px;
    font-weight: 800;
    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
  }
}

/* 搜索框 */
.search-section {
  width: 100%;
  max-width: 680px;

  .search-box {
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: 16px;
    box-shadow: var(--shadow-card);

    &:focus-within {
      border-color: var(--color-primary);
    }
  }

  .search-input {
    width: 100%;
    min-height: 80px;
    border: none;
    background: transparent;
    padding: 8px;
    font-size: 16px;
    line-height: 1.6;
    color: var(--color-text-primary);
    outline: none;
    resize: none;
    font-family: inherit;

    &::placeholder {
      color: var(--color-text-tertiary);
    }
  }

  .search-footer {
    display: flex;
    justify-content: flex-end;
    padding-top: 8px;

    .send-btn {
      width: 36px;
      height: 36px;
      background: var(--color-primary);
      color: white;
      border: none;
      border-radius: 50%;
      font-size: 14px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;

      &:hover {
        background: var(--color-primary-hover);
      }
    }
  }
}

/* 案例 */
.examples-section {
  width: 100%;
  max-width: 900px;

  .examples-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
  }

  .example-card {
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: 16px;
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      border-color: var(--color-primary);
      box-shadow: var(--shadow-card);
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }

  .card-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0;
  }

  .card-tag {
    font-size: 11px;
    color: var(--color-text-tertiary);
    background: var(--color-bg-secondary);
    padding: 2px 8px;
    border-radius: var(--radius-sm);
  }

  .card-desc {
    font-size: 12px;
    color: var(--color-text-secondary);
    line-height: 1.5;
    margin: 0;
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .homepage {
    padding: 0 16px;
  }

  .logo-section .brand-name {
    font-size: 28px;
  }

  .examples-section .examples-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
