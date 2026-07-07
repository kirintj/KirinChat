<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { HDialog, HButton, HSelect, HOption } from '@/components/ui'
import { getSkillListAPI } from '../../../apis/interview'

const visible = defineModel<boolean>('visible', { default: false })

const emit = defineEmits<{
  (event: 'confirm', config: VoiceConfig): void
}>()

export interface VoiceConfig {
  skill_id: string
  difficulty: string
  resume_id?: string
  planned_duration: number
  phases: Record<string, boolean>
}

const skillId = ref('')
const difficulty = ref('medium')
const resumeId = ref('')
const duration = ref(30)
const phases = ref({ intro: true, tech: true, project: true, hr: true })

const skills = ref<any[]>([])

const difficulties = [
  { label: '简单', value: 'easy' },
  { label: '中等', value: 'medium' },
  { label: '困难', value: 'hard' },
]
const durations = [15, 30, 45, 60]
const phaseOptions = [
  { key: 'intro', label: '自我介绍' },
  { key: 'tech', label: '技术面试' },
  { key: 'project', label: '项目经验' },
  { key: 'hr', label: 'HR面试' },
]

onMounted(async () => {
  try {
    const skillRes = await getSkillListAPI()
    if (skillRes.data?.status_code === 200) skills.value = skillRes.data.data?.skills || []
  } catch {}
})

function handleConfirm() {
  if (!skillId.value) return
  emit('confirm', {
    skill_id: skillId.value,
    difficulty: difficulty.value,
    resume_id: resumeId.value || undefined,
    planned_duration: duration.value,
    phases: { ...phases.value },
  })
  visible.value = false
}
</script>

<template>
  <HDialog v-model="visible" title="语音面试配置" width="480px">
    <div class="config-form">
      <div class="form-item">
        <label>面试方向</label>
        <HSelect v-model="skillId" placeholder="请选择">
          <HOption v-for="s in skills" :key="s.id" :label="s.name || s.id" :value="s.id" />
        </HSelect>
      </div>
      <div class="form-item">
        <label>难度</label>
        <HSelect v-model="difficulty">
          <HOption v-for="d in difficulties" :key="d.value" :label="d.label" :value="d.value" />
        </HSelect>
      </div>
      <div class="form-item">
        <label>时长（分钟）</label>
        <HSelect v-model="duration">
          <HOption v-for="d in durations" :key="d" :label="d + ' 分钟'" :value="d" />
        </HSelect>
      </div>
      <div class="form-item">
        <label>面试阶段</label>
        <div class="phase-checks">
          <label v-for="p in phaseOptions" :key="p.key" class="phase-check">
            <input type="checkbox" v-model="phases[p.key]" />
            {{ p.label }}
          </label>
        </div>
      </div>
    </div>
    <template #footer>
      <HButton @click="visible = false">取消</HButton>
      <HButton type="primary" @click="handleConfirm" :disabled="!skillId">开始面试</HButton>
    </template>
  </HDialog>
</template>

<style lang="scss" scoped>
.config-form { display: flex; flex-direction: column; gap: 16px; padding: 8px 0; }
.form-item {
  display: flex; flex-direction: column; gap: 6px;
  label { font-size: var(--harmony-font-size-subtitle-s); font-weight: 500; color: var(--harmony-font-primary); }
}
.phase-checks { display: flex; gap: 16px; flex-wrap: wrap; }
.phase-check { display: flex; align-items: center; gap: 4px; font-size: var(--harmony-font-size-subtitle-s); cursor: pointer; input { cursor: pointer; } }
</style>
