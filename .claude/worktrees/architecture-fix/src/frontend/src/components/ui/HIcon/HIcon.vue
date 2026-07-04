<!-- src/frontend/src/components/ui/HIcon/HIcon.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import { getIconChar } from './icon-map'

interface Props {
  name: string
  size?: number | string
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 16,
})

const iconChar = computed(() => getIconChar(props.name))
const sizeStyle = computed(() => typeof props.size === 'number' ? `${props.size}px` : props.size)
</script>

<template>
  <span
    class="h-icon"
    :style="{ fontSize: sizeStyle, color: color || 'inherit' }"
    :title="name"
  >{{ iconChar }}</span>
</template>

<style scoped>
.h-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: 'HarmonyOS Sans Symbols', sans-serif;
  font-style: normal;
  line-height: 1;
  vertical-align: middle;
}
</style>
