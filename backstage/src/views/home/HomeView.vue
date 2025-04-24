<template>
  <div class="home-container">
    <el-row :gutter="20">
      <el-col :span="4">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>用户总数</span>
            </div>
          </template>
          <div class="card-content">
            <h2>{{ userCount }}</h2>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>课程总数</span>
            </div>
          </template>
          <div class="card-content">
            <h2>{{ courseCount }}</h2>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>产品总数</span>
            </div>
          </template>
          <div class="card-content">
            <h2>{{ productCount }}</h2>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>订单总数</span>
            </div>
          </template>
          <div class="card-content">
            <h2>{{ orderCount }}</h2>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>权益规则总数</span>
            </div>
          </template>
          <div class="card-content">
            <h2>{{ entitlementCount }}</h2>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>用户权益总数</span>
            </div>
          </template>
          <div class="card-content">
            <h2>{{ userEntitlementCount }}</h2>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const userCount = ref(0)
const courseCount = ref(0)
const productCount = ref(0)
const orderCount = ref(0)
const entitlementCount = ref(0)
const userEntitlementCount = ref(0)

const fetchData = async () => {
  try {
    // 获取用户总数
    const userResponse = await axios.get('http://10.7.21.239:4455/api/users/count')
    if (userResponse.data.code === 200) {
      userCount.value = userResponse.data.data.total
    }

    // 获取课程总数
    const courseResponse = await axios.get('http://10.7.21.239:4455/courses/count')
    if (courseResponse.data.code === 200) {
      courseCount.value = courseResponse.data.data.total
    }

    // 获取产品总数
    const productResponse = await axios.get('http://10.7.21.239:4455/ai_products/count')
    if (productResponse.data.code === 200) {
      productCount.value = productResponse.data.data.total
    }

    // 获取订单总数
    const orderResponse = await axios.get('http://10.7.21.239:4455/orders/count')
    if (orderResponse.data.code === 200) {
      orderCount.value = orderResponse.data.data.total
    }

    // 获取权益规则总数
    const entitlementResponse = await axios.get('http://10.7.21.239:4455/entitlement_rules/count')
    if (entitlementResponse.data.code === 200) {
      entitlementCount.value = entitlementResponse.data.data.total
    }

    // 获取用户权益总数
    const userEntitlementResponse = await axios.get(
      'http://10.7.21.239:4455/user_entitlements/count',
    )
    if (userEntitlementResponse.data.code === 200) {
      userEntitlementCount.value = userEntitlementResponse.data.data.total
    }
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.home-container {
  padding: 20px;
}

.data-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-content {
  text-align: center;
  padding: 20px 0;
}

.card-content h2 {
  margin: 0;
  font-size: 24px;
  color: #409eff;
}
</style>
