<script setup lang="ts">
import { ref } from 'vue'

interface HUploadFile { name: string; url?: string; size?: number; status?: 'ready' | 'uploading' | 'success' | 'error' }

interface Props {
  action?: string; accept?: string; multiple?: boolean; drag?: boolean; fileList?: HUploadFile[]
}
const props = withDefaults(defineProps<Props>(), { multiple: false, drag: false, fileList: () => [] })
const emit = defineEmits<{ 'update:fileList': [files: HUploadFile[]]; 'change': [files: HUploadFile[]] }>()
const inputRef = ref<HTMLInputElement | null>(null)

function triggerSelect() { inputRef.value?.click() }
function onChange(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files) return
  const newFiles: HUploadFile[] = Array.from(input.files).map(f => ({ name: f.name, size: f.size, status: 'ready' as const }))
  const merged = [...props.fileList, ...newFiles]
  emit('update:fileList', merged); emit('change', merged); input.value = ''
}
function remove(index: number) {
  const files = [...props.fileList]; files.splice(index, 1)
  emit('update:fileList', files); emit('change', files)
}
function onDrop(event: DragEvent) {
  event.preventDefault()
  if (!event.dataTransfer?.files) return
  const newFiles: HUploadFile[] = Array.from(event.dataTransfer.files).map(f => ({ name: f.name, size: f.size, status: 'ready' as const }))
  const merged = [...props.fileList, ...newFiles]
  emit('update:fileList', merged); emit('change', merged)
}
</script>

<template>
  <div class="h-upload">
    <div v-if="drag" class="h-upload__dropzone" @dragover.prevent @drop="onDrop" @click="triggerSelect">
      <slot name="tip"><span class="h-upload__tip">将文件拖拽到此处，或 <em>点击上传</em></span></slot>
    </div>
    <div v-else class="h-upload__trigger" @click="triggerSelect"><slot /></div>
    <input ref="inputRef" type="file" :accept="accept" :multiple="multiple" hidden @change="onChange" />
    <div v-if="fileList.length" class="h-upload__list">
      <div v-for="(file, i) in fileList" :key="i" class="h-upload__file">
        <span class="h-upload__filename">{{ file.name }}</span>
        <span class="h-upload__remove" @click="remove(i)">✕</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.h-upload__dropzone { border: 2px dashed var(--color-border); border-radius: var(--radius-md); padding: 32px; text-align: center; cursor: pointer; transition: border-color var(--duration-fast) var(--easing); color: var(--color-text-tertiary); }
.h-upload__dropzone:hover { border-color: var(--color-primary); }
.h-upload__tip em { color: var(--color-primary); font-style: normal; cursor: pointer; }
.h-upload__list { margin-top: 8px; }
.h-upload__file { display: flex; justify-content: space-between; align-items: center; padding: 6px 10px; background: var(--color-bg-tertiary); border-radius: var(--radius-sm); margin-top: 4px; font-size: var(--font-size-sm); color: var(--color-text-primary); }
.h-upload__remove { cursor: pointer; color: var(--color-text-tertiary); }
.h-upload__remove:hover { color: var(--color-danger); }
</style>
