import { ref, onMounted, onUnmounted } from 'vue'

const BP_TABLET = 768
const BP_DESKTOP = 1200
const BP_WIDE = 1400

function createMediaQuery(query: string) {
  if (typeof window === 'undefined') return { matches: ref(false), cleanup: () => {} }
  const mq = window.matchMedia(query)
  const matches = ref(mq.matches)
  const handler = (e: MediaQueryListEvent) => { matches.value = e.matches }
  mq.addEventListener('change', handler)
  const cleanup = () => mq.removeEventListener('change', handler)
  return { matches, cleanup }
}

export function useBreakpoint() {
  const mobile = createMediaQuery(`(max-width: ${BP_TABLET - 1}px)`)
  const tablet = createMediaQuery(`(min-width: ${BP_TABLET}px) and (max-width: ${BP_DESKTOP - 1}px)`)
  const desktop = createMediaQuery(`(min-width: ${BP_DESKTOP}px)`)
  const wide = createMediaQuery(`(min-width: ${BP_WIDE}px)`)
  const tabletAndBelow = createMediaQuery(`(max-width: ${BP_DESKTOP - 1}px)`)

  const cleanups = [mobile, tablet, desktop, wide, tabletAndBelow]

  onUnmounted(() => {
    cleanups.forEach(c => c.cleanup())
  })

  return {
    isMobile: mobile.matches,
    isTablet: tablet.matches,
    isDesktop: desktop.matches,
    isWide: wide.matches,
    isTabletAndBelow: tabletAndBelow.matches,
  }
}
