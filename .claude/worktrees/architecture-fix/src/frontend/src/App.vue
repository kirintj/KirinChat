<script setup lang="ts">
import { useTheme } from './composables/useTheme'
const { resolved } = useTheme()
</script>

<template>
  <router-view></router-view>
</template> 

<style lang="scss" scoped>


</style>
