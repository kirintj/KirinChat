<script setup lang="ts">
import { inject, ref } from 'vue'
import WorkspaceDesktop from './WorkspaceDesktop.vue'
import WorkspaceMobile from './WorkspaceMobile.vue'

const isMobile = inject<import('vue').Ref<boolean>>('isMobile', ref(false))
</script>

<template>
  <WorkspaceDesktop v-if="!isMobile" />
  <WorkspaceMobile v-else />
</template>
