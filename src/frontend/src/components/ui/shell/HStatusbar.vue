<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  theme?: 'light' | 'dark'
}

const props = withDefaults(defineProps<Props>(), {
  theme: 'light',
})

const currentTime = computed(() => {
  const now = new Date()
  return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
})
</script>

<template>
  <div class="harmony-statusbar" :class="`harmony-statusbar--${theme}`">
    <span class="harmony-statusbar__time">{{ currentTime }}</span>
    <span class="harmony-statusbar__icons">
      <i class="harmony-statusbar__icon harmony-statusbar__icon--wifi" />
      <i class="harmony-statusbar__icon harmony-statusbar__icon--signal" />
      <i class="harmony-statusbar__icon harmony-statusbar__icon--battery" />
    </span>
  </div>
</template>

<style scoped>
.harmony-statusbar {
  width: 360px;
  height: 36px;
  padding: 8px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
  font-family: 'HarmonyOS Sans SC', 'HarmonyOS Sans', sans-serif;
  flex-shrink: 0;
}

.harmony-statusbar--light {
  color: rgba(0, 0, 0, 0.898);
}

.harmony-statusbar--dark {
  color: rgba(255, 255, 255, 1);
}

.harmony-statusbar__time {
  font-size: 15px;
  font-weight: 500;
  line-height: 20px;
}

.harmony-statusbar__icons {
  position: relative;
  width: 96px;
  height: 13px;
  flex: 0 0 auto;
}

.harmony-statusbar__icon {
  position: absolute;
  top: 0;
  width: 15px;
  height: 12px;
  background-size: 100% 100%;
  background-repeat: no-repeat;
}

.harmony-statusbar__icon--wifi {
  left: 0;
  background-image: url('../../../assets/statusbar-wifi-light.png');
}

.harmony-statusbar__icon--signal {
  left: 22px;
  width: 22px;
}

.harmony-statusbar__icon--battery {
  left: 70px;
  width: 26px;
  height: 13px;
  background-image: url('../../../assets/statusbar-battery-light.png');
}

.harmony-statusbar--dark .harmony-statusbar__icon--wifi {
  background-image: url('../../../assets/statusbar-wifi-dark.png');
}

.harmony-statusbar--dark .harmony-statusbar__icon--battery {
  background-image: url('../../../assets/statusbar-battery-dark.png');
}
</style>
