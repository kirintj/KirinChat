<script setup lang="ts">
interface Props {
  data: any[]
  stripe?: boolean
}
withDefaults(defineProps<Props>(), { stripe: false })
</script>

<template>
  <div class="h-table-wrapper">
    <table class="h-table" :class="{ 'h-table--stripe': stripe }">
      <thead>
        <tr><slot name="header" /></tr>
      </thead>
      <tbody>
        <tr v-for="(row, index) in data" :key="index">
          <slot :row="row" :index="index" />
        </tr>
        <tr v-if="data.length === 0">
          <td class="h-table__empty" :colspan="100">暂无数据</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.h-table-wrapper { overflow-x: auto; border: 1px solid var(--color-border); border-radius: var(--radius-md); }
.h-table { width: 100%; border-collapse: collapse; font-size: var(--font-size-base); }
.h-table th, .h-table td { padding: var(--spacing-sm) var(--spacing-md); text-align: left; border-bottom: 1px solid var(--color-border); color: var(--color-text-primary); }
.h-table th { background: var(--color-bg-tertiary); font-weight: 500; color: var(--color-text-secondary); }
.h-table--stripe tbody tr:nth-child(even) { background: var(--color-bg-tertiary); }
.h-table--stripe tbody tr:hover { background: var(--color-bg-hover); }
.h-table__empty { text-align: center; padding: var(--spacing-xl) var(--spacing-md); color: var(--color-text-tertiary); }
</style>
