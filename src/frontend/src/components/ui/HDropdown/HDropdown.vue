<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
interface Props { trigger?: 'click' | 'hover' }
withDefaults(defineProps<Props>(), { trigger: 'click' })
const visible = ref(false)
const toggle = () => { visible.value = !visible.value }
const close = () => { visible.value = false }
const wrapperRef = ref<HTMLElement | null>(null)
function onClickOutside(e: MouseEvent) {
  if (wrapperRef.value && !wrapperRef.value.contains(e.target as Node)) close()
}
onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>

<template>
  <div class="h-dropdown" ref="wrapperRef" @click="trigger === 'click' && toggle()">
    <slot />
    <Transition name="h-dropdown">
      <div v-if="visible" class="h-dropdown__menu" @click="close">
        <slot name="dropdown" />
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.h-dropdown { position: relative; display: inline-flex; }
.h-dropdown__menu {
  position: absolute; top: 100%; right: 0; margin-top: 4px; min-width: 140px;
  background: var(--color-bg-secondary);
  backdrop-filter: blur(20px) saturate(1.2);
  border: 1px solid var(--color-border);
  border-radius: var(--harmony-corner-radius-level8);
  box-shadow: var(--shadow-lg);
  z-index: var(--z-dropdown); overflow: hidden;
}
</style>
