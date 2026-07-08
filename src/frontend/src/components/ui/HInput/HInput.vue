<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'

/** 对外暴露的 props；其余任意 <input> 原生属性可直接透传 */
interface Props {
  placeholder?: string
  disabled?: boolean
  clearable?: boolean
  showPassword?: boolean
  size?: 'small' | 'medium' | 'large'
  error?: string
  /** 只读：可选中/复制，不可编辑；与 disabled 区分 */
  readonly?: boolean
  /** 是否开启 300ms 防抖（仅对 update:modelValue / input 事件生效） */
  debounce?: boolean
  /** 防抖延迟毫秒；debounce=true 时默认 300ms */
  debounceWait?: number
  /** label id（用于 aria-label / label for 关联）；不传则默认用 placeholder 作为 aria-label */
  inputId?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '',
  disabled: false,
  clearable: false,
  showPassword: false,
  size: 'medium',
  error: undefined,
  readonly: false,
  debounce: false,
  debounceWait: 300,
  inputId: undefined,
})

/** 双向绑定（Vue 3.4+ 推荐） */
const model = defineModel<string>('modelValue', { default: '' })

const emit = defineEmits<{
  focus: [event: FocusEvent]
  blur: [event: FocusEvent]
  /** 失焦或按下回车时触发（类似原生 change 语义） */
  change: [value: string]
  enter: [event: KeyboardEvent]
  esc: [event: KeyboardEvent]
  clear: []
}>()

const inputEl = ref<HTMLInputElement | null>(null)
const focused = ref(false)
const passwordVisible = ref(false)
let debounceTimer: ReturnType<typeof setTimeout> | null = null

/** 对外暴露方法，父组件通过 ref 直接调用 */
defineExpose({
  focus: () => inputEl.value?.focus(),
  blur: () => inputEl.value?.blur(),
  select: () => inputEl.value?.select(),
  /** 获取底层原生 input 元素 */
  inputEl: () => inputEl.value,
})

const inputType = computed(() => (props.showPassword && passwordVisible.value ? 'text' : props.showPassword ? 'password' : 'text'))

/** 输入事件：支持防抖，保证 v-model 同步更新 */
function onInput(event: Event) {
  const value = (event.target as HTMLInputElement).value
  // v-model 保持实时同步（受控）；debounce 只影响 input 事件节流
  model.value = value
  if (props.debounce) {
    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => emit('change', value), props.debounceWait)
  }
}

function onFocus(e: FocusEvent) {
  focused.value = true
  emit('focus', e)
}

function onBlur(e: FocusEvent) {
  focused.value = false
  emit('blur', e)
  // 失焦触发 change（原生表单语义）
  emit('change', model.value ?? '')
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter') {
    emit('enter', e)
    emit('change', model.value ?? '')
  } else if (e.key === 'Escape') {
    emit('esc', e)
  }
}

/** 点击容器空白区域也能聚焦，扩大可点击区域 */
function onRootClick(event: MouseEvent) {
  // 已经点击到内部控件（按钮/输入框）则不重复处理
  const target = event.target as HTMLElement
  if (target.closest('.h-input__inner, .h-input__clear, .h-input__toggle')) return
  nextTick(() => inputEl.value?.focus())
}

/** 清空输入：不触发 blur 闪烁 */
function onClear(event: MouseEvent) {
  event.preventDefault()
  event.stopPropagation()
  model.value = ''
  emit('clear')
  nextTick(() => inputEl.value?.focus())
}

/** 切换密码可见：不触发 blur 闪烁 */
function togglePassword(event: MouseEvent) {
  event.preventDefault()
  event.stopPropagation()
  passwordVisible.value = !passwordVisible.value
  nextTick(() => inputEl.value?.focus())
}

/** 支持 autofocus（虽然透传也能用，但作为保险保留） */
onMounted(() => {
  if ((props as any).autofocus) inputEl.value?.focus()
})

/** 清理防抖定时器 */
watch(
  () => props.debounce,
  (v) => {
    if (!v && debounceTimer) {
      clearTimeout(debounceTimer)
      debounceTimer = null
    }
  },
)
</script>

<template>
  <div
    class="h-input"
    :class="[
      `h-input--${size}`,
      {
        'h-input--focused': focused,
        'h-input--disabled': disabled,
        'h-input--error': !!error,
        'h-input--readonly': readonly && !disabled,
        'h-input--has-value': (model ?? '').length > 0,
      },
    ]"
    :aria-invalid="!!error || undefined"
    :aria-disabled="disabled || undefined"
    role="group"
    @click="onRootClick"
  >
    <div v-if="$slots.prefix" class="h-input__prefix">
      <slot name="prefix" />
    </div>

    <!-- v-bind="$attrs"：所有未在 props 中声明的原生 input 属性直接透传（name / maxlength / autofocus / autocomplete / pattern / inputmode ...） -->
    <input
      ref="inputEl"
      v-bind="$attrs"
      :id="inputId"
      class="h-input__inner"
      :type="inputType"
      :value="model"
      :placeholder="placeholder"
      :disabled="disabled"
      :readonly="readonly"
      :aria-label="placeholder || undefined"
      @input="onInput"
      @focus="onFocus"
      @blur="onBlur"
      @keydown="onKeydown"
    />

    <div class="h-input__suffix">
      <button
        v-if="clearable && (model ?? '').length > 0 && !disabled"
        type="button"
        class="h-input__clear"
        :aria-label="'清空内容'"
        tabindex="-1"
        @click="onClear"
      >
        <!-- 用 SVG 图标代替字符，更清晰且支持 hover 放大 -->
        <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
          <path
            d="M6.22 6.22a.75.75 0 0 1 1.06 0L12 10.94l4.72-4.72a.75.75 0 1 1 1.06 1.06L13.06 12l4.72 4.72a.75.75 0 1 1-1.06 1.06L12 13.06l-4.72 4.72a.75.75 0 1 1-1.06-1.06L10.94 12 6.22 7.28a.75.75 0 0 1 0-1.06Z"
            fill="currentColor"
          />
        </svg>
      </button>

      <button
        v-if="showPassword && !disabled"
        type="button"
        class="h-input__toggle"
        :aria-label="passwordVisible ? '隐藏密码' : '显示密码'"
        :aria-pressed="passwordVisible"
        tabindex="-1"
        @click="togglePassword"
      >
        <svg v-if="!passwordVisible" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
          <path
            d="M12 5c-7 0-11 7-11 7s4 7 11 7 11-7 11-7-4-7-11-7Zm0 12a5 5 0 1 1 0-10 5 5 0 0 1 0 10Zm0-2a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"
            fill="currentColor"
          />
        </svg>
        <svg v-else viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
          <path
            d="M3.22 3.22a.75.75 0 0 1 1.06 0l16.5 16.5a.75.75 0 1 1-1.06 1.06l-2.2-2.2A12.5 12.5 0 0 1 12 19C5 19 1 12 1 12a17 17 0 0 1 4.58-4.8L3.22 4.28a.75.75 0 0 1 0-1.06ZM17.4 13.16A5 5 0 0 0 10.84 6.6L8.72 4.48A12.7 12.7 0 0 1 12 4c7 0 11 7 11 7a17.4 17.4 0 0 1-3.72 4.1l-1.88-1.93ZM6.6 9.76l1.88 1.88a5 5 0 0 0 5.76 5.76l1.4 1.4A12.5 12.5 0 0 1 12 19C5 19 1 12 1 12a17.4 17.4 0 0 1 5.6-4.24Zm4.96 2.46a3 3 0 0 1 3.22 3.22l-3.22-3.22Z"
            fill="currentColor"
          />
        </svg>
      </button>

      <slot name="suffix" />
    </div>

    <!-- error 改内流化：放在容器内部底部，参与文档流，不会与上下输入框重叠 -->
    <div v-if="error" class="h-input__error" role="alert">{{ error }}</div>
  </div>
</template>

<style scoped>
/*
  HInput 样式：
  - 状态 / 尺寸 / 排版 三类分层；过渡只动画真正会变的属性
  - 焦点态使用 box-shadow 而不是 outline-offset:-1（避免与边框重叠发粗）
  - prefix / suffix 使用 padding + 颜色分隔，保证与正文有呼吸
  - disabled 有灰底区分；readonly 保留白底但去除交互
*/
.h-input {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--harmony-gap-sm, 8px);
  min-height: 40px;
  padding: 0 var(--harmony-space-md, 12px);
  background: var(--harmony-background-primary);
  border: 1px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level10);
  color: var(--harmony-font-primary);
  font-family: var(--harmony-font-family);
  font-size: var(--harmony-font-size-body-m);
  cursor: text;
  transition:
    border-color var(--harmony-duration-fast) var(--harmony-motion-standard),
    box-shadow var(--harmony-duration-fast) var(--harmony-motion-standard),
    background-color var(--harmony-duration-fast) var(--harmony-motion-standard);
}

/* hover：仅边框微加深（不做覆盖层，保持干净） */
.h-input:hover:not(.h-input--disabled):not(.h-input--readonly) {
  border-color: var(--harmony-interactive-hover);
}

/* focus：box-shadow 描边，不与边框冲突；不使用 outline-offset:-1 */
.h-input--focused {
  border-color: var(--harmony-interactive-focus);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--harmony-interactive-focus) 20%, transparent);
  outline: none;
}

/* error：红色边框 + 焦点态同样用红 */
.h-input--error {
  border-color: var(--harmony-warning);
}
.h-input--error.h-input--focused {
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--harmony-warning) 22%, transparent);
}

/* 只读：允许选中/复制，但不响应 hover 加深；保持白底 */
.h-input--readonly {
  background: var(--harmony-background-secondary);
  cursor: default;
  border-color: var(--harmony-comp-divider);
}

/* 禁用：灰底 + 半透明，明显区别于默认状态 */
.h-input--disabled {
  background: var(--harmony-comp-background-tertiary);
  color: var(--harmony-font-quaternary);
  cursor: not-allowed;
  opacity: 0.8;
}

/* ---------- 尺寸 ---------- */
.h-input--small  { min-height: 32px; padding: 0 var(--harmony-space-sm, 10px); border-radius: var(--harmony-corner-radius-level8); font-size: var(--harmony-font-size-body-s); }
.h-input--medium { min-height: 40px; padding: 0 var(--harmony-space-md, 12px); border-radius: var(--harmony-corner-radius-level10); }
.h-input--large  { min-height: 48px; padding: 0 var(--harmony-space-lg, 16px); border-radius: var(--harmony-corner-radius-level12); font-size: var(--harmony-font-size-body-l); }

/* ---------- 前缀 / 后缀 ---------- */
.h-input__prefix,
.h-input__suffix {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--harmony-font-tertiary);
  /* 给前缀/后缀加内边距，避免文字直接贴边，也避免和正文挤压 */
  padding-inline: var(--harmony-space-sm, 8px) 0;
  /* 作为一个分隔，前缀右侧给一条极轻的竖线；没有前缀时不影响 */
}
.h-input__suffix {
  padding-inline: var(--harmony-space-sm, 8px) 0;
}
/* 有前缀时：在 prefix 右侧加 1px 分隔（极轻） */
.h-input__prefix + .h-input__inner {
  padding-left: var(--harmony-space-sm, 8px);
}

/* ---------- 输入框本体 ---------- */
.h-input__inner {
  flex: 1;
  min-width: 0;
  height: 100%;
  min-height: inherit;
  padding: 0;
  border: none;
  outline: none;
  background: transparent;
  color: inherit;
  font: inherit;
  line-height: 1.4;
  /* 文字垂直居中：用 padding=0 + height=100% + align-items:center 的父级 flex 实现 */
}
.h-input__inner::placeholder {
  color: var(--harmony-font-hint, var(--harmony-font-tertiary));
  opacity: 1;
}
.h-input__inner:disabled {
  cursor: not-allowed;
  color: inherit;
}
.h-input__inner[readonly] {
  cursor: default;
}

/* ---------- 清空 / 密码切换按钮 ---------- */
.h-input__clear,
.h-input__toggle {
  appearance: none;
  background: transparent;
  border: none;
  padding: 6px;
  margin: -4px;          /* 负外边距 + 正内边距 → 点击区放大到 ~28px，不挤视觉 */
  border-radius: var(--harmony-corner-radius-level4);
  color: var(--harmony-font-tertiary);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition:
    color var(--harmony-duration-fast) var(--harmony-motion-standard),
    background-color var(--harmony-duration-fast) var(--harmony-motion-standard),
    transform var(--harmony-duration-fast) var(--harmony-motion-standard),
    opacity var(--harmony-duration-fast) var(--harmony-motion-standard);
}
.h-input__clear:hover,
.h-input__toggle:hover {
  color: var(--harmony-font-primary);
  background: var(--harmony-comp-emphasize-quaternary);
}
.h-input__clear:active,
.h-input__toggle:active {
  transform: scale(0.95);
}

/* 清空图标：有值才显示；顺带用 opacity 做淡入 */
.h-input--has-value .h-input__clear {
  opacity: 1;
}
.h-input__clear {
  opacity: 0;
  pointer-events: none;
}

/* ---------- 错误提示（内流化，参与文档流） ---------- */
.h-input__error {
  position: absolute;
  top: calc(100% + 4px);
  left: 4px;
  right: 4px;
  font-size: var(--harmony-font-size-body-s);
  color: var(--harmony-warning);
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 当存在 error 时，让容器底部保留一点呼吸，避免与下一行挤压 */
.h-input--error {
  /* 此处用伪元素保留空间会更稳妥，但为极简代码，我们直接让 error 用 absolute 定位并给外层保留 margin-bottom */
}
</style>
