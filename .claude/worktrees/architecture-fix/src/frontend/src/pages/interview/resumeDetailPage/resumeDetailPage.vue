<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useResumeStore } from '@/store/resume'
import { getResumePdfUrl } from '@/apis/resume'

const route = useRoute()
const router = useRouter()
const resumeStore = useResumeStore()

onMounted(() => {
  const id = route.params.id as string
  if (id) resumeStore.fetchDetail(id)
})

function downloadPdf() {
  const id = route.params.id as string
  window.open(getResumePdfUrl(id), '_blank')
}

function goBack() {
  router.push('/interview/resume')
}
</script>

<template>
  <div class="resume-detail" v-if="resumeStore.currentResume">
    <div class="detail-header">
      <button class="back-btn" @click="goBack">返回</button>
      <h2>{{ resumeStore.currentResume.filename }}</h2>
      <button v-if="resumeStore.currentResume.status === 'COMPLETED'" class="pdf-btn" @click="downloadPdf">下载 PDF 报告</button>
    </div>

    <div v-if="resumeStore.currentResume.status === 'PROCESSING'" class="analyzing">正在分析中，请稍候...</div>
    <div v-else-if="resumeStore.currentResume.status === 'FAILED'" class="error">分析失败: {{ resumeStore.currentResume.error_message }}</div>

    <div v-else-if="resumeStore.currentResume.analysis_result" class="analysis-content">
      <div class="score-section">
        <div class="score-circle">{{ resumeStore.currentResume.score }}</div>
        <span class="score-label">简历评分</span>
      </div>

      <div class="info-section">
        <h3>基本信息</h3>
        <div class="info-grid">
          <span>姓名: {{ resumeStore.currentResume.analysis_result.basic_info?.name || '未知' }}</span>
          <span>学历: {{ resumeStore.currentResume.analysis_result.basic_info?.education || '未知' }}</span>
          <span>工作年限: {{ resumeStore.currentResume.analysis_result.basic_info?.experience_years || 0 }}年</span>
          <span>职位: {{ resumeStore.currentResume.analysis_result.basic_info?.current_position || '未知' }}</span>
        </div>
      </div>

      <div class="skills-section">
        <h3>技能标签</h3>
        <div class="tags">
          <span v-for="skill in resumeStore.currentResume.analysis_result.skills" :key="skill" class="tag">{{ skill }}</span>
        </div>
      </div>

      <div class="suggestions-section">
        <h3>改进建议</h3>
        <ul><li v-for="s in resumeStore.currentResume.analysis_result.suggestions" :key="s">{{ s }}</li></ul>
      </div>
    </div>
  </div>
  <div v-else class="loading">加载中...</div>
</template>

<style scoped lang="scss">
.resume-detail { padding: 24px; }
.detail-header {
  display: flex; align-items: center; gap: 16px; margin-bottom: 24px;
  h2 { margin: 0; font-size: 18px; }
  .back-btn, .pdf-btn { padding: 6px 16px; border-radius: var(--radius-sm); border: 1px solid var(--color-border); background: var(--color-bg); cursor: pointer; }
  .pdf-btn { background: var(--color-primary); color: #fff; border: none; }
}
.score-section {
  text-align: center; margin-bottom: 32px;
  .score-circle {
    display: inline-flex; align-items: center; justify-content: center;
    width: 100px; height: 100px; border-radius: 50%;
    background: var(--color-primary); color: #fff; font-size: 32px; font-weight: bold;
  }
  .score-label { display: block; margin-top: 8px; color: #999; }
}
.info-section, .skills-section, .suggestions-section {
  margin-bottom: 24px; padding: 16px; background: var(--color-bg); border-radius: var(--radius-sm);
  h3 { margin: 0 0 12px; font-size: 16px; }
}
.info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
.tags {
  display: flex; flex-wrap: wrap; gap: 8px;
  .tag { padding: 4px 12px; background: var(--color-primary); color: #fff; border-radius: 4px; font-size: 13px; }
}
.analyzing, .error, .loading { text-align: center; padding: 60px; color: #999; }
.error { color: #ff4d4f; }
</style>
