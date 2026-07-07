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
.h-table-wrapper { overflow-x: auto; border: 1px solid var(--harmony-comp-divider); border-radius: var(--harmony-corner-radius-level6); }
.h-table { width: 100%; border-collapse: collapse; font-size: var(--harmony-font-size-body-m); }
.h-table th, .h-table td { padding: var(--harmony-padding-level6) var(--harmony-padding-level8); text-align: left; border-bottom: 1px solid var(--harmony-comp-divider); color: var(--harmony-font-primary); }
.h-table th { background: var(--harmony-comp-background-tertiary); font-weight: 500; color: var(--harmony-font-secondary); }
.h-table--stripe tbody tr:nth-child(even) { background: var(--harmony-comp-background-tertiary); }
.h-table--stripe tbody tr:hover { background: var(--harmony-interactive-hover); }
.h-table__empty { text-align: center; padding: var(--harmony-padding-level12) var(--harmony-padding-level8); color: var(--harmony-font-tertiary); }
</style>
