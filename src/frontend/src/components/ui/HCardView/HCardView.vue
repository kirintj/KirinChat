<script setup lang="ts">
interface Props {
  size?: 'max' | 'larger' | 'medium' | 'small' | 'mini'
  clickable?: boolean
}

withDefaults(defineProps<Props>(), {
  size: 'medium',
  clickable: false,
})

const emit = defineEmits<{ click: [event: MouseEvent] }>()
</script>

<template>
  <div
    class="h-card"
    :class="[
      `h-card--${size}`,
      { 'h-card--clickable': clickable },
    ]"
    @click="clickable && emit('click', $event)"
  >
    <div v-if="$slots.cover" class="h-card__cover">
      <slot name="cover" />
    </div>
    <div class="h-card__body">
      <div v-if="$slots.header" class="h-card__header">
        <slot name="header" />
      </div>
      <div class="h-card__content">
        <slot />
      </div>
      <div v-if="$slots.footer" class="h-card__footer">
        <slot name="footer" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.h-card {
  background: var(--harmony-comp-background-secondary);
  border-radius: var(--harmony-corner-radius-level8);
  overflow: hidden;
  box-shadow: var(--harmony-shadow-card);
  transition: box-shadow var(--harmony-duration-fast) var(--harmony-motion-standard),
              transform var(--harmony-duration-fast) var(--harmony-motion-standard);
}

.h-card--clickable {
  cursor: pointer;
}

.h-card--clickable:hover {
  box-shadow: var(--harmony-shadow-card-hover);
  transform: translateY(-1px);
}

.h-card--clickable:active {
  transform: translateY(0);
}

/* 尺寸变体 */
.h-card--max {
  width: 100%;
}

.h-card--larger {
  width: 100%;
  max-width: 480px;
}

.h-card--medium {
  width: 100%;
  max-width: 328px;
}

.h-card--small {
  width: 100%;
  max-width: 160px;
}

.h-card--mini {
  width: 100%;
  max-width: 100px;
}

.h-card__cover {
  width: 100%;
  overflow: hidden;
}

.h-card__cover :deep(img) {
  width: 100%;
  display: block;
}

.h-card__body {
  padding: var(--harmony-padding-level4);
}

.h-card__header {
  margin-bottom: var(--harmony-padding-level2);
}

.h-card__footer {
  margin-top: var(--harmony-padding-level4);
  padding-top: var(--harmony-padding-level4);
  border-top: 1px solid var(--harmony-comp-divider);
}
</style>
