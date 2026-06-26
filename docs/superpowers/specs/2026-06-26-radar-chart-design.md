# 雷达图可视化设计规范

**日期**: 2026-06-26
**状态**: 已批准
**范围**: 在面试报告页面添加分类评分雷达图

---

## 1. 背景与目标

面试报告页面当前使用水平进度条显示各分类评分，缺乏直观的多维度对比视图。

**目标**：在报告页面添加 echarts 雷达图，直观展示各分类评分的分布情况。

**范围**：纯前端功能，使用已安装的 echarts 库，无需后端改动。

---

## 2. 改动范围

### 改动文件

| 文件 | 变更 |
|------|------|
| `src/frontend/src/pages/interview/reportPage/reportPage.vue` | 添加 echarts 雷达图 |

### 不变的部分

- 后端：无变更
- API：无变更
- 数据结构：复用现有 `category_scores`

---

## 3. 设计方案

### 3.1 数据源

`EvaluationReport.category_scores: Record<string, number>`

示例：
```json
{
  "基础知识": 85,
  "算法能力": 72,
  "系统设计": 90,
  "沟通表达": 88
}
```

### 3.2 echarts 配置

```typescript
import * as echarts from 'echarts'

const radarOption = {
  radar: {
    indicator: [
      { name: '基础知识', max: 100 },
      { name: '算法能力', max: 100 },
      { name: '系统设计', max: 100 },
      { name: '沟通表达', max: 100 }
    ],
    shape: 'polygon'
  },
  series: [{
    type: 'radar',
    data: [{
      value: [85, 72, 90, 88],
      areaStyle: { opacity: 0.2 }
    }]
  }]
}
```

### 3.3 UI 位置

在现有分类评分进度条区域下方，添加 `div#radar-chart` 容器，高度 300px。

### 3.4 响应式

使用 `window.addEventListener('resize')` 监听窗口变化，调用 `chart.resize()`。

---

## 4. 已知限制

- 雷达图依赖 `category_scores` 数据，如果评估结果没有分类评分则不显示
- echarts 体积较大（~800KB），但已在依赖中
