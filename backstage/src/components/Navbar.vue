<template>
  <el-menu :default-active="activeIndex" class="navbar" mode="horizontal" router>
    <el-menu-item index="/user">用户管理</el-menu-item>
    <el-menu-item index="/course">课程管理</el-menu-item>
    <el-menu-item index="/product">产品管理</el-menu-item>
    <el-menu-item index="/order">订单管理</el-menu-item>
    <el-menu-item index="/entitlement">权益规则</el-menu-item>
    <el-menu-item index="/user-entitlement">用户权益</el-menu-item>
  </el-menu>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeIndex = ref(route.path)

watch(
  () => route.path,
  (newPath) => {
    activeIndex.value = newPath
  },
)
</script>

<style scoped>
.navbar {
  padding: 0 20px;
  border-bottom: 1px solid #dcdfe6;
}
</style>
