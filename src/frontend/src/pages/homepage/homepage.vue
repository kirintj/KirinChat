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
  background: transparent;
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
    font-size: var(--harmony-font-size-title-s);
    font-weight: 700;
    color: var(--harmony-font-primary);
    margin: 0;
  }
}

/* 搜索框 */
.search-section {
  width: 100%;
  max-width: 500px;

  .search-box {
    background: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 20px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

    &:focus-within {
      border-color: var(--harmony-brand);
    }
  }

  .search-input {
    width: 100%;
    min-height: 80px;
    border: none;
    background: transparent;
    padding: 8px;
    font-size: var(--harmony-font-size-body-m);
    line-height: 1.6;
    color: var(--harmony-font-primary);
    resize: none;
    font-family: inherit;

    &::placeholder {
      color: var(--harmony-font-tertiary);
    }
  }

  .search-footer {
    display: flex;
    justify-content: flex-end;
    padding-top: 8px;

    .send-btn {
      width: 36px;
      height: 36px;
      background: var(--harmony-brand);
      color: white;
      border: none;
      border-radius: 50%;
      font-size: var(--harmony-font-size-body-m);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;

      &:hover {
        opacity: 0.9;
      }
    }
  }
}

/* 案例 */
.examples-section {
  width: 100%;
  max-width: 560px;

  .examples-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }

  .example-card {
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 16px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.15s ease;

    &:hover {
      border-color: var(--harmony-brand);
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
    }

    &:active {
      background: var(--harmony-interactive-pressed);
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }

  .card-title {
    font-size: var(--harmony-font-size-body-m);
    font-weight: 600;
    color: var(--harmony-font-primary);
    margin: 0;
  }

  .card-tag {
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-tertiary);
    background: rgba(0, 0, 0, 0.05);
    padding: 2px 8px;
    border-radius: 8px;
  }

  .card-desc {
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-secondary);
    line-height: 1.5;
    margin: 0;
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .homepage {
    justify-content: flex-start;
    padding-top: 16px;
    gap: 16px;
  }

  .search-section {
    max-width: 100%;
  }

  .examples-section {
    max-width: 100%;
  }
}
</style>
