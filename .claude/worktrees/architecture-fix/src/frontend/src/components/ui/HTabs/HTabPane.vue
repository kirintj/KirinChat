<script setup lang="ts">
import { inject, computed, onMounted } from 'vue'
interface Props { name: string; label: string }
const props = defineProps<Props>()
const tabs = inject<any>('h-tabs')
const isActive = computed(() => tabs?.active.value === props.name)
onMounted(() => tabs?.register(props.name, props.label))
</script>

<template>
  <div v-show="isActive" class="h-tab-pane"><slot /></div>
</template>
