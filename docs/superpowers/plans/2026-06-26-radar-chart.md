# 雷达图可视化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在面试报告页面添加 echarts 雷达图，直观展示各分类评分分布

**Architecture:** 在 reportPage.vue 中引入 echarts，将 `category_scores` 数据转换为雷达图配置，在分类评分进度条下方渲染图表

**Tech Stack:** Vue 3 Composition API, echarts v6

---

### Task 1: 在 reportPage.vue 中添加雷达图

**Files:**
- Modify: `src/frontend/src/pages/interview/reportPage/reportPage.vue`

- [ ] **Step 1: 添加 echarts 导入**

找到 import 语句（第 2-3 行）：
```typescript
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
```

替换为：
```typescript
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
```

- [ ] **Step 2: 添加雷达图 ref 和初始化函数**

找到 `categoryEntries` computed（第 31-34 行）之后，`fetchReport` 函数之前：
```typescript
const categoryEntries = computed(() => {
  if (!report.value?.category_scores) return []
  return Object.entries(report.value.category_scores)
})
```

在其下方插入：
```typescript
// --- 雷达图 ---
const radarChartRef = ref<HTMLElement | null>(null)
let radarChart: echarts.ECharts | null = null

// 初始化雷达图
const initRadarChart = () => {
  if (!radarChartRef.value || !report.value?.category_scores) return
  const scores = report.value.category_scores
  const indicator = Object.keys(scores).map(name => ({ name, max: 100 }))
  const values = Object.values(scores)

  radarChart = echarts.init(radarChartRef.value)
  radarChart.setOption({
    radar: {
      indicator,
      shape: 'polygon',
      splitNumber: 5,
      axisName: {
        color: 'var(--color-text-secondary)',
        fontSize: 12,
      },
      splitLine: { lineStyle: { color: 'var(--color-border)' } },
      splitArea: { show: false },
    },
    series: [{
      type: 'radar',
      data: [{
        value: values,
        areaStyle: { opacity: 0.15 },
        lineStyle: { width: 2 },
      }],
    }],
  })
}

// 窗口 resize 时重绘图表
const handleResize = () => { radarChart?.resize() }
```

- [ ] **Step 3: 在 fetchReport 成功后初始化雷达图**

找到 `fetchReport` 函数中设置 `report.value` 的地方（第 45-46 行和第 52-53 行），在每个成功赋值后添加 `nextTick(initRadarChart)`：

第一个赋值点：
```typescript
        report.value = res.data.data
```
替换为：
```typescript
        report.value = res.data.data
        nextTick(initRadarChart)
```

第二个赋值点：
```typescript
        report.value = res.data.data
```
替换为：
```typescript
        report.value = res.data.data
        nextTick(initRadarChart)
```

- [ ] **Step 4: 添加 onMounted/onUnmounted 生命周期**

找到 `onMounted` 块（第 79-81 行）：
```typescript
onMounted(() => {
  fetchReport()
})
```

替换为：
```typescript
onMounted(() => {
  fetchReport()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  radarChart?.dispose()
})
```

- [ ] **Step 5: 在模板中添加雷达图容器**

找到分类评分区域结束的 `</div>`（第 135 行），在其后插入：
```html
      <!-- 雷达图 -->
      <div v-if="categoryEntries.length > 0" class="section">
        <h3 class="section-title">能力雷达图</h3>
        <div ref="radarChartRef" class="radar-chart"></div>
      </div>
```

- [ ] **Step 6: 添加雷达图样式**

在 `<style>` 的 `.category-fill` 样式之后插入：
```scss
// 雷达图
.radar-chart {
  width: 100%;
  height: 300px;
}
```

- [ ] **Step 7: 验证构建**

Run: `cd src/frontend && npm run build 2>&1 | tail -5`
Expected: 构建成功

- [ ] **Step 8: Commit**

```bash
git add src/frontend/src/pages/interview/reportPage/reportPage.vue
git commit -m "feat(interview): add echarts radar chart to report page"
```
