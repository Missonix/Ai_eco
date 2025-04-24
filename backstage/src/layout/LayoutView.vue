<template>
  <div class="layout-container">
    <el-container>
      <el-aside width="200px">
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          :router="true"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="/courses">
            <el-icon><Reading /></el-icon>
            <span>课程管理</span>
          </el-menu-item>
          <el-menu-item index="/products">
            <el-icon><Goods /></el-icon>
            <span>产品管理</span>
          </el-menu-item>
          <el-menu-item index="/orders">
            <el-icon><List /></el-icon>
            <span>订单管理</span>
          </el-menu-item>
          <el-menu-item index="/entitlements">
            <el-icon><Ticket /></el-icon>
            <span>权益管理</span>
          </el-menu-item>
          <el-menu-item index="/user-entitlements">
            <el-icon><UserFilled /></el-icon>
            <span>用户权益管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header>
          <div class="header-left">
            <img src="@/assets/logo.png" alt="Logo" class="logo" />
          </div>
          <div class="header-right">
            <span class="username">{{ username }}</span>
            <el-button type="text" @click="handleLogout">退出</el-button>
          </div>
        </el-header>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { HomeFilled, User, Reading, Goods, List, Ticket, UserFilled } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

const username = ref(localStorage.getItem('username') || '')
const activeMenu = computed(() => route.path)

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      type: 'warning',
    })

    // 调用登出接口
    const token = localStorage.getItem('access_token')
    await axios.post('http://10.7.21.239:4455/api/admins/logout', null, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    // 清除本地存储
    localStorage.removeItem('access_token')
    localStorage.removeItem('admin_id')
    localStorage.removeItem('username')

    // 跳转到登录页
    router.push('/login')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('登出失败:', error)
      ElMessage.error('登出失败，请重试')
    }
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.el-container {
  height: 100%;
}

.el-aside {
  background-color: #304156;
}

.el-menu {
  border-right: none;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  height: 40px;
  margin-right: 10px;
  vertical-align: middle;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.username {
  color: #606266;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
