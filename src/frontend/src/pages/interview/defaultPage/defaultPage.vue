<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { HButton, HMessage } from '@/components/ui'
import { getSkillListAPI } from '../../../apis/interview'
import type { SkillInfo } from '../../../apis/interview'
import { useInterviewStore } from '../../../store/interview'

const router = useRouter()
const interviewStore = useInterviewStore()
const skills = ref<SkillInfo[]>([])
const loading = ref(false)
const selectedSkill = ref<SkillInfo | null>(null)
const difficulty = ref('MEDIUM')
const questionCount = ref(10)

const difficultyOptions = [
  { value: 'EASY', label: '简单', desc: '基础概念和常见问题' },
  { value: 'MEDIUM', label: '中等', desc: '需要一定深度的分析' },
  { value: 'HARD', label: '困难', desc: '涉及底层原理和系统设计' },
]

const countOptions = [5, 10, 15, 20]

const fetchSkills = async () => {
  loading.value = true
  try {
    const res = await getSkillListAPI()
    if (res.data.status_code === 200 && res.data.data) {
      skills.value = res.data.data.skills || []
    }
  } catch {
    HMessage.error('获取技能列表失败')
  } finally {
    loading.value = false
  }
}

const selectSkill = (skill: SkillInfo) => {
  selectedSkill.value = skill
}

const goBack = () => {
  selectedSkill.value = null
}

const startInterview = async () => {
  if (!selectedSkill.value) return

  interviewStore.skillName = selectedSkill.value.name
  const success = await interviewStore.startInterview(
    selectedSkill.value.id,
    difficulty.value,
    questionCount.value
  )

  if (success) {
    router.push('/interview/chat')
  } else {
    HMessage.error('启动面试失败，请重试')
  }
}

onMounted(() => {
  fetchSkills()
  // If there's an active interview, show it
  if (interviewStore.isActive) {
    router.push('/interview/chat')
  }
})
</script>

<template>
  <div class="default-page">
    <!-- Skill Selection View -->
    <div v-if="!selectedSkill" class="skill-selection">
      <div class="page-header">
        <h2 class="page-title">选择面试方向</h2>
        <p class="page-subtitle">选择一个技术方向，AI 面试官将针对该领域进行深入提问</p>
      </div>

      <div v-if="loading" class="loading-state">加载中...</div>

      <div v-else-if="skills.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <div class="empty-text">暂无可用的面试技能</div>
      </div>

      <div v-else class="skill-grid">
        <div
          v-for="skill in skills"
          :key="skill.id"
          class="skill-card"
          @click="selectSkill(skill)"
        >
          <div class="skill-icon">{{ skill.icon || '📚' }}</div>
          <div class="skill-content">
            <div class="skill-name">{{ skill.name }}</div>
            <div class="skill-desc">{{ skill.description || '暂无描述' }}</div>
            <div class="skill-categories">
              <span
                v-for="cat in skill.categories?.slice(0, 4)"
                :key="cat"
                class="category-tag"
              >
                {{ cat }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="alternative-entry">
        <div class="divider">—— 或者 ——</div>
        <div class="entry-buttons">
          <button class="entry-btn voice-btn" @click="router.push('/voice-interview')">
            <span class="btn-icon">🎙️</span>
            <span class="btn-text">
              <span class="btn-title">语音面试</span>
              <span class="btn-desc">实时语音对话，模拟真实面试场景</span>
            </span>
          </button>
          <button class="entry-btn" @click="router.push('/interview/resume')">上传简历，AI 定制面试</button>
          <button class="entry-btn" @click="router.push('/interview/jd')">粘贴 JD，精准匹配面试</button>
        </div>
      </div>
    </div>

    <!-- Configuration View -->
    <div v-else class="config-view">
      <button class="back-btn" @click="goBack">← 返回</button>

      <div class="config-header">
        <div class="config-icon">{{ selectedSkill.icon || '📚' }}</div>
        <div>
          <h2 class="config-title">{{ selectedSkill.name }}</h2>
          <p class="config-desc">{{ selectedSkill.description || '暂无描述' }}</p>
        </div>
      </div>

      <div class="config-section">
        <div class="section-label">面试难度</div>
        <div class="difficulty-options">
          <div
            v-for="opt in difficultyOptions"
            :key="opt.value"
            :class="['diff-option', { active: difficulty === opt.value }]"
            @click="difficulty = opt.value"
          >
            <div class="diff-label">{{ opt.label }}</div>
            <div class="diff-desc">{{ opt.desc }}</div>
          </div>
        </div>
      </div>

      <div class="config-section">
        <div class="section-label">题目数量</div>
        <div class="count-options">
          <div
            v-for="count in countOptions"
            :key="count"
            :class="['count-option', { active: questionCount === count }]"
            @click="questionCount = count"
          >
            {{ count }} 题
          </div>
        </div>
      </div>

      <HButton
        type="primary"
        size="large"
        :loading="interviewStore.loading"
        class="start-btn"
        @click="startInterview"
      >
        开始面试
      </HButton>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.default-page {
  height: 100%;
  overflow-y: auto;
  padding: 32px 40px;
}

.page-header {
  margin-bottom: 32px;

  .page-title {
    font-size: 24px;
    font-weight: 600;
    color: var(--harmony-font-primary);
    margin: 0 0 8px;
  }

  .page-subtitle {
    font-size: 14px;
    color: var(--harmony-font-secondary);
    margin: 0;
  }
}

.loading-state {
  text-align: center;
  padding: 60px 0;
  color: var(--harmony-font-secondary);
}

.empty-state {
  text-align: center;
  padding: 60px 0;

  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }

  .empty-text {
    color: var(--harmony-font-tertiary);
  }
}

.skill-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.skill-card {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: var(--harmony-comp-background-primary);
  border: 1px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level6);
  cursor: pointer;
  transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);

  &:hover {
    border-color: var(--harmony-brand));
    box-shadow: var(--harmony-shadow-card);
    transform: translateY(-2px);
  }

  .skill-icon {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    background: var(--harmony-comp-emphasize-tertiary);
    border-radius: var(--harmony-corner-radius-level6);
    flex-shrink: 0;
  }

  .skill-content {
    flex: 1;
    min-width: 0;

    .skill-name {
      font-size: 16px;
      font-weight: 600;
      color: var(--harmony-font-primary);
      margin-bottom: 4px;
    }

    .skill-desc {
      font-size: 13px;
      color: var(--harmony-font-secondary);
      margin-bottom: 8px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .skill-categories {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;

      .category-tag {
        font-size: 11px;
        padding: 2px 8px;
        background: var(--harmony-comp-background-secondary);
        color: var(--harmony-font-secondary);
        border-radius: 4px;
      }
    }
  }
}

// Config view
.config-view {
  max-width: 640px;
}

.back-btn {
  background: none;
  border: none;
  color: var(--harmony-brand));
  cursor: pointer;
  font-size: 14px;
  font-family: inherit;
  padding: 0;
  margin-bottom: 24px;

  &:hover {
    text-decoration: underline;
  }
}

.config-header {
  display: flex;
  gap: 20px;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--harmony-comp-divider);

  .config-icon {
    width: 64px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 36px;
    background: var(--harmony-comp-emphasize-tertiary);
    border-radius: var(--harmony-corner-radius-level8);
    flex-shrink: 0;
  }

  .config-title {
    font-size: 22px;
    font-weight: 600;
    color: var(--harmony-font-primary);
    margin: 0 0 4px;
  }

  .config-desc {
    font-size: 14px;
    color: var(--harmony-font-secondary);
    margin: 0;
  }
}

.config-section {
  margin-bottom: 28px;

  .section-label {
    font-size: 14px;
    font-weight: 600;
    color: var(--harmony-font-primary);
    margin-bottom: 12px;
  }
}

.difficulty-options {
  display: flex;
  gap: 12px;

  .diff-option {
    flex: 1;
    padding: 16px;
    background: var(--harmony-comp-background-primary);
    border: 2px solid var(--harmony-comp-divider);
    border-radius: var(--harmony-corner-radius-level6);
    cursor: pointer;
    transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);

    &:hover {
      border-color: var(--harmony-brand));
    }

    &.active {
      border-color: var(--harmony-brand));
      background: var(--harmony-comp-emphasize-tertiary);
    }

    .diff-label {
      font-size: 15px;
      font-weight: 600;
      color: var(--harmony-font-primary);
      margin-bottom: 4px;
    }

    .diff-desc {
      font-size: 12px;
      color: var(--harmony-font-secondary);
    }
  }
}

.count-options {
  display: flex;
  gap: 12px;

  .count-option {
    padding: 10px 24px;
    background: var(--harmony-comp-background-primary);
    border: 2px solid var(--harmony-comp-divider);
    border-radius: var(--harmony-corner-radius-level6);
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    color: var(--harmony-font-primary);
    transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);

    &:hover {
      border-color: var(--harmony-brand));
    }

    &.active {
      border-color: var(--harmony-brand));
      background: var(--harmony-comp-emphasize-tertiary);
      color: var(--harmony-brand));
    }
  }
}

.start-btn {
  margin-top: 12px;
  width: 200px;
}

.alternative-entry {
  margin-top: 24px; text-align: center;
  .divider { color: var(--harmony-font-tertiary); margin-bottom: 16px; }
  .entry-buttons { display: flex; gap: 16px; justify-content: center; }
  .entry-btn {
    padding: 12px 24px; border-radius: var(--harmony-corner-radius-level4);
    border: 1px dashed var(--harmony-comp-divider); background: var(--harmony-comp-background-primary);
    cursor: pointer; font-size: 14px; transition: all 0.2s;
    &:hover { border-color: var(--harmony-brand)); color: var(--harmony-brand)); }

    &.voice-btn {
      display: flex;
      align-items: center;
      gap: 12px;
      border: 1px solid var(--harmony-brand));
      background: var(--harmony-comp-emphasize-tertiary);
      border-style: solid;
      padding: 14px 24px;
      .btn-icon { font-size: 24px; flex-shrink: 0; }
      .btn-text { display: flex; flex-direction: column; text-align: left; }
      .btn-title { font-weight: 600; font-size: 15px; color: var(--harmony-font-primary); }
      .btn-desc { font-size: 12px; color: var(--harmony-font-secondary); margin-top: 2px; }
      &:hover {
        border-color: var(--harmony-interactive-hover);
        box-shadow: var(--harmony-shadow-card);
        transform: translateY(-1px);
        color: inherit;
      }
    }
  }
}
</style>
