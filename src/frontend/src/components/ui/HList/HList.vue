<script setup lang="ts">
interface Props {
  clickable?: boolean
}

withDefaults(defineProps<Props>(), {
  clickable: false,
})

const emit = defineEmits<{ click: [event: MouseEvent] }>()
</script>

<template>
  <div
    class="h-list-item"
    :class="{ 'h-list-item--clickable': clickable }"
    @click="clickable && emit('click', $event)"
  >
    <div v-if="$slots.prefix" class="h-list-item__prefix">
      <slot name="prefix" />
    </div>
    <div class="h-list-item__content">
      <div class="h-list-item__title">
        <slot />
      </div>
      <div v-if="$slots.description" class="h-list-item__desc">
        <slot name="description" />
      </div>
    </div>
    <div v-if="$slots.suffix" class="h-list-item__suffix">
      <slot name="suffix" />
    </div>
  </div>
</template>

<style scoped>
.h-list-item {
  display: flex;
  align-items: center;
  padding: var(--harmony-padding-level4) var(--harmony-padding-level4);
  gap: var(--harmony-padding-level4);
  min-height: var(--harmony-control-height-56);
  box-sizing: border-box;
  transition: background var(--harmony-duration-fast) var(--harmony-motion-standard);
}

.h-list-item--clickable {
  cursor: pointer;
  border-radius: var(--harmony-corner-radius-level8);
}

.h-list-item--clickable:hover {
  background: var(--harmony-interactive-hover);
}

.h-list-item--clickable:active {
  background: var(--harmony-interactive-pressed);
}

.h-list-item__prefix {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.h-list-item__content {
  flex: 1;
  min-width: 0;
}

.h-list-item__title {
  font-size: var(--harmony-font-size-body-m);
  color: var(--harmony-font-primary);
  line-height: 1.4;
}

.h-list-item__desc {
  font-size: var(--harmony-font-size-body-s);
  color: var(--harmony-font-tertiary);
  margin-top: var(--harmony-padding-level1);
}

.h-list-item__suffix {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  color: var(--harmony-font-tertiary);
}
</style>
