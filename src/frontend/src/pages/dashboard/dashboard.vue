<template>
  <div v-if="!isMobile" class="dashboard-container">
    <div class="dashboard-header">
      <div class="title-wrap">
        <h2>数据看板</h2>
      </div>
      <p class="sub">根据模型/智能体与时间范围查看调用与 Token 用量趋势</p>
    </div>

    <div class="filters-container">
      <div class="filter-group">
        <label>模型</label>
        <HSelect
          v-model="filters.model"
          placeholder="全部模型"
          clearable
          filterable
          class="filter-select"
          @change="handleFilterChange"
          style="width: 250px"
        >
          <HOption label="全部" value="" />
          <HOption
            v-for="model in modelsList"
            :key="model"
            :label="model"
            :value="model"
          />
        </HSelect>
      </div>

      <div class="filter-group">
        <label>智能体</label>
        <HSelect
          v-model="filters.agent"
          placeholder="全部智能体"
          clearable
          filterable
          class="filter-select"
          @change="handleFilterChange"
          style="width: 250px"
        >
          <HOption label="全部" value="" />
          <HOption
            v-for="agent in agentsList"
            :key="agent"
            :label="agent"
            :value="agent"
          />
        </HSelect>
      </div>

      <div class="filter-group">
        <label>时间范围</label>
        <HSelect
          v-model="filters.delta_days"
          class="filter-select"
          @change="handleFilterChange"
          style="width: 220px"
        >
          <HOption label="周内" :value="7" />
          <HOption label="月内" :value="30" />
          <HOption label="年内" :value="365" />
          <HOption label="全部" :value="10000" />
        </HSelect>
      </div>

      <HButton
        type="primary"
        class="filter-action"
        @click="handleRefresh"
        :loading="loading"
      >
        刷新数据
      </HButton>
    </div>

    <div class="kpi-container">
      <div class="kpi-card kpi-card--primary">
        <div class="kpi-top">
          <div class="kpi-title">总调用次数</div>
          <div class="kpi-icon">
              <Icon icon="mdi:file-document" :width="22" :height="22" />
            </div>
        </div>
        <div class="kpi-value">{{ totalCalls.toLocaleString() }}</div>
        <div class="kpi-desc">{{ periodText }}</div>
      </div>
      <div class="kpi-card kpi-card--warning">
        <div class="kpi-top">
          <div class="kpi-title">总 Token 消耗</div>
          <div class="kpi-icon">
              <Icon icon="mdi:plus-circle" :width="22" :height="22" />
            </div>
        </div>
        <div class="kpi-value">{{ totalTokens.toLocaleString() }}</div>
        <div class="kpi-desc">输入 + 输出（{{ periodText }}）</div>
      </div>
    </div>

    <div class="charts-container">
      <!-- 调用次数折线图 -->
      <div class="chart-wrapper" style="position: relative;">
        <div v-if="loading" class="loading-overlay">
          <div class="loading-spinner"></div>
        </div>
        <div class="chart-title">调用次数统计</div>
        <div class="chart-content" ref="callCountChartRef"></div>
        <div class="empty" v-if="!hasCallCountData">暂无数据</div>
      </div>

      <!-- Token使用量柱状图 -->
      <div class="chart-wrapper" style="position: relative;">
        <div v-if="loading" class="loading-overlay">
          <div class="loading-spinner"></div>
        </div>
        <div class="chart-title">Token使用量统计</div>
        <div class="chart-content" ref="tokenUsageChartRef"></div>
        <div class="empty" v-if="!hasTokenUsageData">暂无数据</div>
      </div>
    </div>
  </div>

  <!-- ==================== MOBILE: hmos mobile-card ==================== -->
  <div v-else class="dashboard-mobile">
    <!-- KPI section: 2 columns -->
    <section class="dm-section">
      <header class="dm-section__header">
        <h2 class="dm-section__title">数据概览</h2>
      </header>
      <div class="dm-grid-2col">
        <div class="dm-kpi">
          <span class="dm-kpi__value">{{ totalCalls.toLocaleString() }}</span>
          <span class="dm-kpi__label">总调用次数</span>
          <span class="dm-kpi__desc">{{ periodText }}</span>
        </div>
        <div class="dm-kpi">
          <span class="dm-kpi__value">{{ totalTokens.toLocaleString() }}</span>
          <span class="dm-kpi__label">总 Token 消耗</span>
          <span class="dm-kpi__desc">{{ periodText }}</span>
        </div>
      </div>
    </section>

    <!-- Mobile filters -->
    <section class="dm-section">
      <header class="dm-section__header">
        <h2 class="dm-section__title">筛选条件</h2>
      </header>
      <div class="dm-filters">
        <div class="dm-filter">
          <label class="dm-filter__label">模型</label>
          <HSelect
            v-model="filters.model"
            placeholder="全部模型"
            clearable
            filterable
            class="dm-filter__select"
            @change="handleFilterChange"
          >
            <HOption label="全部" value="" />
            <HOption
              v-for="model in modelsList"
              :key="model"
              :label="model"
              :value="model"
            />
          </HSelect>
        </div>
        <div class="dm-filter">
          <label class="dm-filter__label">智能体</label>
          <HSelect
            v-model="filters.agent"
            placeholder="全部智能体"
            clearable
            filterable
            class="dm-filter__select"
            @change="handleFilterChange"
          >
            <HOption label="全部" value="" />
            <HOption
              v-for="agent in agentsList"
              :key="agent"
              :label="agent"
              :value="agent"
            />
          </HSelect>
        </div>
        <div class="dm-filter">
          <label class="dm-filter__label">时间范围</label>
          <HSelect
            v-model="filters.delta_days"
            class="dm-filter__select"
            @change="handleFilterChange"
          >
            <HOption label="周内" :value="7" />
            <HOption label="月内" :value="30" />
            <HOption label="年内" :value="365" />
            <HOption label="全部" :value="10000" />
          </HSelect>
        </div>
        <HButton
          type="primary"
          class="dm-filter__action"
          @click="handleRefresh"
          :loading="loading"
        >
          刷新数据
        </HButton>
      </div>
    </section>

    <!-- Call count chart -->
    <section class="dm-section">
      <header class="dm-section__header">
        <h2 class="dm-section__title">调用次数统计</h2>
      </header>
      <div class="dm-chart">
        <div v-if="loading" class="loading-overlay">
          <div class="loading-spinner"></div>
        </div>
        <div class="dm-chart__content" ref="callCountChartRef"></div>
        <div class="empty" v-if="!hasCallCountData">暂无数据</div>
      </div>
    </section>

    <!-- Token usage chart -->
    <section class="dm-section">
      <header class="dm-section__header">
        <h2 class="dm-section__title">Token使用量统计</h2>
      </header>
      <div class="dm-chart">
        <div v-if="loading" class="loading-overlay">
          <div class="loading-spinner"></div>
        </div>
        <div class="dm-chart__content" ref="tokenUsageChartRef"></div>
        <div class="empty" v-if="!hasTokenUsageData">暂无数据</div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick, computed, inject } from 'vue'
import { HMessage, HSelect, HOption, HButton } from '@/components/ui'
// 按需引入 ECharts，避免打包体积和解析问题
import * as echarts from 'echarts/core'
import type { ECharts as EChartsInstance } from 'echarts/core'
import { LineChart, BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent, DatasetComponent, DataZoomComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
echarts.use([TitleComponent, TooltipComponent, LegendComponent, GridComponent, DatasetComponent, DataZoomComponent, LineChart, BarChart, CanvasRenderer])
import {
  getUsageStatsAPI,
  getUsageCountAPI,
  getUsageModelsAPI,
  getUsageAgentsAPI,
  type UsageStatsRequest,
  type UsageDataByDate,
  type UsageCountByDate
} from '../../apis/usage-stats'

// Mobile detection
const isMobile = inject<import('vue').Ref<boolean>>('isMobile', ref(false))

// 筛选条件
const filters = ref<UsageStatsRequest>({
  model: '',
  agent: '',
  delta_days: 10000
})

// 数据列表
const modelsList = ref<string[]>([])
const agentsList = ref<string[]>([])

// 加载状态
const loading = ref(false)

// 图表引用
const callCountChartRef = ref<HTMLElement | null>(null)
const tokenUsageChartRef = ref<HTMLElement | null>(null)

// 图表实例
let callCountChart: EChartsInstance | null = null
let tokenUsageChart: EChartsInstance | null = null

// KPI 与空数据状态
const totalCalls = ref(0)
const totalTokens = ref(0)
const hasCallCountData = ref(true)
const hasTokenUsageData = ref(true)
const periodText = computed(() => {
  const d = Number(filters.value.delta_days || 10000)
  if (d === 7) return '近7天'
  if (d === 30) return '近30天'
  if (d === 365) return '近一年'
  return '全部时间'
})

// 获取模型列表
const fetchModelsList = async () => {
  try {
    const res = await getUsageModelsAPI()
    if (res.data.status_code === 200) {
      modelsList.value = res.data.data || []
    }
  } catch (error) {
    console.error('获取模型列表失败:', error)
  }
}

// 获取智能体列表
const fetchAgentsList = async () => {
  try {
    const res = await getUsageAgentsAPI()
    if (res.data.status_code === 200) {
      agentsList.value = res.data.data || []
    }
  } catch (error) {
    console.error('获取智能体列表失败:', error)
  }
}

// 初始化调用次数折线图
const initCallCountChart = () => {
  if (!callCountChartRef.value) return
  
  if (callCountChart) {
    callCountChart.dispose()
  }
  
  callCountChart = echarts.init(callCountChartRef.value)
  
  const option = {
    color: ['#5B8FF9', '#61DDAA', '#65789B', '#F6BD16', '#7262fd', '#78D3F8'],
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: [],
      top: 10,
      textStyle: { color: '#606266' }
    },
    grid: {
      left: '3%',
      right: '3%',
      bottom: 40,
      top: 50,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: [],
      axisLine: { lineStyle: { color: '#dcdfe6' } },
      axisLabel: { color: '#606266' }
    },
    yAxis: {
      type: 'value',
      name: '调用次数',
      nameTextStyle: { color: '#606266' },
      splitLine: { lineStyle: { color: '#eee' } },
      axisLabel: { color: '#606266' }
    },
    dataZoom: [{ type: 'inside' }],
    series: []
  }
  
  callCountChart.setOption(option)
}

// 初始化Token使用量柱状图
const initTokenUsageChart = () => {
  if (!tokenUsageChartRef.value) return
  
  if (tokenUsageChart) {
    tokenUsageChart.dispose()
  }
  
  tokenUsageChart = echarts.init(tokenUsageChartRef.value)
  
  const option = {
    color: ['#5AD8A6', '#5B8FF9'],
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params: any) => {
        const list = Array.isArray(params) ? params : []
        const input = list.find((p: any) => p?.seriesName === '输入Token')?.value || 0
        const output = list.find((p: any) => p?.seriesName === '输出Token')?.value || 0
        const total = Number(input || 0) + Number(output || 0)
        const date = list[0]?.axisValueLabel || ''
        return `${date}<br/>输入Token：${input}<br/>输出Token：${output}<br/><b>总Token：${total}</b>`
      }
    },
    legend: {
      data: ['输入Token', '输出Token'],
      top: 10,
      textStyle: { color: '#606266' }
    },
    grid: {
      left: '3%',
      right: '3%',
      bottom: 40,
      top: 50,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: [],
      axisLine: { lineStyle: { color: '#dcdfe6' } },
      axisLabel: { color: '#606266' }
    },
    yAxis: {
      type: 'value',
      name: 'Token数量',
      nameTextStyle: { color: '#606266' },
      splitLine: { lineStyle: { color: '#eee' } },
      axisLabel: { color: '#606266' }
    },
    series: [
      {
        name: '输入Token',
        type: 'bar',
        stack: 'tokens',
        data: [],
        barMaxWidth: 20,
        itemStyle: {}
      },
      {
        name: '输出Token',
        type: 'bar',
        stack: 'tokens',
        data: [],
        barMaxWidth: 20,
        itemStyle: {},
        label: {
          show: true,
          position: 'top',
          color: '#606266',
          fontWeight: 600,
          formatter: (p: any) => {
            const idx = p.dataIndex
            // 输出柱顶端显示 总Token = 输入 + 输出
            const inputVal = (tokenUsageChart?.getOption()?.series?.[0] as any)?.data?.[idx] || 0
            const outputVal = (tokenUsageChart?.getOption()?.series?.[1] as any)?.data?.[idx] || 0
            return `${Number(inputVal || 0) + Number(outputVal || 0)}`
          }
        }
      }
    ]
  }
  
  tokenUsageChart.setOption(option)
}

// 更新调用次数折线图
const updateCallCountChart = (data: UsageCountByDate) => {
  if (!callCountChart) return
  
  const dates = Object.keys(data).sort()
  const seriesMap = new Map<string, number[]>()
  
  // 根据筛选条件确定数据来源（agent或model）
  const dataKey = filters.value.agent ? 'agent' : 'model'
  
  // 收集所有系列数据
  dates.forEach(date => {
    const dayData = data[date][dataKey]
    Object.entries(dayData).forEach(([name, count]) => {
      if (!seriesMap.has(name)) {
        seriesMap.set(name, new Array(dates.length).fill(0))
      }
      const index = dates.indexOf(date)
      seriesMap.get(name)![index] = count
    })
  })
  
  // 构建图表配置
  const series = Array.from(seriesMap.entries()).map(([name, data]) => ({
    name,
    type: 'line',
    data,
    smooth: true,
    symbol: 'circle',
    symbolSize: 6,
    lineStyle: { width: 2 },
    areaStyle: {
      opacity: 0.08
    }
  }))
  
  callCountChart.setOption({
    xAxis: {
      data: dates
    },
    legend: {
      data: Array.from(seriesMap.keys())
    },
    series
  })

  hasCallCountData.value = dates.length > 0 && series.length > 0 && series.some(s => (s.data as number[]).some(v => v > 0))
}

// 更新Token使用量柱状图
const updateTokenUsageChart = (data: UsageDataByDate) => {
  if (!tokenUsageChart) return
  
  const dates = Object.keys(data).sort()
  
  // 根据筛选条件确定数据来源（agent或model）
  const dataKey = filters.value.agent ? 'agent' : 'model'
  
  const inputTokens: number[] = []
  const outputTokens: number[] = []
  const totalTokens: number[] = []
  
  // 聚合每天的Token数据
  dates.forEach(date => {
    const dayData = data[date][dataKey]
    let dayInputTotal = 0
    let dayOutputTotal = 0
    let dayTotal = 0
    
    Object.values(dayData).forEach((tokenData: any) => {
      dayInputTotal += tokenData.input_tokens || 0
      dayOutputTotal += tokenData.output_tokens || 0
      dayTotal += tokenData.total_tokens || 0
    })
    
    inputTokens.push(dayInputTotal)
    outputTokens.push(dayOutputTotal)
    totalTokens.push(dayTotal)
  })
  
  tokenUsageChart.setOption({
    xAxis: {
      data: dates
    },
    series: [
      {
        name: '输入Token',
        data: inputTokens
      },
      {
        name: '输出Token',
        data: outputTokens
      }
    ]
  })

  hasTokenUsageData.value = dates.length > 0 && (inputTokens.some(v => v > 0) || outputTokens.some(v => v > 0))
}

// 获取使用统计数据
const fetchUsageData = async () => {
  loading.value = true
  
  try {
    const params: UsageStatsRequest = {
      agent: filters.value.agent || undefined,
      model: filters.value.model || undefined,
      delta_days: filters.value.delta_days
    }
    
    // 获取调用次数数据
    const countRes = await getUsageCountAPI(params)
    if (countRes.data.status_code === 200) {
      updateCallCountChart(countRes.data.data)
      // 累计调用次数（使用显式遍历避免 unknown 类型问题）
      const dk: 'agent' | 'model' = (filters.value.agent ? 'agent' : 'model')
      let calls = 0
      const dayList = Object.values(countRes.data.data || {}) as Array<any>
      for (const day of dayList) {
        const map = (day?.[dk] || {}) as Record<string, number>
        for (const v of Object.values(map)) calls += Number(v || 0)
      }
      totalCalls.value = calls
    }
    
    // 获取Token使用量数据
    const statsRes = await getUsageStatsAPI(params)
    if (statsRes.data.status_code === 200) {
      updateTokenUsageChart(statsRes.data.data)
      // 累计Token（使用显式遍历避免 unknown 类型问题）
      const dk: 'agent' | 'model' = (filters.value.agent ? 'agent' : 'model')
      let tokens = 0
      const dayList = Object.values(statsRes.data.data || {}) as Array<any>
      for (const day of dayList) {
        const map = (day?.[dk] || {}) as Record<string, { total_tokens?: number }>
        for (const obj of Object.values(map)) tokens += Number(obj?.total_tokens || 0)
      }
      totalTokens.value = tokens
    }
    
    HMessage.success('数据刷新成功')
  } catch (error) {
    console.error('获取使用统计数据失败:', error)
    HMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// 筛选条件变化
const handleFilterChange = () => {
  fetchUsageData()
}

// 刷新数据
const handleRefresh = () => {
  fetchUsageData()
}

// 窗口大小变化处理
const handleResize = () => {
  callCountChart?.resize()
  tokenUsageChart?.resize()
}

// 初始化
onMounted(async () => {
  await nextTick()
  
  // 获取筛选列表
  await Promise.all([
    fetchModelsList(),
    fetchAgentsList()
  ])
  
  // 初始化图表
  initCallCountChart()
  initTokenUsageChart()
  
  // 加载数据
  await fetchUsageData()
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

// 清理
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  
  if (callCountChart) {
    callCountChart.dispose()
    callCountChart = null
  }
  
  if (tokenUsageChart) {
    tokenUsageChart.dispose()
    tokenUsageChart = null
  }
})
</script>

<style scoped lang="scss">
@use '../../styles/breakpoints.scss' as *;

.dashboard-container {
  padding: 24px;
  background-color: transparent;
  min-height: calc(100% - 60px);
}

.dashboard-header {
  margin-bottom: 24px;
  .title-wrap {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .badge {
    font-size: var(--harmony-font-size-body-s);
    padding: 2px 8px;
    border-radius: var(--harmony-corner-radius-level18);
    background: var(--harmony-comp-emphasize-tertiary);
    color: var(--harmony-brand);
  }
  .sub {
    margin-top: 6px;
    color: var(--harmony-font-tertiary);
    font-size: var(--harmony-font-size-subtitle-s);
    font-weight: 500;
    letter-spacing: .2px;
    -webkit-font-smoothing: antialiased;
    font-family: var(--harmony-font-family);
  }
  
  h2 {
    font-size: var(--harmony-font-size-title-m);
    font-weight: 600;
    color: var(--harmony-font-primary);
    margin: 0;
  }
}

.filters-container {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  padding: 16px 20px;
  background: var(--harmony-comp-background-primary);
  border-radius: var(--harmony-corner-radius-level7);
  box-shadow: var(--harmony-shadow-xs);
  margin-bottom: 28px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  min-width: 220px;
  
  label {
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-secondary);
    white-space: nowrap;
    padding-left: 4px;
    font-weight: 600;
    letter-spacing: .3px;
    -webkit-font-smoothing: antialiased;
    font-family: var(--harmony-font-family);
  }
}

/* Select 美化 */
.filter-select {
  min-width: 220px;
}

.filter-action {
  align-self: center;
  margin-left: auto;
  padding: 0 20px;
  border-radius: var(--harmony-corner-radius-level8);
  font-weight: 600;
  letter-spacing: .3px;
  box-shadow: var(--harmony-shadow-xs);
}
.filter-action:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--harmony-shadow-sm);
}
.filter-action:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: var(--harmony-shadow-xs);
}

/* 加载中遮罩 */
.loading-overlay {
  position: absolute;
  inset: 0;
  background: var(--harmony-comp-background-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: inherit;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid var(--harmony-comp-background-secondary);
  border-top-color: var(--harmony-brand);
  border-radius: var(--harmony-corner-radius-level18);
  animation: h-spin 0.6s linear infinite;
}


.kpi-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.kpi-card {
  background: var(--harmony-comp-background-primary);
  border-radius: var(--harmony-corner-radius-level8);
  padding: 16px 18px;
  box-shadow: var(--harmony-shadow-xs);
  position: relative;

  .kpi-title {
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-tertiary);
    margin-bottom: 6px;
  }
  .kpi-value {
    font-size: var(--harmony-font-size-title-m);
    font-weight: 700;
    color: var(--harmony-font-primary);
    line-height: 1.2;
  }
  .kpi-desc {
    margin-top: 8px;
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-tertiary);
  }
  .kpi-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }
  .kpi-icon {
    width: 36px;
    height: 36px;
    border-radius: var(--harmony-corner-radius-level18);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: var(--harmony-comp-emphasize-tertiary);
    color: var(--harmony-brand);
    font-weight: 800;
    box-shadow: inset 0 0 0 1px var(--harmony-comp-divider);
  }
}

.kpi-card--primary {
  background: linear-gradient(180deg, var(--harmony-comp-background-primary) 0%, var(--harmony-comp-emphasize-tertiary) 100%);
}
.kpi-card--warning {
  background: linear-gradient(180deg, var(--harmony-comp-background-primary) 0%, var(--harmony-alert-bg) 100%);
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
  gap: 24px;
}

.chart-wrapper {
  background-color: var(--harmony-comp-background-primary);
  border-radius: var(--harmony-corner-radius-level6);
  box-shadow: var(--harmony-shadow-xs);
  padding: 20px;
  min-height: 400px;
  position: relative;
}

.chart-title {
  font-size: var(--harmony-font-size-body-l);
  font-weight: 600;
  color: var(--harmony-font-primary);
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--harmony-comp-divider);
}

.chart-content {
  width: 100%;
  height: 350px;
}

.empty {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--harmony-font-tertiary);
  font-size: var(--harmony-font-size-subtitle-s);
  pointer-events: none;
}

@include desktop-and-below {
  .charts-container {
    grid-template-columns: 1fr;
  }
}

/* ==================== MOBILE: hmos mobile-card ==================== */
.dashboard-mobile {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-section-gap-mobile, 16px);
  padding-top: var(--harmony-padding-level8, 16px);
}

.dm-section {
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

.dm-grid-2col {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--harmony-card-gap-mobile, 12px);
}

.dm-kpi {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-padding-level2, 4px);
  padding: var(--harmony-padding-level8, 16px);
  background: var(--harmony-comp-background-primary);
  border-radius: var(--harmony-corner-radius-level8, 16px);

  &__value {
    font-size: var(--harmony-font-size-title-s, 20px);
    font-weight: 700;
    color: var(--harmony-font-primary);
  }

  &__label {
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-secondary);
  }

  &__desc {
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-tertiary);
  }
}

.dm-filters {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-padding-level6, 12px);
  padding: var(--harmony-padding-level8, 16px);
  background: var(--harmony-comp-background-primary);
  border-radius: var(--harmony-corner-radius-level8, 16px);
}

.dm-filter {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-padding-level2, 4px);

  &__label {
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-secondary);
    font-weight: 600;
    letter-spacing: 0.3px;
  }

  &__select {
    width: 100%;
  }

  &__action {
    margin-top: var(--harmony-padding-level2, 4px);
    width: 100%;
    border-radius: var(--harmony-corner-radius-level8, 16px);
    font-weight: 600;
  }
}

.dm-chart {
  background: var(--harmony-comp-background-primary);
  border-radius: var(--harmony-corner-radius-level8, 16px);
  padding: var(--harmony-padding-level8, 16px);
  min-height: var(--harmony-control-height-72, 180px);
  position: relative;

  &__content {
    width: 100%;
    min-height: 200px;
    height: 50vw;
    max-height: 320px;
  }
}
</style>
