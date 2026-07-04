import type { Directive } from 'vue'

export const vHLoading: Directive = {
  mounted(el, binding) {
    if (!binding.value) return
    createOverlay(el)
  },
  updated(el, binding) {
    if (binding.value && !el.querySelector('.h-loading-overlay')) {
      createOverlay(el)
    } else if (!binding.value) {
      removeOverlay(el)
    }
  },
  unmounted(el) {
    removeOverlay(el)
  },
}

function createOverlay(el: HTMLElement) {
  el.style.position = 'relative'
  const overlay = document.createElement('div')
  overlay.className = 'h-loading-overlay'
  overlay.innerHTML = '<div class="h-loading-spinner"></div>'
  el.appendChild(overlay)
}

function removeOverlay(el: HTMLElement) {
  const overlay = el.querySelector('.h-loading-overlay')
  if (overlay) overlay.remove()
}
