<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useJdStore } from '@/store/jd'

const router = useRouter()
const jdStore = useJdStore()

async function handleParse() {
  await jdStore.parseJd()
}

async function handleStartInterview() {
  const skill = await jdStore.createSkill()
  if (skill) {
    router.push(`/interview?skillId=${skill.skill_id}`)
  }
}

function goBack() {
  jdStore.reset()
  router.push('/interview')
}
</script>

<template>
  <div class="jd-page">
    <div class="page-header">
      <button class="back-btn" @click="goBack">返回</button>
      <h2>JD 解析 — 精准匹配面试</h2>
    </div>

    <div class="input-section">
      <textarea v-model="jdStore.jdText" placeholder="粘贴职位描述（JD）内容..." rows="10"></textarea>
      <button class="parse-btn" @click="handleParse" :disabled="jdStore.parsing || !jdStore.jdText.trim()">
        {{ jdStore.parsing ? '解析中...' : '开始解析' }}
      </button>
    </div>

    <div v-if="jdStore.parseResult" class="result-section">
      <h3>解析结果</h3>
      <div class="result-grid">
        <div class="result-item">
          <label>公司</label>
          <span>{{ jdStore.parseResult.company }}</span>
        </div>
        <div class="result-item">
          <label>职位</label>
          <span>{{ jdStore.parseResult.position }}</span>
        </div>
        <div class="result-item">
          <label>经验要求</label>
          <span>{{ jdStore.parseResult.experience_required }}</span>
        </div>
      </div>

      <div class="categories-section">
        <h4>技术要求</h4>
        <div class="category-tags">
          <span v-for="cat in jdStore.parseResult.categories" :key="cat.key" class="cat-tag">{{ cat.label }}</span>
        </div>
      </div>

      <button class="start-btn" @click="handleStartInterview" :disabled="jdStore.creating">
        {{ jdStore.creating ? '创建中...' : '开始面试' }}
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.jd-page { padding: 24px; }
.page-header {
  display: flex; align-items: center; gap: 16px; margin-bottom: 24px;
  h2 { margin: 0; font-size: 20px; }
  .back-btn { padding: 6px 16px; border-radius: var(--radius-sm); border: 1px solid var(--color-border); background: var(--color-bg); cursor: pointer; }
}
.input-section {
  textarea {
    width: 100%; padding: 12px; border: 1px solid var(--color-border);
    border-radius: var(--radius-sm); resize: vertical; font-size: 14px; font-family: inherit;
  }
  .parse-btn {
    margin-top: 12px; padding: 10px 24px; background: var(--color-primary);
    color: var(--color-bg); border: none; border-radius: var(--radius-sm); cursor: pointer;
    &:disabled { opacity: 0.6; cursor: not-allowed; }
  }
}
.result-section {
  margin-top: 24px; padding: 20px; background: var(--color-bg); border-radius: var(--radius-sm);
  h3 { margin: 0 0 16px; }
}
.result-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px;
  .result-item {
    label { display: block; font-size: var(--font-size-xs); color: var(--color-text-tertiary); margin-bottom: 4px; }
    span { font-size: var(--font-size-lg); font-weight: 500; }
  }
}
.categories-section { margin-bottom: 20px; h4 { margin: 0 0 12px; } }
.category-tags {
  display: flex; flex-wrap: wrap; gap: 8px;
  .cat-tag { padding: 4px 12px; background: var(--color-primary); color: var(--color-bg); border-radius: 4px; font-size: 13px; }
}
.start-btn {
  padding: 12px 32px; background: var(--color-success); color: var(--color-bg); border: none;
  border-radius: var(--radius-sm); font-size: 16px; cursor: pointer;
  &:disabled { opacity: 0.6; cursor: not-allowed; }
}
</style>
