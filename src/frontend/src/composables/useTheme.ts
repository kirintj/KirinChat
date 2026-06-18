import { ref, computed, watch, onMounted } from 'vue'
import { useLocalStorage } from '@vueuse/core'

type ThemeMode = 'light' | 'dark' | 'system'

export function useTheme() {
  const mode = useLocalStorage<ThemeMode>('agentchat-theme', 'system')
  const systemPrefersDark = ref(false)

  const resolved = computed<'light' | 'dark'>(() => {
    if (mode.value === 'system') {
      return systemPrefersDark.value ? 'dark' : 'light'
    }
    return mode.value
  })

  watch(resolved, (theme) => {
    document.documentElement.setAttribute('data-theme', theme)
  }, { immediate: true })

  onMounted(() => {
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    systemPrefersDark.value = mq.matches
    mq.addEventListener('change', (e) => {
      systemPrefersDark.value = e.matches
    })
  })

  function toggle() {
    mode.value = resolved.value === 'dark' ? 'light' : 'dark'
  }

  return { mode, resolved, toggle }
}
