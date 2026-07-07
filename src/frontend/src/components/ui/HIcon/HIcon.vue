<!-- src/frontend/src/components/ui/HIcon/HIcon.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import { getIconChar } from './icon-map'

interface Props {
  /** HMSymbol Unicode 字符或 icon-map 名称 */
  name?: string
  /** SVG 图标名称（降级模式，从 assets/ 加载） */
  svg?: string
  size?: number | string
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 16,
})

const iconChar = computed(() => props.name ? getIconChar(props.name) : '')
const sizeStyle = computed(() => typeof props.size === 'number' ? `${props.size}px` : props.size)
const svgUrl = computed(() => props.svg ? new URL(`../../../assets/${props.svg}.svg`, import.meta.url).href : '')
</script>

<template>
  <!-- HMSymbol 模式 -->
  <span
    v-if="name"
    class="h-icon h-icon--symbol"
    :style="{ fontSize: sizeStyle, color: color || 'inherit' }"
    :title="name"
  >{{ iconChar }}</span>
  <!-- SVG 降级模式 -->
  <img
    v-else-if="svg"
    class="h-icon h-icon--svg"
    :src="svgUrl"
    :alt="svg"
    :style="{ width: sizeStyle, height: sizeStyle }"
  />
</template>

<style scoped>
.h-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  vertical-align: middle;
  flex-shrink: 0;
}

.h-icon--symbol {
  font-family: 'HMSymbol', 'HarmonyOS Sans Symbols', sans-serif;
  font-style: normal;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.h-icon--svg {
  object-fit: contain;
}
</style>
