<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { HMessage } from '@/components/ui'
import { getInterviewHistoryAPI, getSkillListAPI } from '../../../apis/interview'
import type { InterviewSession } from '../../../apis/interview'
import QuickEntryCard from '../../../components/hub/QuickEntryCard.vue'
import ActiveSessionCard from '../../../components/hub/ActiveSessionCard.vue'
import RecentInterviewItem from '../../../components/hub/RecentInterviewItem.vue'
import SkillStatCard from '../../../components/hub/SkillStatCard.vue'

const router = useRouter()
const loading = ref(true)
const sessions = ref<InterviewSession[]>([])
// skill_id → 中文名称的映射表，从 /skill/list 接口获取
const skillMap = ref<Record<string, string>>({})

// --- 快捷入口配置：4 个面试功能入口 ---
const quickEntries = [
  { icon: '✏️', title: '文字面试', description: '选择技能方向，开始 AI 面试', route: '/interview' },
  { icon: '🎙️', title: '语音面试', description: '实时语音对话，模拟真实面试', route: '/voice-interview' },
  { icon: '📄', title: '上传简历', description: '上传简历获取 AI 分析报告', route: '/interview/resume' },
  { icon: '🔍', title: '解析 JD', description: '粘贴职位描述，定制面试题目', route: '/interview/jd' },
]

// --- 从全量 session 数据中派生各区块所需数据 ---

// 进行中的面试：状态为 IN_PROGRESS 或 CREATED
const activeSessions = computed(() =>
  sessions.value.filter(s => s.status === 'IN_PROGRESS' || s.status === 'CREATED')
)

// 最近面试：取已完成的前 5 条
const recentInterviews = computed(() =>
  sessions.value
    .filter(s => s.status === 'EVALUATED' || s.status === 'COMPLETED')
    .slice(0, 5)
)

interface SkillStat {
  skillName: string
  count: number
  avgScore: number
}

// 技能统计：按 skill_id 聚合面试次数和平均分
const skillStats = computed<SkillStat[]>(() => {
  const evaluated = sessions.value.filter(s => s.status === 'EVALUATED' || s.status === 'COMPLETED')
  const grouped: Record<string, { count: number; totalScore: number }> = {}

  for (const s of evaluated) {
    if (!grouped[s.skill_id]) {
      grouped[s.skill_id] = { count: 0, totalScore: 0 }
    }
    grouped[s.skill_id].count += 1
    if (s.total_score != null) {
      grouped[s.skill_id].totalScore += s.total_score
    }
  }

  return Object.entries(grouped).map(([skillId, stats]) => ({
    skillName: skillMap.value[skillId] || skillId,
    count: stats.count,
    avgScore: stats.totalScore > 0 ? Math.round(stats.totalScore / stats.count * 10) / 10 : 0,
  })).sort((a, b) => b.count - a.count)  // 按面试次数降序排列
})

// 总面试次数
const totalCount = computed(() => skillStats.value.reduce((sum, s) => sum + s.count, 0))
// 总体平均分
const overallAvg = computed(() => {
  const scored = sessions.value.filter(s => s.total_score != null)
  if (scored.length === 0) return 0
  const sum = scored.reduce((acc, s) => acc + (s.total_score ?? 0), 0)
  return Math.round(sum / scored.length * 10) / 10
})

// --- 工具函数 ---

// 将 skill_id 转为中文显示名称，找不到时回退为原始 id
const getSkillName = (skillId: string) => skillMap.value[skillId] || skillId

// --- 数据加载 ---

// 并行获取面试历史和技能列表，减少等待时间
const loadData = async () => {
  loading.value = true
  try {
    const [historyRes, skillRes] = await Promise.all([
      getInterviewHistoryAPI(),
      getSkillListAPI(),
    ])

    if (historyRes.data.status_code === 200 && historyRes.data.data) {
      sessions.value = historyRes.data.data.sessions || []
    }

    // 构建 skill_id → name 映射表，供各区块显示中文名
    if (skillRes.data.status_code === 200 && skillRes.data.data) {
      const map: Record<string, string> = {}
      for (const skill of (skillRes.data.data.skills || [])) {
        map[skill.id] = skill.name
      }
      skillMap.value = map
    }
  } catch {
    HMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="hub-page">
    <!-- 页面标题 -->
    <div class="hub-header">
      <h2 class="hub-title">面试中心</h2>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">加载中...</div>

    <template v-else>
      <!-- 区块1：快捷入口 - 4 个功能入口卡片横排 -->
      <section class="hub-section">
        <h3 class="section-title">快捷入口</h3>
        <div class="quick-entry-grid">
          <QuickEntryCard
            v-for="entry in quickEntries"
            :key="entry.title"
            :icon="entry.icon"
            :title="entry.title"
            :description="entry.description"
            @click="router.push(entry.route)"
          />
        </div>
      </section>

      <!-- 区块2：进行中的面试 - 水平滚动卡片 -->
      <section class="hub-section">
        <div class="section-header">
          <h3 class="section-title">进行中的面试</h3>
          <span class="section-link" @click="router.push('/interview')">查看全部 &rarr;</span>
        </div>
        <div v-if="activeSessions.length > 0" class="active-grid">
          <ActiveSessionCard
            v-for="session in activeSessions"
            :key="session.id"
            :skill-name="getSkillName(session.skill_id)"
            :progress="session.progress"
            @click="router.push({ path: '/interview/chat', query: { sessionId: session.id } })"
          />
        </div>
        <div v-else class="empty-state">
          <p class="empty-text">没有进行中的面试</p>
          <button class="empty-btn" @click="router.push('/interview')">开始新面试</button>
        </div>
      </section>

      <!-- 区块3+4：最近面试 + 技能统计，左右两栏布局 -->
      <div class="bottom-grid">
        <!-- 最近面试摘要 -->
        <section class="hub-section">
          <div class="section-header">
            <h3 class="section-title">最近面试</h3>
            <router-link to="/interview/history" class="view-all-link">查看全部 &rarr;</router-link>
          </div>
          <div v-if="recentInterviews.length > 0" class="recent-list">
            <RecentInterviewItem
              v-for="session in recentInterviews"
              :key="session.id"
              :skill-name="getSkillName(session.skill_id)"
              :score="session.total_score ?? 0"
              :time-label="'已完成'"
              @click="router.push({ path: '/interview/report', query: { sessionId: session.id } })"
            />
          </div>
          <div v-else class="empty-state">
            <p class="empty-text">暂无面试记录</p>
          </div>
        </section>

        <!-- 技能统计概览 -->
        <section class="hub-section">
          <div class="section-header">
            <h3 class="section-title">技能统计</h3>
          </div>
          <div v-if="skillStats.length > 0">
            <!-- 总览数据 -->
            <div class="stats-overview">
              <div class="stat-item">
                <span class="stat-value">{{ totalCount }}</span>
                <span class="stat-label">总面试次数</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ overallAvg }}</span>
                <span class="stat-label">总体平均分</span>
              </div>
            </div>
            <!-- 各技能明细列表 -->
            <div class="stats-list">
              <SkillStatCard
                v-for="stat in skillStats"
                :key="stat.skillName"
                :skill-name="stat.skillName"
                :count="stat.count"
                :avg-score="stat.avgScore"
              />
            </div>
          </div>
          <div v-else class="empty-state">
            <p class="empty-text">暂无统计数据</p>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<style lang="scss" scoped>
.hub-page {
  padding: 24px 32px;
  max-width: 1100px;
  overflow-y: auto;
  height: 100%;
}

.hub-header {
  margin-bottom: 24px;
}

.hub-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary, #1f2937);
  margin: 0;
}

.loading-state {
  text-align: center;
  padding: 48px 0;
  color: var(--text-secondary, #6b7280);
  font-size: 14px;
}

.hub-section {
  margin-bottom: 28px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #1f2937);
  margin: 0 0 14px 0;

  .section-header & {
    margin-bottom: 0;  // section-header 内的标题不需要下边距
  }
}

.section-link {
  font-size: 13px;
  color: var(--primary-color, #6366f1);
  cursor: pointer;

  &:hover {
    text-decoration: underline;
  }
}

.view-all-link {
  font-size: 13px;
  color: var(--harmony-brand));
  text-decoration: none;
  font-weight: 400;

  &:hover {
    text-decoration: underline;
  }
}

// 快捷入口 4 列网格
.quick-entry-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

// 进行中面试水平滚动
.active-grid {
  display: flex;
  gap: 14px;
  overflow-x: auto;
  padding-bottom: 4px;
}

// 底部两栏布局
.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

// 空状态样式
.empty-state {
  text-align: center;
  padding: 32px 16px;
  border-radius: 10px;
  border: 1px dashed var(--border-color, #e5e7eb);
}

.empty-text {
  font-size: 14px;
  color: var(--text-tertiary, #9ca3af);
  margin: 0 0 12px 0;
}

.empty-btn {
  padding: 8px 20px;
  border-radius: 8px;
  border: 1px solid var(--primary-color, #6366f1);
  background: transparent;
  color: var(--primary-color, #6366f1);
  font-size: 13px;
  cursor: pointer;

  &:hover {
    background: var(--primary-light, #eef2ff);
  }
}

// 技能统计总览
.stats-overview {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light, #f3f4f6);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary, #1f2937);
}

.stat-label {
  font-size: 12px;
  color: var(--text-tertiary, #9ca3af);
}

// 响应式：平板端快捷入口改为 2 列，底部堆叠
@media (max-width: 1199px) {
  .quick-entry-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .bottom-grid {
    grid-template-columns: 1fr;
  }
}

// 响应式：移动端快捷入口改为单列
@media (max-width: 767px) {
  .hub-page {
    padding: 16px;
  }

  .quick-entry-grid {
    grid-template-columns: 1fr;
  }
}
</style>
