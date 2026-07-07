/**
 * 通用卡片组件
 * 展示带有图片、标题和描述的基础卡片
 */
<script lang="ts" setup>
interface Props {
  title: string
  detail: string
  type?: string
  imgUrl: string
}

defineProps<Props>()
</script>

<template>
  <div class="common-card">
    <div class="card-content">
      <div class="card-header">
        <img :src="imgUrl" :alt="title" class="card-image" />
        <span class="card-title">{{ title }}</span>
      </div>
      <div class="card-description">
        {{ detail }}
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.common-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 150px;
  background-color: var(--harmony-comp-background-secondary);
  border-radius: var(--harmony-corner-radius-level5);
  padding: 5px 10px;
  margin-right: 15px;
  margin-top: 15px;

  .card-content {
    margin: 5px 0px 0px 10px;

    .card-header {
      display: flex;
      font-size: var(--harmony-font-size-subtitle-l);
      align-items: center;
      font-weight: 600;
      margin-bottom: 15px;

      .card-image {
        margin-right: 10px;
      }

      .card-title {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }

    .card-description {
      font-size: var(--harmony-font-size-body-l);
      font-weight: 500;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }
}
</style>
