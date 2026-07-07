import { computed, watch, type Ref } from 'vue'

/**
 * ECharts 鸿蒙主题 composable
 * 从 HarmonyOS token 提取颜色，支持 light/dark 自动切换
 */
export function useEChartsTheme(chartRef: Ref<any>) {
  const isDark = computed(() => {
    return document.documentElement.getAttribute('data-theme') === 'dark'
  })

  const theme = computed(() => {
    const dark = isDark.value
    return {
      color: [
        '#0a59f7', '#f56c6c', '#67c23a', '#e6a23c',
        '#9b59b6', '#1abc9c', '#3498db', '#e74c3c',
      ],
      backgroundColor: 'transparent',
      textStyle: {
        color: dark ? 'rgba(255,255,255,0.87)' : 'rgba(0,0,0,0.87)',
        fontFamily: "'HarmonyOS Sans', sans-serif",
      },
      title: {
        textStyle: {
          color: dark ? 'rgba(255,255,255,0.87)' : 'rgba(0,0,0,0.87)',
        },
      },
      legend: {
        textStyle: {
          color: dark ? 'rgba(255,255,255,0.6)' : 'rgba(0,0,0,0.6)',
        },
      },
      tooltip: {
        backgroundColor: dark ? 'rgba(30,30,30,0.9)' : 'rgba(255,255,255,0.9)',
        borderColor: dark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
        textStyle: {
          color: dark ? 'rgba(255,255,255,0.87)' : 'rgba(0,0,0,0.87)',
        },
      },
      xAxis: {
        axisLine: { lineStyle: { color: dark ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)' } },
        splitLine: { lineStyle: { color: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' } },
      },
      yAxis: {
        axisLine: { lineStyle: { color: dark ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)' } },
        splitLine: { lineStyle: { color: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' } },
      },
    }
  })

  // 主题切换时自动更新图表
  watch(isDark, () => {
    const chart = chartRef.value
    if (chart) {
      chart.dispose()
      // 调用方需要重新 init
    }
  })

  return { theme, isDark }
}
