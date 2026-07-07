<script setup lang="ts">
import { ref, computed, inject } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isMobile = inject<import('vue').Ref<boolean>>('isMobile', ref(false))
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
  <!-- ==================== DESKTOP ==================== -->
  <div v-if="!isMobile" class="homepage">
    <div class="logo-section">
      <img src="../../assets/mars-agent.svg" alt="Mars Agent" class="logo" />
      <h1 class="brand-name">Mars Agent</h1>
    </div>

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

  <!-- ==================== MOBILE: hmos mobile-card ==================== -->
  <div v-else class="homepage-mobile">
    <!-- Search (first scrollable content item, overlaps titlebar) -->
    <section class="hm-search">
      <div class="hm-search__box">
        <textarea
          v-model="searchQuery"
          placeholder="Mars Agent会完成你的任务并输出结果。"
          class="hm-search__input"
          @keydown="handleKeydown"
        ></textarea>
        <button class="hm-search__btn" @click="handleSearch">➤</button>
      </div>
    </section>

    <!-- Section: examples -->
    <section class="hm-section">
      <header class="hm-section__header">
        <h2 class="hm-section__title">推荐案例</h2>
      </header>
      <div class="hm-grid-2col">
        <div
          v-for="(example, index) in examples"
          :key="index"
          class="hm-card"
          @click="handleExampleClick(example, index)"
        >
          <div class="hm-card__header">
            <h3 class="hm-card__title">{{ example.title }}</h3>
            <span class="hm-card__tag">{{ example.category }}</span>
          </div>
          <p class="hm-card__desc">{{ example.description }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<style lang="scss" scoped>
/* ==================== DESKTOP ==================== */
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

/* ==================== MOBILE: hmos mobile-card ==================== */
.homepage-mobile {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-section-gap-mobile, 16px);
  padding-top: var(--harmony-padding-level8, 16px);
}

/* Search bar — first scrollable content item */
.hm-search {
  position: relative;
  z-index: 30;

  &__box {
    display: flex;
    align-items: flex-end;
    gap: var(--harmony-padding-level4, 8px);
    background: var(--harmony-comp-background-primary);
    border: 1px solid var(--harmony-comp-divider);
    border-radius: var(--harmony-corner-radius-level8, 16px);
    padding: var(--harmony-padding-level6, 12px);
    transition: border-color 0.15s ease;

    &:focus-within {
      border-color: var(--harmony-brand);
    }
  }

  &__input {
    flex: 1;
    min-height: 40px;
    border: none;
    background: transparent;
    padding: var(--harmony-padding-level2, 4px);
    font-size: var(--harmony-font-size-body-m);
    line-height: 1.5;
    color: var(--harmony-font-primary);
    resize: none;
    font-family: inherit;

    &::placeholder {
      color: var(--harmony-font-tertiary);
    }
  }

  &__btn {
    width: var(--harmony-control-height-36, 36px);
    height: var(--harmony-control-height-36, 36px);
    flex-shrink: 0;
    background: var(--harmony-brand);
    color: white;
    border: none;
    border-radius: 50%;
    font-size: var(--harmony-font-size-body-m);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

/* Section with header */
.hm-section {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-padding-level6, 12px);

  &__header {
    display: flex;
    align-items: center;
  }

  &__title {
    font-size: var(--harmony-font-size-body-l, 16px);
    font-weight: 600;
    color: var(--harmony-font-primary);
    margin: 0;
  }
}

/* 2-column card grid (156px + 16px gap + 156px = 328px) */
.hm-grid-2col {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--harmony-card-gap-mobile, 12px);
}

/* Card */
.hm-card {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-padding-level4, 8px);
  padding: var(--harmony-padding-level8, 16px);
  background: var(--harmony-comp-background-primary);
  border: 1px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level8, 16px);
  cursor: pointer;
  transition: background 0.15s ease;

  &:active {
    background: var(--harmony-interactive-pressed);
  }

  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--harmony-padding-level4, 8px);
  }

  &__title {
    font-size: var(--harmony-font-size-body-m);
    font-weight: 600;
    color: var(--harmony-font-primary);
    margin: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__tag {
    flex-shrink: 0;
    font-size: var(--harmony-font-size-caption-l, 12px);
    color: var(--harmony-font-tertiary);
    background: var(--harmony-comp-background-secondary);
    padding: var(--harmony-padding-level1, 2px) var(--harmony-padding-level4, 8px);
    border-radius: var(--harmony-corner-radius-level4, 8px);
  }

  &__desc {
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-secondary);
    line-height: 1.5;
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}
</style>
