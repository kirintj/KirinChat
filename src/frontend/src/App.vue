<script setup lang="ts">
import { useTheme } from './composables/useTheme'
import { HAppShell } from '@/components/ui'
const { resolved } = useTheme()
</script>

<template>
  <HAppShell>
    <template #default="{ isMobile }">
      <router-view v-slot="{ Component, route }">
        <Transition name="harmony-page" mode="out-in">
          <component :is="Component" :key="route.path" />
        </Transition>
      </router-view>
    </template>
  </HAppShell>
</template>

<style scoped>
</style>
