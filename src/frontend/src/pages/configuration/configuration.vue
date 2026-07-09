<template>
  <!-- Desktop: full Monaco editor -->
  <div v-if="!isMobile" class="editor page">
    <div ref="editorContainer" class="editor-container"></div>
    <div class="button">
      <HButton type="secondary" @click="cancel">取消</HButton>
      <HButton type="primary" @click="primary">确定</HButton>
    </div>
  </div>

  <!-- Mobile: hmos mobile-list layout -->
  <div v-else class="mobile-config">
    <div class="mobile-config-header">
      <span class="mobile-config-title">配置编辑</span>
    </div>
    <div class="mobile-config-editor">
      <textarea
        v-model="mobileValue"
        class="mobile-config-textarea"
        spellcheck="false"
        placeholder="请输入配置内容（JSON格式）"
      ></textarea>
    </div>
    <div class="mobile-config-actions">
      <HButton type="secondary" size="small" @click="mobileCancel">取消</HButton>
      <HButton type="primary" size="small" @click="mobilePrimary">确定</HButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import * as monaco from "monaco-editor"
import { ref, onMounted, inject } from "vue"
import { HButton } from '@/components/ui'
import { getConfigAPI, updateConfigAPI } from "../../apis/configuration"

const isMobile = inject<import('vue').Ref<boolean>>('isMobile', ref(false))
const mobileValue = ref("")

const editorContainer = ref<HTMLElement | null>(null)
let editorInstance: monaco.editor.IStandaloneCodeEditor | null = null
const editorValue = ref("")
onMounted(async () => {
  const data = await getConfigAPI()
  editorValue.value = data.data.data
  mobileValue.value = editorValue.value
  if (!isMobile.value && editorContainer.value) {
    editorInstance = monaco.editor.create(editorContainer.value, {
      value: editorValue.value,
      language: "python",
    })
  }
})

const primary = async () => {
  const value = editorInstance?.getValue()
  const formData = new FormData()
  formData.append("data", String(value))
  const data = await updateConfigAPI(formData)
  if (data.data.data !== "更改配置成功") {
    alert("请检查您输入的信息或者格式是否正确，必须为json格式")
    const data = await getConfigAPI()
    editorInstance?.setValue(data.data.data)
  }else{
    alert("更改配置成功")
  }
}
const cancel = ()=>{
  editorInstance?.setValue(editorValue.value)
}

const mobilePrimary = async () => {
  const formData = new FormData()
  formData.append("data", mobileValue.value)
  const data = await updateConfigAPI(formData)
  if (data.data.data !== "更改配置成功") {
    alert("请检查您输入的信息或者格式是否正确，必须为json格式")
    const fresh = await getConfigAPI()
    mobileValue.value = fresh.data.data
  } else {
    editorValue.value = mobileValue.value
    alert("更改配置成功")
  }
}

const mobileCancel = () => {
  mobileValue.value = editorValue.value
}
</script>

<style lang="scss" scoped>
.editor {
  height: calc(100vh - 62px);
  .editor-container {
    margin: 20px;
    width: 100%;
    height: 80%;
  }
  .button {
    display: flex;
    margin-top: 30px;
    justify-content: center;
    .h-button {
      padding: 20px 40px;
    }
  }
}

/* hmos mobile-list pattern */
.mobile-config {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  gap: var(--harmony-spacing-m);
}

.mobile-config-header {
  padding: var(--harmony-spacing-m) 0 var(--harmony-spacing-xs);
}

.mobile-config-title {
  font-size: var(--harmony-font-size-title-s);
  font-weight: var(--harmony-font-weight-bold);
  color: var(--harmony-color-text-primary);
}

.mobile-config-editor {
  flex: 1;
  min-height: 0;
}

.mobile-config-textarea {
  width: 100%;
  height: 100%;
  min-height: 300px;
  border: 1px solid var(--harmony-color-border-secondary);
  border-radius: var(--harmony-radius-m);
  padding: var(--harmony-spacing-m);
  font-family: var(--harmony-font-family-mono, "Courier New", monospace);
  font-size: var(--harmony-font-size-body-s);
  color: var(--harmony-color-text-primary);
  background: var(--harmony-color-bg-surface);
  resize: vertical;
  outline: none;
  box-sizing: border-box;

  &:focus {
    border-color: var(--harmony-color-brand);
  }

  &::placeholder {
    color: var(--harmony-color-text-placeholder);
  }
}

.mobile-config-actions {
  display: flex;
  gap: var(--harmony-spacing-m);
  justify-content: center;
  padding: var(--harmony-spacing-m) 0;
}
</style>
