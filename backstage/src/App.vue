<template>
  <el-config-provider>
    <div class="app-container">
      <Navbar />
      <div class="main-content">
        <router-view />
      </div>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { ElConfigProvider } from 'element-plus'
import Navbar from '@/components/Navbar.vue'
</script>

<style>
#app {
  width: 100%;
  height: 100vh;
}

.app-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.main-content {
  flex: 1;
  overflow: auto;
  background-color: #f5f7fa;
}
</style>
